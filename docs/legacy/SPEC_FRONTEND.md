# SPEC FRONTEND — S2G Energy Dashboard
> Responsable: **Gemini** | Stack: Next.js 14 + TypeScript + Tailwind CSS + Recharts + Axios
> Ingeniería inversa realizada el 2026-03-21

---

## Contexto del sistema

Dashboard web para gestión de estaciones de carga eléctrica.
Se autentica con JWT contra `POST /auth/login`.
Muestra estaciones, permite crear nuevas, cambiar status, y visualiza un gráfico de barras.
Backend en `http://localhost:8000` (FastAPI).

---

## Estructura de archivos (estado actual)

```
frontend-s2g/
├── pages/
│   ├── _app.tsx          ← TIENE CONTENIDO INCORRECTO (Login duplicado)
│   └── index.tsx         ← Dashboard principal (funciona bien)
├── components/
│   ├── login.tsx         ← Correcto
│   ├── StationList.tsx   ← Correcto
│   ├── StationForm.tsx   ← Falta selector de status
│   └── StationChart.tsx  ← Correcto
├── utils/
│   └── api.ts            ← localStorage en SSR (crash)
├── styles/
│   └── globals.css       ← Tailwind directives (nunca se importa)
├── app.js                ← Archivo vacío/inútil
├── package.json          ← Self-dependency rota
└── docker-compose.yml    ← Variable de entorno incorrecta
```

---

## Bugs detectados (ordenados por severidad)

### 🔴 BUG-F01 — `pages/_app.tsx` contiene código incorrecto
**Archivo:** `frontend-s2g/pages/_app.tsx`
**Causa:** El archivo contiene código de un componente Login duplicado (idéntico a una versión antigua), en lugar del wrapper `_app.tsx` que Next.js requiere. Como consecuencia, `styles/globals.css` NUNCA se importa → **Tailwind CSS no funciona en toda la app**.
**Error:** La app puede renderizarse pero sin estilos. En modo estricto de TypeScript podría crashear.

**Contenido actual (incorrecto):**
```tsx
// components/Login.tsx     <-- ¡Comentario equivocado!
import { useState } from 'react'
import api from '../utils/api'
export default function Login() { ... }
```

**Contenido correcto que debe tener `pages/_app.tsx`:**
```tsx
import type { AppProps } from 'next/app'
import '../styles/globals.css'

export default function App({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />
}
```

**Fix:** Reemplazar todo el contenido de `pages/_app.tsx` con el wrapper estándar de Next.js que importa `globals.css`.

---

### 🔴 BUG-F02 — `utils/api.ts`: `localStorage` se accede en SSR (crash)
**Archivo:** `frontend-s2g/utils/api.ts` línea 10
**Causa:** El interceptor de Axios llama `localStorage.getItem('token')` directamente. Durante el Server-Side Rendering de Next.js, `localStorage` no existe (es API del browser). Esto lanza `ReferenceError: localStorage is not defined` al importar `api.ts` en cualquier página.

```typescript
// ACTUAL (roto)
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')  // CRASH en SSR
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// CORRECTO — verificar que estamos en browser
api.interceptors.request.use(config => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token')
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

**Fix:** Envolver el acceso a `localStorage` con `typeof window !== 'undefined'`.

---

### 🔴 BUG-F03 — `package.json`: self-dependency rota
**Archivo:** `frontend-s2g/package.json` línea 12
**Causa:** Tiene `"frontend-s2g": "file:"` en `dependencies`. Esto es una referencia circular al propio paquete. Causa errores en `npm install` o `npm ci` y puede romper el build de Docker.

```json
// ACTUAL (roto)
"dependencies": {
  "axios": "^1.9.0",
  "frontend-s2g": "file:",   // <-- eliminar esta línea
  "next": "14.0.0",
  ...
}

// CORRECTO — eliminar esa entrada
"dependencies": {
  "axios": "^1.9.0",
  "next": "14.0.0",
  ...
}
```

**Fix:** Eliminar la línea `"frontend-s2g": "file:"` del `package.json`.

---

### 🟡 BUG-F04 — `docker-compose.yml`: variable de entorno incorrecta
**Archivo:** `frontend-s2g/docker-compose.yml` línea 10
**Causa:** Se define `API_URL=http://localhost:8000` pero el código usa `NEXT_PUBLIC_API_URL`. Next.js solo expone al browser las variables prefijadas con `NEXT_PUBLIC_`. Además, en Docker la URL debería apuntar al servicio backend, no a localhost.
**Efecto:** En Docker, la app no puede contactar al backend.

```yaml
# ACTUAL (roto)
environment:
  - API_URL=http://localhost:8000

# CORRECTO
environment:
  - NEXT_PUBLIC_API_URL=http://s2g-backend:8000
```

> **Nota para Gemini:** Las variables `NEXT_PUBLIC_*` en Next.js se embeben en el bundle durante el BUILD, no en runtime. Para Docker multi-stage, la variable debe pasarse como `ARG` en el Dockerfile y luego como `ENV`. Revisar si el Dockerfile actual las maneja correctamente.

**Fix:** Cambiar `API_URL` → `NEXT_PUBLIC_API_URL` y ajustar la URL al nombre del servicio Docker.

---

### 🟡 BUG-F05 — `StationForm.tsx`: falta selector de status
**Archivo:** `frontend-s2g/components/StationForm.tsx`
**Causa:** El formulario tiene campos para `name`, `location`, `max_kw`, pero NO tiene `<select>` visible para `status`. El status siempre se envía como `'activo'` (valor por defecto del estado). El usuario no puede elegir el status al crear una estación.

```tsx
// ACTUAL — no hay select de status en el JSX
<form ...>
  <input name="name" ... />
  <input name="location" ... />
  <input name="max_kw" ... />
  <button>Registrar</button>
  {/* status siempre = 'activo', no hay UI para cambiarlo */}
</form>

// CORRECTO — agregar select de status
<form ...>
  <input name="name" ... />
  <input name="location" ... />
  <input name="max_kw" ... />
  <select
    name="status"
    value={form.status}
    onChange={handleChange}
    className="border p-2 rounded"
  >
    <option value="activo">Activo</option>
    <option value="inactivo">Inactivo</option>
  </select>
  <button>Registrar</button>
</form>
```

**Fix:** Agregar `<select name="status">` con opciones `activo`/`inactivo` en el JSX del formulario.

---

### 🟢 BUG-F06 — Falta archivo `.env.local`
**Archivo:** No existe `frontend-s2g/.env.local`
**Causa:** Para desarrollo local (`npm run dev`), Next.js necesita `.env.local` con `NEXT_PUBLIC_API_URL`. Sin él, el `api.ts` usa el fallback `'http://localhost:8000'` que funciona en local pero no es explícito.

**Crear el archivo:**
```bash
# frontend-s2g/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Fix:** Crear `frontend-s2g/.env.local` con la variable.

---

### 🟢 BUG-F07 — `app.js` es un archivo vacío que no pertenece al proyecto
**Archivo:** `frontend-s2g/app.js` (contiene solo `// Next.js main file`)
**Causa:** Archivo placeholder sin código útil. En Next.js Pages Router, el entry point es `pages/_app.tsx`, no `app.js`. Este archivo puede confundir el build o tooling.

**Fix:** Eliminar `frontend-s2g/app.js`.

---

## Resumen de archivos a modificar/crear

| Archivo | Bug | Acción |
|---|---|---|
| `pages/_app.tsx` | F01 | Reemplazar contenido completo |
| `utils/api.ts` | F02 | Guard `typeof window !== 'undefined'` |
| `package.json` | F03 | Eliminar self-dependency |
| `docker-compose.yml` | F04 | Cambiar nombre de env var |
| `components/StationForm.tsx` | F05 | Agregar `<select>` de status |
| `.env.local` | F06 | Crear archivo nuevo |
| `app.js` | F07 | Eliminar |

---

## Orden de ejecución de fixes

1. **F01** → `_app.tsx` correcto con import de Tailwind (sin esto, app sin estilos)
2. **F02** → Guard SSR en `api.ts` (sin esto, crash en Next.js server)
3. **F03** → Eliminar self-dependency en `package.json` (sin esto, `npm install` puede fallar)
4. **F05** → Agregar select de status en `StationForm` (funcionalidad)
5. **F04** → Corregir env var en `docker-compose.yml` (para Docker)
6. **F06** → Crear `.env.local` (para desarrollo local)
7. **F07** → Eliminar `app.js` (limpieza)

---

## Contrato con el Backend

El frontend consume estos endpoints. El backend debe estar corriendo en la URL de `NEXT_PUBLIC_API_URL`:

```
POST   /auth/login
  Body: URLSearchParams { username, password }
  Content-Type: application/x-www-form-urlencoded
  Response: { access_token: string, token_type: "bearer" }

GET    /stations
GET    /stations?status=activo
GET    /stations?status=inactivo
  Headers: Authorization: Bearer <token>
  Response: Array<{ id, name, location, max_kw, status, created_at, updated_at }>

POST   /stations
  Headers: Authorization: Bearer <token>
  Body JSON: { name, location, max_kw, status }
  Response: Station (201)

PATCH  /stations/{id}?new_status=activo|inactivo
  Headers: Authorization: Bearer <token>
  Response: Station
```

> **Atención:** El backend corrige en BUG-B02 el parámetro de `status` → `new_status`.
> El frontend en `index.tsx` línea 51 ya envía `{ params: { status } }`.
> **Actualizar la llamada** en `pages/index.tsx` línea 51:
> ```typescript
> // ACTUAL
> await api.patch(`/stations/${id}`, null, { params: { status } })
> // CORRECTO (alineado con fix de backend BUG-B02)
> await api.patch(`/stations/${id}`, null, { params: { new_status: status } })
> ```

---

## Tipos TypeScript de referencia

```typescript
interface Station {
  id: number
  name: string
  location: string
  max_kw: number
  status: 'activo' | 'inactivo'
  created_at: string
  updated_at: string
}

interface LoginResponse {
  access_token: string
  token_type: 'bearer'
}
```

---

## Cómo correr en desarrollo local

```bash
cd frontend-s2g
npm install          # después de fix F03
npm run dev          # http://localhost:3000
```

Credenciales de prueba: `admin@s2g.com` / `123456`
