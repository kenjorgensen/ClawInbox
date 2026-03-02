from __future__ import annotations

from pathlib import Path
from typing import Iterable


class ChromaStore:
    def __init__(self, path: Path) -> None:
        try:
            import chromadb
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("chromadb is not installed. Install with [vector].") from exc
        self.client = chromadb.PersistentClient(path=str(path))
        self.collection = self.client.get_or_create_collection("messages")

    def upsert(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict] | None,
        documents: list[str],
    ) -> None:
        self.collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)

    def query(self, embedding: list[float], n_results: int = 10) -> dict:
        return self.collection.query(query_embeddings=[embedding], n_results=n_results)
