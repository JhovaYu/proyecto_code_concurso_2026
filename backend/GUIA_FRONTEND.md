# Guía para construir el frontend del MVP

## Estado de este documento

Esta guía permite crear pantallas y datos simulados para el primer flujo: una solicitud comunitaria desde su creación hasta su aprobación o rechazo. Las reglas confirmadas se distinguen de las propuestas de integración.

**El backend todavía no expone rutas ni guarda información.** La estructura de la API, los nombres de rutas, los identificadores y los formatos JSON que aparecen más abajo son propuestas para coordinar al equipo; no son un contrato definitivo. La autenticación, la consulta de información y la conexión con PostgreSQL aún no están implementadas. No enviar datos reales a servicios simulados.

## Actores y alcance

| Actor | Función confirmada para el MVP |
|---|---|
| Representante comunitario autorizado | Crea solicitudes de su comunidad, las envía, las modifica mientras no estén resueltas y responde a peticiones de información. |
| Cuenta autorizada de la ONG | La ONG crea y autoriza las cuentas. Una cuenta autorizada de la ONG revisa solicitudes, pide información y aprueba o rechaza con justificación. |

Una persona que no sea representante autorizado de la comunidad no puede crear ni modificar sus solicitudes. La identidad, la autorización y la pertenencia a una comunidad deberán verificarse en el backend; el frontend puede adaptar la interfaz según el rol, pero ocultar botones no sustituye esa verificación.

El MVP aquí descrito termina al aprobar o rechazar. Los proyectos, pagos, fondos, evaluación multicriterio, archivos adjuntos, notificaciones y reportes quedan fuera de esta guía del primer flujo; no se requiere construirlos para esta entrega.

## Datos para la interfaz

### Solicitud

| Campo | Tipo para maqueta | Regla confirmada |
|---|---|---|
| `comunidad` | Identificador o referencia | La solicitud pertenece a la comunidad representada. Formato pendiente. |
| `titulo` | Texto | Obligatorio al enviar; no admite solo espacios. |
| `descripcion` | Texto largo | Obligatoria al enviar; no admite solo espacios. |
| `categoria` | Texto | Obligatoria al enviar. Catálogo y forma de selección pendientes. |
| `poblacion_estimada` | Número entero | Obligatorio al enviar y mayor que cero. |
| `estado` | Texto enumerado | Uno de los estados de la siguiente tabla. |
| `mensaje_ong` | Texto | Obligatorio cuando la ONG solicita información adicional. |
| `respuesta_representante` | Texto | Obligatorio al responder a esa solicitud de información. |
| `justificacion` | Texto | Obligatoria cuando la ONG aprueba o rechaza. |

El borrador puede contener datos incompletos; las validaciones anteriores aplican al enviarlo. La forma exacta de representar campos vacíos, límites de longitud y categorías sigue pendiente. La lógica actual solo conserva el último par de mensajes en memoria; **no existe todavía un historial consultable**.

### Estados y etiquetas

| Valor de la lógica actual | Etiqueta sugerida | Qué puede mostrar el frontend |
|---|---|---|
| `borrador` | Borrador | Formulario editable y acción de enviar. |
| `enviada` | Enviada | Datos de la solicitud y estado de espera de revisión. |
| `en_revision` | En revisión | Vista de revisión para la ONG; acciones de pedir información o resolver. |
| `informacion_requerida` | Información adicional requerida | Mensaje de la ONG y espacio de respuesta para el representante. |
| `aprobada` | Aprobada | Resultado y justificación, en modo de solo lectura. |
| `rechazada` | Rechazada | Resultado y justificación, en modo de solo lectura. |

## Flujo y acciones

```text
borrador ── enviar ──► enviada ── iniciar revisión ──► en_revision
                          ▲                               │
                          └───── editar en revisión ───────┤
                                                          ├─ aprobar ─► aprobada
                                                          ├─ rechazar ► rechazada
                                                          └─ pedir información ─► informacion_requerida
                                                                                      │
                                    en_revision ◄────────────── responder ────────────┘
```

La flecha de edición indica que una solicitud `en_revision` vuelve a `enviada` cuando el representante la modifica. En `informacion_requerida`, el representante puede actualizar los datos y responder; al responder, vuelve a `en_revision`. El representante puede modificar solicitudes no resueltas; después de aprobar o rechazar ya no se pueden editar. Para responder o resolver, la lógica actual valida nuevamente que los datos obligatorios estén completos.

| Estado | Representante autorizado | Cuenta autorizada de la ONG |
|---|---|---|
| Borrador | Editar y enviar | Sin acción de revisión definida |
| Enviada | Editar | Iniciar revisión |
| En revisión | Editar; vuelve a enviada | Pedir información, aprobar o rechazar |
| Información requerida | Editar y responder con mensaje | Esperar respuesta; otras acciones pendientes de definición |
| Aprobada o rechazada | Consultar resultado; no editar | Consultar resultado; reapertura pendiente de definición |

La consulta y visibilidad concretas aún no están implementadas. La tabla indica los controles que pueden diseñarse, no una garantía de que exista una operación de consulta.

## Pantallas sugeridas

Las siguientes pantallas son una propuesta visual para el flujo confirmado; rutas de navegación, diseño y componentes quedan a cargo del frontend.

1. **Acceso:** entrada a la plataforma y mensajes de acceso denegado. El mecanismo de inicio de sesión y recuperación de cuenta está pendiente.
2. **Solicitudes de la comunidad:** lista simulada con título, categoría, estado y acceso al detalle; estados de carga y lista vacía.
3. **Crear o editar solicitud:** comunidad, título, descripción, categoría y población estimada; acciones para guardar borrador o enviar; errores por campo. Confirmar visualmente que al editar durante la revisión vuelve a enviada.
4. **Detalle para el representante:** datos, estado, mensaje de la ONG cuando corresponda, formulario de respuesta y, al resolverse, justificación.
5. **Bandeja de la ONG:** solicitudes simuladas con comunidad, título, categoría y estado; acceso al detalle. Búsqueda, orden y filtros son propuestas pendientes.
6. **Detalle para la ONG:** datos de la solicitud; iniciar revisión; formulario para solicitar información; acciones de aprobar o rechazar con justificación.

Cada pantalla debería contemplar carga, información vacía, error de validación, acceso denegado, operación fallida y actualización de estado. Los textos definitivos y accesibilidad visual se acuerdan con el equipo de frontend.

## Contrato de API propuesto — no implementado

Para avanzar con maquetas, estas rutas ilustran una posible API REST. Deben acordarse antes de integrarlas; no llamar a estas rutas esperando que funcionen.

| Método | Ruta propuesta | Propósito |
|---|---|---|
| `GET` | `/api/solicitudes/` | Listar solicitudes visibles para la cuenta. |
| `POST` | `/api/solicitudes/` | Crear borrador de una comunidad representada. |
| `GET` | `/api/solicitudes/{id}/` | Consultar detalle autorizado. |
| `PATCH` | `/api/solicitudes/{id}/` | Modificar datos mientras no esté resuelta. |
| `POST` | `/api/solicitudes/{id}/enviar/` | Validar y enviar borrador. |
| `POST` | `/api/solicitudes/{id}/iniciar-revision/` | Iniciar la revisión de una solicitud enviada. |
| `POST` | `/api/solicitudes/{id}/solicitar-informacion/` | Solicitar información con un mensaje. |
| `POST` | `/api/solicitudes/{id}/responder-informacion/` | Responder con un mensaje. |
| `POST` | `/api/solicitudes/{id}/resolver/` | Aprobar o rechazar con justificación. |

Ejemplo **simulado** de detalle; el identificador y su formato son ilustrativos, y no existe todavía una respuesta de API definida:

```json
{
  "id": "ejemplo-001",
  "comunidad": "comunidad-ejemplo",
  "titulo": "Acceso a agua potable",
  "descripcion": "La comunidad requiere apoyo para mejorar el acceso al agua.",
  "categoria": "Agua",
  "poblacion_estimada": 120,
  "estado": "informacion_requerida",
  "mensaje_ong": "¿Pueden ampliar la descripción de la necesidad?",
  "respuesta_representante": "",
  "justificacion": ""
}
```

Ejemplos **propuestos** de cuerpos para acciones:

```json
{"mensaje": "¿Pueden ampliar la descripción de la necesidad?"}
```

```json
{"mensaje": "La necesidad afecta a 120 personas."}
```

```json
{"aprobar": true, "justificacion": "La solicitud cumple los criterios revisados."}
```

Se propone que los errores permitan distinguir validación por campo, falta de autenticación, falta de permisos, recurso inexistente y cambio de estado no permitido. El formato exacto de errores, códigos HTTP, paginación, versionado y mecanismo de autenticación están pendientes de acuerdo. En particular, el cliente nunca debe enviar un `rol`, `autorizado` o lista de comunidades como prueba de identidad.

## Casos para datos simulados

Para construir y revisar las vistas, crear ejemplos ficticios de: borrador incompleto; solicitud enviada; solicitud en revisión; solicitud que requiere información con mensaje de la ONG; respuesta del representante; solicitud aprobada con justificación; y solicitud rechazada con justificación. Añadir pruebas visuales para población cero, campos vacíos, mensaje vacío, usuario sin permisos y lista sin resultados.

## Decisiones pendientes para integrar

- Mecanismo de autenticación y recuperación de acceso.
- Datos de comunidad y usuario que necesita visualizar cada actor; identificadores y catálogo de categorías.
- Rutas definitivas, nombres de campos, formato de errores, paginación y filtros.
- Consulta del historial completo, fechas, responsables, adjuntos y notificaciones.
- Reglas de cancelación o reapertura y permisos de consulta detallados.

Estas decisiones no alteran las reglas confirmadas de esta guía hasta que se acuerden explícitamente.
