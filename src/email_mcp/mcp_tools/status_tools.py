from __future__ import annotations

from sqlmodel import Session, select

from ..db.engine import get_engine
from ..db.helpers import get_or_create_account
from ..db.models import Account, Message
from ..settings import Settings


def register_status_tools(app) -> None:
    @app.tool()
    def sync_status(account_name: str | None = None) -> dict:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            account = get_or_create_account(session, settings, account_name=account_name)
            total_messages = session.exec(
                select(Message).where(Message.account_id == account.id)
            ).all()
            return {
                "account": account.name,
                "emails": len(total_messages),
                "sync_enabled": account.sync_enabled,
                "last_pull_at": account.last_pull_at.isoformat() if account.last_pull_at else None,
                "last_pull_count": account.last_pull_count,
                "last_pull_status": account.last_pull_status,
            }

    @app.tool()
    def set_sync_enabled(enabled: bool, account_name: str | None = None) -> str:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            account = get_or_create_account(session, settings, account_name=account_name)
            account.sync_enabled = enabled
            session.add(account)
            session.commit()
        return f"Sync enabled set to {enabled} for {account_name or settings.account_name}"
