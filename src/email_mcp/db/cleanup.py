from __future__ import annotations

from sqlmodel import Session, select

from .models import Account, Job, Label, Mailbox, Message, MessageLabel, Rule


def delete_messages_by_uids(session: Session, mailbox_id: int, uids: list[int]) -> list[str]:
    if not uids:
        return []
    messages = session.exec(
        select(Message).where(Message.mailbox_id == mailbox_id, Message.uid.in_(uids))
    ).all()
    if not messages:
        return []
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
    return [str(msg.id) for msg in messages if msg.id is not None]


def delete_account_data(session: Session, account_id: int) -> dict:
    messages = session.exec(select(Message).where(Message.account_id == account_id)).all()
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
    mailboxes = session.exec(select(Mailbox).where(Mailbox.account_id == account_id)).all()
    for mailbox in mailboxes:
        session.delete(mailbox)
    labels = session.exec(select(Label).where(Label.account_id == account_id)).all()
    for label in labels:
        session.delete(label)
    rules = session.exec(select(Rule).where(Rule.account_id == account_id)).all()
    for rule in rules:
        session.delete(rule)
    account = session.exec(select(Account).where(Account.id == account_id)).first()
    jobs = []
    if account:
        jobs = session.exec(select(Job).where(Job.account_name == account.name)).all()
        for job in jobs:
            session.delete(job)
        session.delete(account)
    session.commit()
    return {
        "messages": len(messages),
        "mailboxes": len(mailboxes),
        "labels": len(labels),
        "rules": len(rules),
        "jobs": len(jobs),
    }
