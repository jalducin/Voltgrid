# Arquitectura de VoltGrid

## Visión general

VoltGrid es una plataforma SaaS multi-tenant para gestión de estaciones de carga EV. Dos aplicaciones
en un monorepo: `voltgrid-api` (FastAPI) y `voltgrid-web` (Next.js), sobre PostgreSQL 16.

## Backend (`voltgrid-api`)

Arquitectura por capas:

```
api/routers (HTTP, validación I/O)  →  services (lógica de negocio)  →  models + db (persistencia)
```

- **Routers** delgados; toda mutación del dominio pasa por un **service**.
- `station_service.change_status()` es el **punto único** de cambio de estado: actualiza la estación,
  escribe `StatusLog` (auditoría) y difunde por WebSocket. Lo usan el cambio manual, el API y el scheduler.

### Multi-tenancy con RLS

- Cada tabla de cliente lleva `tenant_id` (`TenantMixin`) y tiene RLS **habilitado y forzado**.
- Política `tenant_isolation`:
  `current_setting('app.bypass_rls', true) = 'on' OR tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid`.
- En cada request autenticado, `get_db` fija `app.current_tenant` (vía `set_config(..., is_local=true)`)
  con el `org_id` del token. La app se conecta con un **rol no-superusuario** (los superusuarios ignoran RLS).
- El bypass controlado (`app.bypass_rls`) se usa solo en rutas cross-tenant por naturaleza: login/refresh,
  resolución de dominio SSO, operaciones de superadmin y el scheduler (que fija el tenant por organización).

### Autenticación

- JWT access (15 min) + refresh (7 días) con **rotación** y **detección de reuso** (se guarda solo el
  hash SHA-256 del refresh; el reuso revoca la cadena). Roles vía `require_roles(*)`.
- SSO Google/Microsoft (OIDC, Authlib): callback resuelve dominio→organización y auto-provisiona usuario `viewer`.

### Tiempo real y scheduler

- WebSocket `/ws/stations/{id}/status` autenticado por `?token=`; `ConnectionManager` por estación.
- `AsyncIOScheduler` con jobstore persistente (DSN sync); configuración por organización (`SchedulerConfig`);
  cambios auditados en `StatusLog`. **Una sola instancia** del scheduler (Deployment dedicado en k8s).

### Persistencia

- SQLAlchemy 2.0 async (asyncpg). Migraciones con Alembic (`0001` esquema, `0002` RLS). UUID PK; enums nativos.

## Frontend (`voltgrid-web`)

- Next.js 14 App Router. Cliente Axios con interceptor de refresh automático ante 401. Estado en Zustand.
- Whitelabel dinámico (CSS var `--primary` desde `/orgs/me`). Tiempo real con hook `useWebSocket` + fallback polling.
- Analytics con filtros server-side y export CSV. PWA (`next-pwa`, `output: standalone`).

## Infraestructura

- **Docker Compose**: `postgres` → `migrate` (rol admin, corre Alembic) → `api`/`scheduler` (rol app, RLS) → `web`.
- **Kubernetes (Kustomize)**: base + overlays dev/prod. Postgres StatefulSet (dev) o DB gestionada (prod);
  API Deployment + HPA + probes; **Job** de migración por release; **scheduler replicas=1**; Ingress nginx con
  soporte WebSocket. Migraciones como Job (no initContainer) para no correr N veces con réplicas.
- **CI**: GitHub Actions (pytest+ruff con Postgres, build del frontend, build de imágenes).

## Decisiones clave

- RLS como frontera de aislamiento (no solo `WHERE` en app) → fail-closed.
- Doble DSN: asyncpg (app) + psycopg (jobstore APScheduler).
- WebSockets in-process (un proceso); seam documentado a Redis pub/sub para escalar horizontalmente.
