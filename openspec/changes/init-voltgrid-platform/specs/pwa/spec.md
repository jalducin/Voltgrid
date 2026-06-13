## ADDED Requirements

### Requirement: Aplicación web instalable (PWA)

El frontend SHALL ser una PWA instalable con manifest y service worker, y SHALL funcionar con datos
cacheados cuando no hay conexión.

#### Scenario: Instalación

- **WHEN** un usuario abre la app en un navegador compatible
- **THEN** el navegador ofrece instalarla como aplicación

#### Scenario: Modo offline

- **WHEN** el usuario pierde conexión tras haber cargado el dashboard
- **THEN** la app muestra los datos cacheados sin fallar
