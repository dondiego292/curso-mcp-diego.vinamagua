"""
Suite de pruebas unitarias para el conversor de temperatura.
Verifica criterios de aceptación, fórmulas de conversión y casos borde.
"""

import unittest
from decimal import Decimal
import subprocess
import sys

from conversor_temperatura import (
    convertir_temperatura,
    celsius_a_fahrenheit,
    fahrenheit_a_celsius,
    celsius_a_kelvin,
    kelvin_a_celsius,
    fahrenheit_a_kelvin,
    kelvin_a_fahrenheit,
    redondear,
)


class TestConversionesEstandar(unittest.TestCase):
    """Pruebas para User Story 1: Conversiones bidireccionales C, F y K."""

    def test_celsius_a_fahrenheit(self):
        # 100 °C -> 212.00 °F
        self.assertEqual(celsius_a_fahrenheit(100), Decimal("212.00"))
        self.assertEqual(convertir_temperatura(100, "C", "F"), Decimal("212.00"))
        # 0 °C -> 32.00 °F
        self.assertEqual(celsius_a_fahrenheit(0), Decimal("32.00"))
        self.assertEqual(convertir_temperatura(0, "C", "F"), Decimal("32.00"))
        # -40 °C -> -40.00 °F
        self.assertEqual(celsius_a_fahrenheit(-40), Decimal("-40.00"))
        self.assertEqual(convertir_temperatura(-40, "C", "F"), Decimal("-40.00"))

    def test_fahrenheit_a_celsius(self):
        # 212 °F -> 100.00 °C
        self.assertEqual(fahrenheit_a_celsius(212), Decimal("100.00"))
        self.assertEqual(convertir_temperatura(212, "F", "C"), Decimal("100.00"))
        # 32 °F -> 0.00 °C
        self.assertEqual(fahrenheit_a_celsius(32), Decimal("0.00"))
        self.assertEqual(convertir_temperatura(32, "F", "C"), Decimal("0.00"))
        # -40 °F -> -40.00 °C
        self.assertEqual(fahrenheit_a_celsius(-40), Decimal("-40.00"))
        self.assertEqual(convertir_temperatura(-40, "F", "C"), Decimal("-40.00"))

    def test_celsius_a_kelvin(self):
        # 0 °C -> 273.15 K
        self.assertEqual(celsius_a_kelvin(0), Decimal("273.15"))
        self.assertEqual(convertir_temperatura(0, "C", "K"), Decimal("273.15"))
        # 100 °C -> 373.15 K
        self.assertEqual(celsius_a_kelvin(100), Decimal("373.15"))
        self.assertEqual(convertir_temperatura(100, "C", "K"), Decimal("373.15"))
        # -273.15 °C -> 0.00 K (Cero absoluto)
        self.assertEqual(celsius_a_kelvin(Decimal("-273.15")), Decimal("0.00"))
        self.assertEqual(convertir_temperatura("-273.15", "C", "K"), Decimal("0.00"))

    def test_kelvin_a_celsius(self):
        # 273.15 K -> 0.00 °C
        self.assertEqual(kelvin_a_celsius(Decimal("273.15")), Decimal("0.00"))
        self.assertEqual(convertir_temperatura("273.15", "K", "C"), Decimal("0.00"))
        # 373.15 K -> 100.00 °C
        self.assertEqual(kelvin_a_celsius(Decimal("373.15")), Decimal("100.00"))
        self.assertEqual(convertir_temperatura(373.15, "K", "C"), Decimal("100.00"))
        # 0 K -> -273.15 °C
        self.assertEqual(kelvin_a_celsius(0), Decimal("-273.15"))
        self.assertEqual(convertir_temperatura(0, "K", "C"), Decimal("-273.15"))

    def test_fahrenheit_a_kelvin(self):
        # 32 °F -> 273.15 K
        self.assertEqual(fahrenheit_a_kelvin(32), Decimal("273.15"))
        self.assertEqual(convertir_temperatura(32, "F", "K"), Decimal("273.15"))
        # 212 °F -> 373.15 K
        self.assertEqual(fahrenheit_a_kelvin(212), Decimal("373.15"))
        self.assertEqual(convertir_temperatura(212, "F", "K"), Decimal("373.15"))

    def test_kelvin_a_fahrenheit(self):
        # 273.15 K -> 32.00 °F
        self.assertEqual(kelvin_a_fahrenheit(Decimal("273.15")), Decimal("32.00"))
        self.assertEqual(convertir_temperatura("273.15", "K", "F"), Decimal("32.00"))
        # 373.15 K -> 212.00 °F
        self.assertEqual(kelvin_a_fahrenheit(Decimal("373.15")), Decimal("212.00"))
        self.assertEqual(convertir_temperatura(373.15, "K", "F"), Decimal("212.00"))


class TestValidacionesYCasosBorde(unittest.TestCase):
    """Pruebas para User Story 2: Límites físicos y validación de entradas."""

    def test_rechazo_cero_absoluto(self):
        # Kelvin negativo directo
        with self.assertRaises(ValueError) as ctx:
            convertir_temperatura(-1, "K", "C")
        self.assertIn("cero absoluto", str(ctx.exception).lower())

        with self.assertRaises(ValueError):
            kelvin_a_celsius(-0.01)

        # Celsius bajo cero absoluto (< -273.15 °C)
        with self.assertRaises(ValueError) as ctx:
            convertir_temperatura(-300, "C", "K")
        self.assertIn("cero absoluto", str(ctx.exception).lower())

        with self.assertRaises(ValueError):
            celsius_a_fahrenheit(-274)

        # Fahrenheit bajo cero absoluto (< -459.67 °F)
        with self.assertRaises(ValueError) as ctx:
            convertir_temperatura(-500, "F", "K")
        self.assertIn("cero absoluto", str(ctx.exception).lower())

        with self.assertRaises(ValueError):
            fahrenheit_a_celsius(-460)

    def test_rechazo_entradas_vacias_o_nulas(self):
        # Cadenas vacías
        with self.assertRaises(ValueError) as ctx:
            convertir_temperatura("", "C", "F")
        self.assertIn("no puede estar vacía", str(ctx.exception).lower())

        # Cadenas solo con espacios
        with self.assertRaises(ValueError) as ctx:
            convertir_temperatura("   ", "C", "F")
        self.assertIn("no puede estar vacía", str(ctx.exception).lower())

        # Valor None
        with self.assertRaises(ValueError) as ctx:
            convertir_temperatura(None, "C", "F")
        self.assertIn("no puede estar vacía", str(ctx.exception).lower())

    def test_rechazo_entradas_no_numericas(self):
        # Texto alfabético
        with self.assertRaises(ValueError) as ctx:
            convertir_temperatura("abc", "C", "F")
        self.assertIn("debe ser un número válido", str(ctx.exception).lower())

        # Booleanos
        with self.assertRaises(ValueError) as ctx:
            convertir_temperatura(True, "C", "F")
        self.assertIn("debe ser un número válido", str(ctx.exception).lower())

        with self.assertRaises(ValueError):
            convertir_temperatura(False, "C", "F")

        # Estructuras de datos
        with self.assertRaises(ValueError):
            convertir_temperatura([100], "C", "F")

        with self.assertRaises(ValueError):
            convertir_temperatura({"temp": 100}, "C", "F")

    def test_espacios_en_blanco_alrededor_de_numero(self):
        # Debe admitir espacios alrededor de números válidos tras sanitizar
        self.assertEqual(convertir_temperatura("  100  ", "C", "F"), Decimal("212.00"))
        self.assertEqual(convertir_temperatura(" \t 0 \n ", "C", "K"), Decimal("273.15"))


class TestPrecisionYReflexividad(unittest.TestCase):
    """Pruebas para User Story 3: Conversión reflexiva y formato de precisión."""

    def test_conversiones_reflexivas(self):
        # Celsius a Celsius
        self.assertEqual(convertir_temperatura(25, "C", "C"), Decimal("25.00"))
        self.assertEqual(convertir_temperatura("25.5", "c", "c"), Decimal("25.50"))
        self.assertEqual(convertir_temperatura(-100, "C", "C"), Decimal("-100.00"))

        # Fahrenheit a Fahrenheit
        self.assertEqual(convertir_temperatura(98.6, "F", "F"), Decimal("98.60"))
        self.assertEqual(convertir_temperatura("32", "f", "f"), Decimal("32.00"))

        # Kelvin a Kelvin
        self.assertEqual(convertir_temperatura(300, "K", "K"), Decimal("300.00"))
        self.assertEqual(convertir_temperatura("273.15", "k", "k"), Decimal("273.15"))

    def test_redondeo_a_dos_decimales(self):
        # 37 °C a Fahrenheit = 98.6 -> 98.60
        self.assertEqual(celsius_a_fahrenheit(37), Decimal("98.60"))

        # Redondeo half-up con Decimal directo
        self.assertEqual(redondear(Decimal("35.666")), Decimal("35.67"))
        self.assertEqual(redondear(Decimal("35.664")), Decimal("35.66"))
        self.assertEqual(redondear(Decimal("35.665")), Decimal("35.67"))
        self.assertEqual(redondear(Decimal("12.345")), Decimal("12.35"))


class TestCLI(unittest.TestCase):
    """Pruebas para la interfaz de línea de comandos (CLI)."""

    def test_cli_exito(self):
        result = subprocess.run(
            [sys.executable, "conversor_temperatura.py", "100", "C", "F"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "212.00")

    def test_cli_error_cero_absoluto(self):
        result = subprocess.run(
            [sys.executable, "conversor_temperatura.py", "-1", "K", "C"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error:", result.stderr)
        self.assertIn("cero absoluto", result.stderr.lower())

    def test_cli_error_no_numerico(self):
        result = subprocess.run(
            [sys.executable, "conversor_temperatura.py", "abc", "C", "F"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error:", result.stderr)
        self.assertIn("número válido", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
