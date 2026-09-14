"""Pruebas unitarias para el validador de contraseñas."""

import unittest
from curso_mcp_diego_vinamagua.password_validator import PasswordValidator, validate_password


class TestPasswordValidator(unittest.TestCase):
    def setUp(self):
        self.validator = PasswordValidator()

    def test_empty_password(self):
        result = self.validator.validate("")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.score, 0)
        self.assertEqual(result.strength_label, "Muy Débil")
        self.assertTrue(len(result.errors) > 0)

    def test_short_password(self):
        result = self.validator.validate("Ab1!")
        self.assertFalse(result.is_valid)
        self.assertTrue(any("longitud" in err.lower() or "caracteres" in err.lower() for err in result.errors))

    def test_missing_uppercase(self):
        result = self.validator.validate("password123!")
        self.assertFalse(result.is_valid)
        self.assertTrue(any("mayúscula" in err.lower() for err in result.errors))

    def test_missing_lowercase(self):
        result = self.validator.validate("PASSWORD123!")
        self.assertFalse(result.is_valid)
        self.assertTrue(any("minúscula" in err.lower() for err in result.errors))

    def test_missing_digit(self):
        result = self.validator.validate("PasswordSecure!")
        self.assertFalse(result.is_valid)
        self.assertTrue(any("número" in err.lower() for err in result.errors))

    def test_missing_special_char(self):
        result = self.validator.validate("PasswordSecure123")
        self.assertFalse(result.is_valid)
        self.assertTrue(any("especial" in err.lower() for err in result.errors))

    def test_common_weak_password(self):
        result = self.validator.validate("password123")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.score, 0)

    def test_with_whitespace(self):
        result = self.validator.validate("Pass word 123!@#")
        self.assertFalse(result.is_valid)
        self.assertTrue(any("espacios" in err.lower() for err in result.errors))

    def test_valid_strong_password(self):
        result = self.validator.validate("K9#mQ8$zL2!wX5@v")
        self.assertTrue(result.is_valid)
        self.assertIn(result.strength_label, ["Fuerte", "Muy Fuerte"])
        self.assertGreater(result.score, 75)
        self.assertEqual(len(result.errors), 0)

    def test_convenience_function(self):
        result = validate_password("SuperSecret#2026!")
        self.assertTrue(result.is_valid)
        self.assertGreater(result.score, 70)


if __name__ == "__main__":
    unittest.main()
