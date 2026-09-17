"""
Pruebas unitarias para el conversor de temperatura.
Prueba de forma aislada las funciones matemáticas, de validación y de redondeo.
"""

import unittest
from decimal import Decimal
import sys
from pathlib import Path

# Garantizar resolución del módulo conversor_temperatura
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from conversor_temperatura import (
    celsius_a_fahrenheit,
    fahrenheit_a_celsius,
    celsius_a_kelvin,
    kelvin_a_celsius,
    fahrenheit_a_kelvin,
    kelvin_a_fahrenheit,
    redondear,
    normalizar_unidad,
    validar_y_convertir_a_decimal,
    validar_cero_absoluto,
)


class TestConversionesUnitarias(unittest.TestCase):
    """Pruebas unitarias de fórmulas matemáticas de conversión (User Story 1)."""

    def test_celsius_a_fahrenheit(self):
        # 100 °C -> 212.00 °F
        self.assertEqual(celsius_a_fahrenheit(100), Decimal("212.00"))
        # 0 °C -> 32.00 °F
        self.assertEqual(celsius_a_fahrenheit(0), Decimal("32.00"))
        # -40 °C -> -40.00 °F
        self.assertEqual(celsius_a_fahrenheit(-40), Decimal("-40.00"))

    def test_fahrenheit_a_celsius(self):
        # 212 °F -> 100.00 °C
        self.assertEqual(fahrenheit_a_celsius(212), Decimal("100.00"))
        # 32 °F -> 0.00 °C
        self.assertEqual(fahrenheit_a_celsius(32), Decimal("0.00"))
        # -40 °F -> -40.00 °C
        self.assertEqual(fahrenheit_a_celsius(-40), Decimal("-40.00"))

    def test_celsius_a_kelvin(self):
        # 0 °C -> 273.15 K
        self.assertEqual(celsius_a_kelvin(0), Decimal("273.15"))
        # 100 °C -> 373.15 K
        self.assertEqual(celsius_a_kelvin(100), Decimal("373.15"))
        # -273.15 °C -> 0.00 K (Cero absoluto)
        self.assertEqual(celsius_a_kelvin(Decimal("-273.15")), Decimal("0.00"))

    def test_kelvin_a_celsius(self):
        # 273.15 K -> 0.00 °C
        self.assertEqual(kelvin_a_celsius(Decimal("273.15")), Decimal("0.00"))
        # 373.15 K -> 100.00 °C
        self.assertEqual(kelvin_a_celsius(Decimal("373.15")), Decimal("100.00"))
        # 0 K -> -273.15 °C
        self.assertEqual(kelvin_a_celsius(0), Decimal("-273.15"))

    def test_fahrenheit_a_kelvin(self):
        # 32 °F -> 273.15 K
        self.assertEqual(fahrenheit_a_kelvin(32), Decimal("273.15"))
        # 212 °F -> 373.15 K
        self.assertEqual(fahrenheit_a_kelvin(212), Decimal("373.15"))

    def test_kelvin_a_fahrenheit(self):
        # 273.15 K -> 32.00 °F
        self.assertEqual(kelvin_a_fahrenheit(Decimal("273.15")), Decimal("32.00"))
        # 373.15 K -> 212.00 °F
        self.assertEqual(kelvin_a_fahrenheit(Decimal("373.15")), Decimal("212.00"))


class TestValidacionesUnitarias(unittest.TestCase):
    """Pruebas unitarias para límites físicos y validación de datos (User Story 2)."""

    def test_rechazo_cero_absoluto_funciones_directas(self):
        with self.assertRaises(ValueError) as ctx:
            kelvin_a_celsius(-0.01)
        self.assertIn("cero absoluto", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            kelvin_a_fahrenheit(-1)
        self.assertIn("cero absoluto", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            celsius_a_fahrenheit(-274)
        self.assertIn("cero absoluto", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            celsius_a_kelvin(-300)
        self.assertIn("cero absoluto", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            fahrenheit_a_celsius(-460)
        self.assertIn("cero absoluto", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            fahrenheit_a_kelvin(-500)
        self.assertIn("cero absoluto", str(ctx.exception).lower())

    def test_funcion_validar_cero_absoluto(self):
        # Casos válidos no deben lanzar excepción
        validar_cero_absoluto(Decimal("0"), "K")
        validar_cero_absoluto(Decimal("-273.15"), "C")
        validar_cero_absoluto(Decimal("-459.67"), "F")

        # Casos inválidos deben lanzar ValueError
        with self.assertRaises(ValueError):
            validar_cero_absoluto(Decimal("-0.01"), "K")
        with self.assertRaises(ValueError):
            validar_cero_absoluto(Decimal("-273.16"), "C")
        with self.assertRaises(ValueError):
            validar_cero_absoluto(Decimal("-459.68"), "F")

    def test_rechazo_entradas_vacias_o_nulas(self):
        with self.assertRaises(ValueError) as ctx:
            validar_y_convertir_a_decimal("")
        self.assertIn("no puede estar vacía", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            validar_y_convertir_a_decimal("   ")
        self.assertIn("no puede estar vacía", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            validar_y_convertir_a_decimal(None)
        self.assertIn("no puede estar vacía", str(ctx.exception).lower())

    def test_rechazo_entradas_no_numericas(self):
        with self.assertRaises(ValueError) as ctx:
            validar_y_convertir_a_decimal("abc")
        self.assertIn("debe ser un número válido", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            validar_y_convertir_a_decimal(True)
        self.assertIn("debe ser un número válido", str(ctx.exception).lower())

        with self.assertRaises(ValueError):
            validar_y_convertir_a_decimal(False)

        with self.assertRaises(ValueError):
            validar_y_convertir_a_decimal([100])

        with self.assertRaises(ValueError):
            validar_y_convertir_a_decimal({"temp": 100})

    def test_espacios_en_blanco_alrededor_de_numero(self):
        self.assertEqual(validar_y_convertir_a_decimal("  100  "), Decimal("100"))
        self.assertEqual(validar_y_convertir_a_decimal(" \t 0 \n "), Decimal("0"))

    def test_normalizar_unidad(self):
        self.assertEqual(normalizar_unidad("c"), "C")
        self.assertEqual(normalizar_unidad(" F "), "F")
        self.assertEqual(normalizar_unidad("k"), "K")

        with self.assertRaises(ValueError):
            normalizar_unidad("X")

        with self.assertRaises(ValueError):
            normalizar_unidad("")

        with self.assertRaises(ValueError):
            normalizar_unidad(None)

        with self.assertRaises(ValueError):
            normalizar_unidad(123)


class TestPrecisionYRedondeoUnitario(unittest.TestCase):
    """Pruebas unitarias para redondeo simétrico formal a 2 decimales (User Story 3)."""

    def test_redondeo_a_dos_decimales(self):
        self.assertEqual(redondear(Decimal("35.666")), Decimal("35.67"))
        self.assertEqual(redondear(Decimal("35.664")), Decimal("35.66"))
        self.assertEqual(redondear(Decimal("35.665")), Decimal("35.67"))
        self.assertEqual(redondear(Decimal("12.345")), Decimal("12.35"))
        self.assertEqual(redondear(Decimal("0")), Decimal("0.00"))


if __name__ == "__main__":
    unittest.main()
