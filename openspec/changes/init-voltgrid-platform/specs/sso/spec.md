## ADDED Requirements

### Requirement: Inicio de sesión federado (OIDC)

El sistema SHALL permitir autenticación con Google y Microsoft vía OAuth2/OIDC. Tras el callback, el
sistema SHALL resolver la organización a partir del dominio del correo (`Organization.domain`) y emitir
el mismo par de tokens JWT que el login por contraseña.

#### Scenario: Login SSO con dominio reconocido

- **WHEN** un usuario completa el flujo SSO y su dominio de correo coincide con una organización registrada
- **THEN** el sistema lo autentica, auto-provisiona el usuario con rol `viewer` si no existe, y emite tokens

#### Scenario: Dominio sin organización

- **WHEN** el dominio del correo no corresponde a ninguna organización
- **THEN** el sistema rechaza el acceso con 403
