"""Módulo para validación individual y por lotes (batch) de usuarios con email y contraseña."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Any, Sequence, Optional, Union

from .email_validator import EmailValidator, EmailValidationResult, validate_email
from .password_validator import PasswordValidator, ValidationResult, validate_password


@dataclass
class UserData:
    """Representa los datos de un usuario."""
    username: str
    email: str
    password: str
    id: Optional[Union[str, int]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> UserData:
        """Crea una instancia desde un diccionario."""
        return cls(
            username=str(data.get("username", "") or data.get("usuario", "") or data.get("nombre", "")),
            email=str(data.get("email", "") or data.get("correo", "")),
            password=str(data.get("password", "") or data.get("contrasena", "") or data.get("clave", "")),
            id=data.get("id"),
        )


@dataclass
class UserValidationResult:
    """Resultado de la validación completa de un usuario."""
    user: UserData
    is_valid: bool
    email_result: EmailValidationResult
    password_result: ValidationResult
    custom_errors: List[str] = field(default_factory=list)
    custom_warnings: List[str] = field(default_factory=list)

    @property
    def all_errors(self) -> List[str]:
        """Consolida todos los errores de email, contraseña y reglas cruzadas."""
        errors: List[str] = []
        if not self.email_result.is_valid:
            errors.extend([f"[Email] {e}" for e in self.email_result.errors])
        if not self.password_result.is_valid:
            errors.extend([f"[Contraseña] {e}" for e in self.password_result.errors])
        errors.extend(self.custom_errors)
        return errors


@dataclass
class BatchValidationReport:
    """Reporte consolidado de la validación de una lista de usuarios."""
    results: List[UserValidationResult]
    total_users: int
    valid_count: int
    invalid_count: int
    duplicate_emails: List[str] = field(default_factory=list)
    duplicate_usernames: List[str] = field(default_factory=list)

    @property
    def all_valid(self) -> bool:
        """Indica si todos los usuarios del lote son válidos y sin duplicados."""
        return self.invalid_count == 0 and len(self.duplicate_emails) == 0 and len(self.duplicate_usernames) == 0

    @property
    def success_rate(self) -> float:
        """Porcentaje de usuarios válidos."""
        if self.total_users == 0:
            return 0.0
        return round((self.valid_count / self.total_users) * 100, 2)


class UserValidator:
    """Validador de usuarios individuales y colecciones de usuarios."""

    def __init__(
        self,
        email_validator: Optional[EmailValidator] = None,
        password_validator: Optional[PasswordValidator] = None,
        disallow_password_contains_user_info: bool = True,
    ):
        self.email_validator = email_validator or EmailValidator()
        self.password_validator = password_validator or PasswordValidator()
        self.disallow_password_contains_user_info = disallow_password_contains_user_info

    def validate_user(self, user_input: Union[UserData, Dict[str, Any]]) -> UserValidationResult:
        """Valida a un usuario individual (nombre, email, contraseña y reglas cruzadas)."""
        if isinstance(user_input, dict):
            user = UserData.from_dict(user_input)
        else:
            user = user_input

        email_res = self.email_validator.validate(user.email)
        pwd_res = self.password_validator.validate(user.password)

        custom_errors: List[str] = []
        custom_warnings: List[str] = []

        # 1. Validación de nombre de usuario
        if not user.username or not user.username.strip():
            custom_errors.append("El nombre de usuario no puede estar vacío.")
        elif len(user.username.strip()) < 3:
            custom_errors.append("El nombre de usuario debe tener al menos 3 caracteres.")

        # 2. Reglas de seguridad cruzadas (la contraseña no debe contener el usuario ni partes del email)
        if self.disallow_password_contains_user_info and user.password:
            pwd_lower = user.password.lower()
            
            # Comprobar nombre de usuario
            if user.username and len(user.username) >= 3 and user.username.lower() in pwd_lower:
                custom_errors.append("La contraseña no debe contener el nombre de usuario.")

            # Comprobar parte local del email
            if email_res.local_part and len(email_res.local_part) >= 3 and email_res.local_part.lower() in pwd_lower:
                custom_warnings.append("La contraseña contiene el nombre del correo electrónico (no recomendado).")

        is_valid = email_res.is_valid and pwd_res.is_valid and len(custom_errors) == 0

        return UserValidationResult(
            user=user,
            is_valid=is_valid,
            email_result=email_res,
            password_result=pwd_res,
            custom_errors=custom_errors,
            custom_warnings=custom_warnings,
        )

    def validate_users(self, users: Sequence[Union[UserData, Dict[str, Any]]]) -> BatchValidationReport:
        """Valida una lista de usuarios, verificando integridad individual y unicidad global."""
        results: List[UserValidationResult] = []
        parsed_users: List[UserData] = []

        for item in users:
            res = self.validate_user(item)
            results.append(res)
            parsed_users.append(res.user)

        # Análisis de duplicados globales en el lote
        emails = [u.email.strip().lower() for u in parsed_users if u.email]
        usernames = [u.username.strip().lower() for u in parsed_users if u.username]

        email_counts = Counter(emails)
        username_counts = Counter(usernames)

        duplicate_emails = [email for email, count in email_counts.items() if count > 1]
        duplicate_usernames = [uname for uname, count in username_counts.items() if count > 1]

        # Si hay emails o usernames duplicados, marcar advertencia/error en los resultados
        for res in results:
            clean_email = res.user.email.strip().lower()
            clean_username = res.user.username.strip().lower()

            if clean_email in duplicate_emails:
                res.custom_errors.append(f"Email duplicado en el lote ({res.user.email}).")
                res.is_valid = False

            if clean_username in duplicate_usernames:
                res.custom_errors.append(f"Nombre de usuario duplicado en el lote ({res.user.username}).")
                res.is_valid = False

        valid_count = sum(1 for r in results if r.is_valid)
        invalid_count = len(results) - valid_count

        return BatchValidationReport(
            results=results,
            total_users=len(results),
            valid_count=valid_count,
            invalid_count=invalid_count,
            duplicate_emails=duplicate_emails,
            duplicate_usernames=duplicate_usernames,
        )


def validate_user(user: Union[UserData, Dict[str, Any]]) -> UserValidationResult:
    """Función de conveniencia para validar un usuario."""
    validator = UserValidator()
    return validator.validate_user(user)


def validate_users(users: Sequence[Union[UserData, Dict[str, Any]]]) -> BatchValidationReport:
    """Función de conveniencia para validar un lote de usuarios."""
    validator = UserValidator()
    return validator.validate_users(users)
