"""Validaciones de solicitudes independientes del almacenamiento y transporte."""

from dataclasses import dataclass


@dataclass(frozen=True)
class DatosSolicitud:
    titulo: str
    descripcion: str
    categoria: str
    poblacion_estimada: int


def validar_envio(datos: DatosSolicitud) -> dict[str, str]:
    """Devuelve errores de los campos obligatorios antes de enviar una solicitud."""
    errores = {}
    for nombre in ("titulo", "descripcion", "categoria"):
        valor = getattr(datos, nombre)
        if not isinstance(valor, str) or not valor.strip():
            errores[nombre] = "Este campo es obligatorio."
    if isinstance(datos.poblacion_estimada, bool) or not isinstance(
        datos.poblacion_estimada, int
    ) or datos.poblacion_estimada < 1:
        errores["poblacion_estimada"] = "Indica un número entero mayor que cero."
    return errores
