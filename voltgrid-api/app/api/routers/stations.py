"""Router de estaciones de carga."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Principal, get_db, get_principal, require_roles
from app.models.enums import RoleEnum, StationStatus, StatusSource
from app.schemas.station import (
    StationCreate,
    StationRead,
    StationStatusUpdate,
    StationUpdate,
)
from app.services import station_service

router = APIRouter(prefix="/stations", tags=["stations"])

_operator = require_roles(RoleEnum.operator, RoleEnum.org_admin, RoleEnum.superadmin)
_admin = require_roles(RoleEnum.org_admin, RoleEnum.superadmin)


@router.get("", response_model=list[StationRead])
async def list_stations(
    status: StationStatus | None = None,
    _: Principal = Depends(get_principal),
    db: AsyncSession = Depends(get_db),
) -> list[StationRead]:
    return await station_service.list_stations(db, status_filter=status)


@router.get("/{station_id}", response_model=StationRead)
async def get_station(
    station_id: uuid.UUID,
    _: Principal = Depends(get_principal),
    db: AsyncSession = Depends(get_db),
) -> StationRead:
    return await station_service.get_station(db, station_id)


@router.post("", response_model=StationRead, status_code=201)
async def create_station(
    data: StationCreate,
    principal: Principal = Depends(_operator),
    db: AsyncSession = Depends(get_db),
) -> StationRead:
    return await station_service.create_station(db, data=data, org_id=principal.org_id)


@router.patch("/{station_id}", response_model=StationRead)
async def update_station(
    station_id: uuid.UUID,
    data: StationUpdate,
    _: Principal = Depends(_operator),
    db: AsyncSession = Depends(get_db),
) -> StationRead:
    return await station_service.update_station(db, station_id, data)


@router.patch("/{station_id}/status", response_model=StationRead)
async def change_station_status(
    station_id: uuid.UUID,
    data: StationStatusUpdate,
    principal: Principal = Depends(_operator),
    db: AsyncSession = Depends(get_db),
) -> StationRead:
    station = await station_service.get_station(db, station_id)
    return await station_service.change_status(
        db, station, data.new_status, source=StatusSource.manual, changed_by=principal.user_id
    )


@router.delete("/{station_id}", status_code=204, response_class=Response)
async def delete_station(
    station_id: uuid.UUID,
    _: Principal = Depends(_admin),
    db: AsyncSession = Depends(get_db),
):
    await station_service.delete_station(db, station_id)
    return Response(status_code=204)
