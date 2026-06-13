"""Enumeraciones del dominio (mapeadas a tipos enum nativos de PostgreSQL)."""
from __future__ import annotations

import enum


class RoleEnum(str, enum.Enum):
    """Roles de usuario, de mayor a menor privilegio."""

    superadmin = "superadmin"
    org_admin = "org_admin"
    operator = "operator"
    viewer = "viewer"


class StationStatus(str, enum.Enum):
    """Estados posibles de una estación de carga."""

    available = "available"
    occupied = "occupied"
    offline = "offline"
    maintenance = "maintenance"


class StatusSource(str, enum.Enum):
    """Origen de un cambio de estado registrado en StatusLog."""

    manual = "manual"
    scheduler = "scheduler"
    api = "api"


class SsoProvider(str, enum.Enum):
    """Proveedores de identidad federada soportados."""

    google = "google"
    microsoft = "microsoft"
