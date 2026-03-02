from __future__ import annotations

from pathlib import Path

from sqlmodel import SQLModel, create_engine


def get_engine(db_path: Path):
    return create_engine(f"sqlite:///{db_path}", echo=False)


def init_db(engine) -> None:
    SQLModel.metadata.create_all(engine)
