import os
import unittest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from solicitudes.flujo import Actor, crear_solicitud, enviar_solicitud, ErrorFlujo
from solicitudes.reglas import DatosSolicitud
from solicitudes.serializadores import (
    CrearSolicitudSerializer, DatosBorradorSerializer, MensajeSerializer,
    ResolucionSerializer, SolicitudSerializer,
)


class ContratosTests(unittest.TestCase):
    def test_borrador_incompleto_no_puede_enviarse(self):
        entrada = CrearSolicitudSerializer(data={"comunidad": "c1"})
        self.assertTrue(entrada.is_valid(), entrada.errors)
        valores = dict(entrada.validated_data)
        comunidad = valores.pop("comunidad")
        actor = Actor("r1", True, comunidades_representadas=frozenset({"c1"}))
        solicitud = crear_solicitud(actor, comunidad, DatosSolicitud(**valores))
        self.assertIsNone(SolicitudSerializer(solicitud).data["poblacion_estimada"])
        with self.assertRaises(ErrorFlujo):
            enviar_solicitud(actor, solicitud)

    def test_solicitud_completa_serializada(self):
        entrada = CrearSolicitudSerializer(data={"comunidad": "c1", "titulo": "Agua", "descripcion": "Necesidad", "categoria": "Agua", "poblacion_estimada": 12})
        self.assertTrue(entrada.is_valid(), entrada.errors)
        valores = dict(entrada.validated_data)
        comunidad = valores.pop("comunidad")
        actor = Actor("r1", True, comunidades_representadas=frozenset({"c1"}))
        solicitud = enviar_solicitud(actor, crear_solicitud(actor, comunidad, DatosSolicitud(**valores)))
        salida = SolicitudSerializer(solicitud).data
        self.assertEqual((salida["estado"], salida["poblacion_estimada"]), ("enviada", 12))

    def test_no_admite_identidad_ni_estado_desde_cliente(self):
        for campo in ("autorizado", "es_ong", "estado", "comunidades_representadas"):
            entrada = CrearSolicitudSerializer(data={"comunidad": "c1", campo: True})
            self.assertFalse(entrada.is_valid())
            self.assertIn(campo, entrada.errors)

    def test_edicion_parcial_y_mensajes(self):
        entrada = DatosBorradorSerializer(data={"titulo": "Actualizado"}, partial=True)
        self.assertTrue(entrada.is_valid(), entrada.errors)
        self.assertEqual(dict(entrada.validated_data), {"titulo": "Actualizado"})
        for valor in ("", "   "):
            self.assertFalse(MensajeSerializer(data={"mensaje": valor}).is_valid())

    def test_resolucion_exige_booleano_y_justificacion(self):
        for valor in ("true", 1, None):
            self.assertFalse(ResolucionSerializer(data={"aprobar": valor, "justificacion": "Motivo"}).is_valid())
        self.assertFalse(ResolucionSerializer(data={"aprobar": False, "justificacion": " "}).is_valid())
        self.assertTrue(ResolucionSerializer(data={"aprobar": False, "justificacion": "Motivo"}).is_valid())

    def test_textos_no_aceptan_numeros(self):
        for campo in ("comunidad", "titulo", "descripcion", "categoria"):
            datos = {"comunidad": "c1", campo: 12}
            entrada = CrearSolicitudSerializer(data=datos)
            self.assertFalse(entrada.is_valid(), campo)
            self.assertIn(campo, entrada.errors)
        self.assertFalse(MensajeSerializer(data={"mensaje": 12}).is_valid())
        self.assertFalse(ResolucionSerializer(data={"aprobar": True, "justificacion": 12}).is_valid())

    def test_poblacion_debe_ser_entero_o_nulo_en_borrador(self):
        for valor in (True, 1.0, "12"):
            entrada = DatosBorradorSerializer(data={"poblacion_estimada": valor})
            self.assertFalse(entrada.is_valid(), repr(valor))
        for valor in (None, 0, 12):
            entrada = DatosBorradorSerializer(data={"poblacion_estimada": valor})
            self.assertTrue(entrada.is_valid(), entrada.errors)
