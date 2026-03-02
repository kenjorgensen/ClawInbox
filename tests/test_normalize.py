from email.message import EmailMessage

from email_mcp.normalize import normalize_message


def test_normalize_plain_text():
    message = EmailMessage()
    message["Subject"] = "Hello"
    message["From"] = "a@example.com"
    message["To"] = "b@example.com"
    message.set_content("Hi there")

    raw = message.as_bytes()
    normalized = normalize_message(raw)

    assert normalized.subject == "Hello"
    assert normalized.from_addr == "a@example.com"
    assert normalized.to_addrs == "b@example.com"
    assert "Hi there" in normalized.text
