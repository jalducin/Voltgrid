## ADDED Requirements

### Requirement: Cambios de estado automáticos configurables por organización

El sistema SHALL permitir a un `org_admin` configurar un job que cambie el estado de las estaciones de su
organización cada N minutos. La configuración (`enabled`, `interval_minutes`) SHALL persistirse y los jobs
SHALL sobrevivir a reinicios (jobstore persistente).

#### Scenario: Activar el scheduler

- **WHEN** un `org_admin` guarda `enabled=true` con `interval_minutes=5` en `PUT /scheduler/config`
- **THEN** el sistema programa el job para su organización y lo persiste

#### Scenario: Ejecución auditable

- **WHEN** el job se ejecuta (o se invoca `POST /scheduler/run-now`)
- **THEN** cada cambio de estado genera un `StatusLog` con `source=scheduler` y se difunde por WebSocket
