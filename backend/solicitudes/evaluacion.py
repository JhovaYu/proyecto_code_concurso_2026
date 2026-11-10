"""Aplicación del motor de evaluación al flujo de solicitudes en memoria."""

from dataclasses import replace

from evaluaciones.motor import calcular_puntuacion
from solicitudes.flujo import ErrorFlujo, Estado, exigir_ong


def evaluar_solicitud(actor, solicitud, puntuaciones, pesos):
    """Evalúa en revisión y conserva el resultado previo sin decidir la resolución."""
    exigir_ong(actor)
    if solicitud.estado != Estado.EN_REVISION:
        raise ErrorFlujo("Solo se puede evaluar una solicitud en revisión.")
    resultado = calcular_puntuacion(puntuaciones, pesos)
    return replace(solicitud, evaluaciones=solicitud.evaluaciones + (resultado,),
                   requiere_nueva_evaluacion=False)
