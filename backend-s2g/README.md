# Backend — S2G Energy Dashboard

**Repositorio:** [https://github.com/jalducin/backend-s2g](https://github.com/jalducin/backend-s2g)

API REST para gestión de estaciones de carga eléctrica.

---

## Tecnologías

| | |
|---|---|
| Lenguaje | Python 3.11 |
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Base de datos | SQLite (archivo `s2g.db`) |
| Tareas programadas | APScheduler |
| Autenticación | JWT — python-jose |
| Validación | Pydantic < 2.0 |
| Contenedores | Docker & Docker Compose |

---

## Características

- Autenticación JWT con usuario hardcoded (`admin@s2g.com` / `123456`)
- CRUD de estaciones de carga: crear, listar y actualizar estado
- Filtro por estado en listado (`?status=activo|inactivo`)
- Estadísticas en tiempo real: total, activos, inactivos, suma de kW
- Scheduler automático que alterna estados cada minuto
- Endpoint manual para disparar el scheduler
- Tablas SQLite creadas automáticamente al arrancar
- Carga de datos de ejemplo desde CSV con `scripts/seed.py`

---

## Estructura

```
backend-s2g/
├── app/
│   ├── core/
│   │   ├── auth.py         # JWT: creación y verificación de tokens
│   │   ├── config.py       # Settings desde .env
│   │   ├── database.py     # Engine SQLAlchemy + sesión
│   │   └── scheduler.py    # APScheduler — alterna estados en DB
│   ├── models/
│   │   └── station.py      # Modelo SQLAlchemy Station
│   ├── routers/
│   │   ├── auth.py         # POST /auth/login
│   │   ├── station.py      # CRUD /stations
│   │   ├── stats.py        # GET /stations/stats
│   │   └── scheduler.py    # POST /scheduler/run
│   └── schemas/
│       └── station.py      # Pydantic schemas
├── data/
│   └── estaciones.csv      # 4 estaciones de ejemplo
├── scripts/
│   └── seed.py             # Carga CSV a SQLite
├── .env
├── Dockerfile
├── docker-compose.yml
├── main.py
└── requirements.txt
```

---

## Variables de entorno

Archivo `.env` en `backend-s2g/`:

```dotenv
DATABASE_URL=sqlite:///./s2g.db
SECRET_KEY=a1b2c3d4-e5f6-7890-1234-56789abcdef0
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=720
```

---

## Ejecución

### Con Docker Compose (recomendado)

```bash
cd backend-s2g
docker compose up --build
```

La API queda en `http://localhost:8000`.
Las tablas se crean automáticamente. Para cargar datos de ejemplo:

```bash
docker exec -it s2g-backend python -m scripts.seed
```

### Local sin Docker

```bash
cd backend-s2g
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Endpoints

### Autenticación

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/auth/login` | Login — devuelve JWT |

Body: `application/x-www-form-urlencoded` con `username` y `password`.
Credenciales: `admin@s2g.com` / `123456`

### Estaciones *(requieren `Authorization: Bearer <token>`)*

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/stations` | Lista todas las estaciones |
| GET | `/stations?status=activo` | Lista filtrada por estado |
| POST | `/stations` | Crea nueva estación |
| PATCH | `/stations/{id}?new_status=activo` | Actualiza estado |
| GET | `/stations/stats` | Totales y capacidad agregada |

### Scheduler *(requiere token)*

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/scheduler/run` | Ejecuta manualmente el cambio de estados |

---

## Documentación interactiva

```
http://localhost:8000/docs      # Swagger UI
http://localhost:8000/redoc     # ReDoc
```

---

## Autor

**ISC Juan Valentín Alducin Vázquez** — Mayo 2025
[GitHub](https://github.com/jalducin)

## Licencia

MIT
