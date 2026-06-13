## ADDED Requirements

### Requirement: Autenticación con JWT access + refresh

El sistema SHALL autenticar usuarios por email/contraseña y emitir un token de acceso JWT de corta
duración y un token de refresco de larga duración. Las contraseñas SHALL almacenarse con hash bcrypt.
El token de acceso SHALL incluir `sub`, `org_id`, `role`, `type` y `exp`.

#### Scenario: Login exitoso

- **WHEN** un usuario envía credenciales válidas a `POST /auth/login`
- **THEN** el sistema devuelve `access_token`, `refresh_token` y `token_type`, y actualiza `last_login`

#### Scenario: Login fallido

- **WHEN** un usuario envía credenciales inválidas
- **THEN** el sistema responde 401 sin emitir tokens

### Requirement: Rotación de refresh tokens con detección de reuso

El sistema SHALL rotar el refresh token en cada uso, persistiendo únicamente su hash SHA-256. Al
presentarse un refresh token ya revocado (reuso), el sistema SHALL revocar toda la cadena de tokens.

#### Scenario: Refresh rota el token

- **WHEN** un cliente usa un refresh token válido en `POST /auth/refresh`
- **THEN** el sistema revoca el anterior, encadena `replaced_by` y devuelve un nuevo par de tokens

#### Scenario: Reuso detectado

- **WHEN** se presenta un refresh token ya revocado
- **THEN** el sistema responde 401 y revoca la cadena completa del usuario

### Requirement: Autorización por roles

El sistema SHALL soportar los roles `superadmin`, `org_admin`, `operator`, `viewer` y SHALL restringir
los endpoints según el rol mínimo requerido.

#### Scenario: Acceso denegado por rol insuficiente

- **WHEN** un `viewer` intenta crear una estación (operación de `operator+`)
- **THEN** el sistema responde 403
