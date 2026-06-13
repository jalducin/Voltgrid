"""Seed de datos demo para desarrollo.

Crea una organización demo, un superadmin, un operador y estaciones de ejemplo.
Ejecutar: `python -m scripts.seed` (con la base migrada).
"""
from __future__ import annotations

import asyncio

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.db.tenant import set_bypass_rls
from app.models.enums import RoleEnum, StationStatus
from app.models.organization import Organization
from app.models.station import ChargingStation
from app.models.user import User

DEMO_DOMAIN = "voltgrid.app"


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        async with db.begin():
            await set_bypass_rls(db)

            existing = (
                await db.execute(select(Organization).where(Organization.domain == DEMO_DOMAIN))
            ).scalar_one_or_none()
            if existing is not None:
                print("Seed: la organización demo ya existe; no se hace nada.")
                return

            org = Organization(
                name="VoltGrid Demo",
                slug="demo",
                domain=DEMO_DOMAIN,
                primary_color="#16a34a",
            )
            db.add(org)
            await db.flush()

            db.add_all(
                [
                    User(
                        email=f"admin@{DEMO_DOMAIN}",
                        hashed_password=hash_password("admin123"),
                        role=RoleEnum.superadmin,
                        org_id=org.id,
                        tenant_id=org.id,
                    ),
                    User(
                        email=f"operador@{DEMO_DOMAIN}",
                        hashed_password=hash_password("operador123"),
                        role=RoleEnum.operator,
                        org_id=org.id,
                        tenant_id=org.id,
                    ),
                ]
            )

            stations = [
                ("Estación Centro", "CDMX Centro", 19.4326, -99.1332, 50.0, StationStatus.available),
                ("Estación Norte", "CDMX Norte", 19.5000, -99.1200, 22.0, StationStatus.offline),
                ("Estación Sur", "CDMX Sur", 19.3000, -99.1500, 150.0, StationStatus.available),
                ("Estación Reforma", "Paseo de la Reforma", 19.4270, -99.1677, 75.0, StationStatus.maintenance),
            ]
            db.add_all(
                [
                    ChargingStation(
                        name=n,
                        location=loc,
                        lat=lat,
                        lng=lng,
                        max_kw=kw,
                        status=st,
                        org_id=org.id,
                        tenant_id=org.id,
                    )
                    for (n, loc, lat, lng, kw, st) in stations
                ]
            )
        print("Seed completado: organización demo, usuarios y estaciones creados.")
        print(f"  superadmin: admin@{DEMO_DOMAIN} / admin123")
        print(f"  operator:   operador@{DEMO_DOMAIN} / operador123")


if __name__ == "__main__":
    asyncio.run(seed())
