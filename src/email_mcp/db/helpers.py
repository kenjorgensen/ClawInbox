from __future__ import annotations

from sqlmodel import Session, select

from .models import Account, Mailbox
from ..settings import Settings


def get_or_create_account(session: Session, settings: Settings) -> Account:
    existing = session.exec(select(Account).where(Account.name == settings.account_name)).first()
    if existing:
        return existing
    account = Account(
        name=settings.account_name,
        imap_host=settings.imap_host or "",
        imap_user=settings.imap_user or "",
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
