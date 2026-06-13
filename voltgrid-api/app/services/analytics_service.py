"""Analytics: KPIs (uptime, kWh, sesiones activas) con filtros server-side y export CSV."""
from __future__ import annotations

import csv
import io
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import StationStatus
from app.models.session import ChargingSession
from app.models.station import ChargingStation
from app.models.status_log import StatusLog
from app.schemas.analytics import AnalyticsFilter, KPISummary, StationKPI


def _window(filt: AnalyticsFilter) -> tuple[datetime, datetime]:
    """Resuelve la ventana de tiempo; por defecto, últimos 30 días."""
    now = datetime.now(tz=UTC)
    date_to = filt.date_to or now
    date_from = filt.date_from or (date_to - timedelta(days=30))
    return date_from, date_to


def _station_filters(filt: AnalyticsFilter) -> list:
    conds = []
    if filt.location:
        conds.append(ChargingStation.location.ilike(f"%{filt.location}%"))
    if filt.min_capacity is not None:
        conds.append(ChargingStation.max_kw >= filt.min_capacity)
    if filt.max_capacity is not None:
        conds.append(ChargingStation.max_kw <= filt.max_capacity)
    if filt.status is not None:
        conds.append(ChargingStation.status == filt.status)
    return conds


async def _filtered_stations(db: AsyncSession, filt: AnalyticsFilter) -> list[ChargingStation]:
    stmt = select(ChargingStation)
    conds = _station_filters(filt)
    if conds:
        stmt = stmt.where(and_(*conds))
    return list((await db.execute(stmt)).scalars().all())


async def _uptime_pct(
    db: AsyncSession, station: ChargingStation, date_from: datetime, date_to: datetime
) -> float:
    """Fracción del tiempo (en %) que la estación estuvo 'available' en la ventana."""
    logs = list(
        (
            await db.execute(
                select(StatusLog)
                .where(
                    StatusLog.station_id == station.id,
                    StatusLog.timestamp >= date_from,
                    StatusLog.timestamp <= date_to,
                )
                .order_by(StatusLog.timestamp.asc())
            )
        ).scalars().all()
    )
    total = (date_to - date_from).total_seconds()
    if total <= 0:
        return 0.0
    if not logs:
        # Sin cambios en la ventana: se asume el estado actual durante todo el periodo.
        return 100.0 if station.status == StationStatus.available else 0.0

    up_seconds = 0.0
    # Estado al inicio = old_status del primer log (o su new_status si no hay old).
    prev_status = logs[0].old_status or logs[0].new_status
    prev_time = date_from
    for log in logs:
        if prev_status == StationStatus.available:
            up_seconds += (log.timestamp - prev_time).total_seconds()
        prev_status = log.new_status
        prev_time = log.timestamp
    # Tramo final hasta date_to.
    if prev_status == StationStatus.available:
        up_seconds += (date_to - prev_time).total_seconds()
    return round(min(100.0, max(0.0, up_seconds / total * 100.0)), 2)


async def get_kpis(db: AsyncSession, filt: AnalyticsFilter) -> KPISummary:
    date_from, date_to = _window(filt)
    stations = await _filtered_stations(db, filt)

    station_kpis: list[StationKPI] = []
    total_kwh = 0.0
    total_active = 0
    for st in stations:
        kwh = (
            await db.execute(
                select(func.coalesce(func.sum(ChargingSession.kwh_delivered), 0.0)).where(
                    ChargingSession.station_id == st.id,
                    ChargingSession.started_at >= date_from,
                    ChargingSession.started_at <= date_to,
                )
            )
        ).scalar_one()
        active = (
            await db.execute(
                select(func.count(ChargingSession.id)).where(
                    ChargingSession.station_id == st.id,
                    ChargingSession.ended_at.is_(None),
                )
            )
        ).scalar_one()
        uptime = await _uptime_pct(db, st, date_from, date_to)
        total_kwh += float(kwh)
        total_active += int(active)
        station_kpis.append(
            StationKPI(
                station_id=st.id,
                name=st.name,
                uptime_pct=uptime,
                kwh_delivered=float(kwh),
                active_sessions=int(active),
            )
        )

    avg_uptime = round(sum(k.uptime_pct for k in station_kpis) / len(station_kpis), 2) if station_kpis else 0.0
    return KPISummary(
        total_stations=len(stations),
        total_kwh=round(total_kwh, 2),
        active_sessions=total_active,
        avg_uptime_pct=avg_uptime,
        stations=station_kpis,
    )


async def export_csv(db: AsyncSession, filt: AnalyticsFilter) -> AsyncGenerator[str, None]:
    """Genera el CSV de KPIs por estación, fila a fila (streaming)."""
    summary = await get_kpis(db, filt)
    header_buf = io.StringIO()
    writer = csv.writer(header_buf)
    writer.writerow(["station_id", "name", "uptime_pct", "kwh_delivered", "active_sessions"])
    yield header_buf.getvalue()
    for k in summary.stations:
        row_buf = io.StringIO()
        csv.writer(row_buf).writerow(
            [str(k.station_id), k.name, k.uptime_pct, k.kwh_delivered, k.active_sessions]
        )
        yield row_buf.getvalue()
