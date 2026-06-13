-- =============================================================================
-- VoltGrid — inicialización de PostgreSQL (se ejecuta SOLO en el primer arranque
-- del contenedor, cuando el directorio de datos está vacío).
--
-- IMPORTANTE sobre roles y RLS:
--   * POSTGRES_USER (el superusuario que crea la imagen postgres) es el rol ADMIN.
--     - Es el dueño de la base y de las tablas.
--     - Corre las migraciones de Alembic (CREATE TABLE, CREATE POLICY, etc.).
--     - Los superusuarios IGNORAN Row Level Security (RLS), por eso NO debe usarlo
--       la aplicación en tiempo de ejecución.
--   * voltgrid_app es el rol RUNTIME de la aplicación.
--     - NOSUPERUSER + NOBYPASSRLS  -> RLS sí aplica para este rol (aislamiento por tenant).
--     - Solo tiene DML (SELECT/INSERT/UPDATE/DELETE); NO crea tablas.
--
-- La contraseña de abajo es un PLACEHOLDER de desarrollo. En el .env raíz se define
-- VOLTGRID_APP_PASSWORD y el DATABASE_URL/SYNC_DATABASE_URL de los servicios `api`
-- y `scheduler` usan el rol voltgrid_app con ESA contraseña. Si cambias una, cambia
-- la otra (deben coincidir). En producción usa un secreto gestionado, no este archivo.
-- =============================================================================

-- Extensión usada por la app (UUID/gen_random_uuid, hashing, etc.).
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Rol de aplicación (idempotente por si el script se reaplica manualmente).
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'voltgrid_app') THEN
    CREATE ROLE voltgrid_app LOGIN PASSWORD 'voltgrid_app' NOSUPERUSER NOBYPASSRLS;
  END IF;
END
$$;

-- Conexión a la base actual (la que define POSTGRES_DB). Este script de init se
-- ejecuta ya conectado a POSTGRES_DB, así que current_database() es la base correcta.
DO $$
BEGIN
  EXECUTE format('GRANT CONNECT ON DATABASE %I TO voltgrid_app', current_database());
END
$$;

-- Acceso al esquema public (USAGE para resolver objetos; NO CREATE: la app no crea DDL).
GRANT USAGE ON SCHEMA public TO voltgrid_app;

-- Privilegios por DEFAULT: las tablas/secuencias las crea el rol ADMIN al migrar
-- DESPUÉS de este init. Con ALTER DEFAULT PRIVILEGES, todo objeto que cree el rol
-- ADMIN en `public` otorgará automáticamente DML a voltgrid_app, sin GRANT manual.
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO voltgrid_app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO voltgrid_app;

-- Por si ya existieran objetos (re-ejecución manual): otorga sobre lo existente.
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO voltgrid_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO voltgrid_app;
