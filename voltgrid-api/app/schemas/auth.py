"""Esquemas de autenticación."""
from __future__ import annotations

import uuid

from pydantic import BaseModel, EmailStr

from app.models.enums import RoleEnum
from app.schemas.common import ORMModel


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserMe(ORMModel):
    id: uuid.UUID
    email: EmailStr
    role: RoleEnum
    org_id: uuid.UUID
