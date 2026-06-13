"""Modelo StatusLog: bitácora append-only de cambios de estado de estaciones."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import StationStatus, StatusSource
from app.models.mixins import TenantMixin


class StatusLog(Base, TenantMixin):
    __tablename__ = "status_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    old_status: Mapped[StationStatus | None] = mapped_column(
        Enum(StationStatus, name="station_status_enum"), nullable=True
    )
    new_status: Mapped[StationStatus] = mapped_column(
        Enum(StationStatus, name="station_status_enum"), nullable=False
    )
    changed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    source: Mapped[StatusSource] = mapped_column(
        Enum(StatusSource, name="status_source_enum"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    station: Mapped[ChargingStation] = relationship(back_populates="status_logs")  # noqa: F821
