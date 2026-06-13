"""Router de sesiones de carga."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Principal, get_db, get_principal, require_roles
from app.models.enums import RoleEnum
from app.schemas.session import SessionEnd, SessionRead, SessionStart
from app.services import session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])

_operator = require_roles(RoleEnum.operator, RoleEnum.org_admin, RoleEnum.superadmin)


@router.get("", response_model=list[SessionRead])
async def list_sessions(
    _: Principal = Depends(get_principal),
    db: AsyncSession = Depends(get_db),
) -> list[SessionRead]:
    return await session_service.list_sessions(db)


@router.post("", response_model=SessionRead, status_code=201)
async def start_session(
    data: SessionStart,
    principal: Principal = Depends(_operator),
    db: AsyncSession = Depends(get_db),
) -> SessionRead:
    return await session_service.start_session(db, data=data, org_id=principal.org_id)


@router.post("/{session_id}/end", response_model=SessionRead)
async def end_session(
    session_id: uuid.UUID,
    data: SessionEnd,
    _: Principal = Depends(_operator),
    db: AsyncSession = Depends(get_db),
) -> SessionRead:
    return await session_service.end_session(db, session_id, data)
