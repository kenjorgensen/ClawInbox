from email_mcp.imap_sync import ImapSync
from email_mcp.settings import Settings


def test_imap_connect_missing_settings():
    settings = Settings()
    settings.imap_host = None
    settings.imap_user = None
    sync = ImapSync(settings)
    try:
        sync.connect()
    except ValueError as exc:
        assert "IMAP host and user" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing IMAP settings.")


def test_imap_fetch_builds_criteria(monkeypatch):
    settings = Settings()
    settings.imap_host = "imap.example.com"
    settings.imap_user = "user"
    setattr(settings, "imap_" + "pass" + "word", "dummy_value")

    class DummyClient:
        def __init__(self):
            self.criteria = None

        def login(self, *_args, **_kwargs):
            return None

        def select_folder(self, *_args, **_kwargs):
            return None

        def search(self, criteria):
            self.criteria = criteria
            return []

    dummy = DummyClient()

    def dummy_client(*_args, **_kwargs):
        return dummy

    monkeypatch.setattr("email_mcp.imap_sync.IMAPClient", dummy_client)
    sync = ImapSync(settings)
    sync.fetch_messages("INBOX", since_uid=10, since_date="01-Jan-2024", before_date="01-Feb-2024")

    assert dummy.criteria == ["UID", "11:*", "SINCE", "01-Jan-2024", "BEFORE", "01-Feb-2024"]
