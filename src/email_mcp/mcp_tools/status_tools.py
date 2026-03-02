from __future__ import annotations

from sqlmodel import Session, select

from ..db.engine import get_engine
from ..db.helpers import get_accounts, get_or_create_account
from ..db.models import Message
from ..db.jobs import get_job
from ..settings import Settings
from ..access_log import log_action


def sync_status_impl(account_name: str | None = None) -> dict:
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


def set_sync_enabled_impl(enabled: bool, account_name: str | None = None) -> str:
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


def job_status_impl(job_id: int) -> dict:
    settings = Settings()
    engine = get_engine(settings.data_dir / "email.db")
    with Session(engine) as session:
        job = get_job(session, job_id)
        if not job:
            return {"status": "not_found", "job_id": job_id}
        return {
            "job_id": job.id,
            "name": job.name,
            "status": job.status,
            "account_name": job.account_name,
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "finished_at": job.finished_at.isoformat() if job.finished_at else None,
            "message": job.message,
        }


def register_status_tools(app) -> None:
    @app.tool()
    def sync_status(account_name: str | None = None) -> dict:
        return sync_status_impl(account_name)

    @app.tool()
    def set_sync_enabled(enabled: bool, account_name: str | None = None) -> str:
        return set_sync_enabled_impl(enabled, account_name)

    @app.tool()
    def job_status(job_id: int) -> dict:
        return job_status_impl(job_id)
