from __future__ import annotations

from pathlib import Path

from sqlalchemy import text

from .engine import get_engine, init_db


def _init_fts(engine) -> None:
    with engine.begin() as conn:
        conn.exec_driver_sql(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS message_fts USING fts5(
                subject,
                from_addr,
                to_addrs,
                text,
                content='message',
                content_rowid='id'
            );
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TRIGGER IF NOT EXISTS message_fts_insert AFTER INSERT ON message
            BEGIN
              INSERT INTO message_fts(rowid, subject, from_addr, to_addrs, text)
              VALUES (new.id, new.subject, new.from_addr, new.to_addrs, new.text);
            END;
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TRIGGER IF NOT EXISTS message_fts_delete AFTER DELETE ON message
            BEGIN
              INSERT INTO message_fts(message_fts, rowid, subject, from_addr, to_addrs, text)
              VALUES('delete', old.id, old.subject, old.from_addr, old.to_addrs, old.text);
            END;
            """
        )
        conn.exec_driver_sql(
            """
            CREATE TRIGGER IF NOT EXISTS message_fts_update AFTER UPDATE ON message
            BEGIN
              INSERT INTO message_fts(message_fts, rowid, subject, from_addr, to_addrs, text)
              VALUES('delete', old.id, old.subject, old.from_addr, old.to_addrs, old.text);
              INSERT INTO message_fts(rowid, subject, from_addr, to_addrs, text)
              VALUES (new.id, new.subject, new.from_addr, new.to_addrs, new.text);
            END;
            """
        )
        conn.execute(text("INSERT INTO message_fts(message_fts) VALUES ('rebuild');"))


def migrate(db_path: Path) -> None:
    engine = get_engine(db_path)
    init_db(engine)
    _init_fts(engine)
