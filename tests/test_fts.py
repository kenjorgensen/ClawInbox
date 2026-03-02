from pathlib import Path

from sqlmodel import Session

from email_mcp.db.engine import get_engine
from email_mcp.db.migrate import migrate
from email_mcp.db.models import Account, Mailbox, Message
from email_mcp.db.queries import search_messages_fts


def test_fts_search(tmp_path: Path):
    db_path = tmp_path / "email.db"
    migrate(db_path)
    engine = get_engine(db_path)

    account_id = None
    with Session(engine) as session:
        account = Account(name="test", imap_host="imap.example.com", imap_user="user")
        session.add(account)
        session.commit()
        session.refresh(account)
        account_id = account.id
        mailbox = Mailbox(account_id=account.id, name="INBOX")
        session.add(mailbox)
        session.commit()
        session.refresh(mailbox)
        session.add(
            Message(
                account_id=account.id,
                mailbox_id=mailbox.id,
                uid=1,
                subject="Hello World",
                from_addr="a@example.com",
                to_addrs="b@example.com",
                date="",
                text="This is a test message",
                stored_path="",
            )
        )
        session.commit()

    with Session(engine) as session:
        results = search_messages_fts(session, account_id, "test")
        assert len(results) == 1
