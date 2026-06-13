## ADDED Requirements

### Requirement: Personalización visual por organización

El sistema SHALL permitir que cada organización defina logo (`logo_url`), color primario
(`primary_color`) y nombre de aplicación, y SHALL exponerlos para que el frontend aplique el tema
correspondiente al tenant del usuario.

#### Scenario: Aplicar tema del tenant

- **WHEN** un usuario inicia sesión en una organización con whitelabel configurado
- **THEN** el frontend muestra el logo, color y nombre de esa organización

#### Scenario: Editar whitelabel

- **WHEN** un `org_admin` actualiza el color primario o el logo de su organización
- **THEN** el sistema persiste los cambios y el frontend los refleja en la siguiente carga
