import unittest

from solicitudes.flujo import (
    Actor, ErrorFlujo, Estado, crear_solicitud, editar_solicitud, enviar_solicitud,
    iniciar_revision, solicitar_informacion,
    responder_informacion, resolver_solicitud,
)
from solicitudes.reglas import DatosSolicitud


class FlujoTests(unittest.TestCase):
    def setUp(self):
        self.representante = Actor("rep", True, comunidades_representadas=frozenset({"comunidad"}))
        self.ong = Actor("ong", True, es_ong=True)
        self.datos = DatosSolicitud("Agua", "Falta agua", "Agua", 20)
        self.solicitud = crear_solicitud(self.representante, "comunidad", self.datos)

    def en_revision(self):
        return iniciar_revision(self.ong, enviar_solicitud(self.representante, self.solicitud))

    def test_ciclo_de_informacion_y_resolucion(self):
        solicitud = solicitar_informacion(self.ong, self.en_revision(), "Amplía la descripción")
        solicitud = editar_solicitud(self.representante, solicitud, self.datos)
        solicitud = responder_informacion(self.representante, solicitud, "Información ampliada")
        self.assertEqual(solicitud.estado, Estado.EN_REVISION)
        solicitud = resolver_solicitud(self.ong, solicitud, True, " Cumple los criterios ")
        self.assertEqual((solicitud.estado, solicitud.justificacion), (Estado.APROBADA, "Cumple los criterios"))
        with self.assertRaises(ErrorFlujo):
            editar_solicitud(self.representante, solicitud, self.datos)

    def test_rechazo_requiere_justificacion(self):
        solicitud = self.en_revision()
        with self.assertRaises(ErrorFlujo):
            resolver_solicitud(self.ong, solicitud, False, " ")
        self.assertEqual(resolver_solicitud(self.ong, solicitud, False, "No viable").estado, Estado.RECHAZADA)

    def test_acceso_y_estado(self):
        ajeno = Actor("otro", True, comunidades_representadas=frozenset({"otra"}))
        with self.assertRaises(ErrorFlujo):
            crear_solicitud(ajeno, "comunidad", self.datos)
        with self.assertRaises(ErrorFlujo):
            iniciar_revision(self.representante, enviar_solicitud(self.representante, self.solicitud))
        with self.assertRaises(ErrorFlujo):
            resolver_solicitud(self.ong, self.solicitud, True, "Aprobada")

    def test_no_enviar_o_resolver_solicitud_incompleta(self):
        incompleta = DatosSolicitud("", "Descripción", "Agua", 20)
        with self.assertRaises(ErrorFlujo):
            enviar_solicitud(self.representante, editar_solicitud(self.representante, self.solicitud, incompleta))
        modificada = editar_solicitud(self.representante, self.en_revision(), incompleta)
        self.assertEqual(modificada.estado, Estado.ENVIADA)
        with self.assertRaises(ErrorFlujo):
            resolver_solicitud(self.ong, modificada, True, "Sí")

    def test_mensajes_obligatorios(self):
        revision = self.en_revision()
        with self.assertRaises(ErrorFlujo):
            solicitar_informacion(self.ong, revision, " ")
        pendiente = solicitar_informacion(self.ong, revision, "¿Cuántas personas?")
        with self.assertRaises(ErrorFlujo):
            responder_informacion(self.representante, pendiente, "")
