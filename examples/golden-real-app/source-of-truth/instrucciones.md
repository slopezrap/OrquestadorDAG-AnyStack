# Golden Real App — Instrucciones source-of-truth

## 1. Identidad

- Nombre: Golden Real App
- Objetivo: fixture real para comprobar que el orquestador verifica UI/API/DB/logs sin stubs ni datos inventados.
- Usuario: operador humano que crea, lista y actualiza registros.
- Superficie: web HTML mínima + API HTTP stdlib + SQLite + logs JSON.

## 2. Alcance funcional

| Feature ID | Feature | Pantalla/Ruta | Endpoint principal | Tabla/side effect | Valor |
|---|---|---|---|---|---|
| F1 | Crear item real | / | POST /api/v1/items | items | registro persistido |
| F2 | Aprobar item real | / | PATCH /api/v1/items/{id} | items | transición persistida |
| F3 | Listar items reales | / | GET /api/v1/items | items | lectura persistida visible por control Refresh list |

## 2.5 Domain Logic Contract

| Rule ID | Regla | Tipo | Aplica a | Fuente/razón | Error esperado | Verificación |
|---|---|---|---|---|---|---|
| DR-001 | Todo item debe persistirse con title no vacío y owner proporcionado | invariant | POST /api/v1/items, items | F1/J01 | 400 DOMAIN_VALIDATION_FAILED | fixture real + rechazo de title vacío |
| DR-002 | Solo se pueden actualizar items existentes con estado permitido | state | PATCH /api/v1/items/{id}, items | F2/J02 | 404 DOMAIN_NOT_FOUND o 400 DOMAIN_VALIDATION_FAILED | registro real creado y transición approved |

## 2.6 Application Logic Contract

| App Logic ID | Caso de uso | Trigger | Pasos internos obligatorios | Outputs | Refs |
|---|---|---|---|---|---|
| AL-001 | Crear item real proporcionado | Operador envía formulario o POST con fixture real | validar title/owner; aplicar DR-001; insertar en SQLite; registrar `domain_item_created`; devolver item | item persisted con status draft | J01, CORE-001, DR-001, DATA-001, OBS-001 |
| AL-002 | Aprobar item existente | Operador solicita PATCH sobre item creado | cargar item; aplicar DR-002; validar status allowlist; actualizar SQLite; registrar `domain_item_updated`; devolver item | item persisted con status approved | J02, CORE-002, DR-002, STATE-001, OBS-002 |
| AL-003 | Listar items persistidos | Operador pulsa Refresh list o GET | consultar SQLite ordenado por id; devolver items reales; no inventar rows | lista de items | J01,J02, CORE-003, DATA-001 |

## 2.7 Core Logic Contract

| Core ID | Nombre | Propósito | Inputs | Algoritmo / pasos | Outputs | Evaluación |
|---|---|---|---|---|---|---|
| CORE-001 | Motor mínimo de creación validada | Convertir un payload real proporcionado en un registro persistido válido | title, owner | trim; validar no vacío; insertar con status draft y created_at; devolver fila creada | item draft | EVAL-001 |
| CORE-002 | Motor mínimo de transición de estado | Aplicar transición controlada sobre item existente | item_id, status | comprobar existencia; validar status en {draft, approved}; actualizar status | item actualizado | EVAL-002 |
| CORE-003 | Motor mínimo de lectura persistida | Exponer datos persistidos sin stubs | SQLite items | SELECT id,title,owner,status ORDER BY id | lista real | EVAL-003 |

## 2.8 Permission Logic Contract

| Auth ID | Actor | Resource | Action | Allowed when | Denied when | Error/behavior | Applies to |
|---|---|---|---|---|---|---|---|
| AUTH-001 | Operador humano local | item | create/read/update | entorno golden local sin autenticación productiva | no aplica en fixture | none; fixture intentionally public local | J01,J02,AL-001,AL-002 |

## 2.9 State Logic Contract

| State ID | Entidad | Estados válidos | Transiciones válidas | Transiciones prohibidas | Applies to |
|---|---|---|---|---|---|
| STATE-001 | item.status | draft, approved | draft -> approved, approved -> draft si se solicita explícitamente en API fixture | cualquier status fuera de allowlist | DR-002, AL-002, CORE-002 |

## 2.10 Failure Logic Contract

| Error ID | Escenario | Comportamiento esperado | User/API message | State impact | Recovery | Verify |
|---|---|---|---|---|---|---|
| ERR-001 | title u owner vacío al crear item | Rechazar request y no insertar row | DOMAIN_VALIDATION_FAILED | no DB write | corregir payload y reintentar | EVAL-001 |
| ERR-002 | item inexistente al actualizar | Rechazar request | DOMAIN_NOT_FOUND | no DB write | usar id existente | EVAL-002 |
| ERR-003 | status fuera de allowlist | Rechazar request | DOMAIN_VALIDATION_FAILED | no DB write | usar draft o approved | EVAL-002 |

## 2.11 Data Lifecycle Logic Contract

| Data ID | Entidad | Created by | Mutable fields | Immutable fields | Delete behavior | Audit required |
|---|---|---|---|---|---|---|
| DATA-001 | items | AL-001 / POST /api/v1/items | status | id, title, owner, created_at en fixture golden | temp SQLite por ejecución; cleanup automático por verify_golden_app.py | OBS-001, OBS-002 |

## 2.12 Integration / Side Effect Logic Contract

| Integration ID | Trigger | External/system boundary | Action | Idempotency/failure policy | Applies to |
|---|---|---|---|---|---|
| INT-001 | run-golden-e2e / verify_golden_app.py | local HTTP server + temp SQLite + JSON log file | iniciar app, ejercer UI/API, comprobar DB/logs | tempdir aislado por ejecución; cleanup en finally | J01,J02,EVAL-001,EVAL-002 |

## 2.13 Observability / Audit Contract

| Obs ID | Event | When | Required fields | Used for | Applies to |
|---|---|---|---|---|---|
| OBS-001 | domain_item_created | tras crear item válido | id, owner | demostrar side effect real y logs limpios | AL-001,CORE-001 |
| OBS-002 | domain_item_updated | tras transición de estado | id, status | demostrar transición persistida y logs limpios | AL-002,CORE-002 |
| OBS-003 | domain_validation_rejected | cuando DR-001/DR-002 bloquea request | reason, id si aplica | demostrar error esperado no tratado como crash | ERR-001,ERR-003 |

## 2.14 Evaluation Logic Contract

| Eval ID | Evalúa | Método determinista | Datos | Evidencia esperada | Applies to |
|---|---|---|---|---|---|
| EVAL-001 | creación + DR-001 | `python3 -B -S examples/golden-real-app/verify_golden_app.py --json` | fixtures/real_user_payload.json + title vacío | item creado y DOMAIN_VALIDATION_FAILED para inválido | CORE-001,DR-001 |
| EVAL-002 | transición + DR-002 | `python3 -B -S examples/golden-real-app/verify_golden_app.py --json` | item creado en la misma ejecución | status approved persistido en SQLite | CORE-002,DR-002,STATE-001 |
| EVAL-003 | lectura persistida | `python3 -B -S examples/golden-real-app/verify_golden_app.py --json` | SQLite temp con item creado | Refresh list control presente y GET /api/v1/items declarado | CORE-003,DATA-001 |


## 2.15 Architecture Blueprint Contract

| A42 ID | arc42 section | Decisión / contenido concreto | Impacto en slices | Verify |
|---|---|---|---|---|
| A42-01 | Introduction and Goals | Fixture golden debe probar una app real mínima con UI/API/DB/logs | P01-S01-T001, P01-S01-T002 | run-golden-e2e |
| A42-03 | Context and Scope | El sistema incluye HTML local, API HTTP stdlib, SQLite temporal y log JSON | P01-S01-T001 | wiring + golden e2e |
| A42-04 | Solution Strategy | Construcción screen/journey lane con datos reales/proporcionados | ambas slices | next_wave + verify |
| A42-05 | Building Block View | app.py contiene UI, API router mínimo, servicio y persistencia SQLite | ambas slices | task-pack + e2e |
| A42-06 | Runtime View | Crear, listar y aprobar item en una ejecución temporal aislada | ambas slices | verify_golden_app.py |
| A42-08 | Crosscutting Concepts | Validación, error handling, logs JSON y cleanup en finally | ambas slices | logs clean |
| A42-10 | Quality Requirements | La prueba debe usar datos reales/proporcionados y no stubs | ambas slices | run-golden-e2e --json |
| A42-11 | Risks and Technical Debt | Fixture no representa auth productiva; se documenta como límite intencional | P01-S01-T001 | AUTH-001 indica fixture local público |

## 3. Journey Coverage Matrix

| ID | Milestone | Pantallas/Screens | Acciones/Actions | Endpoints | Tablas/Tables | Estado cliente/Client state | Slices | Verificación/Verification |
|---|---|---|---|---|---|---|---|---|
| J01 | Crear item real | / | completar formulario y pulsar Create real record; pulsar Refresh list | POST /api/v1/items, GET /api/v1/items | items | loading, empty, error_validation, success | P01-S01-T001 | ./scripts/run-golden-e2e.sh --json |
| J02 | Aprobar item real | / | transición approved sobre registro persistido | PATCH /api/v1/items/{id}, GET /api/v1/items/{id} | items | success, not_found, error_validation | P01-S01-T002 | ./scripts/run-golden-e2e.sh --json |

## 4. Reglas de verificación real

- Solo se aceptan datos reales/proporcionados desde `examples/golden-real-app/fixtures/real_user_payload.json`.
- La verificación debe tocar controles humanos reales, persistir en SQLite y revisar logs limpios.
- La verificación debe cubrir la cadena `Journey -> Application Logic -> Core Logic -> Domain Rules -> Permissions -> State -> Errors -> Data -> Integrations -> UI -> Audit -> Verify` al nivel mínimo necesario para este fixture.
