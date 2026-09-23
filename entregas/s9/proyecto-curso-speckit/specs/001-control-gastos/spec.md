# Feature Specification: Sistema de Control de Gastos Personales

**Feature Branch**: `001-control-gastos`

**Created**: 2026-09-23

**Status**: Draft

**Input**: User description: "Sistema de control de gastos personales. Entidades: Usuario, Gasto. Reglas de negocio: Categorías válidas (comida, transporte, entretenimiento, otros), monto > 0, descripción no vacía, límite acumulado por categoría <= 500, aislamiento estricto por usuario. Contratos REST y MCP equivalentes. Contrato de compatibilidad con firmas exactas y casos de prueba explícitos."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Registro y Autenticación de Usuario (Priority: P1)

Como nuevo usuario del sistema, quiero registrarme con mi correo y contraseña, y obtener un token de acceso seguro para interactuar con mis gastos de forma privada y protegida.

**Why this priority**: Es la base de seguridad y aislamiento del sistema; sin autenticación no es posible asociar gastos a un usuario específico ni garantizar privacidad multiusuario.

**Independent Test**: Se puede probar registrando un usuario con credenciales válidas y solicitando un token JWT que permita autenticarse en peticiones subsecuentes.

**Acceptance Scenarios**:

1. **Given** un email no registrado y una contraseña válida, **When** el usuario solicita el registro (`POST /usuarios/`), **Then** el sistema responde con código 201, retorna el usuario creado sin exponer la contraseña (ni su hash), y persiste las credenciales de forma segura.
2. **Given** un email que ya existe en el sistema, **When** se intenta registrar nuevamente, **Then** el sistema responde con código 400 y mensaje descriptivo de email duplicado.
3. **Given** credenciales correctas (email y password), **When** se solicita el token (`POST /usuarios/token`), **Then** el sistema retorna código 200 con un token JWT válido de tipo Bearer.
4. **Given** credenciales incorrectas (password errónea o email inexistente), **When** se solicita el token, **Then** el sistema retorna código 401 (Unauthorized).

---

### User Story 2 - Registro de Gastos con Validación de Reglas de Negocio (Priority: P1)

Como usuario autenticado, quiero registrar un nuevo gasto especificando descripción, monto y categoría, para que el sistema valide que el gasto cumple con las reglas financieras permitidas y lo registre bajo mi cuenta.

**Why this priority**: Representa el núcleo del valor del producto: la captura controlada y validada de transacciones financieras personales.

**Independent Test**: Un usuario autenticado registra un gasto válido y el sistema confirma su persistencia, retornando los detalles del gasto creado y actualizando el acumulado de la categoría.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado y datos válidos (monto > 0, descripción no vacía, categoría permitida y monto acumulado resultante ≤ 500), **When** envía la solicitud (`POST /gastos/`), **Then** el sistema retorna 201 con los datos del gasto creado asociados al `usuario_id` del token.
2. **Given** un gasto con monto menor o igual a cero (≤ 0), **When** se intenta registrar, **Then** el sistema rechaza la operación con error de validación (código 400 / 422).
3. **Given** un gasto con descripción vacía o solo espacios en blanco, **When** se intenta registrar, **Then** el sistema rechaza la operación con error de validación (código 422).
4. **Given** un gasto con categoría no perteneciente a `[comida, transporte, entretenimiento, otros]`, **When** se intenta registrar, **Then** el sistema responde con código 400 indicando categoría inválida como error de negocio controlado.
5. **Given** una categoría cuyo acumulado actual más el nuevo monto supera 500.0, **When** el usuario intenta registrar el gasto, **Then** el sistema rechaza la operación con código 400 indicando límite de categoría excedido sin persistir el gasto.

---

### User Story 3 - Consulta y Listado Paginado de Gastos Propios (Priority: P2)

Como usuario autenticado, quiero consultar mi historial de gastos de forma paginada para revisar mis consumos personales sin riesgo de ver información de otros usuarios.

**Why this priority**: Permite la auditoría y visualización de la información registrada garantizando el aislamiento estricto de datos.

**Independent Test**: Dos usuarios registran gastos diferentes; al listar, cada uno observa exclusivamente sus propios registros, verificando los controles de paginación (`skip` y `limit`).

**Acceptance Scenarios**:

1. **Given** un usuario autenticado con gastos registrados, **When** solicita el listado (`GET /gastos/?skip=0&limit=20`), **Then** recibe código 200 con la lista de sus gastos exclusivamente.
2. **Given** un usuario autenticado, **When** intenta consultar gastos especificando un identificador de otro usuario en query params o headers no autorizados, **Then** el sistema ignora cualquier identificador externo y filtra únicamente por el `usuario_id` extraído del token JWT.
3. **Given** parámetros de paginación inválidos (e.g. `skip < 0` o `limit <= 0`), **When** se realiza la petición, **Then** el sistema responde con código 422 indicando error en los parámetros de consulta.

---

### User Story 4 - Interacción Mediante Herramientas MCP (Priority: P2)

Como usuario de un asistente o agente AI conectado vía Model Context Protocol (MCP), quiero invocar herramientas para registrar y listar mis gastos reutilizando las mismas reglas de negocio y seguridad que la API REST.

**Why this priority**: Asegura paridad funcional multicanal, permitiendo que agentes inteligentes operen sobre el sistema financiero del usuario con total consistencia y sin duplicación de lógica.

**Independent Test**: Invocar la tool MCP `registrar_gasto` y la tool `listar_gastos`, comprobando que ejecutan las mismas validaciones de negocio y devuelven estructuras uniformes.

**Acceptance Scenarios**:

1. **Given** una sesión MCP autenticada (transporte `streamable-http` con token), **When** se invoca `registrar_gasto(descripcion, monto, categoria)`, **Then** la tool ejecuta la validación en `services/`, persiste el gasto para el usuario del token y devuelve los datos del gasto.
2. **Given** una solicitud con categoría inválida o límite de 500 excedido desde MCP, **When** se invoca `registrar_gasto`, **Then** la tool retorna una estructura de error controlada (`{"error": "..."}`) sin interrumpir la sesión MCP ni generar un fallo no controlado.
3. **Given** una invocación a `listar_gastos(skip, limit)`, **When** se procesa la herramienta, **Then** devuelve la lista de gastos correspondientes a la identidad resuelta de la sesión.

---

### Edge Cases

- **Monto límite exacto**: Un gasto que hace que el acumulado de la categoría sea exactamente 500.0 debe ser aceptado; un gasto que resulte en 500.01 debe ser rechazado.
- **Monto cero o negativo**: Valores como `0`, `-0.01` o `-100` deben ser rechazados inmediatamente.
- **Inyección de espacios en blanco en descripción**: Strings compuestos únicamente por espacios (`"   "`) deben ser rechazados como descripción inválida.
- **Acceso sin token o con token expirado**: Cualquier intento de invocar endpoints o tools protegidas sin token válido debe retornar inmediatamente error 401 (Unauthorized).
- **Intento de spoofing de identidad**: Si una solicitud a `/gastos/` incluye en el cuerpo o en la URL un campo `usuario_id` distinto al autenticado, el sistema debe ignorarlo por completo y usar exclusivamente el `usuario_id` del token JWT.
- **Aislamiento de acumulados por usuario**: El límite de 500 por categoría es independiente por cada usuario; el gasto de un usuario no suma al límite de otro.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir el registro de nuevos usuarios mediante email y contraseña, asegurando unicidad en el campo email.
- **FR-002**: El sistema DEBE almacenar las contraseñas aplicando hashing seguro (`passlib[bcrypt]`), prohibiendo el almacenamiento o logging en texto plano.
- **FR-003**: El sistema DEBE autenticar usuarios mediante OAuth2 Password Flow y emitir tokens JWT firmados con algoritmo HS256 y tiempo de expiración configurable.
- **FR-004**: El sistema DEBE exigir token JWT válido en todas las operaciones sobre gastos (`/gastos/`), resolviendo la identidad del usuario autenticado mediante `get_current_user`.
- **FR-005**: El sistema DEBE validar que la categoría de un gasto pertenezca estrictamente a: `comida`, `transporte`, `entretenimiento`, `otros`. Cualquier otra categoría DEBE generar un error de negocio (`CategoriaInvalidaError`, HTTP 400).
- **FR-006**: El sistema DEBE validar que el monto de todo gasto sea estrictamente mayor a cero (`monto > 0`).
- **FR-007**: El sistema DEBE validar que la descripción de todo gasto no sea vacía ni contenga solo espacios en blanco.
- **FR-008**: El sistema DEBE controlar que la suma acumulada de gastos de un usuario en una categoría específica no supere el límite de 500.0 (`LIMITE_POR_CATEGORIA`). Si se supera, DEBE lanzar `LimiteExcedidoError` (HTTP 400).
- **FR-009**: El sistema DEBE garantizar el aislamiento de datos por usuario: un usuario solo puede crear y listar sus propios gastos. Ningún parámetro de entrada puede sobreescribir el `usuario_id` del token.
- **FR-010**: El sistema DEBE permitir listar gastos paginados con parámetros `skip` (por defecto 0) y `limit` (por defecto 20).
- **FR-011**: El sistema DEBE exponer el servidor MCP con tools `registrar_gasto(descripcion, monto, categoria)` y `listar_gastos(skip, limit)` que reutilicen directamente las funciones de `services/`.
- **FR-012**: Las tools MCP DEBEN retornar errores de negocio estructurados (`{"error": "..."}`) sin lanzar excepciones no controladas.
- **FR-013**: En transporte `streamable-http`, MCP DEBE resolver la identidad del token verificado; en transporte `stdio`, DEBE utilizar el usuario demo configurado en `.env` documentando la simplificación.
- **FR-014**: El sistema DEBE responder con códigos HTTP semánticos: `201` para creación, `200` para consultas, `400` para errores de regla de negocio conocidos, `401` para fallos de autenticación, `404` para recursos no encontrados, `422` para fallos de validación de schema, y `500` con `{"detail": "Error interno del servidor"}` para excepciones genéricas.
- **FR-015**: El sistema DEBE separar estrictamente los schemas de entrada (`GastoCreate`) y salida (`GastoOut`), prohibiendo exponer directamente modelos ORM.

### Compatibility & Architectural Constraints (Non-Negotiable)

Para garantizar compatibilidad binaria y cumplir con la Constitución v2.0.0, la solución DEBE implementar con precisión milimétrica las siguientes firmas y estructuras:

1. **`app/services/gastos.py`**:
   - Excepciones: `CategoriaInvalidaError`, `LimiteExcedidoError`.
   - Constante: `LIMITE_POR_CATEGORIA = 500.0`.
   - Funciones (orden posicional exacto, `repo` keyword con default por DIP):
     - `registrar_gasto(db, usuario_id, descripcion, monto, categoria, repo=gastos_repository) -> dict`
     - `listar_gastos(db, usuario_id, skip=0, limit=20, repo=gastos_repository) -> list[dict]`
2. **`app/repositories/gastos.py`** (módulo con funciones puras, NO clase):
   - `guardar(db, usuario_id, descripcion, monto, categoria) -> dict`
   - `listar(db, usuario_id, skip=0, limit=20) -> list[dict]`
   - `total_por_categoria(db, usuario_id, categoria) -> float`
   - Retorno obligatorio de `dict` (o listas de `dict`), nunca instancias directas de modelos ORM.
3. **`app/repositories/usuarios.py`**:
   - `obtener_por_email(db, email) -> Usuario | None`
   - `guardar(db, email, hashed_password) -> Usuario`
4. **Módulos y Símbolos de Integración**:
   - `app.database.get_db`
   - `app.dependencies.get_current_user`
   - `app.dependencies.get_gastos_repo`
   - `app.models.usuario.Usuario(id=, email=, hashed_password=)`
5. **Estructura de Pruebas**:
   - `tests/__init__.py` DEBE existir.
   - Tests unitarios inyectan repositorios falsos sin `unittest.mock`.
   - Cobertura de reglas del 100%, cobertura de líneas de `services/` ≥ 90%, y global ≥ 80%.

### Key Entities

- **Usuario**:
  - `id`: Identificador único (entero o UUID).
  - `email`: Cadena única válida, no nula.
  - `hashed_password`: Hash seguro de la contraseña.
  - *Relaciones*: Posee 0 a N instancias de `Gasto`.
- **Gasto**:
  - `id`: Identificador único.
  - `usuario_id`: Clave foránea al `Usuario` propietario (obligatoria).
  - `descripcion`: Texto descriptivo (no vacío).
  - `monto`: Valor numérico positivo (`monto > 0`).
  - `categoria`: Valor enumerado (`comida`, `transporte`, `entretenimiento`, `otros`).
  - `fecha` / `created_at`: Marca temporal de creación.
- **Categoria**:
  - Valores permitidos: `comida`, `transporte`, `entretenimiento`, `otros`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% de las 5 reglas de negocio explícitas (categoría válida, monto > 0, descripción no vacía, límite de 500 por categoría y aislamiento de usuario) están verificadas mediante pruebas unitarias e integración automatizadas.
- **SC-002**: Cero exposición de contraseñas o hashes en cualquier respuesta de la API o del servidor MCP (tasa de fuga = 0%).
- **SC-003**: 100% de los intentos de consulta o modificación de recursos ajenos son bloqueados o ignorados, garantizando aislamiento total.
- **SC-004**: Los endpoints de creación y listado de gastos responden en menos de 200 ms en condiciones normales de desarrollo/pruebas locales.
- **SC-005**: Cobertura de código superior al 90% en la capa de servicios (`services/`) y superior al 80% en el acumulado global de la aplicación.

## Assumptions

- Se utiliza SQLite como motor de base de datos para desarrollo y pruebas locales, compatible con PostgreSQL para despliegues.
- El límite acumulado de 500.0 aplica sobre el total histórico de gastos registrados en la categoría por el usuario hasta el momento (a menos que se especifique un período mensual mediante una enmienda posterior).
- Los clientes MCP disponen del contexto necesario para enviar parámetros `descripcion`, `monto` y `categoria` de forma estructurada.
- Las variables de entorno `SECRET_KEY`, `DATABASE_URL` y `ACCESS_TOKEN_EXPIRE_MINUTES` se suministran a través de un archivo `.env` basado en `.env.example`.
