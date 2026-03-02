from email.message import EmailMessage

from hypothesis import given, strategies as st

from email_mcp.normalize import normalize_message


safe_subject = st.text(
    min_size=0,
    max_size=50,
    alphabet=st.characters(
        blacklist_categories=("Cs", "Cc"),
        blacklist_characters=["\r", "\n"],
    ),
)

safe_body = st.text(min_size=0, max_size=200)


@given(
    subject=safe_subject,
    body=safe_body,
)
def test_normalize_property(subject, body):
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = "a@example.com"
    message["To"] = "b@example.com"
    message.set_content(body)

    raw = message.as_bytes()
    normalized = normalize_message(raw)

    assert normalized.subject.strip() == subject.strip()
