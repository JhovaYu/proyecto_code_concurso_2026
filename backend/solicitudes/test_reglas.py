import unittest

from solicitudes.reglas import DatosSolicitud, validar_envio


class ValidacionEnvioTests(unittest.TestCase):
    def test_solicitud_completa(self):
        self.assertEqual(validar_envio(DatosSolicitud("Agua", "Falta agua", "Agua", 20)), {})

    def test_campos_vacios_y_poblacion_invalida(self):
        errores = validar_envio(DatosSolicitud(" ", "", "  ", 0))
        self.assertEqual(set(errores), {"titulo", "descripcion", "categoria", "poblacion_estimada"})

    def test_poblacion_booleana_no_es_entero_valido(self):
        self.assertIn("poblacion_estimada", validar_envio(DatosSolicitud("A", "B", "C", True)))


if __name__ == "__main__":
    unittest.main()
