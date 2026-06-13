"""Seguridad: hashing de contraseñas y emisión/validación de JWT (access + refresh)."""
from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

# bcrypt opera sobre máximo 72 bytes; truncamos explícitamente para evitar errores.
_BCRYPT_MAX_BYTES = 72


# --- Contraseñas (bcrypt directo) ---
def hash_password(password: str) -> str:
    pw = password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    pw = plain.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    try:
        return bcrypt.checkpw(pw, hashed.encode("utf-8"))
    except ValueError:
        return False


# --- JWT ---
def _now() -> datetime:
    return datetime.now(tz=UTC)


def create_access_token(*, user_id: uuid.UUID, org_id: uuid.UUID, role: str) -> str:
    """Crea un access token de corta duración con los claims de autorización."""
    now = _now()
    payload = {
        "sub": str(user_id),
        "org_id": str(org_id),
        "role": role,
        "type": ACCESS_TOKEN_TYPE,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "jti": secrets.token_hex(8),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(*, user_id: uuid.UUID, org_id: uuid.UUID) -> tuple[str, datetime]:
    """Crea un refresh token opaco-JWT. Devuelve (token, expiración)."""
    now = _now()
    expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "org_id": str(org_id),
        "type": REFRESH_TOKEN_TYPE,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
        "jti": secrets.token_hex(16),
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token, expires_at


def decode_token(token: str, *, expected_type: str | None = None) -> dict:
    """Decodifica y valida firma/exp. Lanza JWTError si es inválido o el tipo no coincide."""
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    if expected_type is not None and payload.get("type") != expected_type:
        raise JWTError(f"Tipo de token inesperado: {payload.get('type')}")
    return payload


def hash_token(token: str) -> str:
    """SHA-256 hex de un refresh token, para persistirlo sin guardar el valor en claro."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
