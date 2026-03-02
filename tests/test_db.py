from pathlib import Path

from sqlmodel import Session, select

from email_mcp.db.engine import get_engine
from email_mcp.db.migrate import migrate
from email_mcp.db.models import Account


def test_db_roundtrip(tmp_path: Path):
    db_path = tmp_path / "email.db"
    migrate(db_path)
    engine = get_engine(db_path)

    with Session(engine) as session:
        session.add(Account(name="test", imap_host="imap.example.com", imap_user="user"))
        session.commit()

    with Session(engine) as session:
        rows = session.exec(select(Account)).all()
        assert len(rows) == 1
        assert rows[0].name == "test"


def test_account_defaults(tmp_path: Path):
    db_path = tmp_path / "email.db"
    migrate(db_path)
    engine = get_engine(db_path)

    with Session(engine) as session:
        session.add(Account(name="acct", imap_host="imap.example.com", imap_user="user"))
        session.commit()

    with Session(engine) as session:
        account = session.exec(select(Account).where(Account.name == "acct")).first()
        assert account is not None
        assert account.sync_enabled is True
