# Feature Specification: Conversor de Temperatura

**Feature Branch**: `001-conversor-temperatura`

**Created**: 2026-09-16

**Status**: Draft

**Input**: User description: "Conversor de temperatura entre Celsius, Fahrenheit y Kelvin basado en spec_manual.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conversión estándar entre escalas térmicas (Priority: P1)

Como usuario que trabaja con diferentes sistemas de medición térmica, quiero convertir valores de temperatura de manera bidireccional entre Celsius, Fahrenheit y Kelvin para obtener lecturas equivalentes y consistentes en mis actividades.

**Why this priority**: Es la funcionalidad nuclear del sistema. Sin la capacidad de convertir entre las tres escalas principales, el producto no ofrece valor operativo.

**Independent Test**: Puede probarse de forma autónoma solicitando conversiones entre cualquier par de unidades admitidas (Celsius a Fahrenheit, Celsius a Kelvin, Fahrenheit a Kelvin y sus inversas) y verificando que los resultados numéricos correspondan a las equivalencias físicas estándar.

**Acceptance Scenarios**:

1. **Given** una temperatura en grados Celsius (ej. 100 °C), **When** se solicita la conversión a grados Fahrenheit, **Then** el sistema entrega 212.00 °F.
2. **Given** una temperatura en grados Fahrenheit (ej. 32 °F), **When** se solicita la conversión a grados Celsius, **Then** el sistema entrega 0.00 °C.
3. **Given** una temperatura en grados Celsius (ej. 0 °C), **When** se solicita la conversión a Kelvin, **Then** el sistema entrega 273.15 K.
4. **Given** una temperatura en Kelvin (ej. 273.15 K), **When** se solicita la conversión a grados Celsius, **Then** el sistema entrega 0.00 °C.
5. **Given** una temperatura en grados Fahrenheit (ej. 212 °F), **When** se solicita la conversión a Kelvin, **Then** el sistema entrega 373.15 K.
6. **Given** una temperatura en Kelvin (ej. 373.15 K), **When** se solicita la conversión a grados Fahrenheit, **Then** el sistema entrega 212.00 °F.

---

### User Story 2 - Validación de límites físicos e integridad de entradas (Priority: P2)

Como usuario o sistema consumidor, quiero que el conversor verifique que los datos ingresados sean válidos y respeten los límites físicos de la termodinámica, para evitar cálculos erróneos o estados inconsistentes.

**Why this priority**: La integridad de los datos y el respeto al cero absoluto garantizan confiabilidad y previenen errores antes de cualquier cálculo.

**Independent Test**: Puede probarse de forma autónoma ingresando valores menores al cero absoluto (Kelvin < 0), entradas vacías o textos no numéricos, verificando que se rechacen de inmediato con mensajes claros.

**Acceptance Scenarios**:

1. **Given** un valor de temperatura en escala Kelvin inferior a 0 (ej. -1 K), **When** se solicita cualquier conversión, **Then** el sistema rechaza la operación informando que no existen temperaturas inferiores al cero absoluto (0 Kelvin).
2. **Given** una temperatura en Celsius o Fahrenheit equivalente a menos de 0 Kelvin (ej. -300 °C o -500 °F), **When** se solicita la conversión, **Then** el sistema rechaza la operación informando que la temperatura se encuentra por debajo del cero absoluto.
3. **Given** una entrada vacía o con solo espacios en blanco, **When** se procesa la solicitud, **Then** el sistema notifica claramente que la entrada no puede estar vacía.
4. **Given** una entrada con caracteres no numéricos (ej. "abc"), **When** se procesa la solicitud, **Then** el sistema notifica claramente que el valor debe ser un número válido.

---

### User Story 3 - Conversión reflexiva y formato de precisión (Priority: P3)

Como usuario, quiero obtener resultados redondeados de forma estándar a dos decimales y poder solicitar conversiones hacia la misma unidad de origen sin alteraciones numéricas.

**Why this priority**: Asegura uniformidad en la presentación visual de datos y robustez ante solicitudes de conversión redundantes.

**Independent Test**: Puede probarse enviando valores con múltiples decimales o seleccionando la misma unidad de origen y destino, comprobando que el resultado tenga exactamente dos decimales y conserve el valor original.

**Acceptance Scenarios**:

1. **Given** un cálculo cuyo resultado contiene más de dos cifras decimales (ej. 35.6666 °C), **When** se entrega el resultado, **Then** se presenta redondeado a 2 decimales (35.67).
2. **Given** una temperatura de entrada en una escala determinada (ej. 25.50 °C), **When** la unidad de destino es la misma que la unidad de origen (Celsius a Celsius), **Then** el sistema devuelve el mismo valor numérico con formato de dos decimales (25.50 °C).

---

### Edge Cases

- ¿Qué ocurre si la entrada contiene espacios en blanco alrededor de un número válido (ej. "  25.5  ")? El sistema debe admitir y procesar el valor numérico tras limpiar los espacios externos.
- ¿Qué ocurre con el valor exacto del cero absoluto (0 Kelvin / -273.15 °C / -459.67 °F)? Debe procesarse como un valor válido en el límite exacto permitido.
- ¿Qué ocurre cuando la entrada no es un texto ni número (ej. valores nulos)? El sistema debe capturar la condición y mostrar un mensaje de error claro indicando que se requiere una entrada válida.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE admitir conversiones bidireccionales entre las escalas Celsius (°C), Fahrenheit (°F) y Kelvin (K).
- **FR-002**: El sistema DEBE calcular la conversión entre Celsius y Fahrenheit utilizando las relaciones de proporcionalidad térmica estándar ($F = (C \times 9/5) + 32$ y $C = (F - 32) \times 5/9$).
- **FR-003**: El sistema DEBE calcular la conversión entre Celsius y Kelvin aplicando el desplazamiento del cero absoluto ($K = C + 273.15$ y $C = K - 273.15$).
- **FR-004**: El sistema DEBE calcular la conversión entre Fahrenheit y Kelvin aplicando las transformaciones compuestas equivalentes ($K = (F - 32) \times 5/9 + 273.15$ y $F = (K - 273.15) \times 9/5 + 32$).
- **FR-005**: El sistema DEBE redondear el valor numérico resultante de cualquier conversión a exactamente dos (2) cifras decimales utilizando la regla estándar de redondeo simétrico.
- **FR-006**: El sistema DEBE validar que ninguna temperatura resultante o provista sea menor a cero absoluto (0 Kelvin / -273.15 °C / -459.67 °F), rechazando la operación con un mensaje explicativo si se viola esta condición.
- **FR-007**: El sistema DEBE rechazar entradas vacías, compuestas únicamente por espacios o valores nulos, notificando un mensaje de error claro al usuario.
- **FR-008**: El sistema DEBE rechazar entradas que no correspondan a representaciones numéricas válidas, entregando un mensaje comprensible sobre la necesidad de ingresar un número.
- **FR-009**: El sistema DEBE admitir conversiones donde la unidad de origen y destino coincidan, entregando el mismo valor numérico formateado a dos decimales.

### Key Entities *(include if feature involves data)*

- **Escala de Temperatura**: Representa las unidades térmicas admitidas: Celsius (°C), Fahrenheit (°F) y Kelvin (K).
- **Solicitud de Conversión**: Estructura conceptual que agrupa el valor numérico de entrada, la escala de origen y la escala de destino.
- **Resultado de Conversión**: Estructura conceptual que contiene el valor numérico transformado con precisión de 2 decimales y la unidad de medida resultante.
- **Notificación de Error**: Mensaje explicativo emitido cuando una solicitud no cumple con los criterios de validación (vacío, no numérico o fuera del rango físico admitido).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100% de las conversiones entre escalas válidas (Celsius, Fahrenheit, Kelvin) producen resultados con exactitud matemática y precisión de 2 decimales.
- **SC-002**: El 100% de los intentos de ingresar o calcular temperaturas por debajo de 0 Kelvin son rechazados sin excepción antes de emitir un resultado.
- **SC-003**: El 100% de las solicitudes con entradas inválidas (vacías, no numéricas o nulas) devuelven mensajes informativos claros sin interrupciones abruptas o fallos no controlados.
- **SC-004**: El 100% de las conversiones reflexivas (misma unidad de origen y destino) conservan el valor original con exactitud a dos decimales.

## Assumptions

- La funcionalidad se enfoca exclusivamente en las escalas Celsius, Fahrenheit y Kelvin; otras escalas térmicas (Rankine, Réaumur) quedan fuera del alcance inicial.
- El valor estándar para el cero absoluto en Celsius se fija en -273.15 °C de acuerdo con el Sistema Internacional de Unidades.
- El redondeo a 2 decimales adopta el criterio convencional de mitad hacia arriba (round half up) para evitar discrepancias en valores límite.
- No se requiere persistir un historial de transacciones o conversiones en esta versión.
