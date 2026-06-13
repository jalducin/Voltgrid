"""Modelo ChargingSession: una sesión de carga en una estación."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TenantMixin, TimestampMixin


class ChargingSession(Base, TenantMixin, TimestampMixin):
    __tablename__ = "charging_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    station_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("stations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # ended_at nulo => sesión activa.
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    kwh_delivered: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    cost: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)

    station: Mapped[ChargingStation] = relationship(back_populates="sessions")  # noqa: F821
