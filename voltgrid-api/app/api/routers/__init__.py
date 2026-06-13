"""Agrega todos los routers en un único api_router."""
from fastapi import APIRouter

from app.api.routers import (
    analytics,
    auth,
    health,
    organizations,
    scheduler,
    sessions,
    sso,
    stations,
    users,
    ws,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(sso.router)
api_router.include_router(organizations.router)
api_router.include_router(users.router)
api_router.include_router(stations.router)
api_router.include_router(sessions.router)
api_router.include_router(scheduler.router)
api_router.include_router(analytics.router)
api_router.include_router(ws.router)
