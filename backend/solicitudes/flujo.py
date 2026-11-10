"""Reglas de transición en memoria, sin autenticación ni persistencia."""

from dataclasses import dataclass, replace
from enum import Enum

from solicitudes.reglas import DatosSolicitud, validar_envio


class Estado(str, Enum):
    BORRADOR = "borrador"
    ENVIADA = "enviada"
    EN_REVISION = "en_revision"
    INFORMACION_REQUERIDA = "informacion_requerida"
    APROBADA = "aprobada"
    RECHAZADA = "rechazada"


class ErrorFlujo(ValueError):
    """Operación que incumple una regla del flujo."""


@dataclass(frozen=True)
class Actor:
    """La capa de autenticación deberá verificar estos datos antes de usarlos."""

    identificador: str
    autorizado: bool
    es_ong: bool = False
    comunidades_representadas: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Solicitud:
    comunidad: str
    datos: DatosSolicitud
    estado: Estado = Estado.BORRADOR
    justificacion: str = ""
    mensaje_ong: str = ""
    respuesta_representante: str = ""


def exigir_representante(actor: Actor, comunidad: str) -> None:
    if not actor.autorizado or comunidad not in actor.comunidades_representadas:
        raise ErrorFlujo("Se requiere un representante autorizado de la comunidad.")


def exigir_ong(actor: Actor) -> None:
    if not actor.autorizado or not actor.es_ong:
        raise ErrorFlujo("Se requiere una cuenta autorizada de la ONG.")


def crear_solicitud(actor: Actor, comunidad: str, datos: DatosSolicitud) -> Solicitud:
    exigir_representante(actor, comunidad)
    return Solicitud(comunidad=comunidad, datos=datos)


def editar_solicitud(actor: Actor, solicitud: Solicitud, datos: DatosSolicitud) -> Solicitud:
    exigir_representante(actor, solicitud.comunidad)
    if solicitud.estado in (Estado.APROBADA, Estado.RECHAZADA):
        raise ErrorFlujo("Una solicitud resuelta no puede modificarse.")
    estado = Estado.ENVIADA if solicitud.estado == Estado.EN_REVISION else solicitud.estado
    return replace(solicitud, datos=datos, estado=estado)


def enviar_solicitud(actor: Actor, solicitud: Solicitud) -> Solicitud:
    exigir_representante(actor, solicitud.comunidad)
    if solicitud.estado != Estado.BORRADOR:
        raise ErrorFlujo("Solo se puede enviar un borrador.")
    errores = validar_envio(solicitud.datos)
    if errores:
        raise ErrorFlujo(f"La solicitud está incompleta: {', '.join(errores)}.")
    return replace(solicitud, estado=Estado.ENVIADA)


def iniciar_revision(actor: Actor, solicitud: Solicitud) -> Solicitud:
    exigir_ong(actor)
    if solicitud.estado != Estado.ENVIADA:
        raise ErrorFlujo("Solo se puede iniciar la revisión de una solicitud enviada.")
    return replace(solicitud, estado=Estado.EN_REVISION)


def solicitar_informacion(actor: Actor, solicitud: Solicitud, mensaje: str) -> Solicitud:
    exigir_ong(actor)
    if solicitud.estado != Estado.EN_REVISION:
        raise ErrorFlujo("Solo se puede pedir información de una solicitud en revisión.")
    if not isinstance(mensaje, str) or not mensaje.strip():
        raise ErrorFlujo("La solicitud de información requiere un mensaje.")
    return replace(solicitud, estado=Estado.INFORMACION_REQUERIDA,
                   mensaje_ong=mensaje.strip(), respuesta_representante="")


def responder_informacion(actor: Actor, solicitud: Solicitud, mensaje: str) -> Solicitud:
    exigir_representante(actor, solicitud.comunidad)
    if solicitud.estado != Estado.INFORMACION_REQUERIDA:
        raise ErrorFlujo("La solicitud no está esperando información adicional.")
    if not isinstance(mensaje, str) or not mensaje.strip():
        raise ErrorFlujo("La respuesta requiere un mensaje.")
    errores = validar_envio(solicitud.datos)
    if errores:
        raise ErrorFlujo(f"La solicitud está incompleta: {', '.join(errores)}.")
    return replace(solicitud, estado=Estado.EN_REVISION, respuesta_representante=mensaje.strip())


def resolver_solicitud(actor: Actor, solicitud: Solicitud, aprobar: bool, justificacion: str) -> Solicitud:
    exigir_ong(actor)
    if solicitud.estado != Estado.EN_REVISION:
        raise ErrorFlujo("Solo se puede resolver una solicitud en revisión.")
    if not isinstance(aprobar, bool):
        raise ErrorFlujo("La resolución debe indicar aprobación o rechazo.")
    if not isinstance(justificacion, str) or not justificacion.strip():
        raise ErrorFlujo("La resolución requiere una justificación escrita.")
    errores = validar_envio(solicitud.datos)
    if errores:
        raise ErrorFlujo(f"La solicitud está incompleta: {', '.join(errores)}.")
    return replace(solicitud, estado=Estado.APROBADA if aprobar else Estado.RECHAZADA,
                   justificacion=justificacion.strip())
