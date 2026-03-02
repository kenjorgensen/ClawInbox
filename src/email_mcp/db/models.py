from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    imap_host: str
    imap_user: str


class Mailbox(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(index=True, foreign_key="account.id")
    name: str = Field(index=True)


class Message(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(index=True, foreign_key="account.id")
    mailbox_id: int = Field(index=True, foreign_key="mailbox.id")
    uid: int = Field(index=True)
    subject: str = ""
    from_addr: str = ""
    to_addrs: str = ""
    date: str = ""
    text: str = ""
    stored_path: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)


class Label(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(index=True, foreign_key="account.id")
    name: str = Field(index=True)


class MessageLabel(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    message_id: int = Field(index=True, foreign_key="message.id")
    label_id: int = Field(index=True, foreign_key="label.id")
