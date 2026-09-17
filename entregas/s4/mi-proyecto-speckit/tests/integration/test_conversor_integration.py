"""
Pruebas de integración en memoria para el conversor de temperatura.
Verifica la conexión entre componentes (CLI y lógica de negocio, o pipeline
completo de conversión) directamente en memoria, SIN usar subprocess.
"""

import io
import unittest
from contextlib import redirect_stdout, redirect_stderr
from decimal import Decimal
import sys
from pathlib import Path

# Garantizar resolución del módulo conversor_temperatura
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from conversor_temperatura import main, convertir_temperatura


class TestIntegracionCLIEnMemoria(unittest.TestCase):
    """Pruebas de integración en memoria entre el punto de entrada CLI y el motor de conversión."""

    def test_cli_integracion_celsius_a_fahrenheit(self):
        f_stdout = io.StringIO()
        with redirect_stdout(f_stdout):
            codigo = main(["100", "C", "F"])
        self.assertEqual(codigo, 0)
        self.assertEqual(f_stdout.getvalue().strip(), "212.00")

    def test_cli_integracion_celsius_a_kelvin(self):
        f_stdout = io.StringIO()
        with redirect_stdout(f_stdout):
            codigo = main(["0", "C", "K"])
        self.assertEqual(codigo, 0)
        self.assertEqual(f_stdout.getvalue().strip(), "273.15")

    def test_cli_integracion_reflexiva(self):
        f_stdout = io.StringIO()
        with redirect_stdout(f_stdout):
            codigo = main(["25.5", "C", "C"])
        self.assertEqual(codigo, 0)
        self.assertEqual(f_stdout.getvalue().strip(), "25.50")

    def test_cli_integracion_cero_absoluto(self):
        f_stderr = io.StringIO()
        with redirect_stderr(f_stderr):
            codigo = main(["-1", "K", "C"])
        self.assertEqual(codigo, 1)
        self.assertIn("cero absoluto", f_stderr.getvalue().lower())

    def test_cli_integracion_entrada_no_numerica(self):
        f_stderr = io.StringIO()
        with redirect_stderr(f_stderr):
            codigo = main(["abc", "C", "F"])
        self.assertEqual(codigo, 1)
        self.assertIn("número válido", f_stderr.getvalue().lower())

    def test_cli_integracion_unidad_invalida(self):
        f_stderr = io.StringIO()
        with redirect_stderr(f_stderr):
            codigo = main(["100", "Z", "F"])
        self.assertEqual(codigo, 1)
        self.assertIn("unidad no válida", f_stderr.getvalue().lower())


class TestIntegracionPipelineEnMemoria(unittest.TestCase):
    """Pruebas de integración del pipeline completo a través de convertir_temperatura."""

    def test_pipeline_conversiones_estandar(self):
        self.assertEqual(convertir_temperatura(100, "C", "F"), Decimal("212.00"))
        self.assertEqual(convertir_temperatura(212, "F", "C"), Decimal("100.00"))
        self.assertEqual(convertir_temperatura(0, "C", "K"), Decimal("273.15"))
        self.assertEqual(convertir_temperatura("273.15", "K", "C"), Decimal("0.00"))
        self.assertEqual(convertir_temperatura(32, "F", "K"), Decimal("273.15"))
        self.assertEqual(convertir_temperatura("273.15", "K", "F"), Decimal("32.00"))

    def test_pipeline_reflexivo(self):
        self.assertEqual(convertir_temperatura(25, "C", "C"), Decimal("25.00"))
        self.assertEqual(convertir_temperatura("25.5", "c", "c"), Decimal("25.50"))
        self.assertEqual(convertir_temperatura(98.6, "F", "F"), Decimal("98.60"))
        self.assertEqual(convertir_temperatura(300, "K", "K"), Decimal("300.00"))

    def test_pipeline_validacion_cero_absoluto(self):
        with self.assertRaises(ValueError) as ctx:
            convertir_temperatura(-1, "K", "C")
        self.assertIn("cero absoluto", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            convertir_temperatura(-300, "C", "K")
        self.assertIn("cero absoluto", str(ctx.exception).lower())

        with self.assertRaises(ValueError) as ctx:
            convertir_temperatura(-500, "F", "K")
        self.assertIn("cero absoluto", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
