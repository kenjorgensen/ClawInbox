from __future__ import annotations

import time

from sqlmodel import Session, select

from ..db.engine import get_engine
from ..db.helpers import get_accounts, get_or_create_account
from ..db.models import Message
from ..db.queries import (
    find_messages_by_label,
    find_messages_exact_from,
    search_messages_fts,
)
from ..settings import Settings
from ..vector.hybrid import hybrid_rank
from ..access_log import log_action
from ..logging import get_logger

logger = get_logger(__name__)


def search_messages_impl(query: str, limit: int = 20, account_name: str | None = None) -> list[dict]:
    start = time.monotonic()
    settings = Settings()
    engine = get_engine(settings.data_dir / "email.db")
    with Session(engine) as session:
        accounts = get_accounts(session, account_name)
        if not accounts:
            account = get_or_create_account(session, settings, account_name=account_name)
            accounts = [account]
        payload = []
        total = 0
        for account in accounts:
            results = search_messages_fts(session, account.id, query, limit=limit)
            total += len(results)
            payload.extend(
                {
                    "account": account.name,
                    "id": message.id,
                    "subject": message.subject,
                    "from": message.from_addr,
                    "to": message.to_addrs,
                    "date": message.date,
                }
                for message in results
            )
        logger.info("search_messages took %.3fs (results=%s)", time.monotonic() - start, total)
        log_action("search_messages", account_name, "ok", {"count": total})
        return payload


def search_messages_exact_impl(from_addr: str, account_name: str | None = None) -> list[dict]:
    start = time.monotonic()
    settings = Settings()
    engine = get_engine(settings.data_dir / "email.db")
    with Session(engine) as session:
        accounts = get_accounts(session, account_name)
        if not accounts:
            account = get_or_create_account(session, settings, account_name=account_name)
            accounts = [account]
        payload = []
        total = 0
        for account in accounts:
            results = find_messages_exact_from(session, account.id, from_addr)
            total += len(results)
            payload.extend(
                {
                    "account": account.name,
                    "id": message.id,
                    "subject": message.subject,
                    "from": message.from_addr,
                    "to": message.to_addrs,
                    "date": message.date,
                }
                for message in results
            )
        logger.info("search_messages_exact took %.3fs (results=%s)", time.monotonic() - start, total)
        log_action("search_messages_exact", account_name, "ok", {"count": total})
        return payload


def search_messages_by_label_impl(label: str, account_name: str | None = None) -> list[dict]:
    start = time.monotonic()
    settings = Settings()
    engine = get_engine(settings.data_dir / "email.db")
    with Session(engine) as session:
        accounts = get_accounts(session, account_name)
        if not accounts:
            account = get_or_create_account(session, settings, account_name=account_name)
            accounts = [account]
        payload = []
        total = 0
        for account in accounts:
            results = find_messages_by_label(session, account.id, label)
            total += len(results)
            payload.extend(
                {
                    "account": account.name,
                    "id": message.id,
                    "subject": message.subject,
                    "from": message.from_addr,
                    "to": message.to_addrs,
                    "date": message.date,
                }
                for message in results
            )
        logger.info("search_messages_by_label took %.3fs (results=%s)", time.monotonic() - start, total)
        log_action("search_messages_by_label", account_name, "ok", {"count": total})
        return payload


def search_messages_hybrid_impl(
    query: str,
    limit: int = 20,
    vector_limit: int = 10,
    account_name: str | None = None,
) -> list[dict]:
    start = time.monotonic()
    settings = Settings()
    engine = get_engine(settings.data_dir / "email.db")
    with Session(engine) as session:
        accounts = get_accounts(session, account_name)
        if not accounts:
            account = get_or_create_account(session, settings, account_name=account_name)
            accounts = [account]
        payload = []
        total = 0
        for account in accounts:
            fts_results = search_messages_fts(session, account.id, query, limit=limit)
            if not settings.vector_enabled:
                results = fts_results
            else:
                try:
                    from ..vector.chroma_store import ChromaStore
                    from ..vector.embedder import Embedder
                except Exception as exc:  # pragma: no cover - optional dependency
                    raise RuntimeError("Vector search dependencies are not installed. Install with [vector].") from exc
                embedder = Embedder(model_name=settings.embedding_model)
                store = ChromaStore(settings.resolved_vector_dir)
                embedding = embedder.embed([query])[0]
                response = store.query(embedding, n_results=vector_limit)
                ids = [int(item) for item in response.get("ids", [[]])[0]]
                distances = response.get("distances", [[]])[0]
                messages = session.exec(select(Message).where(Message.id.in_(ids))).all()
                message_map = {msg.id: msg for msg in messages}
                vector_results = [
                    (message_map[msg_id], dist)
                    for msg_id, dist in zip(ids, distances)
                    if msg_id in message_map
                ]
                results = hybrid_rank(fts_results, vector_results, limit=limit)
            total += len(results)
            payload.extend(
                {
                    "account": account.name,
                    "id": message.id,
                    "subject": message.subject,
                    "from": message.from_addr,
                    "to": message.to_addrs,
                    "date": message.date,
                }
                for message in results
            )
        logger.info("search_messages_hybrid took %.3fs (results=%s)", time.monotonic() - start, total)
        log_action("search_messages_hybrid", account_name, "ok", {"count": total})
        return payload


def register_search_tools(app) -> None:
    @app.tool()
    def search_messages(query: str, limit: int = 20, account_name: str | None = None) -> dict:
        return {"status": "ok", "results": search_messages_impl(query, limit, account_name)}

    @app.tool()
    def search_messages_exact(from_addr: str, account_name: str | None = None) -> dict:
        return {"status": "ok", "results": search_messages_exact_impl(from_addr, account_name)}

    @app.tool()
    def search_messages_by_label(label: str, account_name: str | None = None) -> dict:
        return {"status": "ok", "results": search_messages_by_label_impl(label, account_name)}

    @app.tool()
    def search_messages_hybrid(
        query: str,
        limit: int = 20,
        vector_limit: int = 10,
        account_name: str | None = None,
    ) -> dict:
        return {"status": "ok", "results": search_messages_hybrid_impl(query, limit, vector_limit, account_name)}
