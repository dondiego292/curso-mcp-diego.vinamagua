# Tasks: Conversor de Temperatura

**Feature**: `001-conversor-temperatura` | **Branch**: `001-conversor-temperatura`  
**Input**: `/specs/001-conversor-temperatura/plan.md`, `/specs/001-conversor-temperatura/spec.md`  

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Inicialización del proyecto y estructura base

- [X] T001 Inicializar la estructura del proyecto y configuración base de Python en `conversor_temperatura.py`
- [X] T002 [P] Crear el archivo base para la suite de pruebas unitarias en `test_conversor_temperatura.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Infraestructura central que DEBE completarse antes de implementar las historias de usuario

- [X] T003 Definir las constantes térmicas de referencia, factores de conversión y precisión `Decimal` (`ROUND_HALF_UP`) en `conversor_temperatura.py`
- [X] T004 [P] Implementar la función de normalización y validación de tipos y formatos de entrada en `conversor_temperatura.py`
- [X] T005 Implementar la validación física del cero absoluto ($K \ge 0$, $C \ge -273.15$, $F \ge -459.67$) con excepciones descriptivas `ValueError` en `conversor_temperatura.py`

**Checkpoint**: Base de validación y precisión establecida. El trabajo en historias de usuario puede comenzar.

---

## Phase 3: User Story 1 - Conversión estándar entre escalas térmicas (Priority: P1) 🎯 MVP

**Goal**: Permitir conversión bidireccional exacta entre Celsius, Fahrenheit y Kelvin cumpliendo con las fórmulas físicas estándar.  
**Independent Test**: `python3 -m unittest test_conversor_temperatura.TestConversionesEstandar -v`

### Tests for User Story 1 (TDD)
- [X] T006 [P] [US1] Escribir pruebas unitarias para conversiones bidireccionales Celsius y Fahrenheit en `test_conversor_temperatura.py`
- [X] T007 [P] [US1] Escribir pruebas unitarias para conversiones bidireccionales Celsius y Kelvin en `test_conversor_temperatura.py`
- [X] T008 [P] [US1] Escribir pruebas unitarias para conversiones bidireccionales Fahrenheit y Kelvin en `test_conversor_temperatura.py`

### Implementation for User Story 1
- [X] T009 [US1] Implementar funciones de conversión matemática entre Celsius y Fahrenheit en `conversor_temperatura.py`
- [X] T010 [US1] Implementar funciones de conversión matemática entre Celsius y Kelvin en `conversor_temperatura.py`
- [X] T011 [US1] Implementar funciones de conversión matemática entre Fahrenheit y Kelvin en `conversor_temperatura.py`
- [X] T012 [US1] Implementar la función unificadora `convertir_temperatura` en `conversor_temperatura.py`

**Checkpoint**: User Story 1 completa y comprobada de manera autónoma como MVP funcional.

---

## Phase 4: User Story 2 - Validación de límites físicos e integridad de entradas (Priority: P2)

**Goal**: Rechazar temperaturas inferiores al cero absoluto, entradas vacías y entradas no numéricas con mensajes de error descriptivos.  
**Independent Test**: `python3 -m unittest test_conversor_temperatura.TestValidacionesYCasosBorde -v`

### Tests for User Story 2 (TDD)
- [X] T013 [P] [US2] Escribir pruebas unitarias para rechazo de temperaturas inferiores a cero absoluto Kelvin en `test_conversor_temperatura.py`
- [X] T014 [P] [US2] Escribir pruebas unitarias para rechazo de entradas vacías o valores nulos en `test_conversor_temperatura.py`
- [X] T015 [P] [US2] Escribir pruebas unitarias para rechazo de entradas no numéricas en `test_conversor_temperatura.py`

### Implementation for User Story 2
- [X] T016 [US2] Integrar validación estricta de cero absoluto y sanitización de espacios en `convertir_temperatura` dentro de `conversor_temperatura.py`
- [X] T017 [US2] Estandarizar los mensajes de error de excepción `ValueError` conforme a `data-model.md` en `conversor_temperatura.py`

**Checkpoint**: User Stories 1 y 2 completamente integradas y validadas contra entradas anómalas.

---

## Phase 5: User Story 3 - Conversión reflexiva y formato de precisión (Priority: P3)

**Goal**: Garantizar que conversiones entre la misma unidad preserven el valor original y que todo resultado se cuantice a 2 decimales (`ROUND_HALF_UP`).  
**Independent Test**: `python3 -m unittest test_conversor_temperatura.TestPrecisionYReflexividad -v`

### Tests for User Story 3 (TDD)
- [X] T018 [P] [US3] Escribir pruebas unitarias para conversiones reflexivas de misma unidad origen y destino en `test_conversor_temperatura.py`
- [X] T019 [P] [US3] Escribir pruebas unitarias para redondeo simétrico a 2 decimales en `test_conversor_temperatura.py`

### Implementation for User Story 3
- [X] T020 [US3] Implementar el atajo de conversión reflexiva y cuantización fija a dos decimales en `conversor_temperatura.py`

**Checkpoint**: Todas las historias de usuario de cálculo y validación operativas.

---

## Phase 6: CLI Interface & Integration

**Purpose**: Proveer interfaz de línea de comandos (`argparse`) con códigos de salida POSIX (0 en éxito, 1 en error)

- [X] T021 [P] Escribir pruebas unitarias para la interfaz CLI y captura de códigos de retorno en `test_conversor_temperatura.py`
- [X] T022 Implementar el punto de entrada CLI con `argparse` y manejo de `sys.exit` en `conversor_temperatura.py`

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Mejoras finales, aseguramiento de calidad y validación de extremo a extremo

- [X] T023 [P] Ejecutar la suite completa de pruebas unitarias en `test_conversor_temperatura.py`
- [X] T024 Ejecutar los escenarios de validación de `quickstart.md` en `conversor_temperatura.py`
- [X] T025 [P] Agregar docstrings descriptivos y anotaciones de tipo completas en `conversor_temperatura.py`

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)**: Sin dependencias, inicio inmediato.
- **Phase 2 (Foundational)**: Requiere Phase 1 completada. Bloquea las historias de usuario.
- **Phase 3 (User Story 1 - P1)**: Requiere Phase 2 completada. Representa el MVP.
- **Phase 4 (User Story 2 - P2)**: Requiere Phase 3 completada para ampliar la robustez de validación.
- **Phase 5 (User Story 3 - P3)**: Requiere Phase 3 y Phase 4 completadas.
- **Phase 6 (CLI Interface)**: Requiere que las funciones centrales de conversión estén listas (Phase 3 a 5).
- **Phase 7 (Polish)**: Requiere que todas las fases anteriores estén completadas.

### Within Each User Story
- Pruebas unitarias escritas primero (TDD).
- Verificación de que las pruebas fallen antes de codificar la lógica.
- Implementación de funciones nucleares hasta superar las pruebas.

### Parallel Opportunities
- T001 y T002 pueden prepararse en paralelo.
- T006, T007 y T008 (pruebas de US1) pueden redactarse en paralelo.
- T013, T014 y T015 (pruebas de US2) pueden redactarse en paralelo.
- T018 y T019 (pruebas de US3) pueden redactarse en paralelo.
- T023 y T025 (polish final) pueden ejecutarse en paralelo.

---

## Parallel Example: User Story 1

```bash
# Escribir en paralelo los bloques de pruebas para US1:
Task T006: "Escribir pruebas unitarias para conversiones bidireccionales Celsius y Fahrenheit en test_conversor_temperatura.py"
Task T007: "Escribir pruebas unitarias para conversiones bidireccionales Celsius y Kelvin en test_conversor_temperatura.py"
Task T008: "Escribir pruebas unitarias para conversiones bidireccionales Fahrenheit y Kelvin en test_conversor_temperatura.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Completar Setup (T001, T002).
2. Completar Foundational (T003, T004, T005).
3. Completar User Story 1 (T006 a T012).
4. Validar User Story 1 de forma independiente: `python3 -m unittest test_conversor_temperatura.py -v`.
5. ¡MVP listo y funcional!

### Incremental Delivery
1. Base lista -> Conversión funcional básica (US1).
2. Añadir protecciones y límites físicos (US2).
3. Añadir optimización reflexiva y cuantización (US3).
4. Exponer CLI y validar con `quickstart.md` (CLI + Polish).
