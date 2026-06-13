"""Lógica de SSO: resolución dominio->tenant y auto-provisión de usuario."""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import SsoProvider
from app.schemas.auth import TokenPair
from app.services import auth_service, organization_service, user_service


async def login_with_email(db: AsyncSession, email: str, provider: SsoProvider) -> TokenPair:
    """Autentica un usuario SSO. Resuelve la org por dominio y auto-provisiona si no existe."""
    domain = email.split("@")[-1].lower()
    org = await organization_service.get_by_domain(db, domain)
    if org is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El dominio del correo no corresponde a ninguna organización",
        )
    user = await user_service.get_by_email(db, email)
    if user is None:
        user = await user_service.create_sso_user(db, email=email, org_id=org.id, provider=provider)
    return await auth_service.issue_token_pair(db, user)
