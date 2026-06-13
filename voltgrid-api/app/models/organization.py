"""Modelo Organization: el tenant raíz (no lleva TenantMixin)."""
from __future__ import annotations

import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    # Whitelabel
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    primary_color: Mapped[str | None] = mapped_column(String(16), nullable=True)

    # org_id y tenant_id son ambos FK a organizations; se fija foreign_keys para desambiguar.
    users: Mapped[list[User]] = relationship(  # noqa: F821
        back_populates="organization", foreign_keys="User.org_id"
    )
    stations: Mapped[list[ChargingStation]] = relationship(  # noqa: F821
        back_populates="organization", foreign_keys="ChargingStation.org_id"
    )
