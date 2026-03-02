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
