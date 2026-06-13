---
description: Estándares del backend VoltGrid (FastAPI, SQLAlchemy 2.0 async, PostgreSQL + RLS, Alembic, auth JWT, WebSockets, APScheduler, pytest).
alwaysApply: true
---

# Estándares del backend (voltgrid-api)

> Aplica a todo el código bajo `voltgrid-api/`. Complementa `docs/base-standards.md`.

## 1. Stack y versiones

- Python 3.12. FastAPI. SQLAlchemy 2.0 **async** (`Mapped`/`mapped_column`, `AsyncSession`).
- PostgreSQL 16 con **Row Level Security (RLS)**. Driver async `asyncpg`; driver sync `psycopg`
  únicamente para el jobstore de APScheduler.
- Alembic para migraciones. `pydantic-settings` v2 para configuración. `python-jose` (JWT),
  `passlib[bcrypt]` (hashing), `Authlib` (SSO OIDC), `APScheduler` (`AsyncIOScheduler`).

## 2. Arquitectura por capas

```
api/routers (HTTP, validación I/O)  ->  services (lógica de negocio)  ->  models + db (persistencia)
```

- Los **routers** son delgados: validan entrada, llaman a un service y serializan salida. Sin SQL en routers.
- Los **services** concentran la lógica y son la única vía para mutar estado del dominio.
- `station_service.change_status()` es el **punto único** de cambio de estado de una estación:
  actualiza la estación, escribe un `StatusLog` y difunde por WebSocket. Manual, API y scheduler pasan por ahí.

## 3. Multi-tenancy y RLS (invariante de seguridad)

- Toda tabla con datos de cliente lleva `tenant_id` (vía `TenantMixin`) y tiene RLS habilitado + forzado.
- La política `tenant_isolation` filtra por `current_setting('app.current_tenant', true)::uuid`.
- El `get_db` fija `SET LOCAL app.current_tenant = :tid` dentro de la transacción del request, a partir del
  `org_id` del usuario autenticado. **Nunca** confiar solo en `WHERE tenant_id = ...` en la app: RLS es la frontera.
- La aplicación se conecta con un rol DB **no-superusuario y sin BYPASSRLS**.
- `superadmin` y el scheduler fijan `app.current_tenant` explícitamente por organización al operar cross-tenant.
- Prueba obligatoria: `tests/integration/test_tenant_isolation.py` (tenant A no puede leer datos de tenant B).

## 4. Modelos y esquemas

- PK `UUID` (`uuid4`) en todas las entidades. Timestamps vía `TimestampMixin` (`created_at`/`updated_at`).
- Enums nativos de PostgreSQL (`Enum(..., name=...)`): `RoleEnum`, `StationStatus`, `StatusSource`, `SsoProvider`.
- Pydantic v2 para schemas (`model_config = ConfigDict(from_attributes=True)`). Separar `*Create`, `*Update`, `*Read`.

## 5. Autenticación y autorización

- JWT access corto (15 min) + refresh largo (7 días) con **rotación** y detección de reuso. Del refresh solo
  se persiste su hash SHA-256 en `refresh_tokens`; al detectar reuso se revoca toda la cadena.
- Claims del access: `sub`, `org_id`, `role`, `type`, `exp`, `iat`, `jti`.
- Guards por rol con `require_roles(*roles)` como dependencia FastAPI. Roles: `superadmin > org_admin > operator > viewer`.
- Secretos solo por variable de entorno; nunca hardcodear claves ni credenciales.

## 6. Realtime y scheduler

- WebSockets autenticados por `?token=` (los navegadores no envían headers en WS). Cerrar con `4401`/`4403` ante fallo.
- `ConnectionManager` mantiene suscriptores por estación; un único `await manager.broadcast(...)` por cambio.
- `AsyncIOScheduler` (comparte el event loop). Jobstore `SQLAlchemyJobStore` con DSN **sync**. Config por org en
  `SchedulerConfig`. Todo cambio automático queda auditado en `StatusLog` con `source=scheduler`.

## 7. Migraciones (Alembic async)

- `migrations/env.py` async; `target_metadata = Base.metadata`. `compare_type=True`.
- RLS no se autogenera: va en una migración dedicada con `op.execute(...)`.
- Prohibido `Base.metadata.create_all` en producción: el esquema lo gobierna Alembic.

## 8. Pruebas (pytest)

- `pytest` + `pytest-asyncio`. Tests de integración contra **PostgreSQL real** (RLS no existe en SQLite).
- Fixtures en `conftest.py`: engine de prueba, `AsyncSession` con rollback por test, `AsyncClient` (httpx + ASGITransport),
  `LifespanManager`, y helpers de auth por rol (`superadmin_headers`, `org_admin_headers`, etc.).
- Cubrir: aislamiento de tenant, rotación/reuso de refresh, CRUD de estaciones, scheduler escribe `StatusLog`,
  broadcast WS, export CSV.

## 9. Salud y operación

- `GET /health/live` (sin DB), `GET /health/ready` (`SELECT 1`), `GET /health` (alias de ready) para probes/healthchecks.
- Logging estructurado; sin secretos en logs (regla PII).
