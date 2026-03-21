# S2G Energy Dashboard

Sistema de gestión de estaciones de carga eléctrica.
Backend FastAPI + SQLite · Frontend Next.js 14 + Tailwind CSS.

---

## Servicios

| Servicio | Tecnología | Puerto |
|---|---|---|
| Backend API | FastAPI + SQLite | `8000` |
| Frontend | Next.js 14 | `3000` |

---

## Requisitos

- Docker >= 20.10
- Docker Compose >= 2.0

---

## Levantar todo con Docker Compose

Desde la raíz del proyecto:

```bash
# Primera vez o después de cambios en código
docker compose up --build

# Siguientes veces (sin rebuild)
docker compose up

# En segundo plano
docker compose up -d --build
```

Servicios disponibles:

```
http://localhost:8000        API Backend
http://localhost:8000/docs   Swagger UI
http://localhost:3000        Dashboard Frontend
```

Cargar datos de ejemplo (opcional, solo una vez):

```bash
docker exec -it s2g-backend python -m scripts.seed
```

Detener y limpiar:

```bash
docker compose down           # detiene contenedores
docker compose down -v        # detiene y borra volumen SQLite
```

---

## Desarrollo local (sin Docker)

### Backend

```bash
cd backend-s2g
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Variables necesarias en `backend-s2g/.env`:

```dotenv
DATABASE_URL=sqlite:///./s2g.db
SECRET_KEY=a1b2c3d4-e5f6-7890-1234-56789abcdef0
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=720
```

### Frontend

```bash
cd frontend-s2g
npm install
npm run dev
```

Variable necesaria en `frontend-s2g/.env.local`:

```dotenv
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Credenciales de prueba

```
Email:    admin@s2g.com
Password: 123456
```

---

## Estructura del repositorio

```
Crud-PythonReact/
├── backend-s2g/           # API FastAPI + SQLite
│   ├── app/
│   │   ├── core/          # config, database, auth, scheduler
│   │   ├── models/        # Station (SQLAlchemy)
│   │   ├── routers/       # auth, station, stats, scheduler
│   │   └── schemas/       # Pydantic schemas
│   ├── data/              # estaciones.csv (datos de ejemplo)
│   ├── scripts/           # seed.py
│   ├── .env
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── main.py
├── frontend-s2g/          # Dashboard Next.js
│   ├── components/        # Login, StationForm, StationList, StationChart
│   ├── pages/             # _app.tsx, index.tsx
│   ├── utils/             # api.ts (Axios + interceptor JWT)
│   ├── styles/            # globals.css (Tailwind)
│   ├── .env.local
│   ├── Dockerfile
│   └── docker-compose.yml
├── docker-compose.yml     # Orquesta backend + frontend
└── README.md
```

---

## API — resumen de endpoints

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/auth/login` | No | Login — devuelve JWT |
| GET | `/stations` | Bearer | Lista estaciones |
| GET | `/stations?status=activo` | Bearer | Lista filtrada |
| POST | `/stations` | Bearer | Crear estación |
| PATCH | `/stations/{id}?new_status=activo` | Bearer | Cambiar estado |
| GET | `/stations/stats` | Bearer | Totales y capacidad |
| POST | `/scheduler/run` | Bearer | Ejecutar scheduler manualmente |

---

## Autor

**ISC Juan Valentín Alducin Vázquez** — Mayo 2025
[GitHub](https://github.com/jalducin)

## Licencia

MIT
