"""Router de configuración del scheduler por organización."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Principal, get_db, require_roles
from app.models.enums import RoleEnum
from app.scheduler.jobs import toggle_station_status
from app.schemas.scheduler import SchedulerConfigRead, SchedulerConfigUpdate
from app.services import scheduler_service

router = APIRouter(prefix="/scheduler", tags=["scheduler"])

_admin = require_roles(RoleEnum.org_admin, RoleEnum.superadmin)


@router.get("/config", response_model=SchedulerConfigRead)
async def get_config(
    principal: Principal = Depends(_admin),
    db: AsyncSession = Depends(get_db),
) -> SchedulerConfigRead:
    return await scheduler_service.get_config(db, principal.org_id)


@router.put("/config", response_model=SchedulerConfigRead)
async def update_config(
    data: SchedulerConfigUpdate,
    principal: Principal = Depends(_admin),
    db: AsyncSession = Depends(get_db),
) -> SchedulerConfigRead:
    return await scheduler_service.update_config(db, principal.org_id, data)


@router.post("/run-now", status_code=202)
async def run_now(
    principal: Principal = Depends(_admin),
) -> dict:
    """Ejecuta el toggle de inmediato para la organización del usuario."""
    await toggle_station_status(str(principal.org_id))
    return {"detail": "Scheduler ejecutado"}
