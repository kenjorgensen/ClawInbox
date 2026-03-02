from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    imap_host: str
    imap_user: str
    sync_enabled: bool = Field(default=True, index=True)
    last_pull_at: datetime | None = Field(default=None, index=True)
    last_pull_count: int = Field(default=0)
    last_pull_status: str = Field(default="")


class Mailbox(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(index=True, foreign_key="account.id")
    name: str = Field(index=True)
    last_uid: int = Field(default=0, index=True)


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


class Rule(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(index=True, foreign_key="account.id")
    name: str = Field(index=True)
    field: str
    pattern: str
    label: str
    enabled: bool = True


class Job(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    status: str = Field(index=True)
    account_name: str | None = Field(default=None, index=True)
    started_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    finished_at: datetime | None = Field(default=None, index=True)
    message: str = Field(default="")
