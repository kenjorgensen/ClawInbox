from pathlib import Path

from sqlmodel import Session

from email_mcp.db.cleanup import delete_messages_by_uids
from email_mcp.db.engine import get_engine
from email_mcp.db.migrate import migrate
from email_mcp.db.models import Account, Mailbox, Message


def test_delete_messages_by_uids(tmp_path: Path):
    db_path = tmp_path / "email.db"
    migrate(db_path)
    engine = get_engine(db_path)

    mailbox_id = None
    with Session(engine) as session:
        account = Account(name="test", imap_host="imap.example.com", imap_user="user")
        session.add(account)
        session.commit()
        session.refresh(account)
        mailbox = Mailbox(account_id=account.id, name="INBOX")
        session.add(mailbox)
        session.commit()
        session.refresh(mailbox)
        mailbox_id = mailbox.id
        session.add(Message(account_id=account.id, mailbox_id=mailbox.id, uid=1, subject="a", from_addr="", to_addrs="", date="", text="", stored_path=""))
        session.add(Message(account_id=account.id, mailbox_id=mailbox.id, uid=2, subject="b", from_addr="", to_addrs="", date="", text="", stored_path=""))
        session.commit()

    with Session(engine) as session:
        removed = delete_messages_by_uids(session, mailbox_id, [2])
        session.commit()
        assert len(removed) == 1
