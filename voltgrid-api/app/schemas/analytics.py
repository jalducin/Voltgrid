"""Esquemas de analytics (KPIs y filtros)."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.enums import StationStatus


class AnalyticsFilter(BaseModel):
    """Filtros server-side para KPIs y export."""

    date_from: datetime | None = None
    date_to: datetime | None = None
    location: str | None = None
    min_capacity: float | None = None
    max_capacity: float | None = None
    status: StationStatus | None = None


class StationKPI(BaseModel):
    station_id: uuid.UUID
    name: str
    uptime_pct: float
    kwh_delivered: float
    active_sessions: int


class KPISummary(BaseModel):
    total_stations: int
    total_kwh: float
    active_sessions: int
    avg_uptime_pct: float
    stations: list[StationKPI]
