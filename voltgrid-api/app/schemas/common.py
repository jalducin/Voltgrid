"""Esquemas base compartidos."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """Base para esquemas de lectura que se construyen desde modelos ORM."""

    model_config = ConfigDict(from_attributes=True)
