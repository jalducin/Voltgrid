## ADDED Requirements

### Requirement: KPIs con filtros server-side

El sistema SHALL exponer KPIs por organización: uptime por estación, kWh entregados y sesiones activas.
Los filtros (fecha, ubicación, capacidad, estado) SHALL aplicarse en el backend, no en el cliente.

#### Scenario: Consultar KPIs filtrados

- **WHEN** un usuario solicita `GET /analytics/kpis` con un rango de fechas y filtro de ubicación
- **THEN** el sistema calcula y devuelve los KPIs solo de su organización aplicando los filtros en la consulta

### Requirement: Exportación a CSV

El sistema SHALL permitir exportar los datos filtrados a CSV mediante una respuesta en streaming.

#### Scenario: Exportar CSV

- **WHEN** un usuario solicita `GET /analytics/export.csv` con filtros
- **THEN** el sistema responde con `text/csv` y `Content-Disposition: attachment` con las filas filtradas
