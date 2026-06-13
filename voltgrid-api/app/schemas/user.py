"""Esquemas de User."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.models.enums import RoleEnum
from app.schemas.common import ORMModel


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    role: RoleEnum = RoleEnum.viewer


class UserUpdate(BaseModel):
    role: RoleEnum | None = None
    password: str | None = Field(default=None, min_length=6)


class UserRead(ORMModel):
    id: uuid.UUID
    email: EmailStr
    role: RoleEnum
    org_id: uuid.UUID
    last_login: datetime | None = None
