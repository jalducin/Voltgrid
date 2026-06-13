"""Esquemas de Organization (incluye whitelabel)."""
from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    domain: str = Field(min_length=3, max_length=255)
    logo_url: str | None = None
    primary_color: str | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = None
    logo_url: str | None = None
    primary_color: str | None = None


class OrganizationRead(ORMModel):
    id: uuid.UUID
    name: str
    slug: str
    domain: str
    logo_url: str | None = None
    primary_color: str | None = None
