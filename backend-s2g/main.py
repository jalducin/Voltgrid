from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.scheduler import start_scheduler
from app.core.database import Base, engine
from app.routers.auth import router as auth_router
from app.routers.station import router as station_router
from app.routers.stats import router as stats_router
from app.routers.scheduler import router as scheduler_router

app = FastAPI(title="S2G Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar todos los routers
app.include_router(auth_router)
app.include_router(station_router)
app.include_router(stats_router)
app.include_router(scheduler_router)

@app.on_event("startup")
def startup_event():
    # Crea las tablas si no existen (SQLite las genera en s2g.db)
    Base.metadata.create_all(bind=engine)
    # Inicia el APScheduler
    start_scheduler()
