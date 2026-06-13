"""Configuración de la aplicación (pydantic-settings v2)."""
from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Settings de VoltGrid leídos desde variables de entorno / .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ENV: str = "dev"

    # Base de datos
    DATABASE_URL: str = "postgresql+asyncpg://voltgrid:voltgrid@localhost:5432/voltgrid"
    SYNC_DATABASE_URL: str = "postgresql+psycopg://voltgrid:voltgrid@localhost:5432/voltgrid"

    # JWT
    JWT_SECRET: str = "cambia-esto-por-una-clave-larga-y-aleatoria"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # SSO / sesión
    SESSION_SECRET_KEY: str = "cambia-esto-tambien"
    OAUTH_REDIRECT_BASE_URL: str = "http://localhost:8000"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT: str = "common"

    # CORS (NoDecode: el valor del .env llega como cadena y lo divide el validador)
    CORS_ORIGINS: Annotated[list[str], NoDecode] = ["http://localhost:3000"]

    # Scheduler
    SCHEDULER_ENABLED: bool = True

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, v: object) -> object:
        """Permite definir CORS_ORIGINS como lista o como cadena separada por comas."""
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @property
    def google_enabled(self) -> bool:
        return bool(self.GOOGLE_CLIENT_ID and self.GOOGLE_CLIENT_SECRET)

    @property
    def microsoft_enabled(self) -> bool:
        return bool(self.MICROSOFT_CLIENT_ID and self.MICROSOFT_CLIENT_SECRET)


@lru_cache
def get_settings() -> Settings:
    """Devuelve la instancia única de Settings (cacheada)."""
    return Settings()


settings = get_settings()
