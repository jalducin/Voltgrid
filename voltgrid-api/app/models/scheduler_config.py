"""Modelo SchedulerConfig: configuración del job de cambio de estado por organización."""
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TenantMixin, TimestampMixin


class SchedulerConfig(Base, TenantMixin, TimestampMixin):
    __tablename__ = "scheduler_configs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    interval_minutes: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    # Id del job en APScheduler (para poder reemplazarlo/eliminarlo).
    job_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
