"""Módulo para validación y evaluación de fortaleza de contraseñas."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

COMMON_WEAK_PASSWORDS = {
    "123456", "12345678", "123456789", "password", "password123", "qwerty",
    "admin", "welcome", "abc123", "iloveyou", "monkey", "dragon", "master",
    "secret", "superman", "111111", "football", "letmein", "princess", "solo"
}

SPECIAL_CHARACTERS = r"!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~"


@dataclass
class RuleResult:
    """Resultado de una regla de validación individual."""
    name: str
    description: str
    passed: bool
    importance: str = "required"  # "required" | "recommended"


@dataclass
class ValidationResult:
    """Resultado completo de la validación de una contraseña."""
    is_valid: bool
    score: int  # 0 a 100
    strength_label: str  # Muy Débil, Débil, Media, Fuerte, Muy Fuerte
    entropy_bits: float
    rules: List[RuleResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class PasswordValidator:
    """Validador y evaluador de seguridad para contraseñas."""

    def __init__(
        self,
        min_length: int = 8,
        recommended_length: int = 12,
        max_length: int = 128,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digits: bool = True,
        require_special: bool = True,
        disallow_common: bool = True,
        disallow_whitespace: bool = True,
        custom_blacklist: Optional[set[str]] = None,
    ):
        self.min_length = min_length
        self.recommended_length = recommended_length
        self.max_length = max_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special = require_special
        self.disallow_common = disallow_common
        self.disallow_whitespace = disallow_whitespace
        self.blacklist = (COMMON_WEAK_PASSWORDS | (custom_blacklist or set()))

    def calculate_entropy(self, password: str) -> float:
        """Calcula la entropía de Shannon/espacio de búsqueda de la contraseña en bits."""
        if not password:
            return 0.0

        charset_size = 0
        if re.search(r"[a-z]", password):
            charset_size += 26
        if re.search(r"[A-Z]", password):
            charset_size += 26
        if re.search(r"[0-9]", password):
            charset_size += 10
        if re.search(f"[{re.escape(SPECIAL_CHARACTERS)}]", password):
            charset_size += len(SPECIAL_CHARACTERS)
        # Caracteres no contemplados previamente
        other_chars = len(set(re.sub(rf"[a-zA-Z0-9{re.escape(SPECIAL_CHARACTERS)}]", "", password)))
        charset_size += other_chars

        if charset_size == 0:
            return 0.0

        return len(password) * math.log2(charset_size)

    def validate(self, password: str) -> ValidationResult:
        """Evalúa las reglas y calcula el puntaje de la contraseña."""
        rules: List[RuleResult] = []
        errors: List[str] = []
        recommendations: List[str] = []

        # 1. Longitud mínima
        len_passed = len(password) >= self.min_length
        rules.append(
            RuleResult(
                name="Longitud mínima",
                description=f"Tener al menos {self.min_length} caracteres",
                passed=len_passed,
                importance="required",
            )
        )
        if not len_passed:
            errors.append(f"La contraseña debe tener al menos {self.min_length} caracteres.")

        # 2. Longitud máxima
        max_passed = len(password) <= self.max_length
        rules.append(
            RuleResult(
                name="Longitud máxima",
                description=f"No exceder {self.max_length} caracteres",
                passed=max_passed,
                importance="required",
            )
        )
        if not max_passed:
            errors.append(f"La contraseña supera el límite de {self.max_length} caracteres.")

        # 3. Mayúsculas
        has_upper = bool(re.search(r"[A-Z]", password))
        if self.require_uppercase:
            rules.append(
                RuleResult(
                    name="Mayúsculas",
                    description="Contener al menos una letra mayúscula (A-Z)",
                    passed=has_upper,
                    importance="required",
                )
            )
            if not has_upper:
                errors.append("Debe incluir al menos una letra mayúscula.")

        # 4. Minúsculas
        has_lower = bool(re.search(r"[a-z]", password))
        if self.require_lowercase:
            rules.append(
                RuleResult(
                    name="Minúsculas",
                    description="Contener al menos una letra minúscula (a-z)",
                    passed=has_lower,
                    importance="required",
                )
            )
            if not has_lower:
                errors.append("Debe incluir al menos una letra minúscula.")

        # 5. Dígitos
        has_digit = bool(re.search(r"[0-9]", password))
        if self.require_digits:
            rules.append(
                RuleResult(
                    name="Números",
                    description="Contener al menos un número (0-9)",
                    passed=has_digit,
                    importance="required",
                )
            )
            if not has_digit:
                errors.append("Debe incluir al menos un número.")

        # 6. Caracteres especiales
        has_special = bool(re.search(f"[{re.escape(SPECIAL_CHARACTERS)}]", password))
        if self.require_special:
            rules.append(
                RuleResult(
                    name="Caracteres especiales",
                    description=f"Contener al menos un símbolo especial ({SPECIAL_CHARACTERS[:10]}...)",
                    passed=has_special,
                    importance="required",
                )
            )
            if not has_special:
                errors.append("Debe incluir al menos un carácter especial.")

        # 7. Espacios en blanco
        has_whitespace = bool(re.search(r"\s", password))
        if self.disallow_whitespace:
            no_spaces = not has_whitespace
            rules.append(
                RuleResult(
                    name="Sin espacios",
                    description="No contener espacios en blanco",
                    passed=no_spaces,
                    importance="required",
                )
            )
            if not no_spaces:
                errors.append("La contraseña no debe contener espacios en blanco.")

        # 8. Contraseñas comunes
        is_common = password.lower() in self.blacklist
        if self.disallow_common:
            rules.append(
                RuleResult(
                    name="No común",
                    description="No ser una contraseña común o fácil de adivinar",
                    passed=not is_common,
                    importance="required",
                )
            )
            if is_common:
                errors.append("Esta contraseña es extremadamente común y fácil de vulnerar.")

        # Reglas recomendadas / Buenas prácticas
        rec_length = len(password) >= self.recommended_length
        rules.append(
            RuleResult(
                name="Longitud robusta (Recomendada)",
                description=f"Alcanzar {self.recommended_length} o más caracteres para alta seguridad",
                passed=rec_length,
                importance="recommended",
            )
        )
        if not rec_length and len_passed:
            recommendations.append(f"Considera usar {self.recommended_length} o más caracteres para mayor robustez.")

        # Repeticiones consecutivas (ej: aaa, 111)
        has_repeated = bool(re.search(r"(.)\1{2,}", password))
        rules.append(
            RuleResult(
                name="Sin repeticiones excesivas",
                description="Evitar 3 o más caracteres iguales seguidos",
                passed=not has_repeated,
                importance="recommended",
            )
        )
        if has_repeated:
            recommendations.append("Evita repetir el mismo carácter 3 o más veces seguidas.")

        # Secuencias obvias (ej: 123, abc)
        has_sequences = self._has_sequential_patterns(password)
        rules.append(
            RuleResult(
                name="Sin secuencias obvias",
                description="Evitar patrones secuenciales (1234, abcd, qwerty)",
                passed=not has_sequences,
                importance="recommended",
            )
        )
        if has_sequences:
            recommendations.append("Evita secuencias predecibles como números o letras consecutivas.")

        # Cálculo de puntaje y entropía
        entropy = self.calculate_entropy(password)
        score = self._compute_score(
            password=password,
            rules=rules,
            entropy=entropy,
            is_common=is_common,
        )

        strength_label = self._get_strength_label(score)
        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            score=score,
            strength_label=strength_label,
            entropy_bits=round(entropy, 2),
            rules=rules,
            errors=errors,
            recommendations=recommendations,
        )

    def _has_sequential_patterns(self, password: str) -> bool:
        """Verifica secuencias ascendentes/descendentes de 4 o más caracteres."""
        pwd_lower = password.lower()
        if len(pwd_lower) < 4:
            return False

        # Secuencias numéricas o alfabéticas
        for i in range(len(pwd_lower) - 3):
            sub = pwd_lower[i : i + 4]
            # ASCII consecutivo ascendente
            if all(ord(sub[j + 1]) - ord(sub[j]) == 1 for j in range(3)):
                return True
            # ASCII consecutivo descendente
            if all(ord(sub[j]) - ord(sub[j + 1]) == 1 for j in range(3)):
                return True

        # Patrones de teclado comunes
        keyboard_patterns = ["qwerty", "asdfgh", "zxcvbn", "123456", "654321"]
        for pattern in keyboard_patterns:
            if pattern in pwd_lower:
                return True

        return False

    def _compute_score(
        self, password: str, rules: List[RuleResult], entropy: float, is_common: bool
    ) -> int:
        """Calcula un puntaje de seguridad de 0 a 100."""
        if not password or is_common:
            return 0

        required_passed = sum(1 for r in rules if r.importance == "required" and r.passed)
        required_total = sum(1 for r in rules if r.importance == "required")
        recommended_passed = sum(1 for r in rules if r.importance == "recommended" and r.passed)
        recommended_total = sum(1 for r in rules if r.importance == "recommended")

        # Proporción de reglas
        req_ratio = (required_passed / required_total) if required_total > 0 else 1.0
        rec_ratio = (recommended_passed / recommended_total) if recommended_total > 0 else 1.0

        # Puntos por entropía (máximo 40 puntos a partir de ~60 bits)
        entropy_points = min(40, int((entropy / 60.0) * 40))

        # Puntos por reglas requeridas (máximo 40 puntos)
        req_points = int(req_ratio * 40)

        # Puntos por recomendaciones y longitud adicional (máximo 20 puntos)
        rec_points = int(rec_ratio * 15)
        extra_len_points = min(5, max(0, len(password) - 12))

        total_score = min(100, entropy_points + req_points + rec_points + extra_len_points)

        # Si no pasa todas las requeridas, castigar el score
        if req_ratio < 1.0:
            total_score = min(total_score, int(req_ratio * 49))

        return max(0, total_score)

    @staticmethod
    def _get_strength_label(score: int) -> str:
        """Devuelve la etiqueta cualitativa de fuerza."""
        if score < 25:
            return "Muy Débil"
        if score < 50:
            return "Débil"
        if score < 75:
            return "Media"
        if score < 90:
            return "Fuerte"
        return "Muy Fuerte"


def validate_password(password: str) -> ValidationResult:
    """Función de conveniencia para validar contraseñas con configuración por defecto."""
    validator = PasswordValidator()
    return validator.validate(password)
