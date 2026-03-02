from __future__ import annotations

from typing import Iterable


class Embedder:
    def __init__(self, model_name: str) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except Exception as exc:  # pragma: no cover - optional dependency
            raise RuntimeError("sentence-transformers is not installed. Install with [vector].") from exc
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: Iterable[str]) -> list[list[float]]:
        return self.model.encode(list(texts), convert_to_numpy=True).tolist()
