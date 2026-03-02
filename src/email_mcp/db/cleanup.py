from __future__ import annotations

from sqlmodel import Session, select

from .models import Message, MessageLabel


def delete_messages_by_uids(session: Session, mailbox_id: int, uids: list[int]) -> int:
    if not uids:
        return 0
    messages = session.exec(
        select(Message).where(Message.mailbox_id == mailbox_id, Message.uid.in_(uids))
    ).all()
    if not messages:
        return 0
    message_ids = [msg.id for msg in messages if msg.id is not None]
    if message_ids:
        links = session.exec(select(MessageLabel).where(MessageLabel.message_id.in_(message_ids))).all()
        for link in links:
            session.delete(link)
    for msg in messages:
        if msg.stored_path:
            try:
                from pathlib import Path

                Path(msg.stored_path).unlink(missing_ok=True)
            except Exception:
                pass
        session.delete(msg)
    return len(messages)
