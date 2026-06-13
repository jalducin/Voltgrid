"""Jobs del scheduler. Ejecutados por APScheduler en el event loop async."""
from __future__ import annotations

import uuid

from app.db.session import AsyncSessionLocal
from app.db.tenant import set_current_tenant
from app.models.enums import StationStatus, StatusSource
from app.services import station_service


async def toggle_station_status(org_id: str) -> None:
    """Alterna el estado de todas las estaciones de una organización.

    available <-> offline. Cada cambio se audita en StatusLog (source=scheduler) y se
    difunde por WebSocket vía `station_service.change_status`.
    """
    tenant_id = uuid.UUID(org_id)
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await set_current_tenant(session, tenant_id)
            stations = await station_service.list_stations(session)
            for st in stations:
                new_status = (
                    StationStatus.offline
                    if st.status == StationStatus.available
                    else StationStatus.available
                )
                await station_service.change_status(
                    session, st, new_status, source=StatusSource.scheduler, changed_by=None
                )
