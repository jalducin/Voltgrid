"""Esquema inicial de VoltGrid (todas las tablas y enums).

Revision ID: 0001
Revises:
Create Date: 2026-06-13
"""
from __future__ import annotations

from alembic import op

from app.models import Base

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # pgcrypto por si se requiere gen_random_uuid en el futuro; los UUID los genera la app.
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")
    bind = op.get_bind()
    # Crea todas las tablas y tipos enum a partir de los modelos registrados.
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
