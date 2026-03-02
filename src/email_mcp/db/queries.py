from __future__ import annotations

from typing import Iterable

from sqlmodel import Session, select

from .models import Label, Message, MessageLabel


def find_messages_by_subject(session: Session, account_id: int, subject: str) -> Iterable[Message]:
    statement = select(Message).where(Message.account_id == account_id, Message.subject.contains(subject))
    return session.exec(statement).all()


def find_messages_exact_from(session: Session, account_id: int, from_addr: str) -> Iterable[Message]:
    statement = select(Message).where(Message.account_id == account_id, Message.from_addr == from_addr)
    return session.exec(statement).all()


def find_messages_by_label(session: Session, account_id: int, label: str) -> Iterable[Message]:
    label_row = session.exec(
        select(Label).where(Label.account_id == account_id, Label.name == label)
    ).first()
    if not label_row:
        return []
    statement = (
        select(Message)
        .join(MessageLabel, MessageLabel.message_id == Message.id)
        .where(MessageLabel.label_id == label_row.id)
    )
    return session.exec(statement).all()
