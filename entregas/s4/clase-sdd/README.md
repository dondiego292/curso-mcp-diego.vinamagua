# Conversor de Temperatura (Spec-Driven Development)

Implementación de un conversor de temperatura siguiendo la metodología **Spec-Driven Development (SDD)**, asegurando cumplimiento estricto de especificaciones, criterios de aceptación y casos borde.

---

## 🎯 Objetivo
Convertir una temperatura entre **Celsius**, **Fahrenheit** y **Kelvin**.

---

## 📋 Especificación y Criterios

### Criterios de Aceptación
- [x] **Convierte correctamente de Celsius a Fahrenheit y viceversa:**
  - $F = (C \times 9/5) + 32$
  - $C = (F - 32) \times 5/9$
- [x] **Convierte correctamente de Celsius a Kelvin y viceversa:**
  - $K = C + 273.15$
  - $C = K - 273.15$
- [x] **Convierte correctamente de Fahrenheit a Kelvin y viceversa:**
  - $K = (F - 32) \times 5/9 + 273.15$
  - $F = (K - 273.15) \times 9/5 + 32$
- [x] **Redondea el resultado a 2 decimales:**
  - Aplica redondeo formal simétrico (`ROUND_HALF_UP`) mediante el módulo `decimal`.
- [x] **Rechaza temperaturas Kelvin inferiores a 0:**
  - El cero absoluto es $0\text{ K}$. Cualquier valor en Kelvin menor a cero levanta un `ValueError` descriptivo.

### Casos Borde
- [x] **Entrada vacía:** Cadenas vacías, cadenas con espacios en blanco o valores `None` generan un mensaje de error claro indicando que la entrada no puede estar vacía.
- [x] **Entrada no numérica:** Valores como `"abc"`, listas, diccionarios o booleanos generan un mensaje de error claro explicando que se espera un número.
- [x] **Temperatura Kelvin inferior a 0:** Rechaza de forma explícita valores negativos en Kelvin (tanto en origen como si la conversión resulta en $< 0\text{ K}$).
- [x] **Conversión de una unidad a la misma unidad:** Por ejemplo Celsius a Celsius devuelve el mismo valor redondeado a 2 decimales.

---

## 🧪 Ejecución de Pruebas Unitarias

Para ejecutar la suite completa de pruebas unitarias (`unittest`):

```bash
python3 -m unittest test_conversor_temperatura.py -v
```

Todas las pruebas validan los 5 criterios de aceptación y los 4 casos borde de la especificación.

---

## 🚀 Uso del Módulo

### En código Python

```python
from conversor_temperatura import convertir_temperatura, celsius_a_fahrenheit

# Conversiones generales
temp_f = convertir_temperatura(100, "C", "F")  # 212.00
temp_k = convertir_temperatura(0, "C", "K")    # 273.15
temp_c = convertir_temperatura(212, "F", "C")  # 100.00

# Misma unidad
misma = convertir_temperatura(25, "C", "C")    # 25.00

# Funciones directas
f = celsius_a_fahrenheit(37)                   # 98.60
```

### Desde la Línea de Comandos (CLI)

#### Modo directo con argumentos:
```bash
python3 conversor_temperatura.py <valor> <unidad_origen> <unidad_destino>
```
Ejemplos:
```bash
python3 conversor_temperatura.py 100 C F
# Salida: 212.00

python3 conversor_temperatura.py 0 C K
# Salida: 273.15
```

#### Modo interactivo:
```bash
python3 conversor_temperatura.py
```
Despliega un menú interactivo en consola con soporte para formato visual de tablas y páneles (usando `rich`).
