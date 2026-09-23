# API REST Contract: Sistema de Control de Gastos Personales

Este documento especifica el contrato de interfaz HTTP REST para la API de control de gastos personales.

---

## 1. Convenciones Globales

- **Formato**: JSON (`application/json`) para todas las solicitudes y respuestas, salvo `/usuarios/token` que recibe `application/x-www-form-urlencoded`.
- **Autenticación**: Cabecera `Authorization: Bearer <token_jwt>`.
- **Estructura de Errores de Negocio**:
  ```json
  {
    "detail": "Descripción del error de negocio"
  }
  ```
- **Estructura de Errores de Validación Pydantic (422)**: Formato estándar FastAPI/Pydantic con detalles de los campos inválidos.
- **Estructura de Error 500 no controlado**:
  ```json
  {
    "detail": "Error interno del servidor"
  }
  ```

---

## 2. Endpoints de Usuarios

### 2.1 Registro de Usuario
- **Ruta**: `POST /usuarios/`
- **Autenticación**: Ninguna.
- **Request Body**:
  ```json
  {
    "email": "usuario@ejemplo.com",
    "password": "PasswordSegura123!"
  }
  ```
- **Respuestas**:
  - `201 Created`:
    ```json
    {
      "id": 1,
      "email": "usuario@ejemplo.com"
    }
    ```
  - `400 Bad Request`: Email duplicado.
    ```json
    {
      "detail": "El email ya está registrado"
    }
    ```
  - `422 Unprocessable Entity`: Formato de email inválido o cuerpo mal formado.

---

### 2.2 Obtención de Token de Acceso (Login)
- **Ruta**: `POST /usuarios/token`
- **Autenticación**: Ninguna.
- **Content-Type**: `application/x-www-form-urlencoded` (`OAuth2PasswordRequestForm`).
- **Request Body**:
  ```text
  username=usuario@ejemplo.com&password=PasswordSegura123!
  ```
- **Respuestas**:
  - `200 OK`:
    ```json
    {
      "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
      "token_type": "bearer"
    }
    ```
  - `401 Unauthorized`: Credenciales inválidas.
    ```json
    {
      "detail": "Credenciales inválidas"
    }
    ```

---

## 3. Endpoints de Gastos

### 3.1 Registro de un Gasto
- **Ruta**: `POST /gastos/`
- **Autenticación**: Requerida (`Bearer <token>`).
- **Request Body**:
  ```json
  {
    "descripcion": "Almuerzo de trabajo",
    "monto": 45.50,
    "categoria": "comida"
  }
  ```
- **Respuestas**:
  - `201 Created`:
    ```json
    {
      "id": 10,
      "usuario_id": 1,
      "descripcion": "Almuerzo de trabajo",
      "monto": 45.50,
      "categoria": "comida",
      "fecha": "2026-09-23T12:30:00"
    }
    ```
  - `400 Bad Request` (Categoría Inválida):
    ```json
    {
      "detail": "Categoría inválida: viajes"
    }
    ```
  - `400 Bad Request` (Límite Excedido):
    ```json
    {
      "detail": "El gasto supera el límite permitido de 500.0 en la categoría comida"
    }
    ```
  - `401 Unauthorized`: Token faltante, inválido o expirado.
    ```json
    {
      "detail": "No autenticado"
    }
    ```
  - `422 Unprocessable Entity`: Monto `<= 0`, descripción vacía, o campo faltante.

---

### 3.2 Listado Paginado de Gastos Propios
- **Ruta**: `GET /gastos/`
- **Autenticación**: Requerida (`Bearer <token>`).
- **Query Parameters**:
  - `skip` (opcional, entero, default: `0`, ge: `0`)
  - `limit` (opcional, entero, default: `20`, ge: `1`, le: `100`)
- **Respuestas**:
  - `200 OK`:
    ```json
    [
      {
        "id": 10,
        "usuario_id": 1,
        "descripcion": "Almuerzo de trabajo",
        "monto": 45.50,
        "categoria": "comida",
        "fecha": "2026-09-23T12:30:00"
      }
    ]
    ```
  - `401 Unauthorized`: Token no provisto o inválido.
  - `422 Unprocessable Entity`: Parámetros `skip` o `limit` negativos o no numéricos.
- **Regla de Aislamiento (Artículo V.1)**:
  - Esta ruta filtra SIEMPRE por el `usuario_id` del token JWT.
  - Nunca acepta ni expone gastos de otros usuarios.
  - No devuelve 403 en listados; si el usuario no tiene gastos, devuelve `[]` con código 200.
