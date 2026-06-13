"""Lógica de organizaciones (tenants) y whitelabel."""
from __future__ import annotations

import uuid

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


async def create_organization(db: AsyncSession, data: OrganizationCreate) -> Organization:
    dup = await db.execute(
        select(Organization).where(
            or_(Organization.slug == data.slug, Organization.domain == data.domain)
        )
    )
    if dup.scalar_one_or_none() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="slug o domain ya existe")
    org = Organization(
        name=data.name,
        slug=data.slug,
        domain=data.domain,
        logo_url=data.logo_url,
        primary_color=data.primary_color,
    )
    db.add(org)
    await db.flush()
    await db.refresh(org)
    return org


async def get_organization(db: AsyncSession, org_id: uuid.UUID) -> Organization:
    org = await db.get(Organization, org_id)
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organización no encontrada")
    return org


async def get_by_domain(db: AsyncSession, domain: str) -> Organization | None:
    return (
        await db.execute(select(Organization).where(Organization.domain == domain))
    ).scalar_one_or_none()


async def update_organization(
    db: AsyncSession, org_id: uuid.UUID, data: OrganizationUpdate
) -> Organization:
    org = await get_organization(db, org_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(org, field, value)
    await db.flush()
    await db.refresh(org)
    return org


async def list_organizations(db: AsyncSession) -> list[Organization]:
    return list((await db.execute(select(Organization))).scalars().all())
