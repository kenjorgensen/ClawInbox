from __future__ import annotations

from dataclasses import dataclass
from email import policy
from email.header import decode_header, make_header
from email.message import EmailMessage
from email.parser import BytesParser

import html2text
from bs4 import BeautifulSoup
from charset_normalizer import from_bytes


@dataclass
class NormalizedMessage:
    subject: str
    from_addr: str
    to_addrs: str
    date: str
    text: str


def _extract_text(message: EmailMessage) -> str:
    if message.is_multipart():
        parts = message.walk()
    else:
        parts = [message]

    text_plain = []
    text_html = []
    for part in parts:
        content_type = part.get_content_type()
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        if content_type == "text/plain":
            text_plain.append(_decode_bytes(payload, part.get_content_charset()))
        elif content_type == "text/html":
            text_html.append(_decode_bytes(payload, part.get_content_charset()))

    if text_plain:
        return "\n".join(text_plain).strip()

    if text_html:
        html = "\n".join(text_html)
        # Prefer BeautifulSoup for reliable text extraction, fallback to html2text.
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator="\n")
        if text.strip():
            return text.strip()
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        return converter.handle(html).strip()

    return ""


def normalize_message(raw: bytes) -> NormalizedMessage:
    message = BytesParser(policy=policy.default).parsebytes(raw)
    text = _extract_text(message)
    subject = _decode_subject(message.get("subject", ""))
    return NormalizedMessage(
        subject=subject,
        from_addr=message.get("from", ""),
        to_addrs=message.get("to", ""),
        date=message.get("date", ""),
        text=text,
    )


def _decode_subject(value: str) -> str:
    try:
        decoded = str(make_header(decode_header(value)))
        return decoded
    except Exception:
        return value


def _decode_bytes(payload: bytes, charset: str | None) -> str:
    if charset:
        try:
            return payload.decode(charset, errors="replace")
        except Exception:
            pass
    try:
        return payload.decode("utf-8", errors="replace")
    except Exception:
        pass
    try:
        return payload.decode("latin-1", errors="replace")
    except Exception:
        pass
    try:
        return str(from_bytes(payload).best())
    except Exception:
        return payload.decode("utf-8", errors="replace")
