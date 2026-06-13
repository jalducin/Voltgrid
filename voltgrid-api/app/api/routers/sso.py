"""Router de SSO (OIDC) con Google y Microsoft vía Authlib."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_public_db
from app.auth.oauth import oauth, provider_enabled
from app.core.config import settings
from app.models.enums import SsoProvider
from app.services import sso_service

router = APIRouter(prefix="/auth/sso", tags=["sso"])


def _frontend_callback_url() -> str:
    base = settings.CORS_ORIGINS[0] if settings.CORS_ORIGINS else "http://localhost:3000"
    return f"{base}/auth/callback"


@router.get("/{provider}/login")
async def sso_login(provider: str, request: Request) -> RedirectResponse:
    """Redirige al proveedor de identidad para iniciar el flujo OIDC."""
    if not provider_enabled(provider):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SSO '{provider}' no configurado (faltan credenciales)",
        )
    client = oauth.create_client(provider)
    redirect_uri = f"{settings.OAUTH_REDIRECT_BASE_URL}/auth/sso/{provider}/callback"
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/{provider}/callback")
async def sso_callback(
    provider: str, request: Request, db: AsyncSession = Depends(get_public_db)
) -> RedirectResponse:
    """Callback OIDC: intercambia el código, resuelve el tenant y emite tokens."""
    if not provider_enabled(provider):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="SSO no configurado")
    client = oauth.create_client(provider)
    token = await client.authorize_access_token(request)
    userinfo = token.get("userinfo") or await client.userinfo(token=token)
    email = userinfo.get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El proveedor no entregó email")

    pair = await sso_service.login_with_email(db, email, SsoProvider(provider))
    # Redirige al frontend con los tokens en el fragmento (no se registran en logs del servidor).
    target = f"{_frontend_callback_url()}#access_token={pair.access_token}&refresh_token={pair.refresh_token}"
    return RedirectResponse(url=target)
