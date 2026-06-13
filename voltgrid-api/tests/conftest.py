"""Fixtures de pruebas. Las pruebas de integración requieren PostgreSQL real (RLS)."""
from __future__ import annotations

import asyncio
import os
import sys
import uuid

# En Windows, asyncpg requiere SelectorEventLoop (Proactor lanza WinError 64).
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Debe fijarse ANTES de importar la app (settings se cachea al importar).
# La app se conecta como rol NO superusuario (voltgrid_app) para que RLS aplique de verdad.
# El setup del esquema usa un rol admin (superusuario) separado.
os.environ.setdefault("SCHEDULER_ENABLED", "false")
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://voltgrid_app:voltgrid_app@localhost:5432/voltgrid"
)
os.environ.setdefault(
    "SYNC_DATABASE_URL", "postgresql+psycopg://voltgrid_app:voltgrid_app@localhost:5432/voltgrid"
)
ADMIN_URL = os.environ.get(
    "ADMIN_DATABASE_URL", "postgresql+asyncpg://voltgrid:voltgrid@localhost:5432/voltgrid"
)

import pytest_asyncio  # noqa: E402
from asgi_lifespan import LifespanManager  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.ext.asyncio import create_async_engine  # noqa: E402

from app.core.security import create_access_token, hash_password  # noqa: E402
from app.db.session import AsyncSessionLocal, engine  # noqa: E402
from app.db.tenant import set_bypass_rls  # noqa: E402
from app.models import Base  # noqa: E402
from app.models.enums import RoleEnum  # noqa: E402
from app.models.organization import Organization  # noqa: E402
from app.models.user import User  # noqa: E402

_RLS_TABLES = ["users", "stations", "charging_sessions", "status_logs", "scheduler_configs", "refresh_tokens"]
_PRED = (
    "(current_setting('app.bypass_rls', true) = 'on' "
    "OR tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid)"
)


@pytest_asyncio.fixture(scope="session")
async def _setup_schema():
    """Crea rol de app, esquema y políticas RLS (como admin) una vez por sesión."""
    admin = create_async_engine(ADMIN_URL)
    async with admin.begin() as conn:
        # Rol de aplicación NO superusuario y SIN BYPASSRLS (clave para que RLS aplique).
        await conn.execute(
            text(
                "DO $$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='voltgrid_app') "
                "THEN CREATE ROLE voltgrid_app LOGIN PASSWORD 'voltgrid_app' NOSUPERUSER NOBYPASSRLS; "
                "END IF; END $$;"
            )
        )
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        for t in _RLS_TABLES:
            await conn.execute(text(f"ALTER TABLE {t} ENABLE ROW LEVEL SECURITY"))
            await conn.execute(text(f"ALTER TABLE {t} FORCE ROW LEVEL SECURITY"))
            await conn.execute(
                text(f"CREATE POLICY tenant_isolation ON {t} USING {_PRED} WITH CHECK {_PRED}")
            )
        # Privilegios para el rol de app.
        await conn.execute(text("GRANT USAGE ON SCHEMA public TO voltgrid_app"))
        await conn.execute(
            text("GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO voltgrid_app")
        )
        await conn.execute(
            text("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO voltgrid_app")
        )
    await admin.dispose()
    yield
    await engine.dispose()


@pytest_asyncio.fixture
async def client(_setup_schema):
    """Cliente HTTP que maneja la app real (lifespan + ASGI)."""
    from main import app

    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


async def _create_org_and_user(slug: str, domain: str, email: str, role: RoleEnum) -> tuple[uuid.UUID, uuid.UUID]:
    """Crea (con bypass RLS) una organización y un usuario; devuelve (org_id, user_id)."""
    async with AsyncSessionLocal() as db:
        async with db.begin():
            await set_bypass_rls(db)
            org = Organization(name=slug, slug=slug, domain=domain)
            db.add(org)
            await db.flush()
            user = User(
                email=email,
                hashed_password=hash_password("secret123"),
                role=role,
                org_id=org.id,
                tenant_id=org.id,
            )
            db.add(user)
            await db.flush()
            return org.id, user.id


def _headers(user_id: uuid.UUID, org_id: uuid.UUID, role: RoleEnum) -> dict:
    token = create_access_token(user_id=user_id, org_id=org_id, role=role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def tenant_a(_setup_schema):
    suffix = uuid.uuid4().hex[:8]
    org_id, user_id = await _create_org_and_user(
        f"orga-{suffix}", f"orga-{suffix}.example.com", f"admin@orga-{suffix}.example.com", RoleEnum.org_admin
    )
    return {"org_id": org_id, "user_id": user_id, "headers": _headers(user_id, org_id, RoleEnum.org_admin)}


@pytest_asyncio.fixture
async def tenant_b(_setup_schema):
    suffix = uuid.uuid4().hex[:8]
    org_id, user_id = await _create_org_and_user(
        f"orgb-{suffix}", f"orgb-{suffix}.example.com", f"admin@orgb-{suffix}.example.com", RoleEnum.org_admin
    )
    return {"org_id": org_id, "user_id": user_id, "headers": _headers(user_id, org_id, RoleEnum.org_admin)}
