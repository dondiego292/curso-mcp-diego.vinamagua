"""Pruebas unitarias para el validador de usuarios y lotes."""

import unittest
from curso_mcp_diego_vinamagua.user_validator import (
    UserData,
    UserValidator,
    validate_user,
    validate_users,
)


class TestUserValidator(unittest.TestCase):
    def setUp(self):
        self.validator = UserValidator()

    def test_valid_user(self):
        user = UserData(
            username="diego_dev",
            email="diego.vinamagua@gmail.com",
            password="Secure#Password2026!",
        )
        res = self.validator.validate_user(user)
        self.assertTrue(res.is_valid)
        self.assertEqual(len(res.custom_errors), 0)

    def test_password_contains_username(self):
        user = UserData(
            username="diego_dev",
            email="diego@empresa.com",
            password="diego_dev#Password2026!",
        )
        res = self.validator.validate_user(user)
        self.assertFalse(res.is_valid)
        self.assertTrue(any("nombre de usuario" in e.lower() for e in res.custom_errors))

    def test_invalid_email_and_password(self):
        user = {"username": "admin", "email": "bademail", "password": "123"}
        res = self.validator.validate_user(user)
        self.assertFalse(res.is_valid)
        self.assertFalse(res.email_result.is_valid)
        self.assertFalse(res.password_result.is_valid)

    def test_batch_validation_with_duplicates(self):
        users = [
            {"username": "user1", "email": "user1@gmail.com", "password": "PassWord#123!"},
            {"username": "user1", "email": "user2@gmail.com", "password": "PassWord#456!"},  # username duplicado
            {"username": "user3", "email": "user1@gmail.com", "password": "PassWord#789!"},  # email duplicado
        ]
        report = validate_users(users)
        self.assertFalse(report.all_valid)
        self.assertEqual(report.total_users, 3)
        self.assertIn("user1@gmail.com", report.duplicate_emails)
        self.assertIn("user1", report.duplicate_usernames)

    def test_batch_validation_all_valid(self):
        users = [
            {"username": "user_alpha", "email": "alpha@empresa.com", "password": "K9#mQ8$zL2!wX5@v"},
            {"username": "user_beta", "email": "beta@empresa.com", "password": "M7#wX9$pL3!kR2@z"},
        ]
        report = validate_users(users)
        self.assertTrue(report.all_valid)
        self.assertEqual(report.valid_count, 2)
        self.assertEqual(report.invalid_count, 0)
        self.assertEqual(report.success_rate, 100.0)


if __name__ == "__main__":
    unittest.main()
