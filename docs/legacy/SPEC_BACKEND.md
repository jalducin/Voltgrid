# SPEC BACKEND — S2G Energy Dashboard
> Responsable: **Claude** | Stack: FastAPI + SQLAlchemy + MySQL + APScheduler
> Ingeniería inversa realizada el 2026-03-21

---

## Contexto del sistema

API REST para gestión de estaciones de carga eléctrica.
Desplegada en Docker con MySQL 8.0. JWT para autenticación.
APScheduler cambia estatus de estaciones cada 1 minuto.

---

## Bugs detectados (ordenados por severidad)

### 🔴 BUG-B01 — `auth.py`: Atributos de Settings en minúsculas incorrectas
**Archivo:** `app/core/auth.py` líneas 11–13, 22
**Causa:** Los campos en `Settings` se definen en MAYÚSCULAS (`SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`) pero se acceden en minúsculas. Pydantic v1 `BaseSettings` expone los atributos con el nombre exacto del campo.
**Error en runtime:** `AttributeError` al crear o verificar tokens → toda la autenticación falla.

```python
# ACTUAL (roto)
expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])

# CORRECTO
expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
```

**Fix:** Cambiar las 4 referencias a mayúsculas en `app/core/auth.py`.

---

### 🔴 BUG-B02 — `station.py` router: parámetro `status` oculta el módulo `fastapi.status`
**Archivo:** `app/routers/station.py` líneas 1, 31–46
**Causa:** El endpoint `PATCH /{station_id}` tiene un parámetro `status: str`. En la línea 39 se usa `status.HTTP_404_NOT_FOUND` esperando el módulo importado, pero `status` en ese scope ya es el string del parámetro.
**Error en runtime:** `AttributeError: 'str' object has no attribute 'HTTP_404_NOT_FOUND'` cuando la estación no existe.

```python
# ACTUAL (roto)
@router.patch("/{station_id}", response_model=Station)
def update_station_status(
    station_id: int,
    status: str,           # <-- oculta el módulo status
    db: Session = Depends(get_db)
):
    ...
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, ...)  # CRASH

# CORRECTO — renombrar el parámetro a new_status
@router.patch("/{station_id}", response_model=Station)
def update_station_status(
    station_id: int,
    new_status: str,
    db: Session = Depends(get_db)
):
    ...
    db_station.status = new_status
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, ...)  # OK
```

**Fix:** Renombrar el parámetro query a `new_status` en la firma y en la asignación.

---

### 🔴 BUG-B03 — Falta `DATABASE_URL` en `.env` y en `docker-compose.yml`
**Archivos:** `backend-s2g/.env`, `backend-s2g/docker-compose.yml`
**Causa:** El default en `config.py` apunta a `127.0.0.1` (localhost), pero dentro de Docker el servicio MySQL se llama `db`. El `.env` actual no tiene `DATABASE_URL`. Docker compose no lo inyecta.
**Error en runtime:** Backend no puede conectar a MySQL → todas las rutas `/stations` fallan con `OperationalError`.

```bash
# Añadir al .env:
DATABASE_URL=mysql+pymysql://root:DevOps25%25@db/s2g_db

# Añadir al docker-compose.yml, sección backend → environment:
DATABASE_URL: mysql+pymysql://root:${MYSQL_ROOT_PASSWORD}@db/${MYSQL_DATABASE}
```

> **Nota:** el `%` en la contraseña debe ser `%25` cuando va en URL, o usar variables separadas.

**Fix:** Agregar `DATABASE_URL` al `.env` con host `db`, e inyectarlo explícitamente en `docker-compose.yml`.

---

### 🔴 BUG-B04 — `docker-compose.yml`: `depends_on` sin condición de salud
**Archivo:** `backend-s2g/docker-compose.yml` línea 24
**Causa:** `depends_on: - db` solo espera que el contenedor *arranque*, no que MySQL esté *listo*. El healthcheck está definido pero no referenciado. El backend intenta conectar antes de que MySQL acepte conexiones.
**Error en runtime:** Race condition → backend crashea al inicio con `Can't connect to MySQL server`.

```yaml
# ACTUAL (roto)
depends_on:
  - db

# CORRECTO
depends_on:
  db:
    condition: service_healthy
```

**Fix:** Cambiar `depends_on` a formato largo con `condition: service_healthy`.

---

### 🟡 BUG-B05 — `GET /stations` no soporta filtro por `?status=`
**Archivo:** `app/routers/station.py` línea 27–29
**Causa:** El frontend envía `GET /stations?status=activo` pero el endpoint ignora el query param y devuelve todas las estaciones.
**Efecto:** El filtro visual del frontend no filtra — muestra todas las estaciones siempre.

```python
# ACTUAL (roto)
@router.get("/", response_model=List[Station])
def get_stations(db: Session = Depends(get_db)):
    return db.query(StationModel).all()

# CORRECTO
from typing import Optional

@router.get("/", response_model=List[Station])
def get_stations(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(StationModel)
    if status:
        q = q.filter(StationModel.status == status)
    return q.all()
```

**Fix:** Agregar parámetro opcional `status: Optional[str] = None` y aplicar filtro si viene.

---

### 🟡 BUG-B06 — `stats.py`: comparación de Enum con string puede fallar
**Archivo:** `app/routers/stats.py` líneas 19–26
**Causa:** `StationModel.status` es `Enum(StatusEnum)` en SQLAlchemy. Filtrar con `== "activo"` (string) funciona en MySQL pero puede fallar en otros drivers o versiones. La práctica correcta es comparar con el enum.

```python
# ACTUAL (frágil)
.filter(StationModel.status == "activo")
.filter(StationModel.status == "inactivo")

# CORRECTO
from app.models.station import StatusEnum
.filter(StationModel.status == StatusEnum.activo)
.filter(StationModel.status == StatusEnum.inactivo)
```

**Fix:** Importar `StatusEnum` en `stats.py` y usar valores de enum en los filtros.

---

### 🟡 BUG-B07 — `scheduler.py`: opera sobre lista vacía en memoria
**Archivo:** `app/core/scheduler.py` + `app/models/fake_db.py`
**Causa:** `fake_db.stations = []` siempre está vacío. El scheduler cambia estatus en esa lista, no en MySQL. No hay efecto en la base de datos.
**Efecto:** El endpoint `POST /scheduler/run` no hace nada útil. La feature de "cambio automático de estado" no funciona.

**Fix recomendado:** Conectar el scheduler a la DB usando una sesión SQLAlchemy:

```python
# app/core/scheduler.py — versión funcional
from apscheduler.schedulers.background import BackgroundScheduler
from app.core.database import SessionLocal
from app.models.station import Station, StatusEnum

def change_status():
    db = SessionLocal()
    try:
        stations = db.query(Station).all()
        for s in stations:
            s.status = StatusEnum.inactivo if s.status == StatusEnum.activo else StatusEnum.activo
        db.commit()
    finally:
        db.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(change_status, "interval", minutes=1)
    scheduler.start()
```

---

### 🟡 BUG-B08 — `auth.py` router: SECRET_KEY hardcodeada, ignora settings
**Archivo:** `app/routers/auth.py` líneas 8–9
**Causa:** El router de auth define sus propias constantes `SECRET_KEY = "s2g_secret_key"` y `ALGORITHM = "HS256"` en lugar de usar `settings`. Los tokens que genera este router no son verificables por `app/core/auth.py` que usa la clave del `.env`.
**Efecto:** Token creado con clave `"s2g_secret_key"` pero verificado con clave `"a1b2c3d4-..."` del `.env` → todos los requests autenticados fallan con 401.

```python
# ACTUAL (roto)
SECRET_KEY = "s2g_secret_key"
ALGORITHM = "HS256"
token = jwt.encode({...}, SECRET_KEY, algorithm=ALGORITHM)

# CORRECTO
from app.core.config import settings
token = jwt.encode({...}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

**Fix:** Eliminar constantes locales en `app/routers/auth.py` y usar `settings`.

---

## Resumen de archivos a modificar

| Archivo | Bugs |
|---|---|
| `app/core/auth.py` | B01 |
| `app/routers/auth.py` | B08 |
| `app/routers/station.py` | B02, B05 |
| `app/routers/stats.py` | B06 |
| `app/core/scheduler.py` | B07 |
| `backend-s2g/.env` | B03 |
| `backend-s2g/docker-compose.yml` | B03, B04 |

---

## Orden de ejecución de fixes

1. **B08** → `auth.py` router usa `settings` (sin esto, nada autentica)
2. **B01** → `core/auth.py` atributos en mayúsculas (sin esto, verify_token crashea)
3. **B03** → `.env` + `docker-compose.yml` con `DATABASE_URL` correcto (sin esto, no hay DB)
4. **B04** → `depends_on` con health condition (sin esto, race condition al arrancar)
5. **B02** → parámetro `new_status` en station router (sin esto, PATCH crashea)
6. **B05** → filtro por status en GET /stations (funcionalidad de filtro)
7. **B06** → comparación con enum en stats (robustez)
8. **B07** → scheduler con DB real (funcionalidad automática)

---

## Contrato de API (estado esperado post-fix)

```
POST   /auth/login                 → {access_token, token_type}   (sin auth)
GET    /stations?status=activo     → Station[]                     (Bearer)
GET    /stations                   → Station[]                     (Bearer)
POST   /stations                   → Station 201                   (Bearer)
PATCH  /stations/{id}?new_status=X → Station                      (Bearer)
GET    /stations/stats             → {total, activos, inactivos, total_kw} (Bearer)
POST   /scheduler/run              → {detail: "Scheduler executed"} (Bearer)
```

---

## Variables de entorno requeridas (`.env` final)

```env
MYSQL_ROOT_PASSWORD=DevOps25%
MYSQL_DATABASE=s2g_db
DATABASE_URL=mysql+pymysql://root:DevOps25%25@db/s2g_db
SECRET_KEY=a1b2c3d4-e5f6-7890-1234-56789abcdef0
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=720
```
