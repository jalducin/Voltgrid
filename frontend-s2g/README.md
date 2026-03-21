# Frontend — S2G Energy Dashboard

**Repositorio:** [https://github.com/jalducin/frontend-s2g](https://github.com/jalducin/frontend-s2g)

Dashboard web para gestión de estaciones de carga eléctrica.

---

## Tecnologías

| | |
|---|---|
| Framework | Next.js 14 (Pages Router) |
| Lenguaje | TypeScript |
| Estilos | Tailwind CSS |
| HTTP | Axios |
| Gráficas | Recharts |
| Contenedores | Docker |

---

## Características

- Login con JWT — token almacenado en `localStorage`
- Dashboard protegido: redirige a login si no hay sesión
- Listado de estaciones en tarjetas con cambio de estado
- Formulario de registro con nombre, ubicación, capacidad y estado
- Filtro por estado (todas / activas / inactivas)
- Gráfica de barras de capacidad por estación (Recharts)

---

## Estructura

```
frontend-s2g/
├── components/
│   ├── login.tsx           # Formulario de autenticación
│   ├── StationForm.tsx     # Crear nueva estación
│   ├── StationList.tsx     # Tarjetas de estaciones
│   └── StationChart.tsx    # Gráfica de barras (Recharts)
├── pages/
│   ├── _app.tsx            # Wrapper Next.js — importa Tailwind
│   └── index.tsx           # Dashboard principal
├── styles/
│   └── globals.css         # Directivas Tailwind
├── utils/
│   └── api.ts              # Instancia Axios con interceptor JWT
├── .env.local
├── Dockerfile
├── docker-compose.yml
├── package.json
├── tailwind.config.js
└── tsconfig.json
```

---

## Variables de entorno

Crear `frontend-s2g/.env.local`:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Ejecución

### Con Docker Compose

```bash
cd frontend-s2g
docker compose up --build
```

Accede en `http://localhost:3000`.

### Local sin Docker

```bash
cd frontend-s2g
npm install
npm run dev
```

Accede en `http://localhost:3000`.

### Build de producción

```bash
npm run build
npm start
```

---

## Credenciales de prueba

```
Email:    admin@s2g.com
Password: 123456
```

---

## Autor

**ISC Juan Valentín Alducin Vázquez** — Mayo 2025
[GitHub](https://github.com/jalducin)

## Licencia

MIT
