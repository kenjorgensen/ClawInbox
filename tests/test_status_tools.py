from pathlib import Path

from sqlmodel import Session

from email_mcp.db.engine import get_engine
from email_mcp.db.migrate import migrate
from email_mcp.db.models import Account, Mailbox, Message
from email_mcp.mcp_tools.status_tools import register_status_tools


class DummyApp:
    def __init__(self) -> None:
        self.tools = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


def _seed(db_path: Path) -> None:
    engine = get_engine(db_path)
    with Session(engine) as session:
        account_a = Account(name="a", imap_host="imap.a", imap_user="usera")
        account_b = Account(name="b", imap_host="imap.b", imap_user="userb")
        session.add(account_a)
        session.add(account_b)
        session.commit()
        session.refresh(account_a)
        session.refresh(account_b)
        mailbox_a = Mailbox(account_id=account_a.id, name="INBOX")
        mailbox_b = Mailbox(account_id=account_b.id, name="INBOX")
        session.add(mailbox_a)
        session.add(mailbox_b)
        session.commit()
        session.add(Message(account_id=account_a.id, mailbox_id=mailbox_a.id, uid=1, subject="a", from_addr="", to_addrs="", date="", text="", stored_path=""))
        session.add(Message(account_id=account_b.id, mailbox_id=mailbox_b.id, uid=2, subject="b", from_addr="", to_addrs="", date="", text="", stored_path=""))
        session.commit()


def test_sync_status_all_accounts(tmp_path, monkeypatch):
    db_path = tmp_path / "email.db"
    migrate(db_path)
    _seed(db_path)
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))

    app = DummyApp()
    register_status_tools(app)
    status = app.tools["sync_status"]()
    accounts = {item["account"] for item in status}
    assert accounts == {"a", "b"}


def test_set_sync_enabled_all_accounts(tmp_path, monkeypatch):
    db_path = tmp_path / "email.db"
    migrate(db_path)
    _seed(db_path)
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))

    app = DummyApp()
    register_status_tools(app)
    result = app.tools["set_sync_enabled"](False)
    assert "2 accounts" in result
