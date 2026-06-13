## ADDED Requirements

### Requirement: Gestión de estaciones de carga

El sistema SHALL permitir crear, listar, consultar, actualizar y eliminar estaciones de carga dentro de
la organización del usuario. Una estación SHALL tener `name`, `location`, `lat`, `lng`, `max_kw` y
`status` (`available`, `occupied`, `offline`, `maintenance`).

#### Scenario: Crear estación

- **WHEN** un `operator` crea una estación con datos válidos
- **THEN** el sistema la persiste con `tenant_id` de su organización y la devuelve con 201

#### Scenario: Listar con filtro por estado

- **WHEN** un usuario solicita `GET /stations?status=available`
- **THEN** el sistema devuelve solo las estaciones de su organización con estado `available`

### Requirement: Cambio de estado auditable

El sistema SHALL registrar cada cambio de estado de una estación en `StatusLog` con `old_status`,
`new_status`, `changed_by`, `source` (`manual`/`scheduler`/`api`) y `timestamp`, y SHALL difundir el
cambio por WebSocket.

#### Scenario: Cambio manual de estado

- **WHEN** un `operator` cambia el estado de una estación vía `PATCH /stations/{id}`
- **THEN** el sistema actualiza el estado, crea un `StatusLog` con `source=manual` y emite el evento por WS
