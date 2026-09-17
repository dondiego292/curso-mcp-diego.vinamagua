# Contrato de Interfaz: CLI (Command Line Interface)

**Comando**: `python3 -m conversor_temperatura`  
**Feature**: `001-conversor-temperatura`  

---

## 1. Sinopsis

```bash
python3 conversor_temperatura.py <VALOR> <ORIGEN> <DESTINO>
# o alternativamente:
python3 -m conversor_temperatura <VALOR> <ORIGEN> <DESTINO>
```

---

## 2. Argumentos Posicionales

| Argumento | Tipo / Formato | Requerido | Descripción |
|---|---|---|---|
| `VALOR` | String / Número | Sí | Valor numérico de temperatura a convertir (ej. `100`, `25.5`, `-40`). |
| `ORIGEN` | `[C, F, K]` | Sí | Escala de temperatura actual (insensible a mayúsculas/minúsculas). |
| `DESTINO` | `[C, F, K]` | Sí | Escala de temperatura objetivo (insensible a mayúsculas/minúsculas). |

---

## 3. Códigos de Salida y Protocolo de Salida

### Salida Exitosa (Código de Retorno: `0`)
- **Canal**: `stdout`
- **Formato**: `<VALOR_CONVERTIDO>` (número con 2 decimales seguido de salto de línea).
- **Ejemplo**:
  ```bash
  $ python3 conversor_temperatura.py 100 C F
  212.00
  ```

### Salida con Error (Código de Retorno: `1`)
- **Canal**: `stderr`
- **Formato**: `Error: <MENSAJE_DESCRIPTIVO>`
- **Ejemplo**:
  ```bash
  $ python3 conversor_temperatura.py -1 K C
  Error: La temperatura no puede ser inferior al cero absoluto (0 Kelvin).
  ```

### Salida de Ayuda (Código de Retorno: `0`)
- **Canal**: `stdout`
- **Invocación**: `python3 conversor_temperatura.py --help`
