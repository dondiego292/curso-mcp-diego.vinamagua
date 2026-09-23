# Model Context Protocol (MCP) Tools Contract: Sistema de Control de Gastos Personales

Este documento define el contrato de herramientas expuestas a través del servidor MCP montado con FastMCP en la aplicación.

---

## 1. Convenciones y Principios MCP (Artículo VI)

1. **Reutilización Directa**: Todas las tools llaman directamente a funciones en `app/services/gastos.py`. Ninguna tool implementa lógica de negocio ni persistencia propia.
2. **Estructura de Errores**: Todo error de validación o regla de negocio se captura y devuelve como:
   ```json
   {
     "error": "Descripción legible del error de negocio"
   }
   ```
   Bajo ninguna circunstancia se lanza una excepción no controlada que interrumpa la sesión del cliente MCP.
3. **Resolución de Identidad**:
   - Transporte `streamable-http`: La tool resuelve la identidad del usuario a partir del token JWT transmitido en la cabecera `Authorization` de la solicitud HTTP subyacente.
   - Transporte `stdio`: Documentado explícitamente en el código como simplificación consciente utilizando el usuario demo definido en `.env` (`DEMO_USER_ID`), solo cuando no exista token disponible.

---

## 2. Definición de Herramientas (Tools)

### 2.1 `registrar_gasto`
- **Nombre**: `registrar_gasto`
- **Descripción**: "Registra un gasto personal con descripción, monto y categoría para el usuario autenticado, validando que el monto sea positivo, la categoría pertenezca a [comida, transporte, entretenimiento, otros] y que no exceda el límite mensual acumulado de 500.0 por categoría."
- **Parámetros**:
  - `descripcion` (`string`, requerido): Detalle del gasto realizado.
  - `monto` (`number`, requerido): Monto monetario gastado (debe ser mayor a 0).
  - `categoria` (`string`, requerido): Una de: `comida`, `transporte`, `entretenimiento`, `otros`.
- **Retorno Exitoso**:
  ```json
  {
    "id": 15,
    "usuario_id": 1,
    "descripcion": "Café y snacks",
    "monto": 12.00,
    "categoria": "comida",
    "fecha": "2026-09-23T14:10:00"
  }
  ```
- **Retorno en Caso de Error**:
  - Categoría inválida:
    ```json
    {
      "error": "Categoría inválida: lujo. Permitidas: comida, transporte, entretenimiento, otros"
    }
    ```
  - Límite excedido:
    ```json
    {
      "error": "El gasto supera el límite permitido de 500.0 en la categoría comida"
    }
    ```
  - Validación de campos:
    ```json
    {
      "error": "El monto debe ser mayor a cero"
    }
    ```

---

### 2.2 `listar_gastos`
- **Nombre**: `listar_gastos`
- **Descripción**: "Obtiene la lista paginada de gastos registrados correspondientes al usuario autenticado en la sesión actual."
- **Parámetros**:
  - `skip` (`integer`, opcional, por defecto `0`): Número de registros a omitir para paginación.
  - `limit` (`integer`, opcional, por defecto `20`): Número máximo de gastos a retornar.
- **Retorno Exitoso**:
  ```json
  [
    {
      "id": 15,
      "usuario_id": 1,
      "descripcion": "Café y snacks",
      "monto": 12.00,
      "categoria": "comida",
      "fecha": "2026-09-23T14:10:00"
    }
  ]
  ```
- **Retorno en Caso de Error**:
  ```json
  {
    "error": "Parámetros de paginación inválidos"
  }
  ```
