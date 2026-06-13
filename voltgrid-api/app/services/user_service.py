"""Lógica de usuarios dentro de una organización."""
from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.enums import RoleEnum, SsoProvider
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    return (await db.execute(select(User).where(User.email == email))).scalar_one_or_none()


async def list_users(db: AsyncSession) -> list[User]:
    return list((await db.execute(select(User))).scalars().all())


async def create_user(db: AsyncSession, *, data: UserCreate, org_id: uuid.UUID) -> User:
    if await get_by_email(db, data.email) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="email ya registrado")
    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
        org_id=org_id,
        tenant_id=org_id,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def create_sso_user(
    db: AsyncSession, *, email: str, org_id: uuid.UUID, provider: SsoProvider
) -> User:
    user = User(
        email=email,
        hashed_password=None,
        role=RoleEnum.viewer,
        org_id=org_id,
        tenant_id=org_id,
        sso_provider=provider,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user_id: uuid.UUID, data: UserUpdate) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    if data.role is not None:
        user.role = data.role
    if data.password is not None:
        user.hashed_password = hash_password(data.password)
    await db.flush()
    await db.refresh(user)
    return user
