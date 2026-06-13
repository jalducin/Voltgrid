"""Modelo User."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import RoleEnum, SsoProvider
from app.models.mixins import TenantMixin, TimestampMixin


class User(Base, TenantMixin, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    # Nullable: usuarios solo-SSO no tienen contraseña local.
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="role_enum"), nullable=False, default=RoleEnum.viewer
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )
    sso_provider: Mapped[SsoProvider | None] = mapped_column(
        Enum(SsoProvider, name="sso_provider_enum"), nullable=True
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organization: Mapped[Organization] = relationship(  # noqa: F821
        back_populates="users", foreign_keys=[org_id]
    )
    refresh_tokens: Mapped[list[RefreshToken]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )
