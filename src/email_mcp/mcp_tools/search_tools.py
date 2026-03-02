from __future__ import annotations

from sqlmodel import Session, select

from ..db.engine import get_engine
from ..db.helpers import get_or_create_account
from ..db.models import Message
from ..db.queries import (
    find_messages_by_label,
    find_messages_exact_from,
    search_messages_fts,
)
from ..settings import Settings
from ..vector.hybrid import hybrid_rank


def register_search_tools(app) -> None:
    @app.tool()
    def search_messages(query: str, limit: int = 20) -> list[dict]:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            account = get_or_create_account(session, settings)
            results = search_messages_fts(session, account.id, query, limit=limit)
            return [
                {
                    "id": message.id,
                    "subject": message.subject,
                    "from": message.from_addr,
                    "to": message.to_addrs,
                    "date": message.date,
                }
                for message in results
            ]

    @app.tool()
    def search_messages_exact(from_addr: str) -> list[dict]:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            account = get_or_create_account(session, settings)
            results = find_messages_exact_from(session, account.id, from_addr)
            return [
                {
                    "id": message.id,
                    "subject": message.subject,
                    "from": message.from_addr,
                    "to": message.to_addrs,
                    "date": message.date,
                }
                for message in results
            ]

    @app.tool()
    def search_messages_by_label(label: str) -> list[dict]:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            account = get_or_create_account(session, settings)
            results = find_messages_by_label(session, account.id, label)
            return [
                {
                    "id": message.id,
                    "subject": message.subject,
                    "from": message.from_addr,
                    "to": message.to_addrs,
                    "date": message.date,
                }
                for message in results
            ]

    @app.tool()
    def search_messages_hybrid(query: str, limit: int = 20, vector_limit: int = 10) -> list[dict]:
        settings = Settings()
        engine = get_engine(settings.data_dir / "email.db")
        with Session(engine) as session:
            account = get_or_create_account(session, settings)
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
            return [
                {
                    "id": message.id,
                    "subject": message.subject,
                    "from": message.from_addr,
                    "to": message.to_addrs,
                    "date": message.date,
                }
                for message in results
            ]
