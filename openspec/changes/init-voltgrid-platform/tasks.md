## 0. Preparación (SIEMPRE PRIMERO)

- [x] 0.1 Crear y cambiar a la feature branch `feature/init-voltgrid-platform`
- [x] 0.2 Montar andamiaje SDD (openspec, docs, ai-specs, .claude, .gemini) e instanciar config/project
- [x] 0.3 Renombrar `backend-s2g`→`voltgrid-api`, `frontend-s2g`→`voltgrid-web`
- [x] 0.4 Crear repo GitHub `jalducin/voltgrid` (público) y push inicial — https://github.com/jalducin/voltgrid

## 1. Backend — núcleo (organizations-multitenancy, auth-rbac)

- [x] 1.1 `pyproject.toml`/`requirements.txt`: dependencias (fastapi, sqlalchemy[asyncio], asyncpg, psycopg, alembic, pydantic-settings, python-jose, passlib[bcrypt], authlib, apscheduler, httpx, itsdangerous, websockets, pytest, pytest-asyncio)
- [x] 1.2 `app/core/config.py` (pydantic-settings v2) y `app/db/{base,session,tenant}.py` (engine async + GUC de tenant)
- [x] 1.3 Modelos: mixins, Organization, User, ChargingStation, ChargingSession, StatusLog, SchedulerConfig, RefreshToken
- [x] 1.4 `app/core/security.py`: hashing + JWT access/refresh + rotación
- [x] 1.5 Routers `auth` y `health`; deps `get_current_user`, `require_roles`
- [x] 1.6 Alembic async + migraciones `0001..0009` (extensiones/enums, tablas, RLS) + seed demo

## 2. Backend — dominio + realtime + scheduler

- [x] 2.1 Routers + services: organizations, users, stations, sessions (CRUD, filtros server-side)
- [x] 2.2 `station_service.change_status()` (punto único) + `StatusLog` + broadcast
- [x] 2.3 WebSockets `/ws/stations/{id}/status` + `ConnectionManager`
- [x] 2.4 APScheduler `AsyncIOScheduler` + jobstore + `/scheduler/config` y `/scheduler/run-now`

## 3. Backend — SSO + analytics + whitelabel

- [x] 3.1 SSO Authlib (Google/Microsoft) + `SessionMiddleware` + mapeo dominio→tenant
- [x] 3.2 Analytics `/analytics/{kpis,stations,export.csv}` con filtros server-side y CSV streaming
- [x] 3.3 Whitelabel en endpoints de organización

## 4. Frontend (Next.js App Router + PWA)

- [x] 4.1 Migrar a App Router; Tailwind + shadcn/ui; cliente Axios con refresh; store Zustand
- [x] 4.2 Login (password + SSO), dashboard estaciones, formulario, cambio de estado
- [x] 4.3 Tiempo real (`useWebSocket`) con fallback polling
- [x] 4.4 Analytics con filtros server-side + export CSV; gráficas Recharts
- [x] 4.5 Whitelabel dinámico; PWA (`next-pwa`, manifest, offline); `app/api/health`

## 5. Infraestructura (Docker, Kubernetes, CI/CD)

- [x] 5.1 Dockerfiles multi-stage no-root (api: entrypoint migrate→uvicorn; web: standalone)
- [x] 5.2 `docker-compose.yml` raíz (postgres + api + web) + init RLS + `.env.example`
- [x] 5.3 Kubernetes Kustomize: base + overlays dev/prod (postgres, api+HPA, migration Job, scheduler replicas=1, web, ingress)
- [x] 5.4 `.github/workflows/ci.yml` (backend pytest+postgres, frontend build) y `deploy.yml` opcional

## 6. Pruebas y verificación (OBLIGATORIO — EL AGENTE EJECUTA)

- [x] 6.1 Revisar/crear pruebas: `test_tenant_isolation`, auth rotation/reuso, stations CRUD, scheduler→StatusLog, WS broadcast, CSV
- [x] 6.2 Ejecutar `pytest` (dirigidas + suite) contra PostgreSQL y crear reporte en `specs/init-voltgrid-platform/reports/AAAA-MM-DD-step-6-pruebas-y-verificacion.md`
- [x] 6.3 Verificación manual (EL AGENTE EJECUTA): `docker compose up --build`, probar `/health/ready`, login, CRUD, WS, analytics, CSV; restaurar estado
- [x] 6.4 Validar k8s: `kustomize build k8s/overlays/dev | kubectl apply --dry-run=client -f -`

## 7. Documentación y cierre (OBLIGATORIO)

- [x] 7.1 README profesional + `docs/ARCHITECTURE.md` + `docs/DOCS_INVENTORY.md`; actualizar `docs/*-standards.md` si cambió algo
- [x] 7.2 Verificación contra los artefactos (reporte Step 6 PASS). Pendiente: `opsx:archive` (requiere CLI OpenSpec) para promover specs a `openspec/specs/`
