"""Lógica de autenticación: login, emisión y rotación de tokens."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import TokenPair


async def _persist_refresh(
    db: AsyncSession, user: User, raw_token: str, expires_at: datetime
) -> RefreshToken:
    rt = RefreshToken(
        user_id=user.id,
        tenant_id=user.org_id,
        token_hash=hash_token(raw_token),
        expires_at=expires_at,
    )
    db.add(rt)
    await db.flush()
    return rt


async def issue_token_pair(db: AsyncSession, user: User) -> TokenPair:
    """Emite un par de tokens nuevos y persiste el hash del refresh."""
    access = create_access_token(user_id=user.id, org_id=user.org_id, role=user.role.value)
    refresh, expires_at = create_refresh_token(user_id=user.id, org_id=user.org_id)
    await _persist_refresh(db, user, refresh, expires_at)
    return TokenPair(access_token=access, refresh_token=refresh)


async def authenticate(db: AsyncSession, email: str, password: str) -> TokenPair:
    """Valida credenciales y emite tokens. Lanza 401 si son inválidas."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None or user.hashed_password is None or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    user.last_login = datetime.now(tz=UTC)
    return await issue_token_pair(db, user)


async def rotate(db: AsyncSession, refresh_token: str) -> TokenPair:
    """Rota un refresh token. Detecta reuso y revoca la cadena del usuario."""
    try:
        payload = decode_token(refresh_token, expected_type="refresh")
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh inválido") from exc

    token_hash = hash_token(refresh_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    stored = result.scalar_one_or_none()

    user_id = uuid.UUID(payload["sub"])

    # Reuso: el token no existe o ya estaba revocado -> revocar toda la cadena.
    if stored is None or stored.revoked:
        await db.execute(
            update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True)
        )
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh revocado")

    now = datetime.now(tz=UTC)
    if stored.expires_at <= now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh expirado")

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario inexistente")

    # Rotación: revocar el actual y emitir uno nuevo encadenado.
    pair = await issue_token_pair(db, user)
    new_stored = (
        await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == hash_token(pair.refresh_token))
        )
    ).scalar_one()
    stored.revoked = True
    stored.replaced_by = new_stored.id
    return pair


async def revoke_all(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Revoca todos los refresh tokens del usuario (logout)."""
    await db.execute(update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True))
