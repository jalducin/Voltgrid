## ADDED Requirements

### Requirement: Contenedorización y orquestación local

El sistema SHALL proveer imágenes Docker multi-stage y no-root para `voltgrid-api` y `voltgrid-web`, y un
`docker-compose.yml` que levante PostgreSQL, la API (con migraciones) y el frontend con un solo comando.

#### Scenario: Levantar el stack local

- **WHEN** se ejecuta `docker compose up --build`
- **THEN** PostgreSQL queda healthy, la API aplica migraciones y responde `GET /health/ready` con 200, y el frontend queda accesible

### Requirement: Despliegue en Kubernetes

El sistema SHALL proveer manifiestos Kubernetes (Kustomize base + overlays dev/prod) para PostgreSQL, la
API (Deployment, Service, HPA, probes), un Job de migración, un Deployment de scheduler con una sola
réplica, el frontend e Ingress con soporte WebSocket.

#### Scenario: Manifiestos válidos

- **WHEN** se ejecuta `kustomize build k8s/overlays/dev | kubectl apply --dry-run=client -f -`
- **THEN** todos los manifiestos validan sin error

### Requirement: Integración continua

El sistema SHALL ejecutar en CI las pruebas del backend (contra PostgreSQL) y el build del frontend en cada PR.

#### Scenario: CI en pull request

- **WHEN** se abre un pull request
- **THEN** el workflow ejecuta lint + pytest del backend y el build del frontend
