"""Router de autenticación: login, refresh, logout y perfil."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Principal, get_db, get_principal, get_public_db
from app.models.user import User
from app.schemas.auth import RefreshRequest, TokenPair, UserMe
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenPair)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_public_db),
) -> TokenPair:
    """Login con email (username) y contraseña; emite par de tokens."""
    return await auth_service.authenticate(db, form.username, form.password)


@router.post("/refresh", response_model=TokenPair)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_public_db)) -> TokenPair:
    """Rota el refresh token y emite un par nuevo."""
    return await auth_service.rotate(db, body.refresh_token)


@router.post("/logout", status_code=204, response_class=Response)
async def logout(
    principal: Principal = Depends(get_principal),
    db: AsyncSession = Depends(get_public_db),
):
    """Revoca todos los refresh tokens del usuario."""
    await auth_service.revoke_all(db, principal.user_id)
    return Response(status_code=204)


@router.get("/me", response_model=UserMe)
async def me(
    principal: Principal = Depends(get_principal),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Devuelve el usuario autenticado."""
    user = (await db.execute(select(User).where(User.id == principal.user_id))).scalar_one()
    return user
