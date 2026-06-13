---
description: Estándares de infraestructura VoltGrid (Docker multi-stage, Docker Compose, Kubernetes con Kustomize, CI/CD GitHub Actions).
alwaysApply: true
---

# Estándares de infraestructura

> Aplica a `voltgrid-api/Dockerfile`, `voltgrid-web/Dockerfile`, `docker-compose.yml`, `k8s/**`, `.github/workflows/**`.

## 1. Imágenes Docker

- **Multi-stage** y **no-root** (usuario dedicado). `HEALTHCHECK` en ambas imágenes.
- API: base `python:3.12-slim`; etapa builder con `build-essential`/`libpq-dev`; runtime con `libpq5`.
  Entrypoint corre `alembic upgrade head` solo si `RUN_MIGRATIONS=true`, luego `uvicorn`.
- Web: base `node:20-alpine`; `output: 'standalone'`; `NEXT_PUBLIC_API_URL` como **build ARG** (se hornea).
  Arranca con `node server.js`.

## 2. Docker Compose (local)

- Servicios: `postgres:16-alpine` (healthcheck `pg_isready`, volumen `pgdata`, init de extensiones/RLS),
  `api` (`depends_on: postgres healthy`, `RUN_MIGRATIONS=true`), `web` (build arg con URL de la API).
  `adminer` opcional bajo `profiles: [tools]`.
- Configuración por `.env` (gitignored) + `.env.example` versionado. Sin secretos reales en el repo.

## 3. Kubernetes (Kustomize)

- Layout: `k8s/base` + `k8s/overlays/{dev,prod}`.
- Postgres como `StatefulSet` + PVC + Service headless en base/dev; en prod preferir **DB gestionada externa**.
- `api`: Deployment con probes (`/health/ready` readiness, `/health/live` liveness+startup), `envFrom` ConfigMap+Secret,
  `securityContext` endurecido (runAsNonRoot, readOnlyRootFilesystem, drop ALL), HPA (CPU 70%, scaleDown estable para WS).
- **Migraciones**: `Job` `alembic upgrade head` por release (no initContainer, para no correr N veces con réplicas).
- **Scheduler**: Deployment dedicado `replicas: 1` con `SCHEDULER_ENABLED=true`; la API corre con `SCHEDULER_ENABLED=false`
  (evita disparos duplicados del job con HPA).
- `web`: Deployment + Service.
- `Ingress` nginx: rutas `/` → web y `/api` → api; TLS con cert-manager; anotaciones WebSocket (timeouts altos + affinity de cookie).
- ConfigMap = no-secreto; Secret = credenciales (DSN del rol app **no-superusuario**, JWT secret, OAuth). Real via SealedSecrets/SOPS/ESO.

## 4. CI/CD (GitHub Actions)

- `ci.yml`: job backend (ruff + pytest con servicio `postgres:16` + `alembic upgrade head`), job frontend (`npm ci` + lint + build),
  job build&push de imágenes (en push a main/tags). `deploy.yml` opcional gated por environment.

## 5. Reglas transversales

- Nada de secretos en el repo ni en logs. Salud expuesta para probes. Idempotencia de migraciones.
- Una fuente canónica por dato de configuración; los manifiestos derivan de overlays, no se duplican a mano.
