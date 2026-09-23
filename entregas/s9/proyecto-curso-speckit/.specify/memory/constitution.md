<!--
Sync Impact Report:
- Version change: 1.0.0 -> 2.0.0
- Modified principles:
  - I. Spec-Driven & Test-First Development -> I. Arquitectura en Capas
  - II. Clean Architecture & Layer Separation -> II. SOLID Aplicado (No Teórico)
  - III. Strict API Contracts & Static Typing -> III. Persistencia
  - IV. Robust Security, Authentication & Error Handling -> IV. Seguridad (No Negociable)
  - V. Simplicity & YAGNI -> V. Diseño de Endpoints REST
- Added principles:
  - VI. MCP: Tools y Reutilización
  - VII. Testing y Cobertura
  - VIII. Compatibilidad y Evolución
- Added sections:
  - Restricciones Técnicas y de Configuración (replaces [SECTION_2_NAME])
  - Flujo de Trabajo y Quality Gates (replaces [SECTION_3_NAME])
- Removed sections:
  - None
- Follow-up TODOs:
  - None
-->

# Control de Gastos Constitution

## Core Principles

### I. Arquitectura en Capas
1. `routers/` reciben la solicitud HTTP, delegan al service correspondiente y traducen su resultado (o excepción) a una respuesta HTTP. Un router NUNCA valida reglas de negocio (ej. "el monto debe ser positivo") — esa lógica vive exclusivamente en `services/`.
2. `services/` contienen toda la lógica de negocio. Un service NUNCA importa SQLAlchemy, `Session`, ni ningún detalle de persistencia directamente.
3. `repositories/` son la única capa autorizada a leer o escribir en la base de datos. Un repository no contiene reglas de negocio, solo operaciones de persistencia (guardar, listar, buscar, sumar).
4. `utils/` son funciones puras (mismo input → mismo output, sin efectos secundarios), sin importar nada de `services/`, `routers/` ni `repositories/`.
5. `mcp/tools/` NUNCA reimplementan lógica de `services/`. Si una tool de MCP y un router necesitan la misma regla, ambos DEBEN llamar al mismo service.
*Rationale: Asegura desacoplamiento estricto, facilita el testing unitario y centraliza las reglas de negocio evitando divergencias entre la API y las tools de MCP.*

### II. SOLID Aplicado (No Teórico)
1. **SRP (Responsabilidad Única)**: Cada función de `services/` hace una sola cosa. La validación (`_validar_x`) está separada de la orquestación (`registrar_x`).
2. **OCP (Abierto/Cerrado)**: Agregar una categoría, un tipo de gasto o una regla nueva se hace agregando un valor a una constante o `Enum`, nunca reescribiendo un bloque `if` condicional ya existente.
3. **DIP (Inversión de Dependencias)**: Todo service que necesite un repository lo DEBE recibir como parámetro con un valor por defecto (`def registrar_gasto(..., repo=gastos_repo)`), nunca importarlo fijo dentro del cuerpo de la función. Esto es innegociable: es lo que permite testear sin recurrir a `unittest.mock`.
4. **Pragmatismo**: No se fuerza LSP ni ISP si el proyecto no tiene jerarquías de clases ni interfaces formales — está prohibido agregar complejidad artificial para cumplir un principio que no aplica todavía.
*Rationale: Mantiene el código simple, extensible y testeable de forma natural sin sobreingeniería.*

### III. Persistencia
1. Se utiliza SQLAlchemy como ORM y Alembic para migraciones. Queda estrictamente PROHIBIDA cualquier sentencia SQL cruda concatenada con strings.
2. SQLite se emplea en desarrollo; el código de `database.py` DEBE funcionar contra Postgres sin tocar `services/` ni `routers/` (usar `connect_args` condicional solo para SQLite).
3. Cada modelo con datos de usuario DEBE incluir `usuario_id` como FK. Ninguna consulta de datos de usuario puede omitir el filtro por `usuario_id`.
*Rationale: Previene inyecciones SQL, asegura portabilidad entre motores de base de datos y garantiza aislamiento multiusuario.*

### IV. Seguridad (No Negociable)
1. **Contraseñas**: Hash obligatorio con `passlib[bcrypt]`. NUNCA se guarda ni se loguea una contraseña en texto plano.
2. **Autenticación**: OAuth2 password flow + JWT firmado con HS256. `ACCESS_TOKEN_EXPIRE_MINUTES` configurable, nunca infinito.
3. **Gestión de Secretos**: `SECRET_KEY` y `DATABASE_URL` viven solo en `.env` (nunca versionado en git). `.env.example` documenta las variables necesarias sin valores reales. `SECRET_KEY` se genera con `openssl rand -hex 32` o equivalente criptográficamente seguro, nunca escrito a mano.
4. **Autorización Estricta**: El `usuario_id` para filtrar, crear o modificar un gasto SIEMPRE proviene del token JWT decodificado (`get_current_user`), NUNCA de un parámetro de la URL, del body, ni de un query param. Esto aplica también a recursos ya existentes: cualquier operación sobre un gasto por `id` (leer, actualizar, eliminar) primero verifica obligatoriamente que ese gasto pertenece al usuario autenticado, antes de modificarlo o devolverlo.
5. **Manejo Seguro de Errores**: Un error no controlado (`Exception` genérica) devuelve `500` con `{"detail": "Error interno del servidor"}` — nunca un stack trace ni el mensaje de la excepción original al cliente. El detalle técnico sí se loguea internamente.
6. **Validación Temprana**: Toda entrada de usuario se valida obligatoriamente con schemas Pydantic antes de llegar a `services/`.
*Rationale: Protege la confidencialidad, integridad y aislamiento de datos de cada usuario frente a vulnerabilidades como IDOR o fuga de información.*

### V. Diseño de Endpoints REST
1. **Convención de Verbos y Códigos HTTP**:
   - `POST` crea (`201`).
   - `GET` lista o lee (`200`).
   - Fallo de autenticación (`401`).
   - Recurso no encontrado (`404`).
   - Error de validación de schema (`422`).
   - Error de regla de negocio conocido (`400` con `{"detail": "..."}`).
   - `403` se reserva exclusivamente para cuando el recurso solicitado existe pero pertenece a otro usuario y la operación lo identifica por `id` explícito en la ruta (ej. `PATCH /gastos/{id}`).
   - Un listado (`GET /gastos/`) NUNCA devuelve `403` — simplemente filtra por el `usuario_id` del JWT y nunca expone ni acepta el de otro usuario.
2. **Paginación**: Toda lista paginada expone `skip` y `limit` como query params, con valores por defecto razonables (ej. `skip=0, limit=20`). Valores inválidos (negativos, no numéricos) son error de schema (`422`).
3. **Separación de Schemas**: Los schemas de entrada y salida son obligatoriamente distintos (`GastoCreate` vs `GastoOut`) — nunca se expone el modelo de SQLAlchemy directamente.
*Rationale: Asegura una API REST predecible, semántica, segura y con contratos de datos claramente desacoplados de la persistencia.*

### VI. MCP: Tools y Reutilización
1. Cada tool de MCP llama directamente a una función de `services/`. Si una tool necesita lógica que no existe en `services/`, esa lógica se agrega en `services/` primero, y la tool la reutiliza — nunca al revés.
2. La descripción de cada tool DEBE ser específica y accionable (ej. "Registra un gasto con descripción, monto y categoría, validando el límite mensual por categoría"), nunca genérica ("maneja gastos").
3. Errores de negocio se devuelven como una estructura clara (`{"error": "..."}`), nunca como una excepción sin controlar que rompa la sesión del cliente MCP.
4. **Transporte e Identidad**:
   - Si el transporte es `stdio` y no hay forma de propagar identidad real de usuario, se documenta explícitamente en el código como simplificación consciente (comentario explicativo), nunca como un olvido silencioso.
   - Si el transporte es `streamable-http` y hay un token verificado, la tool DEBE usar la identidad de ese token (nunca un usuario demo hardcodeado) — el usuario demo es solo el fallback legítimo cuando no hay ningún token disponible.
5. **Acciones Destructivas**: Cualquier tool con efecto destructivo (ej. `eliminar_gasto`) DEBE requerir confirmación explícita gestionada por el servidor, nunca depender de que el modelo de IA decida preguntar por su cuenta.
*Rationale: Convierte el servidor MCP en una interfaz de consumo idéntica a la API HTTP, garantizando paridad de reglas y estabilidad para el cliente MCP.*

### VII. Testing y Cobertura
1. **Pirámide de Pruebas**: Obligatoria: unitarias (mayoría) → integración → API/E2E (minoría).
2. **Sin Mock de Repositorios**: Los tests unitarios de `services/` inyectan un repositorio falso (que cumple el mismo contrato que el real) como parámetro — está terminantemente PROHIBIDO usar `unittest.mock` para esto, porque el diseño con DIP ya lo hace innecesario.
3. **Cobertura Mínima Exigida**:
   - **100% de las reglas de negocio explícitas de `spec.md`** cubiertas por al menos un test unitario cada una (ej. categoría inválida, límite excedido, monto inválido) — cobertura de *reglas*, no solo de líneas.
   - Cobertura de líneas de `services/` ≥ 90%.
   - Cobertura de líneas del conjunto `services/` + `repositories/` + `routers/` + `utils/` ≥ 80%.
*Rationale: Garantiza verificación real del comportamiento del negocio sin tests frágiles acoplados a implementaciones internas.*

### VIII. Compatibilidad y Evolución
1. Cambios en `repositories/` pueden agregar parámetros (ej. `db`, `usuario_id`) pero NO deben romper el contrato de negocio que ya utiliza `services/`.
2. Toda nueva funcionalidad que no sea una extensión directa de la actual merece su propio ciclo completo `/speckit-specify → /speckit-plan → /speckit-tasks → /speckit-implement`, en lugar de sobrecargar la especificación existente hasta volverla ilegible.
*Rationale: Mantiene la estabilidad de los contratos internos y promueve la modularidad e incrementalidad del desarrollo.*

## Restricciones Técnicas y de Configuración
- **Lenguaje y Entorno**: Python 3.10+ gestionado mediante `uv` o entorno virtual estándar.
- **Framework Web**: FastAPI con routers modulares en `routers/`.
- **Validación y Serialización**: Pydantic v2 con schemas diferenciados para entrada y salida en `schemas/`.
- **Capa de Datos**: SQLAlchemy 2.0+ con modelos en `models/` y migraciones declarativas mediante Alembic.
- **Protocolo MCP**: Servidor MCP exponiendo herramientas en `mcp/tools/` conectadas a `services/`.
- **Pruebas Automatizadas**: `pytest` para la suite completa de unitarias e integración.

## Flujo de Trabajo y Quality Gates
1. **Gate de Especificación**: Antes de implementar, la funcionalidad debe contar con su especificación formal (`spec.md`) alineada a las reglas de negocio.
2. **Gate de Arquitectura**: Ningún commit o PR debe mezclar capas (routers con lógica de negocio, services con SQLAlchemy o SQL crudo).
3. **Gate de Testing y Cobertura**:
   - Ejecución exitosa de `pytest` al 100%.
   - Cobertura de reglas del 100%.
   - Cobertura de código ≥ 90% en `services/` y ≥ 80% global.
4. **Gate de Seguridad**: Verificación estricta de extracción de `usuario_id` desde JWT y ausencia de secretos en el control de versiones.

## Governance
Esta Constitución es la autoridad técnica y arquitectónica suprema del proyecto Control de Gastos y prevalece sobre cualquier otra práctica, convención no escrita o atajo de implementación.
- **Principio Fundamental de Desviación**: Si el agente necesita desviarse de cualquier artículo de esta constitución al implementar, DEBE señalarlo explícitamente y esperar aprobación antes de continuar — nunca decidir la desviación en silencio.
- **Procedimiento de Enmiendas**: Toda modificación o ampliación a estos artículos debe documentarse, justificarse y registrarse a través del flujo `/speckit-constitution`.
- **Política de Versionado (SemVer)**:
  - **MAJOR**: Cambios incompatibles con las reglas de gobierno, eliminación o redefinición de artículos constitucionales.
  - **MINOR**: Incorporación de nuevos artículos, herramientas o expansión material de guías sin contradecir las previas.
  - **PATCH**: Correcciones de formato, erratas tipográficas y refinamientos no semánticos.
- **Revisión de Cumplimiento**: Todas las especificaciones (`spec.md`), planes (`plan.md`), tareas (`tasks.md`) y revisiones de código deben verificar y certificar activamente el cumplimiento de estos 8 artículos.

**Version**: 2.0.0 | **Ratified**: 2026-09-23 | **Last Amended**: 2026-09-23
