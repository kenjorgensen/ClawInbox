from pathlib import Path

from sqlmodel import Session

from email_mcp.db.engine import get_engine
from email_mcp.db.migrate import migrate
from email_mcp.db.models import Account, Mailbox, Message
from email_mcp.mcp_tools.maintenance_tools import purge_messages_internal
from email_mcp.settings import Settings


def test_purge_messages(tmp_path: Path):
    db_path = tmp_path / "email.db"
    migrate(db_path)
    engine = get_engine(db_path)

    stored = tmp_path / "message.eml"
    stored.write_text("test")

    with Session(engine) as session:
        account = Account(name="test", imap_host="imap.example.com", imap_user="user")
        session.add(account)
        session.commit()
        session.refresh(account)
        mailbox = Mailbox(account_id=account.id, name="INBOX")
        session.add(mailbox)
        session.commit()
        session.refresh(mailbox)
        session.add(
            Message(
                account_id=account.id,
                mailbox_id=mailbox.id,
                uid=1,
                subject="Hello",
                from_addr="a@example.com",
                to_addrs="b@example.com",
                date="",
                text="body",
                stored_path=str(stored),
            )
        )
        session.commit()

    settings = Settings()
    settings.data_dir = tmp_path
    deleted = purge_messages_internal(settings, account_name="test")
    assert deleted == 1
    assert not stored.exists()


def test_purge_messages_no_label_match(tmp_path: Path):
    db_path = tmp_path / "email.db"
    migrate(db_path)
    engine = get_engine(db_path)

    with Session(engine) as session:
        account = Account(name="test", imap_host="imap.example.com", imap_user="user")
        session.add(account)
        session.commit()

    settings = Settings()
    settings.data_dir = tmp_path
    deleted = purge_messages_internal(settings, account_name="test", label="missing")
    assert deleted == 0
