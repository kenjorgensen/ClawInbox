from __future__ import annotations

from pathlib import Path

from sqlmodel import Session

from .db.engine import get_engine
from .db.helpers import get_or_create_account, get_or_create_mailbox
from .db.migrate import migrate
from .db.models import Message
from .imap_sync import ImapSync
from .logging import configure_logging, get_logger
from .normalize import normalize_message
from .settings import Settings
from .store import store_message

logger = get_logger(__name__)


def _sync_mailbox(settings: Settings, mailbox: str) -> int:
    imap = ImapSync(settings)
    engine = get_engine(_db_path(settings))
    account_id = None
    vector_records: list[tuple[str, str]] = []
    with Session(engine) as session:
        account = get_or_create_account(session, settings)
        account_id = account.id
        mailbox_row = get_or_create_mailbox(session, account.id, mailbox)
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
            session.flush()
            if settings.vector_enabled and row.id is not None and normalized.text:
                vector_records.append((str(row.id), normalized.text))
        session.commit()
    if settings.vector_enabled and vector_records:
        try:
            from .vector.embedder import Embedder
            from .vector.chroma_store import ChromaStore
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("Vector search dependencies are not installed. Install with [vector].") from exc
        embedder = Embedder(model_name=settings.embedding_model)
        store = ChromaStore(settings.resolved_vector_dir)
        ids = [item[0] for item in vector_records]
        texts = [item[1] for item in vector_records]
        embeddings = embedder.embed(texts)
        store.upsert(ids=ids, embeddings=embeddings, metadatas=None, documents=texts)
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

    from .mcp_tools.label_tools import register_label_tools
    from .mcp_tools.rules_tools import register_rules_tools
    from .mcp_tools.search_tools import register_search_tools

    register_label_tools(app)
    register_rules_tools(app)
    register_search_tools(app)

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
