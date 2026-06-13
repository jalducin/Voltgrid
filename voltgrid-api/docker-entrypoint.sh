#!/usr/bin/env bash
# Entrypoint del API: aplica migraciones (si RUN_MIGRATIONS=true) y arranca uvicorn.
set -euo pipefail

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  echo "[entrypoint] Aplicando migraciones Alembic..."
  alembic upgrade head
fi

echo "[entrypoint] Iniciando uvicorn en 0.0.0.0:8000"
exec uvicorn main:app --host 0.0.0.0 --port 8000
