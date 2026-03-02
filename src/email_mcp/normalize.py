from __future__ import annotations

from dataclasses import dataclass
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser

import html2text


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
        if content_type == "text/plain":
            text_plain.append(part.get_content())
        elif content_type == "text/html":
            text_html.append(part.get_content())

    if text_plain:
        return "\n".join(text_plain).strip()

    if text_html:
        converter = html2text.HTML2Text()
        converter.ignore_links = True
        return converter.handle("\n".join(text_html)).strip()

    return ""


def normalize_message(raw: bytes) -> NormalizedMessage:
    message = BytesParser(policy=policy.default).parsebytes(raw)
    text = _extract_text(message)
    return NormalizedMessage(
        subject=message.get("subject", ""),
        from_addr=message.get("from", ""),
        to_addrs=message.get("to", ""),
        date=message.get("date", ""),
        text=text,
    )
