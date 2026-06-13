"""Punto de entrada de la API de VoltGrid."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.routers import api_router
from app.core.config import settings
from app.scheduler import manager as scheduler_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Arranca/detiene el scheduler junto con la app."""
    if settings.SCHEDULER_ENABLED:
        scheduler_manager.start()
    try:
        yield
    finally:
        if settings.SCHEDULER_ENABLED:
            scheduler_manager.shutdown()


def create_app() -> FastAPI:
    app = FastAPI(
        title="VoltGrid API",
        version="1.0.0",
        description="Plataforma SaaS multi-tenant de gestión de estaciones de carga EV.",
        lifespan=lifespan,
    )

    # Sesión requerida por Authlib (almacena el state del flujo OIDC).
    app.add_middleware(SessionMiddleware, secret_key=settings.SESSION_SECRET_KEY)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    return app


app = create_app()
