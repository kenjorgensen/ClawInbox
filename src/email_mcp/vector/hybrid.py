from __future__ import annotations

from typing import Iterable

from ..db.models import Message


def hybrid_rank(
    fts_results: Iterable[Message],
    vector_results: Iterable[tuple[Message, float]],
    limit: int = 20,
    alpha: float = 0.6,
) -> list[Message]:
    fts_list = list(fts_results)
    vector_list = list(vector_results)
    scores: dict[int, float] = {}
    ordered: list[int] = []

    for rank, msg in enumerate(fts_list, start=1):
        score = alpha * (1.0 / rank)
        scores[msg.id or 0] = scores.get(msg.id or 0, 0.0) + score
        ordered.append(msg.id or 0)

    for rank, (msg, distance) in enumerate(vector_list, start=1):
        score = (1.0 - alpha) * (1.0 / rank) * (1.0 - distance)
        scores[msg.id or 0] = scores.get(msg.id or 0, 0.0) + score
        ordered.append(msg.id or 0)

    unique_ids = []
    seen = set()
    for msg_id in ordered:
        if msg_id in seen:
            continue
        seen.add(msg_id)
        unique_ids.append(msg_id)

    ranked = sorted(unique_ids, key=lambda mid: scores.get(mid, 0.0), reverse=True)
    id_map = {msg.id: msg for msg in fts_list}
    for msg, _ in vector_list:
        id_map[msg.id] = msg

    return [id_map[mid] for mid in ranked[:limit] if mid in id_map]
