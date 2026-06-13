## 0. Preparación (SIEMPRE PRIMERO)

- [ ] 0.1 Crear y cambiar a la feature branch `feature/init-voltgrid-platform`
- [ ] 0.2 Montar andamiaje SDD (openspec, docs, ai-specs, .claude, .gemini) e instanciar config/project
- [ ] 0.3 Renombrar `backend-s2g`→`voltgrid-api`, `frontend-s2g`→`voltgrid-web`
- [ ] 0.4 Crear repo GitHub `jalducin/voltgrid` (público) y push inicial

## 1. Backend — núcleo (organizations-multitenancy, auth-rbac)

- [ ] 1.1 `pyproject.toml`/`requirements.txt`: dependencias (fastapi, sqlalchemy[asyncio], asyncpg, psycopg, alembic, pydantic-settings, python-jose, passlib[bcrypt], authlib, apscheduler, httpx, itsdangerous, websockets, pytest, pytest-asyncio)
- [ ] 1.2 `app/core/config.py` (pydantic-settings v2) y `app/db/{base,session,tenant}.py` (engine async + GUC de tenant)
- [ ] 1.3 Modelos: mixins, Organization, User, ChargingStation, ChargingSession, StatusLog, SchedulerConfig, RefreshToken
- [ ] 1.4 `app/core/security.py`: hashing + JWT access/refresh + rotación
- [ ] 1.5 Routers `auth` y `health`; deps `get_current_user`, `require_roles`
- [ ] 1.6 Alembic async + migraciones `0001..0009` (extensiones/enums, tablas, RLS) + seed demo

## 2. Backend — dominio + realtime + scheduler

- [ ] 2.1 Routers + services: organizations, users, stations, sessions (CRUD, filtros server-side)
- [ ] 2.2 `station_service.change_status()` (punto único) + `StatusLog` + broadcast
- [ ] 2.3 WebSockets `/ws/stations/{id}/status` + `ConnectionManager`
- [ ] 2.4 APScheduler `AsyncIOScheduler` + jobstore + `/scheduler/config` y `/scheduler/run-now`

## 3. Backend — SSO + analytics + whitelabel

- [ ] 3.1 SSO Authlib (Google/Microsoft) + `SessionMiddleware` + mapeo dominio→tenant
- [ ] 3.2 Analytics `/analytics/{kpis,stations,export.csv}` con filtros server-side y CSV streaming
- [ ] 3.3 Whitelabel en endpoints de organización

## 4. Frontend (Next.js App Router + PWA)

- [ ] 4.1 Migrar a App Router; Tailwind + shadcn/ui; cliente Axios con refresh; store Zustand
- [ ] 4.2 Login (password + SSO), dashboard estaciones, formulario, cambio de estado
- [ ] 4.3 Tiempo real (`useWebSocket`) con fallback polling
- [ ] 4.4 Analytics con filtros server-side + export CSV; gráficas Recharts
- [ ] 4.5 Whitelabel dinámico; PWA (`next-pwa`, manifest, offline); `app/api/health`

## 5. Infraestructura (Docker, Kubernetes, CI/CD)

- [ ] 5.1 Dockerfiles multi-stage no-root (api: entrypoint migrate→uvicorn; web: standalone)
- [ ] 5.2 `docker-compose.yml` raíz (postgres + api + web) + init RLS + `.env.example`
- [ ] 5.3 Kubernetes Kustomize: base + overlays dev/prod (postgres, api+HPA, migration Job, scheduler replicas=1, web, ingress)
- [ ] 5.4 `.github/workflows/ci.yml` (backend pytest+postgres, frontend build) y `deploy.yml` opcional

## 6. Pruebas y verificación (OBLIGATORIO — EL AGENTE EJECUTA)

- [ ] 6.1 Revisar/crear pruebas: `test_tenant_isolation`, auth rotation/reuso, stations CRUD, scheduler→StatusLog, WS broadcast, CSV
- [ ] 6.2 Ejecutar `pytest` (dirigidas + suite) contra PostgreSQL y crear reporte en `specs/init-voltgrid-platform/reports/AAAA-MM-DD-step-6-pruebas-y-verificacion.md`
- [ ] 6.3 Verificación manual (EL AGENTE EJECUTA): `docker compose up --build`, probar `/health/ready`, login, CRUD, WS, analytics, CSV; restaurar estado
- [ ] 6.4 Validar k8s: `kustomize build k8s/overlays/dev | kubectl apply --dry-run=client -f -`

## 7. Documentación y cierre (OBLIGATORIO)

- [ ] 7.1 README profesional + `docs/ARCHITECTURE.md` + `docs/DOCS_INVENTORY.md`; actualizar `docs/*-standards.md` si cambió algo
- [ ] 7.2 `opsx:verify` contra los artefactos y `opsx:archive` del cambio
