# Modelo de Datos — Chiapas Conecta

**Estado:** propuesta de arquitectura para el backend futuro.  
**Motor objetivo:** PostgreSQL 16 o posterior.  
**Versión del documento:** 1.0  
**Alcance:** MVP funcional de gestión social y evolución prevista.

> Este documento especifica el modelo lógico y sus restricciones. El repositorio actual contiene un prototipo frontend local y no implementa este esquema, autenticación, sincronización con servidor ni procesos descritos aquí. Antes de desplegar, deben confirmarse con la ONG las políticas de privacidad, retención, consentimiento, evaluación y operación financiera.

## 1. Introducción

### Objetivo

Establecer una fuente de verdad común para persistir comunidades, sus necesidades, solicitudes de apoyo, evaluación y priorización, proyectos aprobados, participación de colaboradores, seguimiento y resultados. El modelo guía futuras migraciones de PostgreSQL, validaciones de dominio, integración del frontend, reportes y auditoría; no especifica backend, endpoints ni interfaces.

### Alcance del MVP

El MVP administra organizaciones y usuarios con membresías/roles, comunidades y representantes, catálogo de categorías, solicitudes y su historial, evaluaciones versionadas con puntajes, perfiles y ofertas de especialistas, postulaciones de colaboración, proyectos con hitos/asignaciones, reportes de progreso, notificaciones y auditoría. El alcance concreto se detalla en la sección 3. Finanzas, donaciones, disponibilidad avanzada, credenciales verificadas y analítica extensa quedan fuera del primer corte.

### Principios

1. **Normalización hasta 3FN:** cada hecho se almacena una sola vez; catálogos y relaciones N:M se representan como entidades propias.
2. **Identidad estable:** PK UUID (`gen_random_uuid()`); no se usan nombres ni correos como claves de relación.
3. **Integridad en PostgreSQL:** `NOT NULL`, `CHECK`, `UNIQUE`, FK y transacciones protegen invariantes compartidas.
4. **Trazabilidad:** historial de cambios de estado y bitácora de acciones son conceptos distintos y complementarios.
5. **Privacidad por minimización:** guardar únicamente datos personales y ubicación necesarios; permisos restrictivos y retención definida por política.
6. **Evolución aditiva:** catálogos y versiones permiten cambios de vocabulario/reglas sin reinterpretar registros históricos.
7. **Accesibilidad territorial:** textos en español inicialmente; se deja espacio para localización validada por comunidades, sin asumir traducciones.

### Supuestos explícitos

- Una instalación puede atender varias organizaciones; cada comunidad tiene una organización responsable primaria en MVP. La coadministración se deja para una fase futura.
- `User` es una identidad de acceso global; la autorización de negocio se limita por `OrganizationMembership` y, cuando aplique, por rol.
- Una comunidad puede tener varios representantes y como máximo uno principal activo.
- Una solicitud corresponde a una comunidad y una categoría principal. Etiquetas múltiples pueden añadirse después con relación N:M.
- Una evaluación tiene una versión inmutable del modelo y múltiples puntajes por criterio. La prioridad no se infiere automáticamente de un puntaje sin política aprobada.
- Una solicitud aprobada puede tardar en convertirse en proyecto. Una solicitud puede originar cero o un proyecto; cada proyecto se origina en cero o una solicitud.
- Un proyecto puede tener varias asignaciones, fuentes/partidas financieras y reportes a lo largo del tiempo.
- Montos usan `NUMERIC(14,2)` y moneda ISO 4217 de tres letras. No se asume una moneda exclusiva.
- Las fechas de evento se almacenan como `TIMESTAMPTZ`; fechas civiles como `DATE`; la zona horaria de presentación es configuración, no dato implícito.

### Restricciones y decisiones pendientes

- PostgreSQL no debe almacenar secretos de autenticación en texto plano. Contraseñas/hash, MFA, proveedor de identidad, recuperación y sesiones quedan fuera del diccionario de negocio y requieren diseño de seguridad aparte.
- No se presuponen reglas legales de consentimiento, protección de datos personales, retención, residencia, clasificación de comunidades ni autorización de fotografías/documentos. Son decisiones previas a producción.
- La información étnica, lingüística, geográfica precisa, necesidades y evidencias puede ser sensible. No debe publicarse por defecto; acceso, consentimiento y granularidad deben definirse con las comunidades.
- “Evaluación”, “priorización” y “aprobación” son procesos humanos sujetos a política documentada; el modelo no decide elegibilidad ni sustituye consentimiento informado.
- Reglas de borrado, anonimización, recuperación y cierre de organizaciones quedan sujetas a política institucional.

## 2. Dominios del sistema

### Seguridad e identidad

`User`, `Role`, `Permission`, `OrganizationMembership` (asociación de identidad, organización y rol). Para el MVP no se requiere una entidad puente `UserRole` global: el rol se asigna dentro de la membresía organizacional. En el futuro puede añadirse asignación de varios roles por membresía.

### Organizaciones y comunidades

`Organization`, `Community`, `CommunityRepresentative`, `CommunityResource`, `CommunityNeed`. La pertenencia de usuarios a ONG/organizaciones se almacena en `OrganizationMembership`; no se mezcla el perfil comunitario con la identidad de acceso.

### Catálogos y solicitudes

`ServiceCategory`, `ServiceRequest`, `RequestAttachment`, `RequestStatusHistory`. Categoría es catálogo administrable. Necesidad comunitaria es un registro contextual, distinto del catálogo de categorías.

### Evaluación y priorización

`EvaluationCriteria`, `EvaluationModelVersion`, `RequestEvaluation`, `EvaluationScore`. Una versión agrupa criterios y parámetros; una evaluación conserva la versión aplicada y sus resultados, para reproducibilidad.

### Especialistas y colaboración

`SpecialistProfile`, `ProfessionalCredential`, `ServiceOffering`, `Availability`, `CollaborationApplication`. Perfil profesional y cuenta de acceso son entidades separadas; la disponibilidad es opcional y se omite del MVP.

### Proyectos y seguimiento

`Project`, `ProjectMilestone`, `ProjectAssignment`, `ProgressReport`. Colaboradores son asignaciones a proyectos, no columnas repetidas dentro de `Project`.

### Finanzas

`FundingSource`, `Donation`, `FundAllocation`, `ProjectExpense`. Se difiere el conjunto completo: no se debe presentar el MVP como contabilidad ni como sistema fiscal.

### Auditoría y comunicación

`AuditLog`, `Notification`. La bitácora registra acciones relevantes; el historial de estados conserva la secuencia de negocio. Notificación almacena entrega/lectura, no reemplaza correo/SMS ni garantiza entrega externa.

## 3. MVP

| Entidad | Decisión | Justificación |
|---|---|---|
| User | Obligatoria | Actor autenticado y autoría de operaciones. |
| Role | Obligatoria | Autorización comprensible y asignada por organización. |
| Permission | Postergada (catálogo mínimo configurable) | RBAC fino puede añadirse cuando haya matriz de acceso aprobada; MVP puede usar roles predefinidos. |
| Organization | Obligatoria | Delimita operación, membresías y responsabilidad. |
| OrganizationMembership | Obligatoria | Asocia usuarios, organización, rol y estado. |
| Community | Obligatoria | Núcleo territorial del servicio. |
| CommunityRepresentative | Obligatoria | Contacto/representación y punto de validación comunitaria. |
| CommunityResource | Postergada | Inventario descriptivo no necesario para el flujo base. |
| CommunityNeed | Postergada | Puede modelarse inicialmente mediante la descripción de solicitud; se incorpora si se necesita planificación comunitaria longitudinal. |
| ServiceCategory | Obligatoria | Clasificación y filtros consistentes. |
| ServiceRequest | Obligatoria | Unidad de entrada al proceso. |
| RequestAttachment | Obligatoria si el flujo exige evidencia; entidad incluida | Referencia segura a documentos y evidencia sin guardar binarios en filas. |
| RequestStatusHistory | Obligatoria | Trazabilidad del flujo y explicación de decisiones. |
| EvaluationCriteria | Obligatoria | Hace explícita la evaluación. |
| EvaluationModelVersion | Obligatoria | Reproduce cuál conjunto de criterios se aplicó. |
| RequestEvaluation | Obligatoria | Registra evaluación y dictamen revisable. |
| EvaluationScore | Obligatoria | Puntajes por criterio; permite explicación y auditoría. |
| SpecialistProfile | Obligatoria si hay directorio/postulación en MVP; si no, fase posterior | Necesaria para vincular colaboradores identificables. |
| ProfessionalCredential | Postergada | Verificación documental añade riesgo y operación; no afirmar verificación sin proceso. |
| ServiceOffering | Obligatoria para matching estructurado; puede posponerse si colaboración es manual | Describe los servicios ofrecidos sin campos repetidos en perfil. |
| Availability | Postergada | Agenda y zonas horarias aumentan complejidad. |
| CollaborationApplication | Obligatoria si se reciben postulaciones; en MVP | Permite revisar, aceptar/rechazar y evitar acuerdos informales sin rastro. |
| Project | Obligatoria | Unidad de ejecución posterior a aprobación. |
| ProjectMilestone | Obligatoria | Estructura de planificación y avance. |
| ProjectAssignment | Obligatoria | Registra equipo y función por proyecto. |
| FundingSource | Postergada | Requiere ciclo financiero institucional. |
| Donation | Postergada | Requiere pagos, conciliación y obligaciones regulatorias. |
| FundAllocation | Postergada | Requiere presupuesto y control de fondos. |
| ProjectExpense | Postergada | Requiere controles financieros, comprobantes y políticas contables. |
| ProgressReport | Obligatoria | Seguimiento periódico y evidencia de resultados. |
| AuditLog | Obligatoria | Responsabilidad y trazabilidad de acceso/cambios críticos. |
| Notification | Obligatoria para bandeja interna; entrega externa posterior | Informa cambios sin convertir proveedor de mensajería en fuente de verdad. |

“Obligatoria” define el modelo propuesto del MVP, no el estado del prototipo actual. La inclusión final de especialista/postulación depende de que la primera versión habilite colaboración externa.

## 4. Diccionario de datos

### Convenciones

- `UUID`, `TEXT`, `VARCHAR(n)`, `BOOLEAN`, `INTEGER`, `SMALLINT`, `DATE`, `TIMESTAMPTZ`, `JSONB`, `NUMERIC(p,s)` son tipos PostgreSQL o equivalentes.
- Todas las entidades tienen `id UUID PK DEFAULT gen_random_uuid()` salvo que se indique lo contrario. Todas las tablas mutables incluyen `created_at TIMESTAMPTZ NOT NULL DEFAULT now()` y `updated_at TIMESTAMPTZ NOT NULL DEFAULT now()`; son campos auditables de ciclo de vida. `updated_at` se mantiene en cada actualización mediante aplicación o trigger uniforme.
- FK no especificada como nullable es `NOT NULL`. Borrado predeterminado `RESTRICT`; entidades dependientes puramente asociativas pueden usar `CASCADE` con política explícita. No usar borrado en cascada para auditoría, decisiones o finanzas.
- Valores de estado son `TEXT` con `CHECK` o catálogos; preferir `TEXT + CHECK` cuando el conjunto es estable y catálogo versionado cuando es administrable. No utilizar ENUM PostgreSQL para estados que evolucionan frecuentemente.
- PII se indica como dato personal. Archivos se almacenan fuera de PostgreSQL; se persiste metadato y referencia con acceso controlado.

### Identidad y organización

# Entity: User

Descripción: Identidad de persona con acceso al sistema. Los datos de autenticación se administran mediante componente de identidad seguro aparte.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| email | VARCHAR(320) | Sí | UNIQUE; normalizar minúsculas/espacios | Correo de acceso; dato personal. |
| display_name | VARCHAR(200) | Sí | longitud > 0 | Nombre mostrado. |
| phone_e164 | VARCHAR(16) | No | formato E.164 si existe | Teléfono; dato personal. |
| preferred_locale | VARCHAR(16) | No | locale permitido por configuración | Preferencia de idioma; no prueba competencia lingüística. |
| status | TEXT | Sí | `ACTIVE`, `INVITED`, `SUSPENDED`, `DEACTIVATED` | Estado de acceso. |
| last_login_at | TIMESTAMPTZ | No | — | Último acceso conocido. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: Role

Descripción: Rol de autorización, acotado a una organización. Roles base sugeridos: `ORG_ADMIN`, `CASE_MANAGER`, `EVALUATOR`, `PROJECT_MANAGER`, `FINANCE`, `SPECIALIST`, `COMMUNITY_MEMBER`, `READ_ONLY`; son ejemplos a validar.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| organization_id | UUID | No | FK Organization; NULL solo para roles de sistema | Organización propietaria del rol personalizado. |
| code | VARCHAR(64) | Sí | UNIQUE por organización y código; mayúsculas | Código estable. |
| name | VARCHAR(120) | Sí | — | Etiqueta. |
| description | TEXT | No | — | Alcance esperado. |
| is_system | BOOLEAN | Sí | DEFAULT false | Protege roles base de edición accidental. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: Permission

Descripción: Permiso atómico del catálogo, reservado a autorización granular posterior. No contiene secretos.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| code | VARCHAR(120) | Sí | UNIQUE | Código como `request.read` (propuesta). |
| description | TEXT | No | — | Acción/recurso documentados. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

**Relación adicional:** `RolePermission(role_id, permission_id)` PK compuesta, ambas FK NOT NULL, `created_at`; materializa N:M. Se crea cuando se implemente autorización granular.

### Entity: Organization

Descripción: ONG u organización colaboradora que opera en la plataforma.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| name | VARCHAR(200) | Sí | — | Nombre legal o público según política. |
| slug | VARCHAR(120) | Sí | UNIQUE; formato URL seguro | Identificador legible. |
| organization_type | TEXT | Sí | catálogo controlado | Tipo institucional; definir catálogo con negocio. |
| tax_identifier | VARCHAR(80) | No | UNIQUE cuando exista, cifrado/restringido según política | Identificador fiscal; dato sensible. |
| contact_email | VARCHAR(320) | No | — | Correo institucional. |
| phone_e164 | VARCHAR(16) | No | E.164 si existe | Teléfono institucional. |
| status | TEXT | Sí | `PENDING`, `ACTIVE`, `SUSPENDED`, `CLOSED` | Ciclo institucional. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: OrganizationMembership

Descripción: Relación de pertenencia entre una persona usuaria, una organización y un rol. Sustituye un `UserRole` global que perdería el contexto organizacional.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| organization_id | UUID | Sí | FK Organization | Organización. |
| user_id | UUID | Sí | FK User | Persona. |
| role_id | UUID | Sí | FK Role | Rol dentro de la organización. |
| status | TEXT | Sí | `INVITED`, `ACTIVE`, `SUSPENDED`, `ENDED` | Estado de pertenencia. |
| joined_at | TIMESTAMPTZ | No | — | Alta efectiva. |
| ended_at | TIMESTAMPTZ | No | >= joined_at si ambos existen | Fin de pertenencia. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

**UNIQUE:** (organization_id, user_id, role_id) para membresías activas; si se requiere historial de reingresos, usar índice parcial por estados activos y conservar filas cerradas.

### Comunidades

# Entity: Community

Descripción: Comunidad o localidad atendida. Evita asumir que toda comunidad corresponde a un municipio o a una categoría étnica.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| managing_organization_id | UUID | Sí | FK Organization | Organización responsable en MVP. |
| name | VARCHAR(200) | Sí | — | Nombre preferido por la comunidad. |
| locality_name | VARCHAR(200) | No | — | Localidad administrativa si aplica. |
| municipality | VARCHAR(160) | No | — | Municipio; normalizar a catálogo oficial cuando se defina fuente. |
| state_region | VARCHAR(160) | No | — | Entidad federativa/región. |
| country_code | CHAR(2) | Sí | ISO 3166-1 alpha-2 | País. |
| location | GEOGRAPHY(Point,4326) o lat/lon | No | coordenadas válidas y acceso restringido | Ubicación precisa; PostGIS recomendado solo si se consultan distancias. |
| location_precision | TEXT | No | `EXACT`, `APPROXIMATE`, `UNDISCLOSED` | Precisión consentida. |
| preferred_language | VARCHAR(64) | No | catálogo validado | Idioma preferido si se conoce; registrar de forma respetuosa y voluntaria. |
| description | TEXT | No | — | Contexto no sensible estrictamente necesario. |
| status | TEXT | Sí | `ACTIVE`, `INACTIVE`, `ARCHIVED` | Disponibilidad operativa. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: CommunityRepresentative

Descripción: Persona autorizada por la comunidad para comunicación/representación. No requiere cuenta de plataforma.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| community_id | UUID | Sí | FK Community | Comunidad. |
| user_id | UUID | No | FK User; NULL para representante sin cuenta | Vinculación opcional a usuario. |
| full_name | VARCHAR(200) | Sí | — | Nombre; PII. |
| role_in_community | VARCHAR(120) | No | — | Denominación acordada localmente. |
| contact_phone | VARCHAR(16) | No | E.164 si existe | Contacto PII. |
| contact_email | VARCHAR(320) | No | — | Contacto PII. |
| is_primary | BOOLEAN | Sí | DEFAULT false; máximo uno vigente por comunidad | Representante principal operativo. |
| consent_status | TEXT | Sí | `UNKNOWN`, `GRANTED`, `WITHDRAWN` | Estado documentado de consentimiento para uso de contacto. |
| valid_from / valid_to | DATE | No | valid_to >= valid_from | Periodo de representación. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: CommunityResource

Descripción: Recurso comunitario declarado, para planificación futura; definir vocabulario y sensibilidad antes de habilitar.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| community_id | UUID | Sí | FK Community | Comunidad. |
| resource_type | VARCHAR(80) | Sí | catálogo administrado | Tipo de recurso. |
| name | VARCHAR(200) | Sí | — | Nombre. |
| description | TEXT | No | — | Descripción. |
| quantity | NUMERIC(12,2) | No | >= 0 | Cantidad si es cuantificable. |
| unit | VARCHAR(40) | No | — | Unidad declarada. |
| sensitivity | TEXT | Sí | `PUBLIC`, `INTERNAL`, `RESTRICTED` | Clasificación de acceso. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: CommunityNeed

Descripción: Necesidad identificada y vigente en un momento, potencialmente relacionada con varias solicitudes en el futuro.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| community_id | UUID | Sí | FK Community | Comunidad. |
| service_category_id | UUID | No | FK ServiceCategory | Clasificación opcional. |
| title | VARCHAR(200) | Sí | — | Resumen. |
| description | TEXT | Sí | — | Necesidad con atribución/fuente cuando aplique. |
| identified_at | DATE | Sí | — | Fecha observada. |
| priority_label | TEXT | No | catálogo definido institucionalmente | Prioridad declarada; no sustituye evaluación. |
| status | TEXT | Sí | `OPEN`, `ADDRESSED`, `DEFERRED`, `WITHDRAWN` | Seguimiento. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Catálogos y solicitudes

# Entity: ServiceCategory

Descripción: Catálogo jerárquico de áreas de servicio (p. ej., salud, educación, economía) con códigos estables.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| parent_id | UUID | No | FK ServiceCategory | Categoría padre; no ciclos. |
| code | VARCHAR(64) | Sí | UNIQUE | Código estable. |
| name | VARCHAR(120) | Sí | — | Etiqueta vigente. |
| description | TEXT | No | — | Alcance. |
| sort_order | INTEGER | Sí | DEFAULT 0 | Orden sugerido. |
| is_active | BOOLEAN | Sí | DEFAULT true | No borrar categorías referenciadas; desactivar. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: ServiceRequest

Descripción: Solicitud de servicio/apoyo de una comunidad; concentra datos narrativos y estado del proceso, no duplicados de evaluación.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| organization_id | UUID | Sí | FK Organization | Organización receptora/gestora. |
| community_id | UUID | Sí | FK Community | Comunidad solicitante. |
| service_category_id | UUID | Sí | FK ServiceCategory | Categoría principal. |
| submitted_by_user_id | UUID | No | FK User; NULL para captura asistida sin cuenta | Autor/capturista. |
| representative_id | UUID | No | FK CommunityRepresentative | Representante asociado. |
| title | VARCHAR(200) | Sí | — | Título breve. |
| problem_statement | TEXT | Sí | — | Problema/necesidad expresada. |
| requested_support | TEXT | Sí | — | Apoyo solicitado. |
| beneficiaries_estimate | INTEGER | No | >= 0 | Estimación con alcance documentado. |
| urgency | TEXT | No | catálogo definido; no convertir en aprobación automática | Urgencia declarada. |
| status | TEXT | Sí | catálogo ServiceRequestStatus, sección 7 | Estado actual; cambios también en historial. |
| submitted_at | TIMESTAMPTZ | No | — | Envío. |
| assigned_to_user_id | UUID | No | FK User | Responsable de revisión. |
| decision_summary | TEXT | No | requerido por proceso al aprobar/rechazar | Justificación resumida y accesible. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: RequestAttachment

Descripción: Metadatos de archivo vinculado a una solicitud. El objeto binario reside en almacenamiento privado con URL temporal, no en una URL pública persistente.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| service_request_id | UUID | Sí | FK ServiceRequest | Solicitud. |
| uploaded_by_user_id | UUID | No | FK User | Autoría de carga. |
| storage_key | TEXT | Sí | UNIQUE; nunca URL pública | Clave opaca en storage. |
| original_filename | VARCHAR(255) | Sí | sanitizado | Nombre presentado. |
| media_type | VARCHAR(127) | Sí | allowlist de tipos | MIME declarado/verificado. |
| byte_size | BIGINT | Sí | > 0 y límite de política | Tamaño. |
| checksum_sha256 | CHAR(64) | No | hexadecimal | Integridad opcional. |
| sensitivity | TEXT | Sí | `INTERNAL`, `RESTRICTED` | Clasificación. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: RequestStatusHistory

Descripción: Evento inmutable de transición o registro de estado de solicitud.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| service_request_id | UUID | Sí | FK ServiceRequest | Solicitud. |
| from_status | TEXT | No | Estado permitido; NULL solo creación | Estado previo. |
| to_status | TEXT | Sí | Estado permitido | Estado resultante. |
| changed_by_user_id | UUID | No | FK User; NULL para proceso del sistema | Actor. |
| reason | TEXT | No | requerido en decisiones/retorno según política | Motivo comunicable. |
| changed_at | TIMESTAMPTZ | Sí | DEFAULT now() | Momento de transición. |
| metadata | JSONB | No | datos auxiliares permitidos, sin PII innecesaria | Contexto pequeño y versionado. |

### Evaluación

# Entity: EvaluationCriteria

Descripción: Definición lógica de un criterio evaluativo; los cambios sustantivos crean versión nueva del modelo y no reescriben evaluaciones.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| code | VARCHAR(64) | Sí | UNIQUE | Código estable. |
| name | VARCHAR(160) | Sí | — | Nombre. |
| description | TEXT | Sí | — | Interpretación y guía para consistencia. |
| score_type | TEXT | Sí | `NUMERIC`, `BOOLEAN`, `ENUM` | Tipo de respuesta; MVP recomendado NUMERIC. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: EvaluationModelVersion

Descripción: Versión inmutable de una rúbrica aplicable a una o más categorías. Conserva límites, pesos y vigencia acordada.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| version_code | VARCHAR(64) | Sí | UNIQUE | Versión estable. |
| name | VARCHAR(160) | Sí | — | Nombre de rúbrica. |
| description | TEXT | No | — | Propósito. |
| status | TEXT | Sí | `DRAFT`, `ACTIVE`, `RETIRED` | Publicación. |
| effective_from / effective_to | DATE | No | orden cronológico | Vigencia. |
| published_by_user_id | UUID | No | FK User | Aprobador/publicador. |
| published_at | TIMESTAMPTZ | No | coherente con status | Fecha de publicación. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida; contenido inmutable tras publicar. |

**Relación adicional:** `EvaluationModelCriterion(model_version_id, criterion_id, weight, min_score, max_score, required, sort_order)` PK compuesta; ambas FK; `weight NUMERIC(8,5) CHECK >= 0`; límites y unicidad de criterio por versión. Conserva los criterios y ponderación efectivos.

### Entity: RequestEvaluation

Descripción: Evaluación de una solicitud realizada por una persona o equipo conforme a versión determinada.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| service_request_id | UUID | Sí | FK ServiceRequest | Solicitud. |
| model_version_id | UUID | Sí | FK EvaluationModelVersion | Rúbrica aplicada. |
| evaluator_user_id | UUID | Sí | FK User | Evaluador. |
| status | TEXT | Sí | `DRAFT`, `SUBMITTED`, `VOIDED` | Ciclo de evaluación. |
| score_total | NUMERIC(12,4) | No | calculado a partir de scores según regla versionada | Total reproducible. |
| recommendation | TEXT | No | `RECOMMEND`, `DEFER`, `DO_NOT_RECOMMEND` | Recomendación; no equivale a aprobación. |
| rationale | TEXT | No | requerido al enviar según política | Argumento cualitativo. |
| evaluated_at | TIMESTAMPTZ | No | — | Envío de evaluación. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: EvaluationScore

Descripción: Respuesta/puntaje para un criterio de una evaluación.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| request_evaluation_id | UUID | Sí | FK RequestEvaluation | Evaluación. |
| criterion_id | UUID | Sí | FK EvaluationCriteria | Criterio; debe estar en la versión usada por evaluación. |
| numeric_score | NUMERIC(12,4) | No | dentro de límites versionados | Puntaje numérico. |
| value | JSONB | No | para tipo ENUM/BOOLEAN futuro, esquema validado | Valor tipado alternativo; no duplicar junto a numeric_score. |
| notes | TEXT | No | — | Evidencia/justificación breve. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

**UNIQUE:** (request_evaluation_id, criterion_id). `CHECK` exige exactamente un valor acorde con `score_type`; integridad de pertenencia a versión validable con FK compuesta hacia tabla modelo-criterio (agregar columnas de versión a clave o trigger diferido).

### Especialistas y colaboración

# Entity: SpecialistProfile

Descripción: Perfil de prestación de servicios ligado opcionalmente a una cuenta de usuario. Puede representar persona natural; no presupone evaluación de seguridad o aval profesional.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| user_id | UUID | Sí | FK User; UNIQUE | Cuenta propietaria. |
| public_name | VARCHAR(200) | Sí | — | Nombre de perfil. |
| bio | TEXT | No | moderación y consentimiento de publicación | Presentación. |
| base_location_text | VARCHAR(200) | No | no guardar coordenada precisa sin necesidad | Ubicación general. |
| verification_status | TEXT | Sí | sección 7 | Estado de revisión de identidad/credenciales, según alcance definido. |
| profile_visibility | TEXT | Sí | `PRIVATE`, `ORGANIZATION_ONLY`, `PUBLIC` | Visibilidad consentida. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: ProfessionalCredential

Descripción: Declaración/documento profesional. Los archivos deben usar almacenamiento privado y acceso restringido.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| specialist_profile_id | UUID | Sí | FK SpecialistProfile | Perfil. |
| credential_type | VARCHAR(80) | Sí | catálogo controlado | Tipo de acreditación. |
| issuer_name | VARCHAR(200) | No | — | Emisor declarado. |
| credential_reference | VARCHAR(160) | No | restringido; no usar como clave | Referencia privada. |
| issued_on / expires_on | DATE | No | expires_on >= issued_on | Vigencia declarada. |
| verification_status | TEXT | Sí | `PENDING`, `VERIFIED`, `REJECTED`, `EXPIRED` | Estado documental. |
| verified_by_user_id | UUID | No | FK User | Revisor. |
| verified_at | TIMESTAMPTZ | No | — | Fecha de revisión. |
| document_storage_key | TEXT | No | storage privado | Evidencia. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: ServiceOffering

Descripción: Servicio ofrecido por un especialista y asociado a categoría, independiente del perfil general.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| specialist_profile_id | UUID | Sí | FK SpecialistProfile | Proveedor. |
| service_category_id | UUID | Sí | FK ServiceCategory | Área. |
| title | VARCHAR(160) | Sí | — | Oferta. |
| description | TEXT | No | — | Alcance. |
| delivery_mode | TEXT | Sí | `IN_PERSON`, `REMOTE`, `HYBRID`, `UNSPECIFIED` | Modalidad. |
| service_area | TEXT | No | zona textual; geoespacial futuro | Cobertura. |
| is_active | BOOLEAN | Sí | DEFAULT true | Disponibilidad general de oferta. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: Availability

Descripción: Ventana de disponibilidad del especialista; fase posterior por complejidad de recurrencia y zona horaria.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| specialist_profile_id | UUID | Sí | FK SpecialistProfile | Especialista. |
| starts_at / ends_at | TIMESTAMPTZ | Sí | ends_at > starts_at | Intervalo. |
| timezone | VARCHAR(64) | Sí | nombre IANA | Zona horaria original para agenda. |
| recurrence_rule | TEXT | No | RFC 5545 validado si se habilita | Recurrencia futura. |
| status | TEXT | Sí | `AVAILABLE`, `BLOCKED`, `BOOKED` | Estado. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: CollaborationApplication

Descripción: Postulación de especialista/organización/voluntario a una solicitud o proyecto. Se fija exactamente un destino en MVP; para proyecto, incluir solicitud origen si se necesita trazabilidad.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| service_request_id | UUID | No | FK ServiceRequest | Solicitud destino. |
| project_id | UUID | No | FK Project | Proyecto destino. |
| specialist_profile_id | UUID | No | FK SpecialistProfile | Postulante individual. |
| organization_id | UUID | No | FK Organization | Organización postulante. |
| applicant_user_id | UUID | Sí | FK User | Persona que envía. |
| message | TEXT | No | — | Propuesta. |
| status | TEXT | Sí | sección 7 | Estado. |
| reviewed_by_user_id | UUID | No | FK User | Revisor. |
| reviewed_at | TIMESTAMPTZ | No | — | Fecha de decisión. |
| decision_note | TEXT | No | — | Motivo comunicable. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

**Restricciones:** exactamente un destino y al menos un postulante (perfil o organización); `CHECK`/validación diferida. Evitar duplicados activos por destino/postulante con índices únicos parciales. Si voluntariado no tiene perfil de especialista, su identidad puede ser solo `applicant_user_id`.

### Proyectos y seguimiento

# Entity: Project

Descripción: Unidad de ejecución aprobada, vinculada a solicitud de origen opcional. Su creación no cambia por sí sola la solicitud si la transición no se registra.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| organization_id | UUID | Sí | FK Organization | Responsable. |
| source_request_id | UUID | No | FK ServiceRequest; UNIQUE cuando no NULL | Solicitud origen; admite proyectos sin solicitud. |
| name | VARCHAR(200) | Sí | — | Nombre. |
| objective | TEXT | Sí | — | Objetivo acordado. |
| scope | TEXT | No | — | Alcance/límites. |
| status | TEXT | Sí | sección 7 | Estado. |
| planned_start / planned_end | DATE | No | planned_end >= planned_start | Plan. |
| actual_start / actual_end | DATE | No | orden temporal coherente | Ejecución real. |
| owner_user_id | UUID | No | FK User | Responsable individual. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: ProjectMilestone

Descripción: Hito verificable de planificación/ejecución de un proyecto.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| project_id | UUID | Sí | FK Project | Proyecto. |
| title | VARCHAR(200) | Sí | — | Hito. |
| description | TEXT | No | — | Criterio de cierre. |
| sequence_no | INTEGER | Sí | > 0; UNIQUE(project_id, sequence_no) | Orden. |
| planned_date | DATE | No | — | Fecha prevista. |
| completed_at | TIMESTAMPTZ | No | — | Cierre efectivo. |
| status | TEXT | Sí | `PLANNED`, `IN_PROGRESS`, `COMPLETED`, `BLOCKED`, `CANCELLED` | Estado. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: ProjectAssignment

Descripción: Asignación de una persona especialista o miembro organizacional a un proyecto y función. Evita columnas repetidas y permite historial de colaboración.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| project_id | UUID | Sí | FK Project | Proyecto. |
| user_id | UUID | No | FK User | Persona asignada. |
| organization_id | UUID | No | FK Organization | Organización colaboradora. |
| specialist_profile_id | UUID | No | FK SpecialistProfile | Perfil relacionado. |
| role_name | VARCHAR(120) | Sí | — | Función en proyecto; catálogo futuro. |
| status | TEXT | Sí | `INVITED`, `ACTIVE`, `COMPLETED`, `WITHDRAWN`, `REMOVED` | Estado de asignación. |
| assigned_at | TIMESTAMPTZ | Sí | DEFAULT now() | Inicio. |
| ended_at | TIMESTAMPTZ | No | >= assigned_at | Fin. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

**Restricción:** al menos una identidad (user, organization, specialist profile); evitar dos asignaciones activas equivalentes por proyecto.

### Entity: ProgressReport

Descripción: Informe de avance/evidencia con fecha de referencia, autor y estado de revisión.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| project_id | UUID | Sí | FK Project | Proyecto. |
| milestone_id | UUID | No | FK ProjectMilestone; debe pertenecer al mismo proyecto | Hito relacionado. |
| author_user_id | UUID | Sí | FK User | Autor. |
| reporting_period_start / reporting_period_end | DATE | No | end >= start | Periodo cubierto. |
| summary | TEXT | Sí | — | Avance narrativo. |
| outcomes | TEXT | No | evidencia de resultados, distinguiendo estimados de medidos | Resultados. |
| blockers | TEXT | No | — | Bloqueos. |
| status | TEXT | Sí | `DRAFT`, `SUBMITTED`, `REVIEWED`, `RETURNED` | Revisión. |
| submitted_at | TIMESTAMPTZ | No | — | Envío. |
| reviewed_by_user_id | UUID | No | FK User | Revisor. |
| reviewed_at | TIMESTAMPTZ | No | — | Revisión. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

**Entidad complementaria recomendada:** `ProgressReportAttachment` (id UUID, progress_report_id FK, storage_key, filename, media_type, byte_size, sensitivity, created_at) si se adjunta evidencia. Reutilizar metadatos seguros sin un campo de archivo libre.

### Finanzas (futuras)

# Entity: FundingSource

Descripción: Fuente de fondos o subvención, no una cuenta bancaria. Finanzas completa requiere aprobación institucional y conciliación externa.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| organization_id | UUID | Sí | FK Organization | Receptora/gestora. |
| name | VARCHAR(200) | Sí | — | Fuente. |
| source_type | TEXT | Sí | catálogo por definir | Tipo de financiación. |
| donor_organization_id | UUID | No | FK Organization | Entidad donante si está registrada. |
| currency_code | CHAR(3) | Sí | ISO 4217 | Moneda. |
| amount_committed | NUMERIC(14,2) | No | >= 0 | Importe comprometido. |
| received_on | DATE | No | — | Recepción. |
| restrictions | TEXT | No | — | Condiciones del fondo. |
| status | TEXT | Sí | `PLANNED`, `COMMITTED`, `RECEIVED`, `CLOSED`, `CANCELLED` | Ciclo del fondo. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: Donation

Descripción: Registro de donación y su conciliación; nunca almacenar datos completos de tarjeta ni credenciales de pago.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| organization_id | UUID | Sí | FK Organization | Receptora. |
| funding_source_id | UUID | No | FK FundingSource | Fuente agrupadora. |
| donor_organization_id | UUID | No | FK Organization | Donante institucional; donante individual requiere modelo privado separado. |
| amount | NUMERIC(14,2) | Sí | > 0 | Importe. |
| currency_code | CHAR(3) | Sí | ISO 4217 | Moneda. |
| donated_at | TIMESTAMPTZ | Sí | — | Fecha de donación. |
| payment_reference | VARCHAR(200) | No | referencia del proveedor, restringida y no secreta | Conciliación. |
| status | TEXT | Sí | `PLEDGED`, `RECEIVED`, `REFUNDED`, `CANCELLED` | Estado. |
| acknowledgment_status | TEXT | No | catálogo por definir | Acuse. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: FundAllocation

Descripción: Compromiso de un monto de fuente de fondos a un proyecto; no sustituye libro contable de doble partida.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| funding_source_id | UUID | Sí | FK FundingSource | Fuente. |
| project_id | UUID | Sí | FK Project | Proyecto. |
| allocated_amount | NUMERIC(14,2) | Sí | >= 0 | Monto asignado. |
| currency_code | CHAR(3) | Sí | debe coincidir con fuente o incluir conversión explícita | Moneda. |
| allocated_at | TIMESTAMPTZ | Sí | DEFAULT now() | Fecha. |
| status | TEXT | Sí | `PROPOSED`, `APPROVED`, `RELEASED`, `CLOSED`, `CANCELLED` | Estado. |
| approved_by_user_id | UUID | No | FK User | Aprobador. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Entity: ProjectExpense

Descripción: Gasto declarado/asociado a proyecto y fuente, con evidencia restringida. Debe conciliarse con política contable oficial.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| project_id | UUID | Sí | FK Project | Proyecto. |
| fund_allocation_id | UUID | No | FK FundAllocation | Partida financiadora. |
| amount | NUMERIC(14,2) | Sí | > 0 | Monto. |
| currency_code | CHAR(3) | Sí | ISO 4217 | Moneda. |
| incurred_on | DATE | Sí | — | Fecha del gasto. |
| category_code | VARCHAR(64) | Sí | catálogo de gasto por definir | Clasificación. |
| description | TEXT | Sí | — | Concepto. |
| receipt_storage_key | TEXT | No | storage privado | Comprobante. |
| status | TEXT | Sí | `DRAFT`, `SUBMITTED`, `APPROVED`, `REJECTED`, `VOIDED` | Revisión. |
| submitted_by_user_id | UUID | Sí | FK User | Declarante. |
| approved_by_user_id | UUID | No | FK User | Aprobador distinto cuando la política lo exija. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

### Auditoría y comunicación

# Entity: AuditLog

Descripción: Evento append-only de acción relevante y registro de antes/después limitado por minimización de datos.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| actor_user_id | UUID | No | FK User; NULL para sistema/proceso externo | Actor. |
| organization_id | UUID | No | FK Organization | Contexto organizacional. |
| action | VARCHAR(100) | Sí | catálogo de acciones | Acción (`CREATE`, `UPDATE`, `STATUS_CHANGE`, `READ_RESTRICTED`, etc.). |
| entity_type | VARCHAR(100) | Sí | nombre lógico allowlisted | Tipo de registro afectado. |
| entity_id | UUID | No | identificador del registro; no FK polimórfica | Registro afectado; FK no posible sin tabla común. |
| occurred_at | TIMESTAMPTZ | Sí | DEFAULT now() | Fecha/hora. |
| old_values | JSONB | No | excluir secretos/PII no necesaria | Estado anterior filtrado. |
| new_values | JSONB | No | excluir secretos/PII no necesaria | Estado nuevo filtrado. |
| request_id | UUID | No | correlación técnica | Correlación de operación. |
| ip_address | INET | No | retención restringida | Dirección de origen; guardar solo con finalidad aprobada. |

Sin `updated_at`: los eventos son inmutables. Revocar UPDATE/DELETE al rol aplicativo, proteger acceso y retención. Para escala, particionar por fecha y archivar conforme a política.

### Entity: Notification

Descripción: Mensaje interno dirigido a usuario para informar un evento; su entrega externa se procesa fuera de este registro.

Campos:

| Campo | Tipo | Obligatorio | Restricciones | Descripción |
|---|---|---:|---|---|
| id | UUID | Sí | PK | Identificador. |
| recipient_user_id | UUID | Sí | FK User | Destinatario. |
| notification_type | VARCHAR(80) | Sí | catálogo | Tipo de evento. |
| title | VARCHAR(200) | Sí | — | Título. |
| body | TEXT | Sí | no incluir datos sensibles innecesarios | Contenido. |
| related_entity_type | VARCHAR(100) | No | allowlist | Entidad relacionada. |
| related_entity_id | UUID | No | relación lógica polimórfica | Identificador relacionado. |
| read_at | TIMESTAMPTZ | No | — | Lectura. |
| delivery_status | TEXT | Sí | `QUEUED`, `SENT`, `FAILED`, `NOT_REQUIRED` | Estado de despacho externo/interno. |
| created_at / updated_at | TIMESTAMPTZ | Sí | auditoría | Ciclo de vida. |

## 5. Relaciones

`A (1) → (N) B` significa que cada B pertenece a un A y A puede tener cero o muchos B. La obligatoriedad de cada FK se indica en el diccionario.

| Relación | Cardinalidad | Implementación / motivo |
|---|---|---|
| Organization → OrganizationMembership | 1:N | Una organización tiene membresías. |
| User → OrganizationMembership | 1:N | Una persona puede colaborar con varias organizaciones. |
| Role → OrganizationMembership | 1:N | Un rol puede asignarse a varias membresías. |
| Role ↔ Permission | N:M | `RolePermission`; catálogo atómico futuro. |
| Organization → Community | 1:N | Organización responsable en MVP; historial de responsable puede requerir tabla de asignación futura. |
| Community → CommunityRepresentative | 1:N | Varios representantes con máximo uno principal vigente. |
| User → CommunityRepresentative | 1:0..N | Vinculación opcional; persona puede representar varias comunidades solo si procede. |
| Community → CommunityResource | 1:N | Inventario opcional. |
| Community → CommunityNeed | 1:N | Necesidades longitudinales. |
| ServiceCategory (padre) → ServiceCategory (hija) | 1:N | Jerarquía de catálogo acíclica. |
| Community → ServiceRequest | 1:N | Historial de solicitudes de la comunidad. |
| Organization → ServiceRequest | 1:N | Organización receptora/gestora. |
| ServiceCategory → ServiceRequest | 1:N | Cada solicitud tiene una categoría principal. |
| ServiceRequest → RequestAttachment | 1:N | Evidencias privadas. |
| ServiceRequest → RequestStatusHistory | 1:N | Transiciones inmutables. |
| EvaluationModelVersion ↔ EvaluationCriteria | N:M | `EvaluationModelCriterion` define peso, límites y obligatoriedad por versión. |
| ServiceRequest → RequestEvaluation | 1:N | Puede haber evaluaciones independientes o reevaluaciones; no sobrescribir dictámenes. |
| EvaluationModelVersion → RequestEvaluation | 1:N | Versión aplicada. |
| RequestEvaluation → EvaluationScore | 1:N | Un puntaje por criterio incluido en la versión. |
| EvaluationCriteria → EvaluationScore | 1:N | Criterio puntuado en evaluaciones. |
| User → SpecialistProfile | 1:0..1 | Perfil profesional opcional de la cuenta. |
| SpecialistProfile → ProfessionalCredential | 1:N | Credenciales declaradas. |
| SpecialistProfile → ServiceOffering | 1:N | Varias ofertas. |
| ServiceCategory → ServiceOffering | 1:N | Clasificación de la oferta. |
| SpecialistProfile → Availability | 1:N | Agenda futura. |
| ServiceRequest/Project → CollaborationApplication | 1:N | Destino exactamente uno, mediante FK nullable con CHECK. |
| SpecialistProfile/Organization/User → CollaborationApplication | 1:N | Postulante individual, institucional o voluntario; reglas de exclusividad explícitas. |
| ServiceRequest → Project | 1:0..1 | Solicitud puede estar aprobada y aún sin proyecto; FK opcional UNIQUE en Project. Proyectos externos pueden no tener solicitud. |
| Organization → Project | 1:N | Responsable del proyecto. |
| Project → ProjectMilestone | 1:N | Hitos ordenados. |
| Project → ProjectAssignment | 1:N | Equipo por proyecto. |
| Project → ProgressReport | 1:N | Informes cronológicos. |
| ProjectMilestone → ProgressReport | 1:0..N | Un informe puede referirse a un hito opcional. |
| Organization → FundingSource | 1:N | Fuentes gestionadas. |
| FundingSource → Donation | 1:0..N | Una donación puede contribuir a una fuente. |
| FundingSource ↔ Project | N:M | `FundAllocation` registra monto, moneda, estado y aprobación. |
| Project → ProjectExpense | 1:N | Gastos declarados. |
| User → AuditLog | 1:N | Actor opcional por sistema. |
| User → Notification | 1:N | Destinatario. |

La relación solicitud-proyecto no es obligatoria en ninguno de los extremos: una solicitud aprobada no exige creación inmediata; un proyecto puede originarse fuera de una solicitud. `UNIQUE(Project.source_request_id)` evita más de un proyecto por solicitud sin obligar a que exista proyecto.

## 6. Reglas de Integridad

### Integridad de entidades

- Cada tabla tiene PK UUID y valores requeridos no nulos explícitos.
- Correos de usuario se normalizan antes de `UNIQUE`; considerar índice único sobre `lower(email)` para garantía independiente de collation.
- Campos de texto con límites deben rechazar cadenas vacías cuando la semántica lo exija (`CHECK (length(trim(...)) > 0)`).
- Fechas e intervalos usan restricciones de orden; cantidades, puntajes y montos usan límites no negativos o rangos de su versión.
- Unicidad principal de representante se garantiza con índice único parcial, por ejemplo `(community_id) WHERE is_primary AND valid_to IS NULL` (definir además cómo tratar fecha futura de vigencia).
- Solo la tabla puente modela las N:M; no listas CSV ni arreglos de IDs.
- Estados y tipos restringidos se validan mediante `CHECK` o FK a catálogo, nunca por texto libre no controlado.

### Integridad referencial

- Toda FK debe indexarse cuando sirva a joins/borrado; PostgreSQL no crea automáticamente índice en la columna referenciante.
- Usar `ON DELETE RESTRICT` para organizaciones, solicitudes, evaluaciones, proyectos, finanzas y datos auditables. Desactivación lógica en lugar de borrar historial.
- `CASCADE` se limita a tablas puente sin historial propio, tras confirmar la regla de retención.
- No existe FK polimórfica real para `AuditLog.entity_type/entity_id` ni notificaciones relacionadas; usar allowlist en aplicación, o introducir tabla de referencia común si se requiere integridad fuerte.
- Solicitud y proyecto deben pertenecer a contexto organizacional consistente; el MVP usa misma organización gestora. La regla debe validarse transaccionalmente o con clave compuesta/FK si no hay organización común.
- `EvaluationScore.criterion_id` debe estar dentro de `EvaluationModelVersion` de su evaluación y respetar rango; preferir FK compuesta o trigger diferido.
- `ProgressReport.milestone_id`, si está presente, debe pertenecer al mismo `project_id`.

### Restricciones de negocio

1. Correo de usuario único tras normalización.
2. Un usuario puede tener múltiples roles mediante varias membresías y varias organizaciones.
3. Una comunidad tiene como máximo un representante principal vigente; puede no tenerlo durante registro inicial.
4. Una solicitud aprobada genera cero o un proyecto. No cambiar solicitud a `PLANNING`/`IN_PROGRESS` sin decisión de crear proyecto según flujo acordado.
5. Un estado actual debe corresponder al último evento de `RequestStatusHistory`; insertar el evento y actualizar `ServiceRequest.status` en una única transacción. Un trigger diferido puede ayudar, pero la secuencia transaccional debe ser fuente de consistencia.
6. Transiciones de estado válidas se restringen al grafo de sección 7; no se permite mutación directa sin historial.
7. Una evaluación enviada requiere todos los criterios `required` y valores dentro de rango; puntaje total se calcula desde pesos y fórmula versionada, no se edita manualmente.
8. Evaluación y aprobación son distintas: solo un actor autorizado puede decidir aprobación/rechazo; recomendación del evaluador no produce transición automática.
9. Una postulación tiene destino único, postulante válido y una decisión registrada al salir de revisión.
10. No permitir gasto/partida en moneda incompatible sin operación de conversión explícita y fecha/tipo de cambio (fuera del MVP).
11. Cambios de rol, estado, dictamen, acceso a dato restringido y operaciones financieras deben producir evento de auditoría.
12. Adjuntos validan tamaño, MIME real, acceso, retención y escaneo contra malware en el servicio de almacenamiento.

## 7. Estados de negocio

Los estados siguientes son vocabulario propuesto. Las transiciones deben ejecutarse con concurrencia optimista o bloqueo de fila para evitar actualizaciones concurrentes incompatibles.

### ServiceRequestStatus

`DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `INFO_REQUIRED`, `EVALUATED`, `APPROVED`, `REJECTED`, `PLANNING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`.

| Desde | Hacia permitido | Condición orientativa |
|---|---|---|
| DRAFT | SUBMITTED, CANCELLED | Envío completo; cancelación antes de envío. |
| SUBMITTED | UNDER_REVIEW, INFO_REQUIRED, CANCELLED | Recepción y asignación; puede solicitarse información. |
| UNDER_REVIEW | INFO_REQUIRED, EVALUATED, CANCELLED | Evaluación completa para pasar a EVALUATED. |
| INFO_REQUIRED | SUBMITTED, UNDER_REVIEW, CANCELLED | Respuesta; se reanuda revisión. |
| EVALUATED | APPROVED, REJECTED, INFO_REQUIRED | Decisión autorizada y motivada o nueva información. |
| APPROVED | PLANNING, CANCELLED | Proyecto puede planificarse; cancelación motivada. |
| PLANNING | IN_PROGRESS, CANCELLED | Plan y responsables definidos. |
| IN_PROGRESS | COMPLETED, CANCELLED | Cierre con informe y resultados; cancelación motivada. |
| REJECTED | (terminal) | Reabrir requiere procedimiento explícito o nueva solicitud; no reescritura. |
| COMPLETED | (terminal) | Correcciones por evento/nota, no reabrir ordinariamente. |
| CANCELLED | (terminal) | Nueva iniciativa se registra con trazabilidad propia. |

`EVALUATED → APPROVED` y `APPROVED → PLANNING` pueden registrarse en la solicitud; crear `Project` es transacción aparte ligada a solicitud para no adelantar la decisión.

### ProjectStatus

`DRAFT`, `PLANNED`, `ACTIVE`, `ON_HOLD`, `COMPLETED`, `CANCELLED`, `ARCHIVED`.

Transiciones recomendadas: `DRAFT → PLANNED/CANCELLED`; `PLANNED → ACTIVE/ON_HOLD/CANCELLED`; `ACTIVE → ON_HOLD/COMPLETED/CANCELLED`; `ON_HOLD → ACTIVE/CANCELLED`; terminales `COMPLETED`, `CANCELLED` pueden pasar a `ARCHIVED` solo por retención, no por cambio del resultado. Sincronizar con solicitud mediante eventos explícitos, no estados duplicados implícitos.

### SpecialistVerificationStatus

`UNVERIFIED`, `PENDING`, `VERIFIED`, `REJECTED`, `EXPIRED`, `SUSPENDED`.

Transiciones recomendadas: `UNVERIFIED → PENDING`; `PENDING → VERIFIED/REJECTED`; `VERIFIED → EXPIRED/SUSPENDED`; `REJECTED → PENDING` si se permite nueva evidencia; `EXPIRED → PENDING`; `SUSPENDED → PENDING/REJECTED` tras revisión. El estado del perfil no debe etiquetarse como “certificado” sin criterios y responsable documentados.

### CollaborationStatus

`SUBMITTED`, `UNDER_REVIEW`, `INFO_REQUIRED`, `ACCEPTED`, `REJECTED`, `WITHDRAWN`, `CANCELLED`.

Transiciones recomendadas: `SUBMITTED → UNDER_REVIEW/WITHDRAWN`; `UNDER_REVIEW → INFO_REQUIRED/ACCEPTED/REJECTED/WITHDRAWN`; `INFO_REQUIRED → UNDER_REVIEW/WITHDRAWN`; `ACCEPTED → CANCELLED` si se revoca colaboración con motivo; `REJECTED`, `WITHDRAWN`, `CANCELLED` terminales. Una aceptación puede originar `ProjectAssignment` en una transacción y no debe duplicar asignaciones activas.

Otros catálogos de estado: User, Organization, OrganizationMembership, RequestEvaluation, ProjectMilestone, ProgressReport, FundingSource, Donation, FundAllocation y ProjectExpense aparecen con valores definidos en sus campos. Todo nuevo estado requiere revisión de transiciones y reportes.

## 8. Índices recomendados

La PK UUID incluye índice único automáticamente. Los índices se ajustan con `EXPLAIN (ANALYZE, BUFFERS)` sobre consultas reales; evitar indexar todos los campos por anticipado.

| Entidad | PK / UNIQUE | INDEX recomendado | Justificación |
|---|---|---|---|
| User | PK; unique `lower(email)` | `(status)` si se filtra acceso | Login y prevención de duplicados. |
| Role | PK; unique `(organization_id, code)` considerando NULL global | `(organization_id)` | Roles por organización. |
| Permission | PK; unique `(code)` | — | Resolución por código. |
| RolePermission | PK `(role_id, permission_id)` | índice inverso `(permission_id, role_id)` | Consultas desde permisos. |
| Organization | PK; unique `(slug)`, identificador fiscal normalizado cuando política lo permita | `(status)` | Búsqueda/administración. |
| OrganizationMembership | PK; unique parcial de membresía activa | `(user_id, status)`, `(organization_id, status)` | Contexto de autorización y listados. |
| Community | PK | `(managing_organization_id, status)`, `(municipality)`; GiST(location) solo con PostGIS y consulta geográfica | Listas territoriales. |
| CommunityRepresentative | PK; único parcial de representante principal vigente | `(community_id)`, `(user_id)` parcial | Contacto vigente. |
| CommunityResource | PK | `(community_id, resource_type)` | Inventario por comunidad. |
| CommunityNeed | PK | `(community_id, status)`, `(service_category_id, status)` | Priorización operativa. |
| ServiceCategory | PK; unique `(code)` | `(parent_id, is_active, sort_order)` | Árbol/filtros. |
| ServiceRequest | PK | `(organization_id, status, created_at DESC)`, `(community_id, created_at DESC)`, `(assigned_to_user_id, status)` | Cola de trabajo, historial comunitario y asignación. |
| RequestAttachment | PK; unique `(storage_key)` | `(service_request_id, created_at)` | Lista de evidencia y acceso. |
| RequestStatusHistory | PK | `(service_request_id, changed_at DESC)` | Línea temporal. |
| EvaluationCriteria | PK; unique `(code)` | — | Resolución del criterio. |
| EvaluationModelVersion | PK; unique `(version_code)` | `(status, effective_from)` | Selección de rúbrica publicada. |
| EvaluationModelCriterion | PK compuesta | índice `(criterion_id, model_version_id)` | Lookup inverso y validación. |
| RequestEvaluation | PK | `(service_request_id, status)`, `(evaluator_user_id, evaluated_at DESC)` | Reevaluación y carga de evaluadores. |
| EvaluationScore | PK; unique `(request_evaluation_id, criterion_id)` | `(criterion_id)` | Puntajes por evaluación/criterio. |
| SpecialistProfile | PK; unique `(user_id)` | `(verification_status, profile_visibility)` | Búsqueda de perfiles aprobados. |
| ProfessionalCredential | PK | `(specialist_profile_id, verification_status)` | Revisión documental. |
| ServiceOffering | PK | `(service_category_id, is_active)`, `(specialist_profile_id, is_active)` | Matching de oferta. |
| Availability | PK | `(specialist_profile_id, starts_at, ends_at)`; GiST range si agenda avanzada | Búsqueda temporal. |
| CollaborationApplication | PK | `(service_request_id, status, created_at DESC)`, `(project_id, status)`, índices únicos parciales postulante-destino activo | Revisión y evitar duplicados. |
| Project | PK; unique parcial `(source_request_id)` | `(organization_id, status, planned_start)` | Restricción de un proyecto por solicitud y cartera. |
| ProjectMilestone | PK; unique `(project_id, sequence_no)` | `(project_id, status, planned_date)` | Seguimiento de hitos. |
| ProjectAssignment | PK | `(project_id, status)`, índices parciales por user/org activos | Equipo activo. |
| ProgressReport | PK | `(project_id, created_at DESC)`, `(author_user_id, submitted_at DESC)` | Cronología y autoría. |
| FundingSource | PK | `(organization_id, status)` | Carteras de fondos. |
| Donation | PK | `(organization_id, donated_at DESC)`, `(funding_source_id, status)` | Conciliación/listados. |
| FundAllocation | PK; UNIQUE si la política limita una asignación por fuente/proyecto | `(project_id, status)`, `(funding_source_id, status)` | Control de asignaciones. |
| ProjectExpense | PK | `(project_id, incurred_on DESC, status)`, `(fund_allocation_id)` | Revisión financiera. |
| AuditLog | PK | `(occurred_at DESC)`, `(entity_type, entity_id, occurred_at DESC)`, `(actor_user_id, occurred_at DESC)` | Investigación y auditoría. Particionar por fecha si volumen lo justifica. |
| Notification | PK | `(recipient_user_id, read_at, created_at DESC)`, `(delivery_status, created_at)` | Bandeja y despacho. |

Índices parciales propuestos deben usar estados que representen actividad y ajustarse a la política final. Índices GIN sobre JSONB solo si existen consultas concretas; los campos JSON no sustituyen columnas consultables.

## 9. Estrategia de auditoría

`AuditLog` registra usuario/actor, acción, fecha, entidad afectada, valores anteriores y nuevos filtrados, organización y correlación técnica. Debe distinguir actor humano de proceso del sistema; `actor_user_id = NULL` no significa automáticamente anónimo.

- Escribir auditoría dentro de la misma transacción que el cambio crítico para no perder correlación.
- Capturar cambios de estado, dictámenes, asignaciones, membresías/roles, acceso a registros restringidos, y operaciones financieras futuras.
- Usar allowlist de campos para `old_values/new_values`; excluir contraseñas, tokens, secretos, datos de pago, contenido sensible de adjuntos y PII no necesaria. Registrar identificadores/referencias cuando baste.
- Restringir UPDATE/DELETE al rol de aplicación y acceso de lectura a responsables autorizados; considerar almacenamiento append-only externo para requisitos de mayor garantía.
- Mantener `RequestStatusHistory` como historial de dominio visible y `AuditLog` como evidencia técnica/administrativa. No duplicar la historia de negocio en un JSON genérico.
- Política de retención, anonimización, exportación y particionamiento queda por definir con asesoría de privacidad. `AuditLog` también puede contener PII indirecta.
- Proteger el registro contra fuga de información en logs de aplicación. La bitácora no debe guardar cuerpo HTTP indiscriminado.

## 10. Estrategia de crecimiento

### Gestión financiera avanzada

Evolucionar el conjunto financiero hacia presupuestos por periodo/categoría, compromisos, desembolsos, conciliación con proveedor/banco, tipos de cambio fechados, aprobaciones segregadas y libro contable de doble partida si la organización lo necesita. `ProjectExpense` no es libro contable. No incorporar datos de tarjeta; usar proveedor de pagos y token/referencia opaca. Preservar moneda original y conversión con tasa y fecha explícitas.

### Donaciones

Separar donante individual e institucional con minimización y consentimiento; registrar intención, pago, reembolso, recibo/acuse y referencia del proveedor de forma auditable. La identidad del donante puede requerir acceso más restringido que la gestión de proyecto. Confirmar requisitos fiscales y de pagos antes de habilitar.

### Reportes

Construir vistas/materializaciones de lectura derivadas de las tablas transaccionales, con fecha de corte y definiciones documentadas. No duplicar indicadores manualmente como campos editables. Versionar definiciones de métricas y conservar denominadores, periodo y fuente de datos.

### Analytics

Crear un almacén analítico o réplicas de lectura con datos minimizados/pseudonimizados; separar carga operativa de agregaciones. Aplicar controles para grupos pequeños y ubicación para evitar reidentificación. Definir linaje, calidad, permisos, política de exportación y consentimiento. `JSONB` no debe ser el depósito analítico general.

### Aplicación móvil y operación offline

Incorporar sincronización con identificadores UUID generados en cliente cuando se requiera, claves de idempotencia, versiones optimistas (`row_version`), marca de borrado lógico solo si la sincronización lo exige, conflictos explícitos y cola de operaciones. No aceptar como verdad final cambios offline concurrentes de autorización, evaluación, aprobación o finanzas. Cifrar cachés locales y sincronizar adjuntos con cargas reanudables y permisos temporales.

### IA futura

La IA puede asistir con clasificación, resumen o sugerencias, pero no aprobar solicitudes ni asignar prioridad definitiva automáticamente. Registrar cada resultado en entidad futura `ModelInference` con versión de modelo/prompt, fecha, entradas referenciadas, salida, confianza, revisión humana y política de retención. No enviar PII/comunidades a servicios externos sin base legal, consentimiento y controles. Evaluar sesgos lingüísticos/territoriales con participación comunitaria; mantener decisión humana explicable y mecanismo de corrección.

### Riesgos y mitigaciones

| Riesgo | Mitigación del modelo/operación |
|---|---|
| Exposición de ubicación, lengua, identidad o necesidad comunitaria | Minimización, precisión geográfica graduada, autorización por organización, cifrado/controles y publicación privada por defecto. |
| Evaluación sesgada o incomprensible | Versionar rúbricas, conservar justificación, calibración humana y revisión comunitaria; separar recomendación de decisión. |
| Estados divergentes entre solicitud e historial/proyecto | Transiciones transaccionales, historial inmutable y revisión periódica de consistencia. |
| Pérdida/alteración de evidencia | Storage privado, checksums, retención, permisos y bitácora de acceso. |
| Colaboración externa no verificada | Estados explícitos, credenciales opcionales verificadas con evidencia y no afirmar aval donde no existe. |
| Complejidad financiera prematura | Mantener dominio financiero fuera del MVP; revisión contable y regulatoria antes de activar. |
| Catálogos territoriales o traducciones incorrectos | Fuente institucional y revisión por hablantes competentes; nunca inferir identidad cultural. |
| Reportes que reidentifican grupos pequeños | Supresión/agregación, análisis de riesgo y control de exportación. |
| Borrado incompatible con auditoría/retención | Política de ciclo de vida y anonimización aprobada antes de producción. |

## Decisiones de modelado y normalización

- **No duplicar contacto de comunidad en solicitud:** la solicitud referencia representante; si el contacto cambia, preservar instantánea solo si existe requisito legal/operativo documentado.
- **No almacenar colección de roles, criterios o colaboradores en JSON/arrays:** relaciones puente sostienen 3FN e integridad.
- **Categorías vs necesidades:** `ServiceCategory` es vocabulario común; `CommunityNeed` es necesidad contextual y temporal.
- **Evaluación versionada:** peso/rango viven en `EvaluationModelCriterion`, no en una copia editable de `EvaluationCriteria`; scores referencian evaluación y criterio.
- **Especialista vs credencial/oferta:** separar atributos multivaluados y procesos de verificación del perfil 1:1.
- **Solicitud vs proyecto:** solicitud representa demanda/decisión; proyecto, ejecución. El enlace nullable/único evita imponer ejecución inmediata o crear dos proyectos para una solicitud.
- **Historial vs estado actual:** estado actual facilita consultas; historial permite reconstrucción. Deben actualizarse juntos de forma transaccional.
- **Auditoría vs historial de negocio:** bitácora técnica no sustituye explicaciones de estados ni decisión visible para quien solicita.

## Riesgos de implementación del modelo

1. Polimorfismo de `AuditLog`, `Notification` y `CollaborationApplication` reduce integridad referencial. Si la garantía de FK es prioritaria, separar tablas de aplicación por destino o crear tabla supertipo común de registros referenciables.
2. La unicidad parcial basada en “vigente” y validación temporal compleja puede requerir exclusión GiST, trigger o transacción serializable; un simple `is_primary` no interpreta fechas futuras.
3. La regla de una organización responsable por comunidad limita gobernanza compartida; una evolución debe introducir `CommunityOrganization` con vigencias y rol, no sobrescribir el único FK.
4. El borrado lógico no reemplaza una política de retención ni resolución de solicitudes de eliminación. Definirlo antes de persistir PII real.
5. Este modelo no incluye localización multilingüe completa, consentimiento granular, formularios dinámicos, catálogo municipal oficial, turnos, mensajería externa ni libro contable. Requieren requisitos antes de diseño.

