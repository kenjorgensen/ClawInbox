from email_mcp.store import store_message


def test_store_message(tmp_path):
    path = store_message(tmp_path, "Account Name", "INBOX/Primary", 42, b"raw")
    assert path.exists()
    assert path.read_bytes() == b"raw"


def test_store_sanitizes_names(tmp_path):
    path = store_message(tmp_path, "Acct/One", "Weird Box", 1, b"data")
    assert "Acct_One" in str(path)
    assert "Weird_Box" in str(path)
