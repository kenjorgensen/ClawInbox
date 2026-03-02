from __future__ import annotations

from sqlmodel import Session, select

from ..db.engine import get_engine
from ..db.helpers import get_or_create_account
from ..db.models import Label, Message, MessageLabel
from ..settings import Settings


def register_label_tools(app) -> None:
    @app.tool()
    def create_label(name: str) -> str:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            account = get_or_create_account(session, settings)
            existing = session.exec(
                select(Label).where(Label.account_id == account.id, Label.name == name)
            ).first()
            if existing:
                return f"Label already exists: {name}"
            label = Label(account_id=account.id, name=name)
            session.add(label)
            session.commit()
        return f"Created label {name}"

    @app.tool()
    def list_labels() -> list[str]:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            account = get_or_create_account(session, settings)
            labels = session.exec(select(Label).where(Label.account_id == account.id)).all()
            return [label.name for label in labels]

    @app.tool()
    def apply_label(message_id: int, label_name: str) -> str:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            account = get_or_create_account(session, settings)
            label = session.exec(
                select(Label).where(Label.account_id == account.id, Label.name == label_name)
            ).first()
            if not label:
                label = Label(account_id=account.id, name=label_name)
                session.add(label)
                session.commit()
                session.refresh(label)
            message = session.exec(select(Message).where(Message.id == message_id)).first()
            if not message:
                return f"Message not found: {message_id}"
            existing = session.exec(
                select(MessageLabel).where(MessageLabel.message_id == message.id, MessageLabel.label_id == label.id)
            ).first()
            if existing:
                return f"Label already applied: {label_name}"
            session.add(MessageLabel(message_id=message.id, label_id=label.id))
            session.commit()
        return f"Applied label {label_name} to message {message_id}"

    @app.tool()
    def remove_label(message_id: int, label_name: str) -> str:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            account = get_or_create_account(session, settings)
            label = session.exec(
                select(Label).where(Label.account_id == account.id, Label.name == label_name)
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
        return f"Removed label {label_name} from message {message_id}"
