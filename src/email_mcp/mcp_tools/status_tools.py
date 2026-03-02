from __future__ import annotations

from sqlmodel import Session, select

from ..db.engine import get_engine
from ..db.helpers import get_accounts, get_or_create_account
from ..db.models import Message
from ..settings import Settings
from ..access_log import log_action


def register_status_tools(app) -> None:
    @app.tool()
    def sync_status(account_name: str | None = None) -> dict:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            accounts = get_accounts(session, account_name)
            if not accounts:
                account = get_or_create_account(session, settings, account_name=account_name)
                accounts = [account]
            statuses = []
            for account in accounts:
                total_messages = session.exec(
                    select(Message).where(Message.account_id == account.id)
                ).all()
                statuses.append(
                    {
                        "account": account.name,
                        "emails": len(total_messages),
                        "sync_enabled": account.sync_enabled,
                        "last_pull_at": account.last_pull_at.isoformat() if account.last_pull_at else None,
                        "last_pull_count": account.last_pull_count,
                        "last_pull_status": account.last_pull_status,
                    }
                )
            if account_name:
                log_action("sync_status", account_name, "ok", {"count": 1})
                return statuses[0]
            log_action("sync_status", None, "ok", {"count": len(statuses)})
            return statuses

    @app.tool()
    def set_sync_enabled(enabled: bool, account_name: str | None = None) -> str:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            accounts = get_accounts(session, account_name)
            if not accounts:
                account = get_or_create_account(session, settings, account_name=account_name)
                accounts = [account]
            for account in accounts:
                account.sync_enabled = enabled
                session.add(account)
            session.commit()
        if account_name:
            log_action("set_sync_enabled", account_name, "ok", {"enabled": enabled})
            return f"Sync enabled set to {enabled} for {account_name}"
        log_action("set_sync_enabled", None, "ok", {"enabled": enabled, "count": len(accounts)})
        return f"Sync enabled set to {enabled} for {len(accounts)} accounts"
