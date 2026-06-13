"""Router de analytics: KPIs con filtros server-side y export CSV."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import Principal, get_db, get_principal
from app.schemas.analytics import AnalyticsFilter, KPISummary
from app.services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/kpis", response_model=KPISummary)
async def kpis(
    filt: AnalyticsFilter = Depends(),
    _: Principal = Depends(get_principal),
    db: AsyncSession = Depends(get_db),
) -> KPISummary:
    return await analytics_service.get_kpis(db, filt)


@router.get("/export.csv")
async def export_csv(
    filt: AnalyticsFilter = Depends(),
    _: Principal = Depends(get_principal),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    return StreamingResponse(
        analytics_service.export_csv(db, filt),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=voltgrid-analytics.csv"},
    )
