# app/core/config.py
import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()  # Carga el .env en memoria

class Settings(BaseSettings):
    # URL de la BD
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./s2g.db"
    )
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "cambia_esto_por_una_clave_segura")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 720))

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
