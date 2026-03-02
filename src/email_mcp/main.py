from __future__ import annotations

from pathlib import Path
import time

from sqlmodel import Session, select

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


def _parse_scopes(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [scope.strip() for scope in value.split(",") if scope.strip()]


def _build_auth(settings: Settings):
    if settings.auth_mode == "none":
        return None, None

    if not settings.auth_issuer_url or not settings.auth_resource_server_url:
        raise ValueError("Auth requires EMAIL_MCP_AUTH_ISSUER_URL and EMAIL_MCP_AUTH_RESOURCE_SERVER_URL.")

    from mcp.server.auth.settings import AuthSettings

    auth_settings = AuthSettings(
        issuer_url=settings.auth_issuer_url,
        resource_server_url=settings.auth_resource_server_url,
        required_scopes=_parse_scopes(settings.auth_required_scopes),
    )

    if settings.auth_mode == "bearer":
        if not settings.bearer_token:
            raise ValueError("Bearer auth requires EMAIL_MCP_BEARER_TOKEN.")
        from .auth.auth_bearer import StaticTokenVerifier

        token_verifier = StaticTokenVerifier(
            token=settings.bearer_token,
            scopes=_parse_scopes(settings.auth_required_scopes) or [],
        )
        return auth_settings, token_verifier

    if settings.auth_mode == "oauth":
        from .auth.auth_oauth import PlaceholderOAuthProvider

        return auth_settings, PlaceholderOAuthProvider()

    raise ValueError(f"Unknown auth mode: {settings.auth_mode}")


def _apply_overrides(
    settings: Settings,
    account_name: str | None = None,
    imap_host: str | None = None,
    imap_user: str | None = None,
    imap_password: str | None = None,
) -> Settings:
    if account_name:
        settings.account_name = account_name
    if imap_host:
        settings.imap_host = imap_host
    if imap_user:
        settings.imap_user = imap_user
    if imap_password:
        settings.imap_password = imap_password
    return settings


def _sync_mailbox(settings: Settings, mailbox: str) -> int:
    imap = ImapSync(settings)
    engine = get_engine(_db_path(settings))
    account_id = None
    vector_records: list[tuple[str, str]] = []
    start = time.monotonic()
    with Session(engine) as session:
        account = get_or_create_account(session, settings)
        account_id = account.id
        mailbox_row = get_or_create_mailbox(session, account.id, mailbox)
        last_uid = mailbox_row.last_uid or 0
        max_uid = last_uid
        for message in imap.fetch_messages(mailbox, since_uid=last_uid):
            existing = session.exec(
                select(Message).where(
                    Message.mailbox_id == mailbox_row.id,
                    Message.uid == message.uid,
                )
            ).first()
            if existing:
                continue
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
            if message.uid > max_uid:
                max_uid = message.uid
        if max_uid != last_uid:
            mailbox_row.last_uid = max_uid
            session.add(mailbox_row)
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
    logger.info(
        "Synced mailbox %s for account %s in %.3fs",
        mailbox,
        account_id,
        time.monotonic() - start,
    )
    return 0


def _db_path(settings: Settings) -> Path:
    return settings.data_dir / "email.db"


def build_server():
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception as exc:  # pragma: no cover - optional at runtime
        raise RuntimeError("mcp[cli] is required to run the server.") from exc

    settings = Settings()
    auth_settings, auth_provider_or_verifier = _build_auth(settings)
    app_kwargs = {
        "host": settings.http_host,
        "port": settings.http_port,
        "auth": auth_settings,
    }
    if settings.auth_mode == "bearer":
        app_kwargs["token_verifier"] = auth_provider_or_verifier
    elif settings.auth_mode == "oauth":
        app_kwargs["auth_server_provider"] = auth_provider_or_verifier

    app = FastMCP("email-mcp", **app_kwargs)

    @app.tool()
    def list_mailboxes(account_name: str | None = None, imap_host: str | None = None, imap_user: str | None = None) -> list[str]:
        settings = Settings()
        _apply_overrides(settings, account_name=account_name, imap_host=imap_host, imap_user=imap_user)
        settings.ensure_dirs()
        configure_logging(settings.log_level)
        imap = ImapSync(settings)
        try:
            return imap.list_mailboxes()
        finally:
            imap.disconnect()

    @app.tool()
    def sync_mailbox(
        mailbox: str,
        account_name: str | None = None,
        imap_host: str | None = None,
        imap_user: str | None = None,
        imap_password: str | None = None,
    ) -> str:
        settings = Settings()
        _apply_overrides(
            settings,
            account_name=account_name,
            imap_host=imap_host,
            imap_user=imap_user,
            imap_password=imap_password,
        )
        settings.ensure_dirs()
        configure_logging(settings.log_level)
        migrate(_db_path(settings))
        _sync_mailbox(settings, mailbox)
        return f"Synced {mailbox}"

    from .mcp_tools.label_tools import register_label_tools
    from .mcp_tools.maintenance_tools import register_maintenance_tools
    from .mcp_tools.rules_tools import register_rules_tools
    from .mcp_tools.search_tools import register_search_tools

    register_label_tools(app)
    register_maintenance_tools(app)
    register_rules_tools(app)
    register_search_tools(app)

    return app


def main() -> None:
    settings = Settings()
    settings.ensure_dirs()
    configure_logging(settings.log_level)
    migrate(_db_path(settings))
    app = build_server()
    app.run(transport=settings.transport)


if __name__ == "__main__":
    main()
