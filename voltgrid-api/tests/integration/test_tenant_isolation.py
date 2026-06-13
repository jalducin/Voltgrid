"""Prueba clave: aislamiento entre tenants vía RLS."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_tenant_cannot_read_other_tenant_stations(client, tenant_a, tenant_b):
    # tenant A crea una estación.
    payload = {"name": "EA-1", "location": "A", "max_kw": 50, "status": "available"}
    created = await client.post("/stations", json=payload, headers=tenant_a["headers"])
    assert created.status_code == 201, created.text
    station_id = created.json()["id"]

    # tenant B NO debe ver la estación de A en su listado.
    list_b = await client.get("/stations", headers=tenant_b["headers"])
    assert list_b.status_code == 200
    ids_b = [s["id"] for s in list_b.json()]
    assert station_id not in ids_b

    # tenant B NO debe poder consultarla por id (RLS -> 404).
    get_b = await client.get(f"/stations/{station_id}", headers=tenant_b["headers"])
    assert get_b.status_code == 404

    # tenant A sí la ve.
    list_a = await client.get("/stations", headers=tenant_a["headers"])
    assert station_id in [s["id"] for s in list_a.json()]
