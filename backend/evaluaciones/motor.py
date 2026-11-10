"""Cálculo de evaluación; la autorización de la ONG se verifica antes de invocarlo."""

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from math import isfinite
from types import MappingProxyType
from typing import Mapping

CRITERIOS = ("urgencia", "impacto_social", "severidad")
PESOS_INICIALES = MappingProxyType({"urgencia": 40, "impacto_social": 30, "severidad": 30})


@dataclass(frozen=True)
class DesgloseCriterio:
    puntuacion: Fraction
    peso: Fraction
    aporte: Fraction


@dataclass(frozen=True)
class ResultadoEvaluacion:
    puntaje: Fraction
    desglose: Mapping[str, DesgloseCriterio]


def _numero_exacto(valor: object, nombre: str) -> Fraction:
    if isinstance(valor, bool) or not isinstance(valor, (int, float, Decimal, Fraction)):
        raise ValueError(f"{nombre} debe ser un número finito.")
    if isinstance(valor, float):
        if not isfinite(valor):
            raise ValueError(f"{nombre} debe ser un número finito.")
        return Fraction(str(valor))
    if isinstance(valor, Decimal) and not valor.is_finite():
        raise ValueError(f"{nombre} debe ser un número finito.")
    return Fraction(valor)


def calcular_puntuacion(puntuaciones: Mapping[str, object], pesos: Mapping[str, object]) -> ResultadoEvaluacion:
    """Calcula el promedio exacto y su desglose, sin decidir ni asignar umbrales.

    Los pesos son porcentajes explícitos que suman 100. No se redondea el resultado.
    """
    for nombre, valores in (("puntuaciones", puntuaciones), ("pesos", pesos)):
        if not isinstance(valores, Mapping) or set(valores) != set(CRITERIOS):
            raise ValueError(f"{nombre} debe incluir exactamente los tres criterios.")

    notas = {clave: _numero_exacto(puntuaciones[clave], clave) for clave in CRITERIOS}
    factores = {clave: _numero_exacto(pesos[clave], f"peso de {clave}") for clave in CRITERIOS}
    if any(nota < 0 or nota > 10 for nota in notas.values()):
        raise ValueError("Cada puntuación debe estar entre 0 y 10.")
    if any(peso < 0 for peso in factores.values()) or sum(factores.values()) != 100:
        raise ValueError("Los pesos deben ser no negativos y sumar 100 %.")
    desglose = {
        clave: DesgloseCriterio(notas[clave], factores[clave], notas[clave] * factores[clave] / 100)
        for clave in CRITERIOS
    }
    return ResultadoEvaluacion(sum(item.aporte for item in desglose.values()), MappingProxyType(desglose))
