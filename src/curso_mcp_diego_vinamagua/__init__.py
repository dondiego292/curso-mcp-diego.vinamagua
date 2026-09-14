"""Curso MCP - Validador de Contraseñas, Correos y Usuarios."""

from .password_validator import (
    PasswordValidator,
    ValidationResult,
    RuleResult,
    validate_password,
)
from .email_validator import (
    EmailValidator,
    EmailValidationResult,
    EmailRuleResult,
    validate_email,
)
from .user_validator import (
    UserData,
    UserValidationResult,
    BatchValidationReport,
    UserValidator,
    validate_user,
    validate_users,
)


def main() -> None:
    from .cli import main as cli_main
    cli_main()


__all__ = [
    "PasswordValidator",
    "ValidationResult",
    "RuleResult",
    "validate_password",
    "EmailValidator",
    "EmailValidationResult",
    "EmailRuleResult",
    "validate_email",
    "UserData",
    "UserValidationResult",
    "BatchValidationReport",
    "UserValidator",
    "validate_user",
    "validate_users",
    "main",
]
