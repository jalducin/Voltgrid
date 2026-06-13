"""Lógica de sesiones de carga."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import ChargingSession
from app.schemas.session import SessionEnd, SessionStart


async def list_sessions(db: AsyncSession) -> list[ChargingSession]:
    stmt = select(ChargingSession).order_by(ChargingSession.started_at.desc())
    return list((await db.execute(stmt)).scalars().all())


async def start_session(
    db: AsyncSession, *, data: SessionStart, org_id: uuid.UUID
) -> ChargingSession:
    session = ChargingSession(
        station_id=data.station_id,
        user_id=data.user_id,
        tenant_id=org_id,
        started_at=datetime.now(tz=UTC),
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return session


async def end_session(
    db: AsyncSession, session_id: uuid.UUID, data: SessionEnd
) -> ChargingSession:
    session = await db.get(ChargingSession, session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sesión no encontrada")
    if session.ended_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La sesión ya finalizó")
    session.ended_at = datetime.now(tz=UTC)
    session.kwh_delivered = data.kwh_delivered
    session.cost = data.cost
    await db.flush()
    await db.refresh(session)
    return session
