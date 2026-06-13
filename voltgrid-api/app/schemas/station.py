"""Esquemas de ChargingStation."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import StationStatus
from app.schemas.common import ORMModel


class StationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    location: str = Field(min_length=1, max_length=255)
    lat: float | None = None
    lng: float | None = None
    max_kw: float = Field(gt=0)
    status: StationStatus = StationStatus.offline


class StationUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    lat: float | None = None
    lng: float | None = None
    max_kw: float | None = Field(default=None, gt=0)


class StationStatusUpdate(BaseModel):
    new_status: StationStatus


class StationRead(ORMModel):
    id: uuid.UUID
    name: str
    location: str
    lat: float | None = None
    lng: float | None = None
    max_kw: float
    status: StationStatus
    org_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
