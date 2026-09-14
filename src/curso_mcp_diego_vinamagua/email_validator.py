"""Módulo para validación y verificación de formato de correos electrónicos."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Set, Dict

# Dominios temporales/desechables conocidos
DISPOSABLE_DOMAINS: Set[str] = {
    "mailinator.com", "tempmail.com", "10minutemail.com", "guerrillamail.com",
    "trashmail.com", "yopmail.com", "sharklasers.com", "dispostable.com",
    "getairmail.com", "mytemp.email"
}

# Correcciones comunes de errores tipográficos en dominios populares
COMMON_DOMAIN_TYPOS: Dict[str, str] = {
    "gmial.com": "gmail.com",
    "gamil.com": "gmail.com",
    "gmaill.com": "gmail.com",
    "gnail.com": "gmail.com",
    "hotmial.com": "hotmail.com",
    "hotmai.com": "hotmail.com",
    "hotmali.com": "hotmail.com",
    "outlok.com": "outlook.com",
    "outloo.com": "outlook.com",
    "yaho.com": "yahoo.com",
    "yahooo.com": "yahoo.com",
    "iclou.com": "icloud.com",
}


@dataclass
class EmailRuleResult:
    """Resultado de una comprobación individual del email."""
    name: str
    description: str
    passed: bool
    importance: str = "required"  # "required" | "warning"


@dataclass
class EmailValidationResult:
    """Resultado completo de la validación de un correo electrónico."""
    is_valid: bool
    email: str
    normalized_email: Optional[str] = None
    local_part: Optional[str] = None
    domain: Optional[str] = None
    is_disposable: bool = False
    suggested_domain: Optional[str] = None
    rules: List[EmailRuleResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class EmailValidator:
    """Validador y normalizador de direcciones de correo electrónico."""

    # Regex estándar conforme a especificaciones generales de RFC 5322
    EMAIL_REGEX = re.compile(
        r"^(?P<local>[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+)"
        r"@"
        r"(?P<domain>[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+)$"
    )

    def __init__(
        self,
        allow_disposable: bool = False,
        check_domain_typos: bool = True,
        custom_disposable_domains: Optional[Set[str]] = None,
    ):
        self.allow_disposable = allow_disposable
        self.check_domain_typos = check_domain_typos
        self.disposable_domains = DISPOSABLE_DOMAINS | (custom_disposable_domains or set())

    def validate(self, email: str) -> EmailValidationResult:
        """Valida minuciosamente una dirección de correo electrónico."""
        raw_email = email.strip() if email else ""
        rules: List[EmailRuleResult] = []
        errors: List[str] = []
        warnings: List[str] = []

        # 1. No vacío
        is_not_empty = bool(raw_email)
        rules.append(
            EmailRuleResult(
                name="Presencia de texto",
                description="El correo no debe estar vacío",
                passed=is_not_empty,
                importance="required",
            )
        )
        if not is_not_empty:
            errors.append("El correo no puede estar vacío.")
            return EmailValidationResult(
                is_valid=False,
                email=email,
                rules=rules,
                errors=errors,
            )

        # 2. Sin espacios internos
        has_no_spaces = " " not in raw_email
        rules.append(
            EmailRuleResult(
                name="Sin espacios",
                description="No debe contener espacios en blanco",
                passed=has_no_spaces,
                importance="required",
            )
        )
        if not has_no_spaces:
            errors.append("El correo no debe contener espacios.")

        # 3. Límite de longitud total (RFC 5321: máx 254 caracteres)
        length_ok = len(raw_email) <= 254
        rules.append(
            EmailRuleResult(
                name="Longitud total",
                description="Longitud máxima de 254 caracteres",
                passed=length_ok,
                importance="required",
            )
        )
        if not length_ok:
            errors.append(f"El correo excede el límite máximo de 254 caracteres (tiene {len(raw_email)}).")

        # 4. Estructura con un único '@'
        at_count = raw_email.count("@")
        has_single_at = at_count == 1
        rules.append(
            EmailRuleResult(
                name="Símbolo arroba (@)",
                description="Debe contener exactamente un símbolo '@'",
                passed=has_single_at,
                importance="required",
            )
        )
        if at_count == 0:
            errors.append("Falta el símbolo '@' en el correo.")
        elif at_count > 1:
            errors.append("El correo no puede contener más de un símbolo '@'.")

        local_part: Optional[str] = None
        domain_part: Optional[str] = None
        suggested_domain: Optional[str] = None
        is_disposable: bool = False

        if has_single_at:
            local_part, domain_part = raw_email.split("@", 1)

            # 5. Validación de parte local
            local_length_ok = 1 <= len(local_part) <= 64
            rules.append(
                EmailRuleResult(
                    name="Longitud parte local (usuario)",
                    description="El nombre de usuario debe tener entre 1 y 64 caracteres",
                    passed=local_length_ok,
                    importance="required",
                )
            )
            if not local_length_ok:
                errors.append(f"La parte local del usuario debe tener entre 1 y 64 caracteres (tiene {len(local_part)}).")

            # Puntos consecutivos o inicio/fin con punto en local part
            no_consecutive_dots_local = ".." not in local_part and not local_part.startswith(".") and not local_part.endswith(".")
            rules.append(
                EmailRuleResult(
                    name="Puntos válidos en usuario",
                    description="No debe empezar, terminar ni tener puntos consecutivos en la parte local",
                    passed=no_consecutive_dots_local,
                    importance="required",
                )
            )
            if not no_consecutive_dots_local:
                errors.append("La parte del usuario no puede empezar, terminar ni contener puntos consecutivos ('..').")

            # 6. Validación de dominio
            domain_has_dot = "." in domain_part and not domain_part.startswith(".") and not domain_part.endswith(".")
            rules.append(
                EmailRuleResult(
                    name="Estructura de dominio",
                    description="El dominio debe contener al menos un punto y una extensión (TLD)",
                    passed=domain_has_dot,
                    importance="required",
                )
            )
            if not domain_has_dot:
                errors.append("El dominio debe contener al menos un punto y una extensión válida (ej. .com, .es).")

            # Extensión TLD mínima de 2 letras
            domain_parts = domain_part.split(".")
            tld = domain_parts[-1] if domain_parts else ""
            tld_valid = len(tld) >= 2 and tld.isalpha()
            rules.append(
                EmailRuleResult(
                    name="Extensión TLD válida",
                    description="La extensión final del dominio (TLD) debe tener al menos 2 caracteres alfabéticos",
                    passed=tld_valid,
                    importance="required",
                )
            )
            if not tld_valid:
                errors.append(f"La extensión del dominio '{tld}' no es válida.")

            # 7. Coincidencia de sintaxis general con regex RFC
            match = self.EMAIL_REGEX.match(raw_email)
            syntax_ok = match is not None
            rules.append(
                EmailRuleResult(
                    name="Sintaxis general RFC",
                    description="Formato y caracteres permitidos según RFC 5322",
                    passed=syntax_ok,
                    importance="required",
                )
            )
            if not syntax_ok and not errors:
                errors.append("El correo contiene caracteres no permitidos o formato inválido.")

            # 8. Verificación de dominio desechable / temporal
            domain_lower = domain_part.lower()
            is_disposable = domain_lower in self.disposable_domains
            if is_disposable:
                rules.append(
                    EmailRuleResult(
                        name="Dominio permanente",
                        description="El correo no debe provenir de un servicio temporal/desechable",
                        passed=False,
                        importance="required" if not self.allow_disposable else "warning",
                    )
                )
                if not self.allow_disposable:
                    errors.append(f"El dominio '{domain_lower}' es un servicio de correo temporal/desechable no permitido.")
                else:
                    warnings.append(f"Advertencia: '{domain_lower}' es un servicio de correo temporal.")
            else:
                rules.append(
                    EmailRuleResult(
                        name="Dominio permanente",
                        description="No es un correo temporal desechable",
                        passed=True,
                        importance="required" if not self.allow_disposable else "warning",
                    )
                )

            # 9. Detección de posibles errores tipográficos en dominios
            if self.check_domain_typos and domain_lower in COMMON_DOMAIN_TYPOS:
                suggested_domain = COMMON_DOMAIN_TYPOS[domain_lower]
                suggested_email = f"{local_part}@{suggested_domain}"
                warnings.append(f"¿Quisiste escribir '{suggested_email}' en vez de '{raw_email}'?")

        is_valid = len(errors) == 0
        normalized_email = f"{local_part}@{domain_part.lower()}" if (local_part and domain_part) else None

        return EmailValidationResult(
            is_valid=is_valid,
            email=raw_email,
            normalized_email=normalized_email,
            local_part=local_part,
            domain=domain_part.lower() if domain_part else None,
            is_disposable=is_disposable,
            suggested_domain=suggested_domain,
            rules=rules,
            errors=errors,
            warnings=warnings,
        )


def validate_email(email: str) -> EmailValidationResult:
    """Función de conveniencia para validar un correo electrónico."""
    validator = EmailValidator()
    return validator.validate(email)
