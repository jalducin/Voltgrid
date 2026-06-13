"""Gestión del AsyncIOScheduler con jobstore persistente en PostgreSQL."""
from __future__ import annotations

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings

# Jobstore persistente: usa el DSN SYNC (psycopg) porque APScheduler es síncrono internamente.
_jobstores = {"default": SQLAlchemyJobStore(url=settings.SYNC_DATABASE_URL)}

scheduler = AsyncIOScheduler(jobstores=_jobstores, timezone="UTC")


def start() -> None:
    """Arranca el scheduler (rehidrata jobs persistidos)."""
    if not scheduler.running:
        scheduler.start()


def shutdown() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
