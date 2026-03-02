from __future__ import annotations

from datetime import datetime

from sqlmodel import Session, select

from .models import Job


def create_job(session: Session, name: str, account_name: str | None = None) -> Job:
    job = Job(name=name, status="started", account_name=account_name)
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def update_job(session: Session, job_id: int, status: str, message: str | None = None) -> Job | None:
    job = session.exec(select(Job).where(Job.id == job_id)).first()
    if not job:
        return None
    job.status = status
    if status in ("done", "failed"):
        job.finished_at = datetime.utcnow()
    if message is not None:
        job.message = message
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def get_job(session: Session, job_id: int) -> Job | None:
    return session.exec(select(Job).where(Job.id == job_id)).first()
