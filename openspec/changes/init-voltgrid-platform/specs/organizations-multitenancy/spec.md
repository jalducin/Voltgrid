## ADDED Requirements

### Requirement: Organización como tenant raíz

El sistema SHALL representar cada cliente como una `Organization` con `id` (UUID), `name`, `slug` único,
`domain` único, y campos de whitelabel (`logo_url`, `primary_color`). Toda entidad de cliente SHALL
referenciar su organización mediante `tenant_id`.

#### Scenario: Crear organización

- **WHEN** un `superadmin` crea una organización con `name`, `slug` y `domain` válidos
- **THEN** el sistema persiste la organización con un `id` UUID y la devuelve con código 201

#### Scenario: Slug y dominio únicos

- **WHEN** se intenta crear una organización con un `slug` o `domain` ya existente
- **THEN** el sistema rechaza la operación con código 409

### Requirement: Aislamiento de datos entre tenants (RLS)

El sistema SHALL aislar los datos por organización mediante Row Level Security de PostgreSQL. Cada tabla
de cliente SHALL tener RLS habilitado y forzado con una política que filtre por
`current_setting('app.current_tenant')`. La aplicación SHALL fijar el tenant actual por transacción a
partir del `org_id` del usuario autenticado y SHALL conectarse con un rol DB sin BYPASSRLS.

#### Scenario: Un tenant no puede leer datos de otro

- **WHEN** un usuario de la organización A solicita un recurso (estación, sesión, etc.) de la organización B
- **THEN** el sistema NO devuelve el recurso (404/lista vacía), aunque exista en la base de datos

#### Scenario: No se puede escribir en otro tenant

- **WHEN** un usuario autenticado intenta crear o modificar una fila con `tenant_id` distinto al suyo
- **THEN** la política RLS `WITH CHECK` rechaza la operación
