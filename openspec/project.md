# Contexto del proyecto

Este documento da contexto a los agentes de IA sobre VoltGrid.

## Qué es

**VoltGrid** es una plataforma SaaS whitelabel, multi-tenant y en tiempo real para operadores de
infraestructura de carga de vehículos eléctricos. Permite monitorear, gestionar y analizar estaciones
de carga desde un solo dashboard, con soporte para múltiples organizaciones (tenants), roles de usuario
y personalización visual por organización.

## Stack tecnológico

- Lenguaje(s): Python 3.12 (backend), TypeScript / Node 20 (frontend).
- Framework(s): FastAPI (backend), Next.js 14 App Router (frontend).
- Base de datos: PostgreSQL 16 (multi-tenant con Row Level Security).
- Otros: SQLAlchemy 2.0 async + Alembic, APScheduler, WebSockets, Authlib (SSO OIDC),
  Docker, Kubernetes (Kustomize), GitHub Actions.

## Arquitectura

API REST por capas: `api/routers` (HTTP) → `services` (lógica de negocio) → `models`/`db` (persistencia).
Realtime por WebSockets con un `ConnectionManager` por estación. Multi-tenancy con `tenant_id` por fila
y RLS de PostgreSQL como frontera de aislamiento (la app corre con un rol DB no-superusuario y fija
`app.current_tenant` por transacción). Scheduler con APScheduler y jobstore persistente. El frontend
consume la API y el canal WS, con whitelabel dinámico por tenant y soporte PWA.

```
voltgrid-web (Next.js)  ──REST/WS──►  voltgrid-api (FastAPI)  ──►  PostgreSQL (RLS multi-tenant)
```

## Convenciones

- Idioma: documentación y comentarios en español; identificadores de código en inglés.
- Commits: conventional commits.
- Ramas: `feature/[change-name]`.
- Estándares por área en `docs/*-standards.md`.

## Comandos clave

- Backend — instalar: `pip install -r voltgrid-api/requirements.txt`
- Backend — pruebas: `cd voltgrid-api && pytest`
- Backend — migraciones: `cd voltgrid-api && alembic upgrade head`
- Frontend — instalar: `cd voltgrid-web && npm install`
- Frontend — desarrollo: `cd voltgrid-web && npm run dev`
- Todo el stack: `docker compose up --build`
- Kubernetes (dev): `kustomize build k8s/overlays/dev | kubectl apply -f -`
