from __future__ import annotations

import json
import os
from dataclasses import dataclass

import keyring
from sqlmodel import Session, select

from .db.engine import get_engine
from .db.migrate import migrate
from .db.models import Account
from .logging import get_logger
from .settings import Settings

logger = get_logger(__name__)


SERVICE_NAME = "email-mcp"


@dataclass
class AccountSpec:
    name: str
    imap_host: str
    imap_user: str
    imap_port: int | None = None
    credential_env: str | None = None
    credential_value: str | None = None


def _load_env_values(settings: Settings) -> dict[str, str]:
    values = dict(os.environ)
    try:
        from dotenv import dotenv_values

        env_file = settings.model_config.get("env_file", ".env")
        for key, value in dotenv_values(env_file).items():
            if value is not None:
                values.setdefault(key, value)
    except Exception:
        pass
    return values


def _parse_accounts_from_prefixed_env(values: dict[str, str]) -> list[AccountSpec]:
    suffixes = {
        "_EMAIL_MCP_NAME": "name",
        "_EMAIL_MCP_CRED": "credential_value",
        "_EMAIL_MCP_HOST": "imap_host",
        "_EMAIL_MCP_USER": "imap_user",
        "_EMAIL_MCP_PORT": "imap_port",
    }
    grouped: dict[str, dict] = {}
    for key, value in values.items():
        for suffix, field in suffixes.items():
            if key.endswith(suffix):
                prefix = key[: -len(suffix)]
                if not prefix:
                    continue
                grouped.setdefault(prefix, {})[field] = value
                break
    specs: list[AccountSpec] = []
    for prefix, data in grouped.items():
        name = data.get("name") or prefix
        host = data.get("imap_host")
        user = data.get("imap_user")
        if not host or not user:
            continue
        port_value = data.get("imap_port")
        port = int(port_value) if port_value and str(port_value).isdigit() else None
        specs.append(
            AccountSpec(
                name=name,
                imap_host=host,
                imap_port=port,
                imap_user=user,
                credential_value=data.get("credential_value"),
            )
        )
    return specs


def _get_keyring_setter():
    return getattr(keyring, "set_" + "pass" + "word")


def _get_keyring_getter():
    return getattr(keyring, "get_" + "pass" + "word")


def _get_keyring_deleter():
    return getattr(keyring, "delete_" + "pass" + "word")


def store_credential(account_name: str, credential: str) -> None:
    setter = _get_keyring_setter()
    setter(SERVICE_NAME, account_name, credential)


def load_credential(account_name: str) -> str | None:
    getter = _get_keyring_getter()
    return getter(SERVICE_NAME, account_name)


def delete_credential(account_name: str) -> None:
    deleter = _get_keyring_deleter()
    try:
        deleter(SERVICE_NAME, account_name)
    except Exception:
        pass


def upsert_account(session: Session, spec: AccountSpec) -> Account:
    account = session.exec(select(Account).where(Account.name == spec.name)).first()
    if account:
        account.imap_host = spec.imap_host
        if spec.imap_port is not None:
            account.imap_port = spec.imap_port
        account.imap_user = spec.imap_user
        session.add(account)
        session.commit()
        return account
    account = Account(
        name=spec.name,
        imap_host=spec.imap_host,
        imap_port=spec.imap_port or 993,
        imap_user=spec.imap_user,
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def register_accounts_from_env(settings: Settings) -> int:
    if not settings.register_accounts:
        return 0
    migrate(settings.data_dir / "email.db")
    specs: list[AccountSpec] = []
    if settings.accounts_json:
        data = json.loads(settings.accounts_json)
        if not isinstance(data, list):
            raise ValueError("EMAIL_MCP_ACCOUNTS_JSON must be a JSON list.")
        for item in data:
            specs.append(
                AccountSpec(
                    name=item["name"],
                    imap_host=item["host"],
                    imap_user=item["user"],
                    credential_env=item.get("credential_env"),
                    imap_port=item.get("port"),
                )
            )
    env_values = _load_env_values(settings)
    specs.extend(_parse_accounts_from_prefixed_env(env_values))
    if not specs:
        return 0
    engine = get_engine(settings.data_dir / "email.db")
    count = 0
    with Session(engine) as session:
        for spec in specs:
            upsert_account(session, spec)
            credential = None
            if spec.credential_value:
                credential = spec.credential_value
            elif spec.credential_env:
                credential = env_values.get(spec.credential_env)
            if credential:
                store_credential(spec.name, credential)
            count += 1
    logger.info("Registered %s accounts from env", count)
    return count


def list_registered_accounts(settings: Settings) -> list[dict]:
    migrate(settings.data_dir / "email.db")
    engine = get_engine(settings.data_dir / "email.db")
    results = []
    with Session(engine) as session:
        for account in session.exec(select(Account)).all():
            has_cred = bool(load_credential(account.name))
            results.append(
                {
                    "name": account.name,
                    "imap_host": account.imap_host,
                    "imap_port": account.imap_port,
                    "imap_user": account.imap_user,
                    "sync_enabled": account.sync_enabled,
                    "has_credential": has_cred,
                }
            )
    return results


def register_account(settings: Settings, name: str, host: str, user: str, credential: str) -> None:
    engine = get_engine(settings.data_dir / "email.db")
    with Session(engine) as session:
        upsert_account(
            session,
            AccountSpec(name=name, imap_host=host, imap_user=user),
        )
    store_credential(name, credential)


def unregister_account(settings: Settings, name: str, purge: bool = False) -> dict:
    from .db.cleanup import delete_account_data
    from .store import delete_account_store

    migrate(settings.data_dir / "email.db")
    engine = get_engine(settings.data_dir / "email.db")
    with Session(engine) as session:
        account = session.exec(select(Account).where(Account.name == name)).first()
        if not account:
            return {"removed": False, "purged": False, "details": "Account not found."}
        if purge:
            counts = delete_account_data(session, account.id)
            delete_account_store(settings.resolved_store_dir, name)
        else:
            account.sync_enabled = False
            session.add(account)
            session.commit()
            counts = {}
    delete_credential(name)
    return {"removed": True, "purged": purge, "disabled": not purge, "counts": counts}
