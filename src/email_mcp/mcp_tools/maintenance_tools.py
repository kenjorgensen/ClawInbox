from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from sqlmodel import Session, select

from ..db.engine import get_engine
from ..db.helpers import get_accounts, get_or_create_account
from ..db.models import Label, Message, MessageLabel
from ..settings import Settings
from ..access_log import log_action


def _delete_file(path: str) -> None:
    try:
        Path(path).unlink(missing_ok=True)
    except Exception:
        pass


def purge_messages_internal(
    settings: Settings,
    account_name: str | None = None,
    label: str | None = None,
    older_than_days: int | None = None,
) -> int:
    engine = get_engine(settings.data_dir / "email.db")
    cutoff = None
    if older_than_days is not None:
        cutoff = datetime.utcnow() - timedelta(days=older_than_days)
    with Session(engine) as session:
        accounts = get_accounts(session, account_name)
        if not accounts:
            account = get_or_create_account(session, settings, account_name=account_name)
            accounts = [account]
        count = 0
        for account in accounts:
            statement = select(Message).where(Message.account_id == account.id)
            if cutoff is not None:
                statement = statement.where(Message.created_at < cutoff)
            messages = session.exec(statement).all()
            if label:
                label_row = session.exec(
                    select(Label).where(Label.account_id == account.id, Label.name == label)
                ).first()
                if not label_row:
                    continue
                message_ids = {
                    link.message_id
                    for link in session.exec(
                        select(MessageLabel).where(MessageLabel.label_id == label_row.id)
                    ).all()
                }
                messages = [msg for msg in messages if msg.id in message_ids]
            for message in messages:
                if message.stored_path:
                    _delete_file(message.stored_path)
                session.delete(message)
                count += 1
        session.commit()
    return count


def register_maintenance_tools(app) -> None:
    @app.tool()
    def purge_messages(
        account_name: str | None = None,
        label: str | None = None,
        older_than_days: int | None = None,
    ) -> str:
        settings = Settings()
        count = purge_messages_internal(settings, account_name, label, older_than_days)
        log_action("purge_messages", account_name, "ok", {"count": count})
        return f"Deleted {count} messages."
