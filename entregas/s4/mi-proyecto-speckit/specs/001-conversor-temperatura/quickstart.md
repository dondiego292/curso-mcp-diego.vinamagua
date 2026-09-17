# Quickstart: Validación del Conversor de Temperatura

**Feature**: `001-conversor-temperatura`  
**Fecha**: 2026-09-16  

Esta guía describe los pasos para verificar de principio a fin el funcionamiento del conversor de temperatura, tanto a través de su suite de pruebas automatizadas como en sus interfaces programmatic (Python API) y CLI.

---

## 1. Prerrequisitos

- Python 3.9 o superior instalado (`python3 --version`).
- No se requieren bibliotecas externas ni entornos virtuales complejos (usa exclusivamente la biblioteca estándar de Python).

---

## 2. Ejecución de Pruebas Unitarias

Para comprobar automáticamente todos los criterios de aceptación y casos borde definidos en [spec.md](./spec.md):

```bash
python3 -m unittest test_conversor_temperatura.py -v
```

**Resultado esperado**:
- Todas las pruebas deben pasar exitosamente (`OK`).
- Validación completa de conversiones C-F, C-K, F-K, redondeo a 2 decimales y captura de casos borde (Kelvin < 0, entradas vacías, entradas no numéricas).

---

## 3. Verificación Interactiva (Python API)

Para probar la biblioteca desde el intérprete interactivo de Python:

```bash
python3
```

```python
from conversor_temperatura import convertir_temperatura, celsius_a_fahrenheit

# Caso 1: Celsius a Fahrenheit
print(celsius_a_fahrenheit(100))
# Esperado: 212.00

# Caso 2: Conversión genérica Celsius a Kelvin
print(convertir_temperatura(0, "C", "K"))
# Esperado: 273.15

# Caso 3: Misma unidad (reflexivo)
print(convertir_temperatura(25.5, "C", "C"))
# Esperado: 25.50

# Caso 4: Manejo de error por cero absoluto
try:
    convertir_temperatura(-1, "K", "C")
except ValueError as e:
    print(f"Error capturado correctamente: {e}")
```

Consulta detalles completos de firmas y excepciones en [python-api.md](./contracts/python-api.md).

---

## 4. Verificación por Línea de Comandos (CLI)

Ejecución directa en terminal:

```bash
# 1. Caso estándar C -> F
python3 conversor_temperatura.py 100 C F
# Salida esperada: 212.00

# 2. Caso estándar F -> K
python3 conversor_temperatura.py 212 F K
# Salida esperada: 373.15

# 3. Caso borde: Entrada bajo cero absoluto
python3 conversor_temperatura.py -300 C K
# Salida esperada en stderr: Error: La temperatura no puede ser inferior al cero absoluto (0 Kelvin).

# 4. Caso borde: Entrada no numérica
python3 conversor_temperatura.py abc C F
# Salida esperada en stderr: Error: La entrada debe ser un número válido.
```

Consulta detalles de los códigos de salida y protocolo en [cli-interface.md](./contracts/cli-interface.md).
