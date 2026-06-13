"""Dependencias compartidas: principal autenticado, guards por rol y sesiones de BD."""
from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.db.tenant import set_bypass_rls, set_current_tenant
from app.models.enums import RoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


@dataclass
class Principal:
    """Identidad derivada del access token (sin tocar la BD)."""

    user_id: uuid.UUID
    org_id: uuid.UUID
    role: RoleEnum


async def get_principal(token: str | None = Depends(oauth2_scheme)) -> Principal:
    """Decodifica el access token y devuelve el principal. 401 si es inválido."""
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autenticado")
    try:
        payload = decode_token(token, expected_type="access")
        return Principal(
            user_id=uuid.UUID(payload["sub"]),
            org_id=uuid.UUID(payload["org_id"]),
            role=RoleEnum(payload["role"]),
        )
    except (JWTError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido") from exc


def require_roles(*roles: RoleEnum):
    """Factory de dependencia que exige uno de los roles dados."""

    async def _dep(principal: Principal = Depends(get_principal)) -> Principal:
        if principal.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permiso denegado")
        return principal

    return _dep


async def get_db(principal: Principal = Depends(get_principal)) -> AsyncGenerator[AsyncSession, None]:
    """Sesión con `app.current_tenant` fijado al tenant del usuario (aplica RLS)."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await set_current_tenant(session, principal.org_id)
            yield session


async def get_public_db() -> AsyncGenerator[AsyncSession, None]:
    """Sesión privilegiada (bypass RLS) para rutas cross-tenant: login, refresh, SSO.

    No requiere autenticación. Úsese solo en endpoints públicos de autenticación.
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await set_bypass_rls(session)
            yield session


async def get_superadmin_db(
    principal: Principal = Depends(require_roles(RoleEnum.superadmin)),
) -> AsyncGenerator[AsyncSession, None]:
    """Sesión privilegiada (bypass RLS) restringida a superadmin para gestión cross-tenant."""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await set_bypass_rls(session)
            yield session
