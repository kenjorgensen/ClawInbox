from __future__ import annotations

from pathlib import Path

from sqlmodel import Session, select

from .db.engine import get_engine
from .db.migrate import migrate
from .db.models import Account, Mailbox, Message
from .imap_sync import ImapSync
from .logging import configure_logging, get_logger
from .normalize import normalize_message
from .settings import Settings
from .store import store_message

logger = get_logger(__name__)


def _get_or_create_account(session: Session, settings: Settings) -> Account:
    existing = session.exec(select(Account).where(Account.name == settings.account_name)).first()
    if existing:
        return existing
    account = Account(
        name=settings.account_name,
        imap_host=settings.imap_host or "",
        imap_user=settings.imap_user or "",
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def _get_or_create_mailbox(session: Session, account_id: int, mailbox: str) -> Mailbox:
    existing = session.exec(
        select(Mailbox).where(Mailbox.account_id == account_id, Mailbox.name == mailbox)
    ).first()
    if existing:
        return existing
    row = Mailbox(account_id=account_id, name=mailbox)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


def _sync_mailbox(settings: Settings, mailbox: str) -> int:
    imap = ImapSync(settings)
    engine = get_engine(_db_path(settings))
    account_id = None
    with Session(engine) as session:
        account = _get_or_create_account(session, settings)
        account_id = account.id
        mailbox_row = _get_or_create_mailbox(session, account.id, mailbox)
        for message in imap.fetch_messages(mailbox):
            normalized = normalize_message(message.raw)
            stored_path = store_message(settings.resolved_store_dir, settings.account_name, mailbox, message.uid, message.raw)
            row = Message(
                account_id=account.id,
                mailbox_id=mailbox_row.id,
                uid=message.uid,
                subject=normalized.subject,
                from_addr=normalized.from_addr,
                to_addrs=normalized.to_addrs,
                date=normalized.date,
                text=normalized.text,
                stored_path=str(stored_path),
            )
            session.add(row)
        session.commit()
    imap.disconnect()
    logger.info("Synced mailbox %s for account %s", mailbox, account_id)
    return 0


def _db_path(settings: Settings) -> Path:
    return settings.data_dir / "email.db"


def build_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:  # pragma: no cover - optional at runtime
        raise RuntimeError("mcp[cli] is required to run the server.") from exc

    app = FastMCP("email-mcp")

    @app.tool()
    def list_mailboxes() -> list[str]:
        settings = Settings()
        settings.ensure_dirs()
        configure_logging(settings.log_level)
        imap = ImapSync(settings)
        try:
            return imap.list_mailboxes()
        finally:
            imap.disconnect()

    @app.tool()
    def sync_mailbox(mailbox: str) -> str:
        settings = Settings()
        settings.ensure_dirs()
        configure_logging(settings.log_level)
        migrate(_db_path(settings))
        _sync_mailbox(settings, mailbox)
        return f"Synced {mailbox}"

    return app


def main() -> None:
    settings = Settings()
    settings.ensure_dirs()
    configure_logging(settings.log_level)
    migrate(_db_path(settings))
    app = build_server()
    app.run()


if __name__ == "__main__":
    main()
