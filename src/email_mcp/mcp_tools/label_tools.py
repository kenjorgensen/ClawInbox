from __future__ import annotations

from sqlmodel import Session, select

from ..db.engine import get_engine
from ..db.helpers import get_accounts, get_or_create_account
from ..db.models import Label, Message, MessageLabel
from ..settings import Settings
from ..access_log import log_action


def create_label_impl(name: str, account_name: str | None = None) -> str:
    settings = Settings()
    engine = get_engine(settings.data_dir / "email.db")
    with Session(engine) as session:
        accounts = get_accounts(session, account_name)
        if not accounts:
            account = get_or_create_account(session, settings, account_name=account_name)
            accounts = [account]
        created = 0
        for account in accounts:
            existing = session.exec(
                select(Label).where(Label.account_id == account.id, Label.name == name)
            ).first()
            if existing:
                continue
            session.add(Label(account_id=account.id, name=name))
            created += 1
        session.commit()
    if account_name:
        result = f"Created label {name}" if created else f"Label already exists: {name}"
        log_action("create_label", account_name, "ok", {"created": created})
        return result
    log_action("create_label", None, "ok", {"created": created})
    return f"Created label {name} for {created} accounts"


def list_labels_impl(account_name: str | None = None) -> list[str]:
    settings = Settings()
    engine = get_engine(settings.data_dir / "email.db")
    with Session(engine) as session:
        accounts = get_accounts(session, account_name)
        if not accounts:
            account = get_or_create_account(session, settings, account_name=account_name)
            accounts = [account]
        labels = []
        for account in accounts:
            rows = session.exec(select(Label).where(Label.account_id == account.id)).all()
            for label in rows:
                if account_name:
                    labels.append(label.name)
                else:
                    labels.append(f"{account.name}:{label.name}")
        log_action("list_labels", account_name, "ok", {"count": len(labels)})
        return labels


def apply_label_impl(message_id: int, label_name: str, account_name: str | None = None) -> str:
    settings = Settings()
    engine = get_engine(settings.data_dir / "email.db")
    with Session(engine) as session:
        message = session.exec(select(Message).where(Message.id == message_id)).first()
        if not message:
            return f"Message not found: {message_id}"
        account_id = message.account_id
        if account_name:
            account = get_or_create_account(session, settings, account_name=account_name)
            account_id = account.id
        label = session.exec(
            select(Label).where(Label.account_id == account_id, Label.name == label_name)
        ).first()
        if not label:
            label = Label(account_id=account_id, name=label_name)
            session.add(label)
            session.commit()
            session.refresh(label)
        existing = session.exec(
            select(MessageLabel).where(MessageLabel.message_id == message.id, MessageLabel.label_id == label.id)
        ).first()
        if existing:
            return f"Label already applied: {label_name}"
        session.add(MessageLabel(message_id=message.id, label_id=label.id))
        session.commit()
    log_action("apply_label", account_name, "ok", {"message_id": message_id, "label": label_name})
    return f"Applied label {label_name} to message {message_id}"


def remove_label_impl(message_id: int, label_name: str, account_name: str | None = None) -> str:
    settings = Settings()
    engine = get_engine(settings.data_dir / "email.db")
    with Session(engine) as session:
        message = session.exec(select(Message).where(Message.id == message_id)).first()
        if not message:
            return f"Message not found: {message_id}"
        account_id = message.account_id
        if account_name:
            account = get_or_create_account(session, settings, account_name=account_name)
            account_id = account.id
        label = session.exec(
            select(Label).where(Label.account_id == account_id, Label.name == label_name)
        ).first()
        if not label:
            return f"Label not found: {label_name}"
        link = session.exec(
            select(MessageLabel).where(MessageLabel.message_id == message_id, MessageLabel.label_id == label.id)
        ).first()
        if not link:
            return f"Label not applied: {label_name}"
        session.delete(link)
        session.commit()
    log_action("remove_label", account_name, "ok", {"message_id": message_id, "label": label_name})
    return f"Removed label {label_name} from message {message_id}"


def register_label_tools(app) -> None:
    @app.tool()
    def create_label(name: str, account_name: str | None = None) -> str:
        return create_label_impl(name, account_name)

    @app.tool()
    def list_labels(account_name: str | None = None) -> list[str]:
        return list_labels_impl(account_name)

    @app.tool()
    def apply_label(message_id: int, label_name: str, account_name: str | None = None) -> str:
        return apply_label_impl(message_id, label_name, account_name)

    @app.tool()
    def remove_label(message_id: int, label_name: str, account_name: str | None = None) -> str:
        return remove_label_impl(message_id, label_name, account_name)
