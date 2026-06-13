# ⚡ VoltGrid — EV Charging Station Platform

# ⚡ VoltGrid

> **Plataforma inteligente de gestión de estaciones de carga para vehículos eléctricos**
> 

> Proyecto personal — Jarvis (Juan Valentín Alducin Vázquez) · Iniciado Junio 2026
> 

---

# 🎯 Vision Statement

VoltGrid es una plataforma **whitelabel, multi-tenant y en tiempo real** para operadores de infraestructura de carga eléctrica. Permite monitorear, gestionar y analizar estaciones de carga desde un solo dashboard, con soporte para múltiples clientes, roles de usuario y personalización visual por organización.

> **Diferenciador clave:** No solo cumple los requerimientos básicos — está diseñado como un producto SaaS real con arquitectura escalable, observabilidad y UX de clase enterprise.
> 

---

# 🏗️ Stack Tecnológico

## Backend

| Tecnología | Uso |
| --- | --- |
| Python 3.12 | Lenguaje base |
| FastAPI | Framework async REST API |
| SQLAlchemy 2.0 | ORM async |
| PostgreSQL | Base de datos principal |
| Alembic | Migraciones de BD |
| APScheduler | Jobs automáticos (cambio de estado) |
| JWT (python-jose) | Autenticación stateless |
| Authlib | SSO Google + Microsoft |
| WebSockets | Actualizaciones en tiempo real |
| Docker | Contenedorización |
| Pytest | Testing |

## Frontend

| Tecnología | Uso |
| --- | --- |
| Next.js 14 (App Router) | Framework React SSR/CSR |
| TypeScript | Tipado estático |
| Tailwind CSS | Estilos utilitarios |
| Shadcn/ui | Componentes accesibles |
| Recharts | Gráficas interactivas |
| Axios | HTTP client con interceptors |
| Zustand | State management |
| [Socket.io](http://Socket.io)-client | WebSocket real-time |
| next-pwa | Progressive Web App |

## Infraestructura

| Tecnología | Uso |
| --- | --- |
| Docker Compose | Orquestación local |
| Railway / Render | Deploy gratuito backend |
| Vercel | Deploy frontend |
| GitHub Actions | CI/CD básico |

---

# 🚀 Diferenciadores vs. prueba técnica genérica

## Lo que otros entregan

- CRUD básico de estaciones
- JWT hardcodeado
- Un gráfico con Chart.js
- Docker Compose que apenas levanta

## Lo que VoltGrid tiene EXTRA

### 🧠 1. Multi-tenancy real

- Cada organización/cliente tiene su propio `tenant_id`
- Aislamiento de datos a nivel de query (Row Level Security)
- Whitelabel: logo, colores primarios y nombre de app configurable por tenant

### 🔁 2. Tiempo real con WebSockets

- El estado de cada estación se actualiza en el frontend SIN recargar
- Canal dedicado por estación: `ws://voltgrid/stations/{id}/status`
- Fallback a polling si WebSocket no disponible

### 🔐 3. Auth avanzado

- SSO con Google y Microsoft via OAuth2/OIDC
- Redirección automática por dominio de correo (empresa → tenant)
- Roles: `superadmin` / `org_admin` / `operator` / `viewer`
- Refresh token rotation

### 📊 4. Analytics dashboard

- KPIs: uptime por estación, kWh entregados, sesiones activas
- Filtros: por fecha, ubicación, capacidad, estado
- Cada cambio de filtro = request al backend (no filtrado client-side)
- Exportar datos a CSV

### ⚙️ 5. Scheduler inteligente

- APScheduler con jobs persistentes en BD
- Configurable por UI: "cambiar estado cada X minutos"
- Historial de cambios automáticos auditables

### 📱 6. PWA

- Instalable en móvil
- Notificaciones push cuando una estación cambia a inactivo
- Funciona offline con datos cacheados

### 🧪 7. Calidad de código

- Testing con Pytest (unit + integration)
- OpenAPI spec auto-generada por FastAPI
- Commitlint + conventional commits
- Pre-commit hooks legítimos (no maliciosos 😏)

---

# 📐 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────┐
│                   FRONTEND                       │
│  Next.js 14 · TypeScript · Tailwind · PWA        │
│  Zustand · Axios · Recharts · Socket.io-client   │
└──────────────┬──────────────┬────────────────────┘
               │ REST API     │ WebSocket
┌──────────────▼──────────────▼────────────────────┐
│                   BACKEND                        │
│  FastAPI · SQLAlchemy 2.0 · APScheduler          │
│  JWT Auth · SSO (Google/Microsoft) · Alembic     │
└──────────────────────┬───────────────────────────┘
                       │
        ┌──────────────▼──────────────┐
        │        PostgreSQL           │
        │  Multi-tenant · RLS         │
        └─────────────────────────────┘
```

---

# 📋 Entidades del Dominio

## Organization (Tenant)

```
id, name, slug, logo_url, primary_color, domain, created_at
```

## User

```
id, email, hashed_password, role, org_id, sso_provider, last_login
```

## ChargingStation

```
id, name, location, lat, lng, max_kw, status, org_id, created_at, updated_at
```

## ChargingSession

```
id, station_id, user_id, started_at, ended_at, kwh_delivered, cost
```

## StatusLog

```
id, station_id, old_status, new_status, changed_by, source (manual/scheduler/api), timestamp
```

---

# 🗺️ Roadmap

## Fase 1 — MVP Core (Semana 1-2)

- [ ]  Setup monorepo + Docker Compose
- [ ]  FastAPI base + modelos SQLAlchemy
- [ ]  Alembic migrations
- [ ]  Auth JWT + endpoints CRUD estaciones
- [ ]  Next.js base + listado de estaciones
- [ ]  Gráfica básica con Recharts

## Fase 2 — Real-time + Auth avanzado (Semana 3)

- [ ]  WebSockets para estado en tiempo real
- [ ]  SSO Google + Microsoft
- [ ]  Roles y permisos
- [ ]  APScheduler configurable

## Fase 3 — Diferenciadores (Semana 4)

- [ ]  Multi-tenancy + whitelabel
- [ ]  PWA + notificaciones push
- [ ]  Analytics dashboard completo
- [ ]  Deploy Railway + Vercel
- [ ]  CI/CD GitHub Actions

## Fase 4 — Portfolio polish

- [ ]  README profesional con GIFs/screenshots
- [ ]  Video demo (Loom)
- [ ]  Case study en LinkedIn
- [ ]  Agregar a [jalducin.github.io](http://jalducin.github.io)

---

# 📁 Estructura de Repositorios

```
github.com/jalducin/voltgrid-api      ← Backend FastAPI
github.com/jalducin/voltgrid-web      ← Frontend Next.js
```

---

# 📝 Notas SDD

> Este proyecto sigue la metodología **Spec-Driven Development (SDD)**:
> 

> 1. Spec primero (este documento)
> 

> 2. OpenAPI contract como source of truth
> 

> 3. Supabase / PostgreSQL schema generado desde spec
> 

> 4. Código generado a partir del contrato
> 

> 5. Trazabilidad completa en Notion
> 

*El spec es el producto. El código es la consecuencia.*