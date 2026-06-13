## ADDED Requirements

### Requirement: Estado de estaciones en tiempo real por WebSocket

El sistema SHALL exponer un canal WebSocket por estación (`/ws/stations/{id}/status`) que difunda los
cambios de estado a los clientes suscritos. El canal SHALL autenticar al cliente por token y SHALL
rechazar el acceso a estaciones de otra organización.

#### Scenario: Recibir actualización en vivo

- **WHEN** un cliente autenticado suscrito a una estación recibe un cambio de estado
- **THEN** el sistema envía por el WebSocket el nuevo estado sin que el cliente recargue

#### Scenario: WebSocket no autenticado

- **WHEN** un cliente intenta conectar sin token válido
- **THEN** el sistema cierra la conexión con código 4401

#### Scenario: Fallback a polling

- **WHEN** el cliente no puede establecer el WebSocket
- **THEN** el cliente obtiene el estado vía `GET /stations` (polling) y la app sigue funcionando
