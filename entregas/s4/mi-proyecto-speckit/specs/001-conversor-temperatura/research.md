# Research: Conversor de Temperatura

**Feature**: `001-conversor-temperatura`  
**Date**: 2026-09-16  
**Status**: Completed  

---

## 1. Estrategia de Precisión Aritmética y Redondeo

### Decision
Utilizar el módulo `decimal` de la biblioteca estándar de Python (`from decimal import Decimal, ROUND_HALF_UP`) para todos los cálculos y redondeos a 2 decimales.

### Rationale
- Los números de punto flotante estándar de Python (`float`) introducen imprecisiones binarias inherentes (por ejemplo, representaciones infinitas en base 2 de números decimales finitos).
- La función nativa `round()` de Python 3 utiliza redondeo bancario ("round half to even"), lo que produciría discrepancias con los criterios de aceptación esperados en la especificación (donde 0.005 debe redondear a 0.01).
- `Decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)` proporciona un comportamiento determinista, exacto y conforme con la norma ISO/IEC y los estándares de conversión física.

### Alternatives considered
- **Uso de `float` nativo con `round()`**: Rechazado debido a comportamientos de redondeo no intuitivos en valores frontera y errores de precisión residual.
- **Bibliotecas externas (ej. `numpy`)**: Rechazado para mantener el proyecto con cero dependencias externas y máxima portabilidad.

---

## 2. Validación de Entradas y Límites Físicos (Cero Absoluto)

### Decision
Implementar una capa de validación temprana en dos fases antes de cualquier operación matemática:
1. **Validación Sintáctica**: Comprobar que la entrada no sea nula (`None`), no esté vacía ni compuesta únicamente por espacios en blanco, y que pueda ser parseada como número.
2. **Validación Semántica y Física**: Normalizar las unidades (admitiendo mayúsculas y minúsculas: 'C', 'F', 'K') y verificar que la temperatura de entrada no esté por debajo del cero absoluto:
   - Kelvin: $K \ge 0$
   - Celsius: $C \ge -273.15$
   - Fahrenheit: $F \ge -459.67$

Si alguna validación falla, se genera una excepción descriptiva `ValueError` con un mensaje claro en español.

### Rationale
- Cumple directamente con los criterios de aceptación y casos borde establecidos en `spec.md` (FR-006, FR-007, FR-008).
- Evita propagación de estados inválidos o cálculos termodinámicamente imposibles.

### Alternatives considered
- **Permitir que Python lance excepciones nativas sin capturar**: Rechazado porque mensajes como `TypeError: unsupported operand type` o `ValueError: could not convert string to float` no son amigables ni específicos para el usuario.
- **Retornar valores centinela (ej. `None` o `-1`)**: Rechazado porque los valores centinela complican la API y pueden ser interpretados erróneamente como temperaturas reales.

---

## 3. Arquitectura de Interfaces (Librería + CLI)

### Decision
Estructurar el conversor con una doble interfaz desacoplada:
1. **Módulo / Librería Python**: Funciones puras e independientes (`celsius_a_fahrenheit`, `fahrenheit_a_celsius`, `celsius_a_kelvin`, `kelvin_a_celsius`, `fahrenheit_a_kelvin`, `kelvin_a_fahrenheit`, y la función general `convertir_temperatura(valor, origen, destino)`).
2. **Interfaz de Línea de Comandos (CLI)**: Utilizar `argparse` de la biblioteca estándar para permitir ejecución directa desde la terminal (`python -m conversor_temperatura <valor> <origen> <destino>`), enviando resultados a `stdout` con código de salida 0 y errores a `stderr` con código de salida 1.

### Rationale
- Garantiza reutilización directa en cualquier script o aplicación en Python.
- Facilita pruebas automatizadas rápidas tanto a nivel unitario como por scripts de integración en terminal.

### Alternatives considered
- **Solo función general sin funciones individuales**: Rechazado porque las funciones específicas proporcionan mayor claridad semántica y simplicidad cuando se conoce la conversión de antemano.
- **Solo script CLI**: Rechazado porque impide la importación como librería en otros módulos.
