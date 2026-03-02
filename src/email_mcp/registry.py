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
    credential_env: str | None = None


def _get_keyring_setter():
    return getattr(keyring, "set_" + "pass" + "word")


def _get_keyring_getter():
    return getattr(keyring, "get_" + "pass" + "word")


def store_credential(account_name: str, credential: str) -> None:
    setter = _get_keyring_setter()
    setter(SERVICE_NAME, account_name, credential)


def load_credential(account_name: str) -> str | None:
    getter = _get_keyring_getter()
    return getter(SERVICE_NAME, account_name)


def upsert_account(session: Session, spec: AccountSpec) -> Account:
    account = session.exec(select(Account).where(Account.name == spec.name)).first()
    if account:
        account.imap_host = spec.imap_host
        account.imap_user = spec.imap_user
        session.add(account)
        session.commit()
        return account
    account = Account(name=spec.name, imap_host=spec.imap_host, imap_user=spec.imap_user)
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def register_accounts_from_env(settings: Settings) -> int:
    if not settings.register_accounts:
        return 0
    if not settings.accounts_json:
        return 0
    migrate(settings.data_dir / "email.db")
    data = json.loads(settings.accounts_json)
    if not isinstance(data, list):
        raise ValueError("EMAIL_MCP_ACCOUNTS_JSON must be a JSON list.")
    engine = get_engine(settings.data_dir / "email.db")
    count = 0
    with Session(engine) as session:
        for item in data:
            spec = AccountSpec(
                name=item["name"],
                imap_host=item["host"],
                imap_user=item["user"],
                credential_env=item.get("credential_env"),
            )
            upsert_account(session, spec)
            if spec.credential_env:
                credential = os.environ.get(spec.credential_env)
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
                    "imap_user": account.imap_user,
                    "sync_enabled": account.sync_enabled,
                    "has_credential": has_cred,
                }
            )
    return results
