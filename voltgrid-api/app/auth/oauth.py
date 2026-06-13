"""Registro de clientes OAuth/OIDC (Authlib) para SSO con Google y Microsoft.

Los clientes solo se registran si hay credenciales configuradas. Sin ellas, el SSO
queda deshabilitado pero la app funciona con login por contraseña.
"""
from __future__ import annotations

from authlib.integrations.starlette_client import OAuth

from app.core.config import settings

oauth = OAuth()

if settings.google_enabled:
    oauth.register(
        name="google",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

if settings.microsoft_enabled:
    oauth.register(
        name="microsoft",
        client_id=settings.MICROSOFT_CLIENT_ID,
        client_secret=settings.MICROSOFT_CLIENT_SECRET,
        server_metadata_url=(
            f"https://login.microsoftonline.com/{settings.MICROSOFT_TENANT}/v2.0/.well-known/openid-configuration"
        ),
        client_kwargs={"scope": "openid email profile"},
    )


def provider_enabled(provider: str) -> bool:
    return (provider == "google" and settings.google_enabled) or (
        provider == "microsoft" and settings.microsoft_enabled
    )
