"""Modelo ChargingStation."""
from __future__ import annotations

import uuid

from sqlalchemy import Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import StationStatus
from app.models.mixins import TenantMixin, TimestampMixin


class ChargingStation(Base, TenantMixin, TimestampMixin):
    __tablename__ = "stations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_kw: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[StationStatus] = mapped_column(
        Enum(StationStatus, name="station_status_enum"),
        nullable=False,
        default=StationStatus.offline,
    )
    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    organization: Mapped[Organization] = relationship(  # noqa: F821
        back_populates="stations", foreign_keys=[org_id]
    )
    sessions: Mapped[list[ChargingSession]] = relationship(  # noqa: F821
        back_populates="station", cascade="all, delete-orphan"
    )
    status_logs: Mapped[list[StatusLog]] = relationship(  # noqa: F821
        back_populates="station", cascade="all, delete-orphan"
    )
