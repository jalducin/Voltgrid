## Context

VoltGrid se reconstruye desde un MVP (FastAPI + SQLite) hacia una plataforma SaaS multi-tenant en
tiempo real. El documento de visión define entidades (Organization, User, ChargingStation,
ChargingSession, StatusLog), diferenciadores (multi-tenancy + RLS, realtime, SSO, scheduler, analytics,
whitelabel, PWA) y stack objetivo. Este diseño fija el CÓMO para implementar sin ambigüedad.

## Goals / Non-Goals

**Goals:**
- Aislamiento real entre tenants con RLS de PostgreSQL (no solo filtros de aplicación).
- Auth robusta (JWT access+refresh con rotación, roles) y SSO OIDC.
- Realtime por WebSockets y scheduler auditable configurable por organización.
- Analytics con filtros server-side y export CSV; whitelabel por tenant.
- Despliegue reproducible: Docker, Docker Compose, Kubernetes (Kustomize), CI/CD.
- Trazabilidad SDD: specs como fuente de verdad.

**Non-Goals (en esta iteración):**
- Pasarela de pagos / facturación real.
- Fan-out de WebSockets entre múltiples procesos (se documenta el seam a Redis/LISTEN-NOTIFY).
- Notificaciones push productivas (se entrega scaffold; requiere VAPID).
- Alta disponibilidad de PostgreSQL gestionada (se recomienda DB administrada en prod).

## Decisions

### Backend
- **Capas**: `api/routers` → `services` → `models/db`. Routers delgados; toda mutación de dominio en services.
- **RLS como frontera**: cada tabla de cliente lleva `tenant_id` y RLS forzado con política
  `tenant_isolation` sobre `current_setting('app.current_tenant', true)::uuid`. `get_db` hace
  `SET LOCAL app.current_tenant` por transacción. La app usa un rol DB no-superusuario. *Alternativa
  descartada*: solo `WHERE tenant_id=...` en la app (frágil; un olvido filtra datos).
- **SQLAlchemy 2.0 async** + asyncpg; `psycopg` (sync) solo para `SQLAlchemyJobStore` de APScheduler.
- **UUID PK** en todas las entidades (evita enumeración cross-tenant). Enums nativos de PostgreSQL.
- **Auth**: JWT HS256 con `python-jose`. Access 15 min; refresh 7 días con **rotación** y detección de
  reuso (se guarda solo el hash SHA-256 del refresh; reuso → revoca la cadena). Guards `require_roles(*)`.
- **SSO** con Authlib (Google + Microsoft OIDC), `SessionMiddleware`; callback resuelve dominio→`Organization.domain`,
  auto-provisiona usuario `viewer`. Credenciales por env (placeholders).
- **Realtime**: WebSocket `/ws/stations/{id}/status`, auth por `?token=`, `ConnectionManager` por estación.
  `station_service.change_status()` es el único punto que muta estado → `StatusLog` → broadcast.
- **Scheduler**: `AsyncIOScheduler` (comparte event loop), jobstore persistente; `SchedulerConfig` por org;
  cambios auditados en `StatusLog (source=scheduler)`. *Alternativa descartada*: `BackgroundScheduler`
  (no comparte loop, no permite await del broadcast/DB async).
- **Analytics**: queries de agregación RLS-scoped (uptime desde `status_logs`, kWh desde sesiones, sesiones
  activas `ended_at IS NULL`). Filtros como modelo Pydantic. Export CSV con `StreamingResponse`.
- **Alembic async**; RLS en migración dedicada con `op.execute`. Sin `create_all`.

### Frontend
- Next.js 14 **App Router**, TypeScript, Tailwind + shadcn/ui, Zustand (sesión/whitelabel), Axios con
  interceptores (refresh automático), Recharts. PWA con `next-pwa`, `output: 'standalone'`.
- `NEXT_PUBLIC_API_URL` build-time (ARG en Docker). Hook `useWebSocket` con fallback a polling.

### Infraestructura
- Dockerfiles multi-stage no-root con healthcheck. Compose: postgres + api (migra) + web.
- Kubernetes Kustomize (base + overlays dev/prod): Postgres StatefulSet (dev) / DB gestionada (prod),
  api Deployment+Service+HPA, **Job** de migración, **Deployment de scheduler replicas=1**, web, Ingress nginx con TLS y WS.
- CI/CD GitHub Actions: test backend (pytest + postgres), build frontend, build&push imágenes.

## Risks / Trade-offs

- **RLS mal configurado fuga datos** → política `WITH CHECK` + test `test_tenant_isolation` obligatorio + rol no-superusuario.
- **APScheduler en N réplicas duplica jobs** → Deployment de scheduler dedicado `replicas=1`; API con `SCHEDULER_ENABLED=false`.
- **WebSockets en memoria no escalan horizontalmente** → affinity de cookie en Ingress; seam documentado a Redis pub/sub.
- **Doble DSN (async + sync)** por el jobstore → derivar el DSN sync de la misma DB; documentado en config.
- **SSO/PWA push dependen de credenciales externas** → entregados con placeholders y documentación; no bloquean el resto.
- **Migración destructiva de esquema** → greenfield en PostgreSQL; sin migración de datos legacy de SQLite (seed demo nuevo).

## Migration Plan

1. Andamiaje SDD + rename de carpetas + repo GitHub.
2. Backend núcleo: modelos, RLS, auth, Alembic, health, tests base.
3. Dominio + realtime + scheduler.
4. SSO + analytics + whitelabel.
5. Frontend App Router + PWA.
6. Docker + Kubernetes + CI/CD.
7. Documentación, verificación y archive.

Rollback: el código S2G previo permanece en el historial git; cada fase es una rama `feature/*` con PR.

## Open Questions

- ¿Proveedor de Kubernetes objetivo (EKS/GKE/AKS/local) para afinar overlays e Ingress? (Se asume nginx-ingress + cert-manager.)
- ¿Se habilitará SSO en esta entrega (requiere credenciales OAuth del usuario)?
- ¿Notificaciones push productivas (requiere VAPID) o solo PWA instalable/offline en esta iteración?
