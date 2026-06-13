"""Helpers para el contexto de tenant usado por las políticas RLS de PostgreSQL."""
from __future__ import annotations

import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# GUC que leen las políticas RLS: current_setting('app.current_tenant').
TENANT_GUC = "app.current_tenant"
# GUC de bypass controlado para rutas privilegiadas (login, SSO, superadmin, scheduler).
BYPASS_GUC = "app.bypass_rls"


async def set_current_tenant(session: AsyncSession, tenant_id: uuid.UUID) -> None:
    """Fija el tenant actual para la transacción en curso (SET LOCAL).

    Debe ejecutarse dentro de una transacción abierta. Las políticas RLS comparan
    `tenant_id` de cada fila contra este valor.
    """
    # SET LOCAL no admite parámetros bind; set_config(..., is_local=true) sí.
    await session.execute(
        text("SELECT set_config(:guc, :tid, true)"),
        {"guc": TENANT_GUC, "tid": str(tenant_id)},
    )


async def set_bypass_rls(session: AsyncSession) -> None:
    """Activa el bypass de RLS para la transacción en curso (SET LOCAL).

    Uso EXCLUSIVO de rutas privilegiadas que son cross-tenant por naturaleza:
    autenticación (lookup global por email), resolución de dominio SSO, operaciones
    de superadmin y el scheduler (que itera organizaciones). Nunca en rutas de usuario.
    """
    await session.execute(text("SELECT set_config(:guc, 'on', true)"), {"guc": BYPASS_GUC})
