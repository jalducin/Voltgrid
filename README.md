# ⚡ VoltGrid — EV Charging Station Platform

> Plataforma SaaS **multi-tenant, whitelabel y en tiempo real** para operadores de infraestructura de
> carga de vehículos eléctricos. Construida con **Spec-Driven Development (OpenSpec)**.
>
> Estado: MVP funcional verificado de extremo a extremo (Docker Compose) · Alcance funcional en
> [`openspec/changes/init-voltgrid-platform/`](openspec/changes/init-voltgrid-platform/proposal.md).

---

## 🎯 Qué resuelve

Permite a cada operador (organización) monitorear y gestionar sus estaciones de carga desde un solo
dashboard, con aislamiento total de datos entre clientes y personalización visual por marca.

- **Multi-tenancy real**: cada organización ve solo sus datos, garantizado por Row Level Security de PostgreSQL.
- **Tiempo real**: el estado de cada estación se actualiza en vivo por WebSocket (con fallback a polling).
- **Roles**: `superadmin`, `org_admin`, `operator`, `viewer`.
- **Analytics**: uptime por estación, kWh entregados, sesiones activas; filtros server-side y export CSV.
- **Scheduler**: cambios de estado automáticos configurables por organización y auditables.
- **Whitelabel**: logo, color y nombre por organización. **PWA** instalable.

## 🏗️ Arquitectura

```
┌──────────────────────────────────────────────────────────────┐
│  voltgrid-web — Next.js 14 (App Router) · Tailwind · PWA       │
│  Zustand · Axios (refresh) · Recharts · WebSocket client       │
└───────────────┬───────────────────────────┬──────────────────┘
                │ REST (Bearer JWT)          │ WebSocket
┌───────────────▼───────────────────────────▼──────────────────┐
│  voltgrid-api — FastAPI · SQLAlchemy 2.0 async                 │
│  Auth JWT+refresh · RBAC · SSO OIDC · APScheduler · WS manager │
│  api/routers → services → models/db                            │
└───────────────────────────┬──────────────────────────────────┘
                            │  asyncpg (rol NO superusuario)
┌───────────────────────────▼──────────────────────────────────┐
│  PostgreSQL 16 — multi-tenant con Row Level Security (RLS)     │
│  app.current_tenant por transacción · políticas tenant_isolation│
└────────────────────────────────────────────────────────────────┘
```

Detalle: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## 🛠️ Tecnologías

| Capa | Stack |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 async, asyncpg, Alembic, pydantic-settings, python-jose, bcrypt, Authlib, APScheduler, websockets |
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind, Zustand, Axios, Recharts, next-pwa |
| Datos | PostgreSQL 16 (RLS multi-tenant) |
| Infra | Docker (multi-stage), Docker Compose, Kubernetes (Kustomize), GitHub Actions |

## 📦 Requisitos

- Docker >= 24 y Docker Compose v2 (camino recomendado).
- Para desarrollo local sin Docker: Python 3.12, Node 20, PostgreSQL 16.

## 🚀 Configuración (quickstart con Docker)

```bash
git clone https://github.com/jalducin/voltgrid.git
cd voltgrid
cp .env.example .env            # ajusta secretos si quieres

# Construir imágenes (secuencial para evitar carrera de build con la imagen compartida)
docker compose build api web
docker compose up -d

# Cargar datos demo (una vez)
docker compose exec api python -m scripts.seed
```

Servicios:

```
http://localhost:8000        API
http://localhost:8000/docs   Swagger / OpenAPI
http://localhost:3000        Dashboard (PWA)
```

Credenciales demo: `admin@voltgrid.app / admin123` (superadmin) · `operador@voltgrid.app / operador123`.

> El servicio `scheduler` (1 réplica) es opcional en local: `docker compose --profile scheduler up -d`.
> Adminer: `docker compose --profile tools up -d adminer` → http://localhost:8080.

### Desarrollo local sin Docker

```bash
# Backend
cd voltgrid-api && python -m venv .venv && . .venv/Scripts/activate   # (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
alembic upgrade head && python -m scripts.seed
uvicorn main:app --reload

# Frontend
cd voltgrid-web && npm install && npm run dev
```

## ⚙️ Scripts

| Comando | Qué hace |
|---|---|
| `docker compose up -d` | Levanta postgres + migrate + api + web |
| `cd voltgrid-api && pytest` | Pruebas backend (requiere PostgreSQL) |
| `cd voltgrid-api && ruff check .` | Lint backend |
| `cd voltgrid-api && alembic upgrade head` | Aplica migraciones |
| `cd voltgrid-web && npm run build` | Build de producción del frontend |
| `kubectl kustomize k8s/overlays/dev` | Renderiza manifiestos de Kubernetes |

## 🧪 Pruebas y CI

- Backend: `pytest` (unidad + integración contra PostgreSQL real, incluye prueba de **aislamiento de tenant**).
- Frontend: `npm run build` + `npm run lint`.
- CI: [`.github/workflows/ci.yml`](.github/workflows/ci.yml) corre lint+pytest (con servicio Postgres) y build del frontend en cada PR.

## 📁 Estructura

```
voltgrid/
├── voltgrid-api/        # API FastAPI (app/api, core, db, models, schemas, services, realtime, scheduler, auth)
│   ├── migrations/      # Alembic (esquema + RLS)
│   └── tests/           # pytest (unit + integration)
├── voltgrid-web/        # Next.js App Router (app/, lib/, components/) + PWA
├── infra/postgres/init/ # Bootstrap del rol de app y extensiones
├── k8s/                 # Kustomize: base + overlays/{dev,prod}
├── .github/workflows/   # CI/CD
├── docs/                # Estándares y arquitectura (ver DOCS_INVENTORY.md)
├── openspec/            # Spec-Driven Development (proposal/specs/design/tasks)
└── docker-compose.yml   # postgres + migrate + api + scheduler + web
```

## 🔗 API

REST documentada automáticamente por FastAPI en `/docs` (OpenAPI). Autenticación con `Authorization: Bearer <access_token>`.
Endpoints principales: `/auth/*`, `/orgs/*`, `/users`, `/stations`, `/sessions`, `/scheduler/*`, `/analytics/*`,
WebSocket `/ws/stations/{id}/status?token=`.

## 📚 Documentación

Índice maestro: [`docs/DOCS_INVENTORY.md`](docs/DOCS_INVENTORY.md). Arquitectura: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
Estándares por área en `docs/*-standards.md`.

## 🔄 Cómo contribuir (SDD)

Este proyecto sigue **Spec-Driven Development (OpenSpec)**: la especificación es la fuente de verdad.

1. Crear rama `feature/<change-name>`.
2. Crear el cambio en `openspec/changes/<change>/` (proposal → specs → design → tasks) usando las plantillas de `openspec/schemas/`.
3. Implementar; escribir/actualizar pruebas; ejecutarlas (el agente ejecuta la verificación).
4. Verificación manual según el tipo de cambio + actualizar documentación.
5. PR; al completar, archivar el cambio (`opsx:archive`) promoviendo los specs a `openspec/specs/`.

## 📄 Licencia

MIT — Juan Valentín Alducin Vázquez ([@jalducin](https://github.com/jalducin)), 2026.
