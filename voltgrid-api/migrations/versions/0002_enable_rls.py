"""Habilita Row Level Security y políticas de aislamiento por tenant.

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-13
"""
from __future__ import annotations

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

# Tablas con tenant_id (organizations es la raíz del tenant y NO lleva RLS).
TENANT_TABLES = [
    "users",
    "stations",
    "charging_sessions",
    "status_logs",
    "scheduler_configs",
    "refresh_tokens",
]

# La política permite acceso si está activo el bypass controlado (rutas privilegiadas)
# o si el tenant_id de la fila coincide con app.current_tenant. Fail-closed si no hay contexto.
_PREDICATE = (
    "(current_setting('app.bypass_rls', true) = 'on' "
    "OR tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)"
)


def upgrade() -> None:
    for table in TENANT_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"CREATE POLICY tenant_isolation ON {table} "
            f"USING {_PREDICATE} WITH CHECK {_PREDICATE}"
        )


def downgrade() -> None:
    for table in TENANT_TABLES:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
