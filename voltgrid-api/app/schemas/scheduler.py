"""Esquemas del scheduler por organización."""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.common import ORMModel


class SchedulerConfigUpdate(BaseModel):
    enabled: bool
    interval_minutes: int = Field(ge=1, le=1440)


class SchedulerConfigRead(ORMModel):
    enabled: bool
    interval_minutes: int
