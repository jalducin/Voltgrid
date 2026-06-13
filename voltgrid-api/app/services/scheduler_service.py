"""Lógica de configuración del scheduler por organización."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scheduler_config import SchedulerConfig
from app.scheduler.jobs import toggle_station_status
from app.scheduler.manager import scheduler
from app.schemas.scheduler import SchedulerConfigUpdate


async def get_config(db: AsyncSession, org_id: uuid.UUID) -> SchedulerConfig:
    cfg = (
        await db.execute(select(SchedulerConfig).where(SchedulerConfig.org_id == org_id))
    ).scalar_one_or_none()
    if cfg is None:
        cfg = SchedulerConfig(org_id=org_id, tenant_id=org_id, enabled=False, interval_minutes=5)
        db.add(cfg)
        await db.flush()
        await db.refresh(cfg)
    return cfg


def _job_id(org_id: uuid.UUID) -> str:
    return f"toggle:{org_id}"


async def update_config(
    db: AsyncSession, org_id: uuid.UUID, data: SchedulerConfigUpdate
) -> SchedulerConfig:
    cfg = await get_config(db, org_id)
    cfg.enabled = data.enabled
    cfg.interval_minutes = data.interval_minutes
    job_id = _job_id(org_id)

    if data.enabled:
        scheduler.add_job(
            toggle_station_status,
            trigger="interval",
            minutes=data.interval_minutes,
            args=[str(org_id)],
            id=job_id,
            replace_existing=True,
        )
        cfg.job_id = job_id
    else:
        if scheduler.get_job(job_id) is not None:
            scheduler.remove_job(job_id)
        cfg.job_id = None

    await db.flush()
    await db.refresh(cfg)
    return cfg
