"""Router de usuarios dentro de una organización."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Principal, get_db, require_roles
from app.models.enums import RoleEnum
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])

_admin = require_roles(RoleEnum.org_admin, RoleEnum.superadmin)


@router.get("", response_model=list[UserRead])
async def list_users(
    _: Principal = Depends(_admin),
    db: AsyncSession = Depends(get_db),
) -> list[UserRead]:
    return await user_service.list_users(db)


@router.post("", response_model=UserRead, status_code=201)
async def create_user(
    data: UserCreate,
    principal: Principal = Depends(_admin),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    return await user_service.create_user(db, data=data, org_id=principal.org_id)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    _: Principal = Depends(_admin),
    db: AsyncSession = Depends(get_db),
) -> UserRead:
    return await user_service.update_user(db, user_id, data)
