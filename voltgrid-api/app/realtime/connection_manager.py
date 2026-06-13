"""Gestor de conexiones WebSocket: suscriptores por estación y broadcast.

Implementación in-process (un solo proceso). Para escalar horizontalmente se
sustituiría el broadcast por un fan-out vía Redis pub/sub o LISTEN/NOTIFY de Postgres.
"""
from __future__ import annotations

import asyncio
import uuid

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._subscribers: dict[uuid.UUID, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, station_id: uuid.UUID, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._subscribers.setdefault(station_id, set()).add(ws)

    async def disconnect(self, station_id: uuid.UUID, ws: WebSocket) -> None:
        async with self._lock:
            subs = self._subscribers.get(station_id)
            if subs:
                subs.discard(ws)
                if not subs:
                    self._subscribers.pop(station_id, None)

    async def broadcast(self, station_id: uuid.UUID, message: dict) -> None:
        """Envía `message` (JSON) a todos los suscriptores de la estación; poda sockets muertos."""
        async with self._lock:
            subs = list(self._subscribers.get(station_id, set()))
        dead: list[WebSocket] = []
        for ws in subs:
            try:
                await ws.send_json(message)
            except Exception:  # noqa: BLE001 - el socket murió; lo podamos
                dead.append(ws)
        if dead:
            async with self._lock:
                subs_set = self._subscribers.get(station_id)
                if subs_set:
                    for ws in dead:
                        subs_set.discard(ws)


# Singleton de proceso (lo comparten routers WS y el scheduler).
manager = ConnectionManager()
