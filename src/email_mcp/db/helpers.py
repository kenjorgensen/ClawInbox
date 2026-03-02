from __future__ import annotations

from sqlmodel import Session, select

from .models import Account, Mailbox
from ..settings import Settings


def get_accounts(session: Session, account_name: str | None = None) -> list[Account]:
    if account_name:
        account = session.exec(select(Account).where(Account.name == account_name)).first()
        return [account] if account else []
    return session.exec(select(Account)).all()


def get_or_create_account(
    session: Session,
    settings: Settings,
    account_name: str | None = None,
    imap_host: str | None = None,
    imap_user: str | None = None,
) -> Account:
    name = account_name or settings.account_name
    host = imap_host or settings.imap_host or ""
    user = imap_user or settings.imap_user or ""
    existing = session.exec(select(Account).where(Account.name == name)).first()
    if existing:
        if host and existing.imap_host != host:
            existing.imap_host = host
        if user and existing.imap_user != user:
            existing.imap_user = user
        session.add(existing)
        session.commit()
        return existing
    account = Account(
        name=name,
        imap_host=host,
        imap_user=user,
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def get_or_create_mailbox(session: Session, account_id: int, mailbox: str) -> Mailbox:
    existing = session.exec(
        select(Mailbox).where(Mailbox.account_id == account_id, Mailbox.name == mailbox)
    ).first()
    if existing:
        return existing
    row = Mailbox(account_id=account_id, name=mailbox)
    session.add(row)
    session.commit()
    session.refresh(row)
    return row
