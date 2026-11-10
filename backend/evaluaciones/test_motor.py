import unittest
from decimal import Decimal
from fractions import Fraction

from evaluaciones.motor import PESOS_INICIALES, calcular_puntuacion


class MotorEvaluacionTests(unittest.TestCase):
    def setUp(self):
        self.notas = {"urgencia": 10, "impacto_social": 6, "severidad": 2}
        self.pesos = PESOS_INICIALES.copy()

    def test_promedio_ponderado_y_desglose(self):
        resultado = calcular_puntuacion(self.notas, self.pesos)
        self.assertEqual(resultado.puntaje, Fraction(32, 5))
        self.assertEqual(resultado.desglose["urgencia"].aporte, 4)
        self.assertEqual(resultado.desglose["urgencia"].peso, 40)
        self.assertEqual(resultado.desglose["urgencia"].puntuacion, 10)

    def test_resultado_exacto_sin_redondeo(self):
        notas = {"urgencia": 1, "impacto_social": 0, "severidad": 0}
        pesos = {"urgencia": Fraction(100, 3), "impacto_social": Fraction(100, 3), "severidad": Fraction(100, 3)}
        self.assertEqual(calcular_puntuacion(notas, pesos).puntaje, Fraction(1, 3))

    def test_acepta_decimales_y_cero_como_peso(self):
        notas = {"urgencia": Decimal("9.5"), "impacto_social": 0, "severidad": 0}
        pesos = {"urgencia": 100, "impacto_social": 0, "severidad": 0}
        self.assertEqual(calcular_puntuacion(notas, pesos).puntaje, Fraction(19, 2))

    def test_rechaza_criterios_faltantes_o_adicionales(self):
        for valores in ({"urgencia": 3}, {**self.notas, "otro": 3}):
            with self.subTest(valores=valores), self.assertRaises(ValueError):
                calcular_puntuacion(valores, self.pesos)

    def test_rechaza_puntuaciones_invalidas(self):
        for valor in (-1, 11, True, "5", float("nan"), float("inf")):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                calcular_puntuacion({**self.notas, "urgencia": valor}, self.pesos)

    def test_rechaza_pesos_invalidos(self):
        for pesos in (dict.fromkeys(self.pesos, 0), {**self.pesos, "urgencia": -1},
                      {**self.pesos, "urgencia": float("inf")}, {"urgencia": 1},
                      {**self.pesos, "urgencia": 41}, {**self.pesos, "urgencia": True}):
            with self.subTest(pesos=pesos), self.assertRaises(ValueError):
                calcular_puntuacion(self.notas, pesos)


if __name__ == "__main__":
    unittest.main()
