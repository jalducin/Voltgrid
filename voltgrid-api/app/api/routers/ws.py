"""WebSocket de estado de estaciones en tiempo real."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from jose import JWTError

from app.core.security import decode_token
from app.db.session import AsyncSessionLocal
from app.db.tenant import set_current_tenant
from app.models.station import ChargingStation
from app.realtime.connection_manager import manager

router = APIRouter()

# Códigos de cierre WS personalizados.
WS_UNAUTHENTICATED = 4401
WS_FORBIDDEN = 4403


@router.websocket("/ws/stations/{station_id}/status")
async def station_status_ws(websocket: WebSocket, station_id: uuid.UUID) -> None:
    """Canal por estación. Autentica por `?token=` y valida pertenencia al tenant."""
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=WS_UNAUTHENTICATED)
        return
    try:
        payload = decode_token(token, expected_type="access")
        org_id = uuid.UUID(payload["org_id"])
    except (JWTError, KeyError, ValueError):
        await websocket.close(code=WS_UNAUTHENTICATED)
        return

    # Verifica que la estación pertenezca al tenant del usuario (RLS).
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await set_current_tenant(session, org_id)
            station = await session.get(ChargingStation, station_id)
    if station is None:
        await websocket.close(code=WS_FORBIDDEN)
        return

    await manager.connect(station_id, websocket)
    # Snapshot inicial.
    await websocket.send_json({"station_id": str(station_id), "status": station.status.value})
    try:
        while True:
            # Mantiene viva la conexión; ignora el contenido recibido (keepalive/ping).
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(station_id, websocket)
