"""Router de organizaciones (tenants) y whitelabel."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Principal, get_db, get_principal, get_superadmin_db, require_roles
from app.models.enums import RoleEnum
from app.schemas.organization import OrganizationCreate, OrganizationRead, OrganizationUpdate
from app.services import organization_service

router = APIRouter(prefix="/orgs", tags=["organizations"])


@router.post("", response_model=OrganizationRead, status_code=201)
async def create_org(
    data: OrganizationCreate,
    db: AsyncSession = Depends(get_superadmin_db),
) -> OrganizationRead:
    """Crea una organización (solo superadmin)."""
    return await organization_service.create_organization(db, data)


@router.get("", response_model=list[OrganizationRead])
async def list_orgs(db: AsyncSession = Depends(get_superadmin_db)) -> list[OrganizationRead]:
    """Lista todas las organizaciones (solo superadmin)."""
    return await organization_service.list_organizations(db)


@router.get("/me", response_model=OrganizationRead)
async def my_org(
    principal: Principal = Depends(get_principal),
    db: AsyncSession = Depends(get_db),
) -> OrganizationRead:
    """Devuelve la organización del usuario actual (whitelabel)."""
    return await organization_service.get_organization(db, principal.org_id)


@router.patch("/me", response_model=OrganizationRead)
async def update_my_org(
    data: OrganizationUpdate,
    principal: Principal = Depends(require_roles(RoleEnum.org_admin, RoleEnum.superadmin)),
    db: AsyncSession = Depends(get_db),
) -> OrganizationRead:
    """Actualiza el whitelabel de la organización del usuario (org_admin+)."""
    return await organization_service.update_organization(db, principal.org_id, data)
