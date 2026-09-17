"""
Pruebas end-to-end (E2E) para el conversor de temperatura.
Ejecuta el programa completo como subproceso independiente mediante subprocess,
verificando stdout, stderr y códigos de retorno del sistema operativo.
"""

import subprocess
import sys
import unittest
from pathlib import Path

# Localizar la ruta exacta al script ejecutable y a la raíz
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT_PATH = PROJECT_ROOT / "conversor_temperatura.py"


class TestConversorE2E(unittest.TestCase):
    """Pruebas end-to-end del conversor ejecutado como proceso CLI."""

    def test_cli_exito(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "100", "C", "F"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "212.00")

    def test_cli_reflexiva(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "25.5", "C", "C"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "25.50")

    def test_cli_error_cero_absoluto(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "-1", "K", "C"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error:", result.stderr)
        self.assertIn("cero absoluto", result.stderr.lower())

    def test_cli_error_no_numerico(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "abc", "C", "F"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Error:", result.stderr)
        self.assertIn("número válido", result.stderr.lower())


if __name__ == "__main__":
    unittest.main()
