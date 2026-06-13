"""Pruebas de integración del flujo de autenticación (login, refresh rotation, reuso)."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.asyncio(loop_scope="session")


async def test_login_and_refresh_rotation(client, tenant_a):
    # Login con credenciales del fixture (password secret123).
    me = await client.get("/auth/me", headers=tenant_a["headers"])
    assert me.status_code == 200
    login_email = me.json()["email"]

    resp = await client.post(
        "/auth/login", data={"username": login_email, "password": "secret123"}
    )
    assert resp.status_code == 200, resp.text
    tokens = resp.json()
    assert tokens["access_token"] and tokens["refresh_token"]

    # Refresh rota el token.
    r1 = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r1.status_code == 200, r1.text
    new_tokens = r1.json()
    assert new_tokens["refresh_token"] != tokens["refresh_token"]

    # Reuso del refresh viejo -> 401.
    reuse = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert reuse.status_code == 401


async def test_login_invalid_credentials(client, tenant_a):
    me = await client.get("/auth/me", headers=tenant_a["headers"])
    login_email = me.json()["email"]
    resp = await client.post("/auth/login", data={"username": login_email, "password": "mala"})
    assert resp.status_code == 401
