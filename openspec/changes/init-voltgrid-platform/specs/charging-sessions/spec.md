## ADDED Requirements

### Requirement: Registro de sesiones de carga

El sistema SHALL registrar sesiones de carga asociadas a una estación, con `started_at`, `ended_at`
(nullable mientras está activa), `kwh_delivered` y `cost`. Una sesión activa SHALL tener `ended_at` nulo.

#### Scenario: Iniciar sesión de carga

- **WHEN** se inicia una sesión en una estación de la organización del usuario
- **THEN** el sistema crea la sesión con `started_at` y `ended_at = null`

#### Scenario: Cerrar sesión de carga

- **WHEN** se finaliza una sesión activa indicando `kwh_delivered`
- **THEN** el sistema fija `ended_at` y calcula/almacena el `cost`
