"""Motor async de SQLAlchemy y dependencia de sesión con contexto de tenant (RLS)."""
from __future__ import annotations

import uuid
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

# Engine async (asyncpg). pool_pre_ping evita conexiones muertas.
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia base: entrega una sesión async sin contexto de tenant.

    Útil para endpoints públicos (login, health) donde aún no hay tenant resuelto.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def get_tenant_session(
    tenant_id: uuid.UUID | None,
) -> AsyncGenerator[AsyncSession, None]:
    """Entrega una sesión con `app.current_tenant` fijado para que aplique RLS.

    El GUC se fija con SET LOCAL dentro de la transacción, por lo que no se filtra
    a otras conexiones del pool. Si `tenant_id` es None, no se fija (fail-closed: las
    políticas RLS devuelven 0 filas).
    """
    from app.db.tenant import set_current_tenant

    async with AsyncSessionLocal() as session:
        async with session.begin():
            if tenant_id is not None:
                await set_current_tenant(session, tenant_id)
            yield session
