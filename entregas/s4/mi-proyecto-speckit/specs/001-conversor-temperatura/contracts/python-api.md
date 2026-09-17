# Contrato de Interfaz: Python API

**Módulo**: `conversor_temperatura`  
**Feature**: `001-conversor-temperatura`  

---

## 1. Función General de Conversión

### `convertir_temperatura`

Convierte un valor numérico de temperatura entre dos unidades soportadas (`'C'`, `'F'`, `'K'`).

```python
def convertir_temperatura(
    valor: Union[int, float, str, Decimal],
    origen: str,
    destino: str
) -> Decimal:
    """
    Convierte una temperatura entre Celsius, Fahrenheit y Kelvin.

    Args:
        valor: Magnitud de temperatura (numérica o texto numérico).
        origen: Unidad de entrada ('C', 'F', 'K', insensible a mayúsculas).
        destino: Unidad de salida ('C', 'F', 'K', insensible a mayúsculas).

    Returns:
        Decimal: Valor resultante redondeado a 2 decimales (ROUND_HALF_UP).

    Raises:
        ValueError: Si la entrada está vacía, no es numérica, la unidad es inválida,
                    o la temperatura se sitúa por debajo del cero absoluto (0 Kelvin).
    """
```

---

## 2. Funciones de Conversión Directa

### Celsius <-> Fahrenheit
```python
def celsius_a_fahrenheit(valor: Union[int, float, str, Decimal]) -> Decimal:
    """F = (C * 9/5) + 32"""

def fahrenheit_a_celsius(valor: Union[int, float, str, Decimal]) -> Decimal:
    """C = (F - 32) * 5/9"""
```

### Celsius <-> Kelvin
```python
def celsius_a_kelvin(valor: Union[int, float, str, Decimal]) -> Decimal:
    """K = C + 273.15"""

def kelvin_a_celsius(valor: Union[int, float, str, Decimal]) -> Decimal:
    """C = K - 273.15"""
```

### Fahrenheit <-> Kelvin
```python
def fahrenheit_a_kelvin(valor: Union[int, float, str, Decimal]) -> Decimal:
    """K = (F - 32) * 5/9 + 273.15"""

def kelvin_a_fahrenheit(valor: Union[int, float, str, Decimal]) -> Decimal:
    """F = (K - 273.15) * 9/5 + 32"""
```

---

## 3. Garantías del Contrato

1. **Inmutabilidad de tipo de salida**: Toda función retorna un objeto `Decimal` con formato cuantizado de 2 decimales (`Decimal('0.00')`).
2. **Determinismo**: Mismas entradas producen siempre la misma salida.
3. **Manejo de errores**: Las condiciones inválidas nunca producen excepciones silenciosas, retornos `None` ni caídas inesperadas; siempre lanzan `ValueError` con mensajes explicativos legibles por humanos.
