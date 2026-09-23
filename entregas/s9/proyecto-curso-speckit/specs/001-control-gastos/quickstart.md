# Quickstart Validation Guide: Sistema de Control de Gastos Personales

Esta guía detalla los pasos para configurar el entorno, ejecutar la suite de pruebas y validar manualmente los flujos principales de la aplicación tanto vía API REST como por herramientas MCP.

---

## 1. Prerrequisitos

- Python 3.12 instalado.
- Gestor de paquetes `uv` (o `pip` / `venv`).
- SQLite 3.

---

## 2. Configuración del Entorno Local

1. **Instalación de dependencias**:
   ```bash
   uv pip install fastapi uvicorn "sqlalchemy>=2.0" alembic "pydantic>=2.0" pydantic-settings "passlib[bcrypt]" pyjwt "mcp[cli]<2" pytest httpx
   ```

2. **Variables de entorno**:
   Crear archivo `.env` a partir de `.env.example`:
   ```bash
   cat <<EOF > .env
   SECRET_KEY=e8340d826a7989914cf3df8417621c17243c22b9b77d632338b813f89d38c642
   DATABASE_URL=sqlite:///./gastos.db
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   DEMO_USER_ID=1
   EOF
   ```

3. **Migraciones de Base de Datos**:
   ```bash
   alembic upgrade head
   ```

---

## 3. Ejecución de Pruebas Automatizadas

Para validar las reglas de negocio, el aislamiento y los contratos sin levantar el servidor:

```bash
# Ejecutar todas las pruebas con cobertura detallada
pytest -v --cov=app tests/

# Ejecutar pruebas unitarias puras (con RepositorioFalso, sin mock)
pytest -v tests/unit/

# Ejecutar pruebas de integración con base de datos SQLite en memoria
pytest -v tests/integration/

# Ejecutar pruebas end-to-end de API con TestClient
pytest -v tests/api/
```

---

## 4. Validación Manual End-to-End (Flujo HTTP)

1. **Iniciar el servidor FastAPI**:
   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```

2. **Paso 1: Registrar un usuario**:
   ```bash
   curl -X POST http://127.0.0.1:8000/usuarios/ \
     -H "Content-Type: application/json" \
     -d '{"email": "ana@ejemplo.com", "password": "Password123!"}'
   # Esperado: 201 Created con {"id": 1, "email": "ana@ejemplo.com"}
   ```

3. **Paso 2: Iniciar sesión y obtener token JWT**:
   ```bash
   TOKEN=$(curl -s -X POST http://127.0.0.1:8000/usuarios/token \
     -d "username=ana@ejemplo.com&password=Password123!" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
   echo "Token: $TOKEN"
   # Esperado: Token JWT alfanumérico
   ```

4. **Paso 3: Registrar un gasto válido**:
   ```bash
   curl -X POST http://127.0.0.1:8000/gastos/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"descripcion": "Supermercado semanal", "monto": 150.0, "categoria": "comida"}'
   # Esperado: 201 Created con objeto Gasto
   ```

5. **Paso 4: Validar rechazo por categoría inválida**:
   ```bash
   curl -X POST http://127.0.0.1:8000/gastos/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"descripcion": "Boleto de avión", "monto": 100.0, "categoria": "viajes"}'
   # Esperado: 400 Bad Request con {"detail": "Categoría inválida: viajes"}
   ```

6. **Paso 5: Validar rechazo por límite acumulado excedido (> 500.0)**:
   ```bash
   # El acumulado previo en 'comida' es 150.0. Intentar sumar 400.0 (total 550.0):
   curl -X POST http://127.0.0.1:8000/gastos/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"descripcion": "Cena de gala", "monto": 400.0, "categoria": "comida"}'
   # Esperado: 400 Bad Request con {"detail": "El gasto supera el límite permitido de 500.0 en la categoría comida"}
   ```

7. **Paso 6: Listar gastos paginados**:
   ```bash
   curl -X GET "http://127.0.0.1:8000/gastos/?skip=0&limit=10" \
     -H "Authorization: Bearer $TOKEN"
   # Esperado: 200 OK con lista conteniendo únicamente el gasto de 150.0
   ```

---

## 5. Validación de Herramientas MCP

El servidor FastMCP está expuesto en la ruta montada `/mcp` sobre FastAPI:

- Enviar payload de invocación de herramienta `registrar_gasto`:
  - Entrada: `{"name": "registrar_gasto", "arguments": {"descripcion": "Taxi", "monto": 15.0, "categoria": "transporte"}}`
  - Esperado: Objeto JSON con el gasto registrado para el usuario autenticado.
- Enviar payload con categoría inválida:
  - Esperado: `{"error": "Categoría inválida: ..."}`
