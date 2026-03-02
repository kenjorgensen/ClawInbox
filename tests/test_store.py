from email_mcp.store import store_message


def test_store_message(tmp_path):
    path = store_message(tmp_path, "Account Name", "INBOX/Primary", 42, b"raw")
    assert path.exists()
    assert path.read_bytes() == b"raw"
