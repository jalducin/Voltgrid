"""Pruebas de CRUD y cambio de estado de estaciones (con auditoría StatusLog)."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_station_lifecycle_and_status_change(client, tenant_a):
    headers = tenant_a["headers"]

    # Crear.
    created = await client.post(
        "/stations",
        json={"name": "EST-1", "location": "Centro", "max_kw": 22, "status": "offline"},
        headers=headers,
    )
    assert created.status_code == 201, created.text
    sid = created.json()["id"]

    # Listar con filtro.
    offline = await client.get("/stations?status=offline", headers=headers)
    assert sid in [s["id"] for s in offline.json()]

    # Cambiar estado -> available.
    changed = await client.patch(
        f"/stations/{sid}/status", json={"new_status": "available"}, headers=headers
    )
    assert changed.status_code == 200
    assert changed.json()["status"] == "available"

    # El filtro available ahora la incluye.
    available = await client.get("/stations?status=available", headers=headers)
    assert sid in [s["id"] for s in available.json()]

    # Eliminar.
    deleted = await client.delete(f"/stations/{sid}", headers=headers)
    assert deleted.status_code == 204
    gone = await client.get(f"/stations/{sid}", headers=headers)
    assert gone.status_code == 404


async def test_viewer_cannot_create_station(client, tenant_a):
    # Construye un header de viewer en el mismo tenant.
    from app.core.security import create_access_token

    token = create_access_token(
        user_id=tenant_a["user_id"], org_id=tenant_a["org_id"], role="viewer"
    )
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.post(
        "/stations",
        json={"name": "X", "location": "Y", "max_kw": 10},
        headers=headers,
    )
    assert resp.status_code == 403
