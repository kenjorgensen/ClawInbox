from __future__ import annotations

from typing import Iterable

from sqlalchemy import text as sql_text
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


def search_messages_fts(session: Session, account_id: int, query: str, limit: int = 20) -> Iterable[Message]:
    sql = sql_text(
        """
        SELECT
          message.id,
          message.account_id,
          message.mailbox_id,
          message.uid,
          message.subject,
          message.from_addr,
          message.to_addrs,
          message.date,
          message.text,
          message.stored_path,
          message.created_at
        FROM message
        JOIN message_fts ON message_fts.rowid = message.id
        WHERE message.account_id = :account_id
          AND message_fts MATCH :query
        ORDER BY bm25(message_fts)
        LIMIT :limit;
        """
    )
    rows = session.exec(
        sql,
        params={"account_id": account_id, "query": query, "limit": limit},
    ).mappings()
    return [Message(**row) for row in rows]
