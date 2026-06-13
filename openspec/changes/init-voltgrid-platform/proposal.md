## Why

El proyecto actual (S2G) es un CRUD mínimo de estaciones de carga sobre SQLite que no cubre la visión de
producto descrita en `⚡ VoltGrid — EV Charging Station Platform`: una plataforma SaaS whitelabel,
multi-tenant y en tiempo real. Se reconstruye el sistema sobre PostgreSQL con aislamiento real entre
clientes (RLS), autenticación robusta, realtime, scheduler auditable, analytics y despliegue en
Docker/Kubernetes, adoptando además el flujo Spec-Driven Development (OpenSpec).

## What Changes

- **BREAKING**: se renombra `backend-s2g` → `voltgrid-api` y `frontend-s2g` → `voltgrid-web`.
- **BREAKING**: se migra de SQLite a **PostgreSQL 16** con SQLAlchemy 2.0 async y Alembic (se elimina `Base.metadata.create_all`).
- **BREAKING**: el modelo de datos pasa a UUID + multi-tenant; `StationStatus` se enriquece
  (`available/occupied/offline/maintenance`) reemplazando `activo/inactivo`.
- Nueva autenticación: JWT access + refresh con rotación y roles (`superadmin/org_admin/operator/viewer`).
- SSO Google/Microsoft (OIDC) con mapeo dominio→tenant (requiere credenciales externas).
- Realtime por WebSockets; APScheduler configurable por organización y auditable.
- Analytics (uptime, kWh, sesiones activas) con filtros server-side y export CSV.
- Whitelabel por organización (logo, color, nombre).
- Frontend reescrito a Next.js 14 App Router con PWA.
- Docker multi-stage, Docker Compose con PostgreSQL, manifiestos Kubernetes (Kustomize) y CI/CD.

## Capabilities

### New Capabilities
- `organizations-multitenancy`: organizaciones (tenants) y aislamiento de datos con RLS de PostgreSQL.
- `auth-rbac`: autenticación JWT con refresh rotation y autorización por roles.
- `sso`: inicio de sesión federado con Google y Microsoft (OIDC) y mapeo dominio→tenant.
- `charging-stations`: gestión (CRUD) de estaciones de carga y cambio de estado auditable.
- `charging-sessions`: registro de sesiones de carga (kWh, costo, duración).
- `status-scheduler`: cambios de estado automáticos configurables por organización (APScheduler).
- `realtime-ws`: difusión en tiempo real del estado de estaciones por WebSockets.
- `analytics-export`: KPIs con filtros server-side y exportación a CSV.
- `whitelabel`: personalización visual por organización.
- `pwa`: aplicación web instalable con soporte offline.
- `infra-docker-k8s`: contenedorización, orquestación local y despliegue en Kubernetes con CI/CD.

### Modified Capabilities
(ninguna — no hay specs previos en `openspec/specs/`.)

## Impact

- Código: reescritura completa de `voltgrid-api` (app/api, core, db, models, schemas, services, realtime, scheduler, auth,
  migrations, tests) y de `voltgrid-web` (app/, lib/, components/). Nuevos `Dockerfile`, `docker-compose.yml`, `k8s/`, `.github/workflows/`.
- Dependencias backend nuevas: asyncpg, psycopg, alembic, pydantic-settings, authlib, httpx, itsdangerous, websockets, pytest-asyncio.
- Dependencias frontend nuevas: shadcn/ui, zustand, next-pwa, socket/ws client.
- Externo: requiere credenciales OAuth (Google/Microsoft) y llaves VAPID (push) para habilitar SSO y notificaciones.
- Datos: nuevo esquema PostgreSQL gobernado por Alembic; seed demo para desarrollo.
