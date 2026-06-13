# Despliegue Kubernetes — VoltGrid

Manifiestos gestionados con **Kustomize**: una `base` común y overlays por entorno.

## Estructura

```
k8s/
├── base/                        # Manifiestos canónicos (no se aplican directo en prod)
│   ├── kustomization.yaml       # Agrupa recursos + genera ConfigMap de init de Postgres
│   ├── namespace.yaml           # Namespace voltgrid (los overlays lo sustituyen)
│   ├── configmap.yaml           # Config NO secreta (ENV, JWT_ALGORITHM, CORS, etc.)
│   ├── secret.example.yaml      # PLANTILLA de Secret (placeholders; ver abajo)
│   ├── postgres/                # StatefulSet + Service headless + PVC (volumeClaimTemplates)
│   ├── api/                     # Deployment + Service + HPA + Job de migración
│   ├── scheduler/               # Deployment del scheduler (replicas=1)
│   ├── web/                     # Deployment + Service del frontend
│   └── ingress.yaml             # Ingress nginx (/ -> web, /api -> api) + TLS + WebSocket
└── overlays/
    ├── dev/                     # namespace voltgrid-dev, 1 réplica, imágenes :dev, host dev
    └── prod/                    # namespace voltgrid-prod, más réplicas, host/issuer prod
```

## Reglas de arquitectura (no negociables)

### 1. Rol de aplicación NO superusuario (RLS)
El aislamiento multi-tenant usa **Row Level Security** de Postgres. **Los superusuarios
ignoran RLS**, así que la app NUNCA debe conectarse como superusuario en runtime.

- `DATABASE_URL` / `SYNC_DATABASE_URL` (Secret) -> rol **`voltgrid_app`** (`NOSUPERUSER NOBYPASSRLS`).
  Lo usan los Deployments `api` y `scheduler`.
- El rol `voltgrid_app` y sus privilegios se crean en `infra/postgres/init/01-init.sql`
  (se monta en el StatefulSet vía ConfigMap `voltgrid-postgres-init`).

### 2. Migraciones como Job (rol admin)
Las migraciones (`alembic upgrade head`) crean tablas y políticas, así que necesitan el
rol **admin** (dueño de tablas), no `voltgrid_app`.

- Se ejecutan en un **Job** (`api/migration-job.yaml`), **no** en un initContainer:
  con varias réplicas de la API, un initContainer correría las migraciones N veces.
- Alembic lee `DATABASE_URL`; el Job mapea el Secret `MIGRATIONS_DATABASE_URL`
  (rol admin) a `DATABASE_URL`.
- Los Deployments `api` y `scheduler` corren con `RUN_MIGRATIONS=false`.

### 3. Scheduler de una sola réplica
APScheduler corre **en proceso**. Con más de una instancia, los jobs se dispararían por
duplicado.

- Deployment `scheduler` dedicado: `replicas: 1`, `strategy: Recreate`, `SCHEDULER_ENABLED=true`,
  **sin HPA**.
- La `api` corre con `SCHEDULER_ENABLED=false` (puede escalar con HPA sin duplicar jobs).

### 4. Ingress y WebSocket
`/` enruta a `web:3000` y `/api` a `api:8000`. Para conexiones WebSocket persistentes,
el Ingress lleva timeouts altos (`proxy-read/send-timeout: 3600`) y *affinity* por cookie
para pegar cada WS al mismo pod de API.

## Secretos

`base/secret.example.yaml` es solo una **plantilla con placeholders**. No apliques sus
valores en producción. Gestiona los secretos reales con **SealedSecrets**, **SOPS** o
**External Secrets Operator (ESO)**. Claves esperadas: `POSTGRES_PASSWORD`,
`DATABASE_URL`, `SYNC_DATABASE_URL`, `MIGRATIONS_DATABASE_URL`, `JWT_SECRET`,
`SESSION_SECRET_KEY`, `GOOGLE_CLIENT_ID/SECRET`, `MICROSOFT_CLIENT_ID/SECRET`.

## Base de datos en producción

El StatefulSet de Postgres es práctico para dev / k8s local. En **producción se prefiere
una BD gestionada externa** (RDS, Cloud SQL, Azure DB): excluye los manifiestos de
`postgres/` del despliegue y apunta los DSN del Secret al endpoint gestionado
(ver nota en `overlays/prod/kustomization.yaml`).

## Desplegar

> El ConfigMap de init de Postgres se genera desde `infra/postgres/init/01-init.sql`
> (fuente única, compartida con docker-compose). Como ese archivo vive FUERA de `k8s/`,
> hay que pasar **siempre** `--load-restrictor LoadRestrictionsNone`.

Validar (build local, sin aplicar):

```bash
kubectl kustomize --load-restrictor LoadRestrictionsNone k8s/overlays/dev
kubectl kustomize --load-restrictor LoadRestrictionsNone k8s/overlays/prod
```

Aplicar:

```bash
# DEV
kubectl apply -k k8s/overlays/dev --load-restrictor LoadRestrictionsNone

# PROD
kubectl apply -k k8s/overlays/prod --load-restrictor LoadRestrictionsNone
```

Tras el despliegue, el **Job de migración** corre `alembic upgrade head`. Verifícalo:

```bash
kubectl -n voltgrid-dev get jobs
kubectl -n voltgrid-dev logs job/voltgrid-migrate
```

> Los Jobs son inmutables en su spec: para re-ejecutar migraciones en un nuevo release,
> bórralo y reaplica, o usa un sufijo de release en el nombre del Job.
