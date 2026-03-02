from __future__ import annotations

from sqlmodel import Session, select

from ..db.engine import get_engine
from ..db.helpers import get_or_create_account
from ..db.models import Message, Rule
from ..normalize import NormalizedMessage
from ..rules.rules_engine import apply_rules, load_rules
from ..settings import Settings


def register_rules_tools(app) -> None:
    @app.tool()
    def create_rule(name: str, field: str, pattern: str, label: str, enabled: bool = True) -> str:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            account = get_or_create_account(session, settings)
            rule = Rule(
                account_id=account.id,
                name=name,
                field=field,
                pattern=pattern,
                label=label,
                enabled=enabled,
            )
            session.add(rule)
            session.commit()
        return f"Created rule {name}"

    @app.tool()
    def list_rules() -> list[str]:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            account = get_or_create_account(session, settings)
            rules = session.exec(select(Rule).where(Rule.account_id == account.id)).all()
            return [rule.name for rule in rules]

    @app.tool()
    def apply_rules_to_message(message_id: int) -> list[str]:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            account = get_or_create_account(session, settings)
            message = session.exec(select(Message).where(Message.id == message_id)).first()
            if not message:
                return []
            rules = session.exec(select(Rule).where(Rule.account_id == account.id)).all()
            specs = load_rules(rules)
            normalized = NormalizedMessage(
                subject=message.subject,
                from_addr=message.from_addr,
                to_addrs=message.to_addrs,
                date=message.date,
                text=message.text,
            )
            return apply_rules(normalized, specs)
