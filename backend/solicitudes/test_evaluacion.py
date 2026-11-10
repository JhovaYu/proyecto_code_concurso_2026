import unittest

from evaluaciones.motor import PESOS_INICIALES
from solicitudes.evaluacion import evaluar_solicitud
from solicitudes.flujo import (
    Actor, ErrorFlujo, Estado, crear_solicitud, editar_solicitud, enviar_solicitud,
    iniciar_revision, resolver_solicitud,
)
from solicitudes.reglas import DatosSolicitud


class EvaluacionSolicitudTests(unittest.TestCase):
    def setUp(self):
        self.ong = Actor("ong", True, es_ong=True)
        self.representante = Actor("rep", True, comunidades_representadas=frozenset({"c"}))
        self.datos = DatosSolicitud("Agua", "Necesidad", "Agua", 10)
        self.solicitud = crear_solicitud(self.representante, "c", self.datos)
        self.puntajes = {"urgencia": 10, "impacto_social": 5, "severidad": 5}

    def test_solo_ong_puede_evaluar_en_revision(self):
        with self.assertRaises(ErrorFlujo):
            evaluar_solicitud(self.ong, self.solicitud, self.puntajes, PESOS_INICIALES)
        enviada = enviar_solicitud(self.representante, self.solicitud)
        revision = iniciar_revision(self.ong, enviada)
        with self.assertRaises(ErrorFlujo):
            evaluar_solicitud(self.representante, revision, self.puntajes, PESOS_INICIALES)
        evaluada = evaluar_solicitud(self.ong, revision, self.puntajes, PESOS_INICIALES)
        self.assertEqual(evaluada.estado, Estado.EN_REVISION)
        self.assertEqual(evaluada.evaluaciones[0].puntaje, 7)
        with self.assertRaises(TypeError):
            evaluada.evaluaciones[0].desglose["urgencia"] = None

    def test_cambio_conserva_historial_y_exige_nueva_evaluacion(self):
        enviada = enviar_solicitud(self.representante, self.solicitud)
        revision = iniciar_revision(self.ong, enviada)
        evaluada = evaluar_solicitud(self.ong, revision, self.puntajes, PESOS_INICIALES)
        modificada = editar_solicitud(self.representante, evaluada, DatosSolicitud("Agua", "Nueva necesidad", "Agua", 10))
        self.assertTrue(modificada.requiere_nueva_evaluacion)
        self.assertEqual(len(modificada.evaluaciones), 1)
        revision = iniciar_revision(self.ong, modificada)
        with self.assertRaises(ErrorFlujo):
            resolver_solicitud(self.ong, revision, True, "Motivo")
        reevaluada = evaluar_solicitud(self.ong, revision, self.puntajes, PESOS_INICIALES)
        self.assertFalse(reevaluada.requiere_nueva_evaluacion)
        self.assertEqual(len(reevaluada.evaluaciones), 2)
        self.assertEqual(resolver_solicitud(self.ong, reevaluada, True, "Motivo").estado, Estado.APROBADA)
