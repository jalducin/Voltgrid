"""Endpoints de salud para healthchecks de Docker y probes de Kubernetes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_public_db

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def live() -> dict:
    """Liveness: el proceso responde. No toca la base de datos."""
    return {"status": "ok"}


@router.get("/health/ready")
async def ready(response: Response, db: AsyncSession = Depends(get_public_db)) -> dict:
    """Readiness: verifica conectividad con la base de datos."""
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:  # noqa: BLE001
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unavailable"}


@router.get("/health")
async def health(response: Response, db: AsyncSession = Depends(get_public_db)) -> dict:
    """Alias de readiness para HEALTHCHECK de Docker e Ingress."""
    return await ready(response, db)
