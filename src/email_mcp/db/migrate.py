from __future__ import annotations

from pathlib import Path

from .engine import get_engine, init_db


def migrate(db_path: Path) -> None:
    engine = get_engine(db_path)
    init_db(engine)
