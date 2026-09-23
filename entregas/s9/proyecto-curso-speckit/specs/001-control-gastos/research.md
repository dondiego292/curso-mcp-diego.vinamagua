# Research & Technical Decisions: Sistema de Control de Gastos Personales

Este documento consolida las decisiones técnicas, patrones arquitectónicos y justificaciones para la implementación del sistema conforme a la Constitución v2.0.0 y la especificación `001-control-gastos`.

---

## 1. Framework Web y Runtime

- **Decisión**: Python 3.12 y FastAPI.
- **Razón**: FastAPI provee soporte nativo para async/await, generación automática de documentación OpenAPI, validación estricta en tiempo de ejecución con Pydantic v2, y un sistema de inyección de dependencias (`Depends`) idóneo para la autenticación y sesiones de base de datos.
- **Alternativas consideradas**:
  - *Flask*: Menor soporte tipado nativo; requiere extensiones adicionales para OpenAPI y validación Pydantic.
  - *Django / DRF*: Demasiado pesado para este dominio, introduce acoplamiento con su propio ORM violando la inversión de dependencias estipulada en la Constitución.

---

## 2. Persistencia y Migraciones

- **Decisión**: SQLAlchemy 2.0 (estilo declarativo 2.0 con `Mapped` y `mapped_column`) y Alembic para migraciones. Base de datos SQLite en desarrollo (`sqlite:///./gastos.db`) configurando condicionalmente `connect_args={"check_same_thread": False}`.
- **Razón**: Satisface el Artículo III.1 y III.2. SQLAlchemy 2.0 desacopla la definición de modelos y permite que los repositorios devuelvan diccionarios puros (`dict`), aislando la persistencia de los servicios. Alembic garantiza versionado reproducible de esquemas.
- **Alternativas consideradas**:
  - *SQL crudo / sqlite3 directo*: Prohibido explícitamente por el Artículo III.1 (riesgo de inyección SQL y mantenimiento deficiente).
  - *Tortoise ORM / Peewee*: Menor madurez en el ecosistema corporativo y menor flexibilidad para portabilidad SQLite/Postgres sin alterar código.

---

## 3. Seguridad, Hashing y Tokens JWT

- **Decisión**:
  - Hashing de contraseñas: `passlib[bcrypt]` (utilizando `CryptContext(schemes=["bcrypt"], deprecated="auto")`).
  - Emisión y validación de tokens: `PyJWT` firmando con algoritmo `HS256`.
  - Configuración: `pydantic-settings` (`BaseSettings`) leyendo desde archivo `.env` (`SECRET_KEY`, `DATABASE_URL`, `ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Razón**: Cumple estrictamente con el Artículo IV. Prohíbe texto plano, garantiza expiración finita del token y resuelve el `usuario_id` exclusivamente desde las claims del JWT en `get_current_user`.
- **Alternativas consideradas**:
  - *python-jose*: Presenta problemas de mantenimiento en versiones recientes de Python 3.12; `PyJWT` es el estándar activo más robusto.
  - *Argon2*: Aunque seguro, bcrypt cumple con creces el requerimiento no negociable de compatibilidad con Sesiones 6-8.

---

## 4. Inversión de Dependencias (DIP) y Estrategia de Testing

- **Decisión**:
  - Toda función de servicio en `app/services/gastos.py` recibe el repositorio mediante parámetro con valor por defecto:
    `def registrar_gasto(db, usuario_id, descripcion, monto, categoria, repo=gastos_repository) -> dict`
  - En pruebas unitarias (`tests/unit/`), se inyecta un `RepositorioFalso` (objeto o módulo que emula `guardar`, `listar` y `total_por_categoria` en memoria).
  - Queda prohibido el uso de `unittest.mock` para simular la capa de datos (Artículo VII.2).
- **Razón**: Permite pruebas unitarias ultra-rápidas, determinísticas y desacopladas de I/O o motores de base de datos.
- **Alternativas consideradas**:
  - *Mocks con `unittest.mock.patch`*: Rechazado y prohibido por la Constitución v2.0.0; genera tests frágiles acoplados al nombre del import y disfraza un mal diseño de dependencias.

---

## 5. Integración de Model Context Protocol (MCP)

- **Decisión**: Paquete `mcp[cli]<2` utilizando `FastMCP`. El servidor MCP se monta sobre la misma aplicación FastAPI exponiendo transporte `streamable-http`, reutilizando exactamente las funciones de `app/services/gastos.py`.
- **Razón**: Satisface el Artículo VI y la solicitud del usuario. `FastMCP` sobre `streamable-http` permite resolver la identidad del usuario a partir de los headers/tokens de la petición HTTP subyacente. Para transporte `stdio`, se documenta en comentarios el fallback a un usuario demo configurado en `.env`.
- **Alternativas consideradas**:
  - *Proceso MCP independiente*: Mayor complejidad de orquestación y despliegue; montar FastMCP dentro de la app FastAPI unifica el ciclo de vida y la configuración.

---

## 6. Mapeo de Excepciones y Respuestas de Error

- **Decisión**:
  - Excepciones de dominio en `app/services/gastos.py`: `CategoriaInvalidaError` y `LimiteExcedidoError`.
  - En `routers/gastos.py`, se capturan estas excepciones y se traducen a HTTP 400 con `{"detail": str(e)}`.
  - En `mcp/tools/gastos.py`, se capturan y se devuelven como `{"error": str(e)}` (Artículo VI.3).
  - Errores no controlados (`Exception`) son capturados por un manejador global de FastAPI devolviendo HTTP 500 con `{"detail": "Error interno del servidor"}` (Artículo IV.5).
- **Razón**: Preserva la frontera de abstracción entre lógica de negocio y capas de presentación/transporte sin filtrar detalles internos.
