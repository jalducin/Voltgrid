"""Lógica de estaciones. `change_status` es el punto único de cambio de estado."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import StationStatus, StatusSource
from app.models.station import ChargingStation
from app.models.status_log import StatusLog
from app.realtime.connection_manager import manager
from app.schemas.station import StationCreate, StationUpdate


async def list_stations(
    db: AsyncSession, *, status_filter: StationStatus | None = None
) -> list[ChargingStation]:
    stmt = select(ChargingStation).order_by(ChargingStation.created_at.desc())
    if status_filter is not None:
        stmt = stmt.where(ChargingStation.status == status_filter)
    return list((await db.execute(stmt)).scalars().all())


async def get_station(db: AsyncSession, station_id: uuid.UUID) -> ChargingStation:
    station = await db.get(ChargingStation, station_id)
    if station is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estación no encontrada")
    return station


async def create_station(
    db: AsyncSession, *, data: StationCreate, org_id: uuid.UUID
) -> ChargingStation:
    station = ChargingStation(
        name=data.name,
        location=data.location,
        lat=data.lat,
        lng=data.lng,
        max_kw=data.max_kw,
        status=data.status,
        org_id=org_id,
        tenant_id=org_id,
    )
    db.add(station)
    await db.flush()
    await db.refresh(station)
    return station


async def update_station(
    db: AsyncSession, station_id: uuid.UUID, data: StationUpdate
) -> ChargingStation:
    station = await get_station(db, station_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(station, field, value)
    await db.flush()
    await db.refresh(station)
    return station


async def delete_station(db: AsyncSession, station_id: uuid.UUID) -> None:
    station = await get_station(db, station_id)
    await db.delete(station)


async def change_status(
    db: AsyncSession,
    station: ChargingStation,
    new_status: StationStatus,
    *,
    source: StatusSource,
    changed_by: uuid.UUID | None,
) -> ChargingStation:
    """Punto ÚNICO de cambio de estado: actualiza, audita en StatusLog y difunde por WS."""
    old_status = station.status
    station.status = new_status
    log = StatusLog(
        station_id=station.id,
        tenant_id=station.tenant_id,
        old_status=old_status,
        new_status=new_status,
        changed_by=changed_by,
        source=source,
    )
    db.add(log)
    await db.flush()
    # Refresca para cargar columnas calculadas en servidor (updated_at) y evitar lazy-load async.
    await db.refresh(station)

    await manager.broadcast(
        station.id,
        {
            "station_id": str(station.id),
            "status": new_status.value,
            "old_status": old_status.value if old_status else None,
            "source": source.value,
            "timestamp": datetime.now(tz=UTC).isoformat(),
        },
    )
    return station
