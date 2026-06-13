"""Esquemas de ChargingSession."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class SessionStart(BaseModel):
    station_id: uuid.UUID
    user_id: uuid.UUID | None = None


class SessionEnd(BaseModel):
    kwh_delivered: float = Field(ge=0)
    cost: float | None = Field(default=None, ge=0)


class SessionRead(ORMModel):
    id: uuid.UUID
    station_id: uuid.UUID
    user_id: uuid.UUID | None = None
    started_at: datetime
    ended_at: datetime | None = None
    kwh_delivered: float
    cost: float | None = None
