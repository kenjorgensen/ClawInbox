from __future__ import annotations

from sqlmodel import Session, select

from ..db.engine import get_engine
from ..db.helpers import get_accounts, get_or_create_account
from ..db.models import Message, Rule
from ..normalize import NormalizedMessage
from ..rules.rules_engine import apply_rules, load_rules
from ..settings import Settings
from ..access_log import log_action


def create_rule_impl(
    name: str,
    field: str,
    pattern: str,
    label: str,
    enabled: bool = True,
    account_name: str | None = None,
) -> str:
    settings = Settings()
    engine = get_engine(settings.data_dir / "email.db")
    with Session(engine) as session:
        accounts = get_accounts(session, account_name)
        if not accounts:
            account = get_or_create_account(session, settings, account_name=account_name)
            accounts = [account]
        created = 0
        for account in accounts:
            rule = Rule(
                account_id=account.id,
                name=name,
                field=field,
                pattern=pattern,
                label=label,
                enabled=enabled,
            )
            session.add(rule)
            created += 1
        session.commit()
    if account_name:
        log_action("create_rule", account_name, "ok", {"created": created})
        return f"Created rule {name}"
    log_action("create_rule", None, "ok", {"created": created})
    return f"Created rule {name} for {created} accounts"


def list_rules_impl(account_name: str | None = None) -> list[str]:
    settings = Settings()
    engine = get_engine(settings.data_dir / "email.db")
    with Session(engine) as session:
        accounts = get_accounts(session, account_name)
        if not accounts:
            account = get_or_create_account(session, settings, account_name=account_name)
            accounts = [account]
        names = []
        for account in accounts:
            rules = session.exec(select(Rule).where(Rule.account_id == account.id)).all()
            for rule in rules:
                if account_name:
                    names.append(rule.name)
                else:
                    names.append(f"{account.name}:{rule.name}")
        log_action("list_rules", account_name, "ok", {"count": len(names)})
        return names


def apply_rules_to_message_impl(message_id: int, account_name: str | None = None) -> list[str]:
    settings = Settings()
    engine = get_engine(settings.data_dir / "email.db")
    with Session(engine) as session:
        message = session.exec(select(Message).where(Message.id == message_id)).first()
        if not message:
            return []
        account_id = message.account_id
        if account_name:
            account = get_or_create_account(session, settings, account_name=account_name)
            account_id = account.id
        rules = session.exec(select(Rule).where(Rule.account_id == account_id)).all()
        specs = load_rules(rules)
        normalized = NormalizedMessage(
            subject=message.subject,
            from_addr=message.from_addr,
            to_addrs=message.to_addrs,
            date=message.date,
            text=message.text,
        )
        labels = apply_rules(normalized, specs)
        log_action("apply_rules_to_message", account_name, "ok", {"count": len(labels)})
        return labels


def register_rules_tools(app) -> None:
    @app.tool()
    def create_rule(
        name: str,
        field: str,
        pattern: str,
        label: str,
        enabled: bool = True,
        account_name: str | None = None,
    ) -> dict:
        return {"status": "ok", "result": create_rule_impl(name, field, pattern, label, enabled, account_name)}

    @app.tool()
    def list_rules(account_name: str | None = None) -> dict:
        return {"status": "ok", "rules": list_rules_impl(account_name)}

    @app.tool()
    def apply_rules_to_message(message_id: int, account_name: str | None = None) -> dict:
        return {"status": "ok", "labels": apply_rules_to_message_impl(message_id, account_name)}
