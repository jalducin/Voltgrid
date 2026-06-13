# Inventario de documentación

Índice maestro de la documentación de VoltGrid. Cada dato tiene una fuente canónica; los demás enlazan, no copian.

| Documento | Contenido | Canónico de |
|---|---|---|
| [`README.md`](../README.md) | Puerta de entrada: qué es, quickstart, scripts, estructura, contribuir (SDD) | Onboarding |
| [`docs/ARCHITECTURE.md`](ARCHITECTURE.md) | Arquitectura backend/frontend/infra, RLS, auth, realtime | Arquitectura |
| [`docs/base-standards.md`](base-standards.md) | Principios base, idioma, reglas OpenSpec | Estándares globales |
| [`docs/backend-standards.md`](backend-standards.md) | Estándares FastAPI/PostgreSQL/RLS/tests | Backend |
| [`docs/frontend-standards.md`](frontend-standards.md) | Estándares Next.js/Tailwind/PWA | Frontend |
| [`docs/infra-standards.md`](infra-standards.md) | Estándares Docker/Kubernetes/CI | Infraestructura |
| [`docs/documentation-standards.md`](documentation-standards.md) | Cómo documentar y mantener consistencia | Documentación |
| [`openspec/project.md`](../openspec/project.md) | Contexto del proyecto para agentes IA | Contexto IA |
| [`openspec/changes/init-voltgrid-platform/`](../openspec/changes/init-voltgrid-platform/proposal.md) | Alcance funcional inicial (proposal/specs/design/tasks) | Spec inicial |
| [`k8s/README.md`](../k8s/README.md) | Layout y despliegue Kubernetes | Despliegue K8s |
| [`docs/legacy/`](legacy/) | Specs históricos del MVP S2G (referencia) | Histórico |

## Fuente de verdad de la API

El contrato de la API se genera automáticamente desde FastAPI (OpenAPI en `/docs` y `/openapi.json`).
No se mantiene una copia manual del contrato.
