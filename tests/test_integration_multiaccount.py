from pathlib import Path

from sqlmodel import Session

from email_mcp.db.engine import get_engine
from email_mcp.db.migrate import migrate
from email_mcp.db.models import Account
from email_mcp.main import sync_mailbox_across_accounts
from email_mcp.settings import Settings


def test_sync_across_accounts(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "email.db"
    migrate(db_path)
    engine = get_engine(db_path)

    with Session(engine) as session:
        session.add(Account(name="a", imap_host="imap.example.com", imap_user="usera"))
        session.add(Account(name="b", imap_host="imap.example.com", imap_user="userb"))
        session.commit()

    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))

    # Avoid network calls by stubbing IMAP methods.
    def _no_fetch(*_args, **_kwargs):
        return []

    def _no_uids(*_args, **_kwargs):
        return []

    monkeypatch.setattr("email_mcp.imap_sync.ImapSync.fetch_messages", _no_fetch)
    monkeypatch.setattr("email_mcp.imap_sync.ImapSync.list_uids", _no_uids)

    settings = Settings()
    settings.ensure_dirs()
    count = sync_mailbox_across_accounts("INBOX", settings)
    assert count == 2
