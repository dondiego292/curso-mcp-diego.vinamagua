# Implementation Plan: Sistema de Control de Gastos Personales

**Branch**: `001-control-gastos` | **Date**: 2026-09-23 | **Spec**: [specs/001-control-gastos/spec.md](spec.md)

**Input**: Feature specification from `/specs/001-control-gastos/spec.md`

## Summary

Implementar el sistema de control de gastos personales aplicando Spec-Driven Development, Clean Architecture en capas desacopladas, persistencia con SQLAlchemy 2.0 y SQLite/PostgreSQL, autenticación robusta mediante OAuth2 Password Flow + JWT, integración de herramientas FastMCP montadas vía streamable-http, y una suite de pruebas automatizadas con inyección de `RepositorioFalso` (sin mocks) que garantiza 100% de cobertura de reglas de negocio y compatibilidad exacta con las firmas de Sesiones 6-8.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: FastAPI, Pydantic v2, `pydantic-settings`, SQLAlchemy 2.0+, Alembic, `PyJWT`, `passlib[bcrypt]`, `mcp[cli]<2` (FastMCP)

**Storage**: SQLite en desarrollo (`sqlite:///./gastos.db`) con soporte nativo para PostgreSQL en producción

**Testing**: `pytest`, `pytest-cov`, `httpx` (`TestClient`), `RepositorioFalso` (sin `unittest.mock`)

**Target Platform**: Linux / macOS / Contenedor Docker (API REST HTTP + Endpoint FastMCP)

**Project Type**: Servicio web RESTful + Servidor de herramientas MCP

**Performance Goals**: Tiempo de respuesta p95 < 200 ms para operaciones CRUD locales; ejecución de la suite de pruebas en < 5 segundos

**Constraints**:
- Cobertura de reglas de negocio de `spec.md` al 100%.
- Cobertura de código ≥ 90% en `app/services/` y ≥ 80% global.
- Respeto irrestricto de las firmas de funciones y módulos definidas en el contrato de compatibilidad de Sesiones 6-8.
- Cero uso de `unittest.mock` para repositorios (Artículo VII.2).

**Scale/Scope**: Gestión multiusuario con estricto aislamiento de datos; límite acumulado de 500.0 por categoría por usuario.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Artículo I (Capas)**: **PASS**. Se define una separación rígida de carpetas: `app/routers/` (HTTP y traducción de excepciones), `app/services/` (lógica de negocio pura sin SQLAlchemy), `app/repositories/` (operaciones de persistencia retornando diccionarios), `app/utils/` (funciones puras sin efectos secundarios) y `app/mcp/tools/` (consumidores directos de `services/`).
- **Artículo II (SOLID)**: **PASS**. SRP por función de servicio; OCP mediante constantes y tuplas de categorías sin reescritura de condicionales; DIP obligatorio recibiendo `repo=gastos_repository` como keyword argument por defecto; diseño pragmático sin clases innecesarias en repositorios.
- **Artículo III (Persistencia)**: **PASS**. SQLAlchemy 2.0 declarativo y Alembic para migraciones; SQLite configurado con `connect_args` condicional; `usuario_id` como clave foránea y filtro mandatorio en toda consulta.
- **Artículo IV (Seguridad)**: **PASS**. Hashing con `passlib[bcrypt]`, OAuth2 + JWT (HS256) con expiración configurable, secretos y URLs en `.env` gestionados por `pydantic-settings`, `usuario_id` resuelto exclusivamente en `get_current_user`, y captura de errores no controlados devolviendo HTTP 500 sin trazas técnicas.
- **Artículo V (REST)**: **PASS**. Códigos HTTP semánticos (201, 200, 400, 401, 404, 422), parámetros `skip` y `limit` con validación, y schemas Pydantic separados de entrada (`GastoCreate`) y salida (`GastoOut`).
- **Artículo VI (MCP)**: **PASS**. Tools en `app/mcp/tools/gastos.py` consumiendo directamente `app/services/gastos.py`, errores de negocio estructurados (`{"error": "..."}`) sin interrumpir la sesión, transporte `streamable-http` con token y fallback documentado para `stdio`.
- **Artículo VII (Testing y Cobertura)**: **PASS**. Pirámide de pruebas organizada en `tests/unit/`, `tests/integration/` y `tests/api/`, uso mandatorio de `RepositorioFalso`, y metas de cobertura cumplidas.
- **Artículo VIII (Compatibilidad y Evolución)**: **PASS**. Se fijan las firmas exactas de `app/services/gastos.py`, `app/repositories/gastos.py` y `app/repositories/usuarios.py`, garantizando compatibilidad binaria con Sesiones 6-8.

## Project Structure

### Documentation (this feature)

```text
specs/001-control-gastos/
├── plan.md              # Este plan de implementación
├── research.md          # Decisiones técnicas y justificaciones (Fase 0)
├── data-model.md        # Entidades, esquemas Pydantic y diagramas ER (Fase 1)
├── quickstart.md        # Guía de validación y escenarios de prueba (Fase 1)
├── contracts/           # Contratos de interfaces externas (Fase 1)
│   ├── rest-api.md      # Contrato de la API REST
│   └── mcp-tools.md     # Contrato de las herramientas MCP
├── checklists/
│   └── requirements.md  # Checklist de calidad de especificación
└── tasks.md             # Tareas de ejecución (/speckit-tasks - Fase 2)
```

### Source Code (repository root)

```text
app/
├── __init__.py
├── config.py                 # Configuración pydantic-settings (.env)
├── database.py               # Motor SQLAlchemy, SessionLocal, get_db
├── dependencies.py           # get_current_user, get_gastos_repo
├── main.py                   # Inicialización FastAPI, montaje de routers y FastMCP
├── mcp/
│   ├── __init__.py
│   ├── server.py             # Instancia FastMCP y configuración streamable-http
│   └── tools/
│       ├── __init__.py
│       └── gastos.py         # Tools registrar_gasto y listar_gastos
├── models/
│   ├── __init__.py
│   ├── gasto.py              # Modelo SQLAlchemy Gasto
│   └── usuario.py            # Modelo SQLAlchemy Usuario
├── repositories/
│   ├── __init__.py
│   ├── gastos.py             # Módulo con guardar, listar, total_por_categoria
│   └── usuarios.py           # Módulo con obtener_por_email, guardar
├── routers/
│   ├── __init__.py
│   ├── gastos.py             # Endpoints POST /gastos/, GET /gastos/
│   └── usuarios.py           # Endpoints POST /usuarios/, POST /usuarios/token
├── schemas/
│   ├── __init__.py
│   ├── gasto.py              # GastoCreate, GastoOut
│   └── usuario.py            # UsuarioCreate, UsuarioOut, Token, TokenData
├── services/
│   ├── __init__.py
│   ├── auth.py               # Hashing bcrypt, creación y validación de JWT
│   └── gastos.py             # registrar_gasto, listar_gastos, CategoriaInvalidaError, LimiteExcedidoError
└── utils/
    ├── __init__.py
    └── security.py           # Funciones puras de verificación y formateo

alembic/
├── env.py
└── versions/

tests/
├── __init__.py               # Requerido explícitamente por el contrato
├── conftest.py               # Fixtures compartidas, TestClient, base de datos en memoria
├── api/
│   ├── __init__.py
│   ├── test_auth.py          # Pruebas de endpoints /usuarios/ y /usuarios/token
│   └── test_gastos_api.py    # Pruebas HTTP de /gastos/ con auth y errores
├── integration/
│   ├── __init__.py
│   └── test_repositories.py  # Pruebas de repositorios contra SQLite real
└── unit/
    ├── __init__.py
    ├── test_fakes.py         # Verificación del contrato de RepositorioFalso
    └── test_gastos_service.py# Pruebas de reglas de negocio inyectando RepositorioFalso
```

**Structure Decision**: Se adopta la estructura por capas modulares en `app/`, donde cada dominio (`gastos`, `usuarios`) cuenta con su archivo específico en cada capa (`models/`, `schemas/`, `repositories/`, `services/`, `routers/`), garantizando el desacoplamiento exigido por la Constitución v2.0.0.

## Complexity Tracking

> **No se registran violaciones a la Constitución**. Cada decisión técnica satisface de forma directa y justificada los 8 Artículos constitucionales.

| Decisión Arquitectónica | Justificación Constitucional | Alternativa Rechazada y Motivo |
|---|---|---|
| Inyección de dependencias con default (`repo=gastos_repository`) | Cumple Artículo II.3 (DIP) y permite tests unitarios aislados sin I/O | Importar el repositorio directamente dentro del servicio: rechazado por impedir el testeo con `RepositorioFalso` sin recurrir a `mock`. |
| Repositorio como módulo de funciones (no clase) | Cumple compatibilidad Sesiones 6-8 y Artículo II.4 (evitar complejidad artificial) | Clases abstractas / interfaces formales: rechazadas por introducir sobreingeniería no requerida en esta etapa del proyecto. |
| Repositorio retorna diccionarios planos (`dict`) | Cumple Artículo I.3 y aísla la persistencia de los servicios | Retornar instancias de modelos SQLAlchemy: rechazado porque acoplaría el ORM a la lógica de negocio. |
| FastMCP montado en FastAPI vía `streamable-http` | Cumple Artículo VI y unifica el ciclo de vida del servicio | Servidor MCP como proceso CLI separado: rechazado por mayor complejidad de despliegue y dificultad para compartir dependencias. |
