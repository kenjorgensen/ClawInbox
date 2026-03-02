from email_mcp.main import list_mailboxes_impl
from email_mcp.db.migrate import migrate


class DummyImap:
    def __init__(self, *_args, **_kwargs):
        self.called = False

    def list_mailboxes(self):
        self.called = True
        return ["INBOX", "Sent"]

    def disconnect(self):
        return None


def test_list_mailboxes_impl_single_account(monkeypatch, tmp_path):
    monkeypatch.setenv("EMAIL_MCP_DATA_DIR", str(tmp_path))
    monkeypatch.setenv("EMAIL_MCP_CACHE_DIR", str(tmp_path / "cache"))
    migrate(tmp_path / "email.db")
    monkeypatch.setattr("email_mcp.main.ImapSync", DummyImap)
    result = list_mailboxes_impl("primary")
    assert result["status"] == "ok"
    assert result["account"] == "primary"
    assert result["mailboxes"] == ["INBOX", "Sent"]
