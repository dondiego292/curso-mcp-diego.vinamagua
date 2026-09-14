"""Pruebas unitarias para el validador de correos electrónicos."""

import unittest
from curso_mcp_diego_vinamagua.email_validator import EmailValidator, validate_email


class TestEmailValidator(unittest.TestCase):
    def setUp(self):
        self.validator = EmailValidator()

    def test_valid_emails(self):
        valid_samples = [
            "usuario@dominio.com",
            "diego.vinamagua@institucion.edu.ec",
            "dev+test123@sub.dominio.org",
            "primer.apellido-123@empresa.co",
        ]
        for email in valid_samples:
            with self.subTest(email=email):
                res = self.validator.validate(email)
                self.assertTrue(res.is_valid, f"Email '{email}' debería ser válido. Errores: {res.errors}")
                self.assertEqual(len(res.errors), 0)

    def test_missing_at_symbol(self):
        res = self.validator.validate("usuariodominio.com")
        self.assertFalse(res.is_valid)
        self.assertTrue(any("falta" in err.lower() or "@" in err for err in res.errors))

    def test_multiple_at_symbols(self):
        res = self.validator.validate("user@@dominio.com")
        self.assertFalse(res.is_valid)

    def test_spaces_in_email(self):
        res = self.validator.validate("user name@dominio.com")
        self.assertFalse(res.is_valid)
        self.assertTrue(any("espacios" in err.lower() for err in res.errors))

    def test_invalid_domain_tld(self):
        res = self.validator.validate("usuario@dominio")
        self.assertFalse(res.is_valid)

    def test_consecutive_dots_in_local(self):
        res = self.validator.validate("user..name@dominio.com")
        self.assertFalse(res.is_valid)

    def test_disposable_domain(self):
        res = self.validator.validate("persona@mailinator.com")
        self.assertFalse(res.is_valid)
        self.assertTrue(res.is_disposable)
        self.assertTrue(any("temporal" in err.lower() or "desechable" in err.lower() for err in res.errors))

    def test_domain_typo_suggestion(self):
        res = self.validator.validate("persona@gmial.com")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.suggested_domain, "gmail.com")
        self.assertTrue(any("gmail.com" in w for w in res.warnings))

    def test_convenience_function(self):
        res = validate_email("contacto@empresa.com")
        self.assertTrue(res.is_valid)
        self.assertEqual(res.domain, "empresa.com")


if __name__ == "__main__":
    unittest.main()
