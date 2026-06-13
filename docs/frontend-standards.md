---
description: Estándares del frontend VoltGrid (Next.js 14 App Router, TypeScript, Tailwind, shadcn/ui, Zustand, Axios, Recharts, PWA).
alwaysApply: true
---

# Estándares del frontend (voltgrid-web)

> Aplica a todo el código bajo `voltgrid-web/`. Complementa `docs/base-standards.md`.

## 1. Stack

- Next.js 14 con **App Router** (`app/`). TypeScript estricto. Tailwind CSS + shadcn/ui para componentes.
- Zustand para estado global (sesión, whitelabel). Axios con interceptores para la API. Recharts para gráficas.
- `next-pwa` para PWA (instalable, offline). `output: 'standalone'` para imagen Docker ligera.

## 2. Estructura

- `app/` con route groups: `(auth)` para login/SSO, `(dashboard)` para vistas autenticadas.
- `components/ui/` (shadcn) y `components/` (compuestos del dominio).
- `lib/` para cliente API, store Zustand, hooks (`useWebSocket`, `useAuth`), y tipos compartidos.
- `app/api/health/route.ts` para healthcheck (proceso, sin llamar a la API).

## 3. Autenticación y API

- Cliente Axios con `baseURL = process.env.NEXT_PUBLIC_API_URL`. Las variables `NEXT_PUBLIC_*` se **hornean en build**;
  en Docker se pasan como `ARG`.
- Interceptores: adjuntar `Authorization: Bearer <access>`; ante 401 intentar `refresh` una vez y reintentar; si falla, cerrar sesión.
- El acceso a `localStorage`/`window` siempre con guard `typeof window !== 'undefined'` (evitar crash en SSR).
- Tokens en memoria + `localStorage`; nunca registrar tokens en consola.

## 4. Tiempo real

- Hook `useWebSocket(stationId)` que abre `wss?token=<access>` y actualiza el estado sin recargar.
- **Fallback a polling** (`GET /stations`) si el WebSocket no está disponible.

## 5. Whitelabel

- Al cargar la sesión se obtiene la organización (logo, color primario, nombre) y se aplican como CSS variables/tema.
- Nada de marca hardcodeada: el nombre y colores vienen del tenant.

## 6. Filtros y analytics

- Cada cambio de filtro dispara una **petición al backend** (no filtrado en cliente). Export CSV vía endpoint del backend.

## 7. Calidad

- Tipar todo (sin `any` salvo justificación). Componentes accesibles (shadcn/Radix).
- `npm run build` y `npm run lint` deben pasar antes de finalizar un cambio.
- Comentarios y textos de UI orientados a usuario final en español; identificadores en inglés.
