# Golden Real App — Technical Guide


## 0. Architecture Blueprint Matrix

| A42 ID | arc42 section | Technical realization | Slice refs | Verify |
|---|---|---|---|---|
| A42-01 | Introduction and Goals | Golden fixture proves real UI/API/DB/log verification | P01-S01-T001,P01-S01-T002 | run-golden-e2e |
| A42-03 | Context and Scope | Local HTML + stdlib HTTP API + temp SQLite + JSON log file | P01-S01-T001 | wiring contract |
| A42-04 | Solution Strategy | Single screen/journey lane, no fake data, direct persistence | all | next-wave + e2e |
| A42-05 | Building Block View | Handler, SQLite repository path, verification harness | all | task-packs |
| A42-06 | Runtime View | create/list/approve sequence in one isolated run | all | verify_golden_app.py |
| A42-08 | Crosscutting Concepts | validation, clean logging, cleanup, no external dependencies | all | runtime log check |
| A42-10 | Quality Requirements | reproducible deterministic test using provided fixture | all | run-golden-e2e --json |
| A42-11 | Risks and Technical Debt | auth intentionally not modeled in golden fixture | P01-S01-T001 | AUTH-001 |

## 1. Stack

Python stdlib + SQLite + JSON logs. No hay dependencias externas.

## 2. Contrato front -> back -> DB

### 2.1 Rutas/pantallas nuevas

| Ruta | Page | Auth | Journey refs | Endpoints consumidos | Estado cliente/provider | Estados UI obligatorios | Next action | Slice ID | Descripción |
|---|---|---|---|---|---|---|---|---|---|
| / | Home | none | J01,J02 | POST /api/v1/items, GET /api/v1/items, PATCH /api/v1/items/{id}, GET /api/v1/items/{id} | server-rendered HTML | loading, empty, error_validation, success | create/refresh/approve | P01-S01-T001 | formulario humano con botones reales |

### 2.2 Endpoints API nuevos

| Method | Path | Request | Response | Auth | Errors | Consumidor front/journey | Tablas/side effects | Slice ID |
|---|---|---|---|---|---|---|---|---|
| GET | /api/v1/items | none | items[] | none | none | J01,J02 | read items | P01-S01-T001 |
| GET | /api/v1/items/{id} | none | item | none | 404 DOMAIN_NOT_FOUND | J02 | read one item | P01-S01-T002 |
| POST | /api/v1/items | title, owner | item | none | 400 DOMAIN_VALIDATION_FAILED | J01 | insert items | P01-S01-T001 |
| PATCH | /api/v1/items/{id} | status | item | none | 404 DOMAIN_NOT_FOUND, 400 DOMAIN_VALIDATION_FAILED | J02 | update items | P01-S01-T002 |

### 2.3 Modelos / tablas

| Tabla | Campos mínimos | Índices / constraints | Slices |
|---|---|---|---|
| items | id, title, owner, status, created_at | title NOT NULL, owner NOT NULL, status allowlist en app | P01-S01-T001, P01-S01-T002 |

### 2.4 Domain Rules Implementation Matrix

| Rule ID | Enforced in | Endpoint | DB constraint | Service/use case | Front UX | Test/fixture | Slice ID |
|---|---|---|---|---|---|---|---|
| DR-001 | backend + DB + UI | POST /api/v1/items | title NOT NULL, owner NOT NULL | AL-001 create item | error_validation | fixtures/real_user_payload.json + empty-title rejection | P01-S01-T001 |
| DR-002 | backend + DB | PATCH /api/v1/items/{id} | id exists + status allowlist | AL-002 update item | success/not_found | SQLite row created by J01 | P01-S01-T002 |

### 2.5 Application/Core Logic Implementation Matrix

| Ref | Implemented in | Endpoint/job | Data touched | Error handling | Evaluation | Slice ID |
|---|---|---|---|---|---|---|
| AL-001 | Handler.do_POST + connect() | POST /api/v1/items | items insert | ERR-001 | EVAL-001 | P01-S01-T001 |
| AL-002 | Handler.do_PATCH + connect() | PATCH /api/v1/items/{id} | items update | ERR-002, ERR-003 | EVAL-002 | P01-S01-T002 |
| AL-003 | Handler.do_GET + connect() | GET /api/v1/items | items read | none | EVAL-003 | P01-S01-T001 |
| CORE-001 | creation validation path | POST /api/v1/items | items insert | ERR-001 | EVAL-001 | P01-S01-T001 |
| CORE-002 | state transition path | PATCH /api/v1/items/{id} | items status | ERR-002, ERR-003 | EVAL-002 | P01-S01-T002 |
| CORE-003 | list/read path | GET /api/v1/items | items read | none | EVAL-003 | P01-S01-T001 |

### 2.6 Policy, State, Failure, Integration and Audit Matrix

| Ref | Implementation detail | Evidence | Slice ID |
|---|---|---|---|
| AUTH-001 | no auth in local golden fixture; all local operator requests allowed | successful local requests | P01-S01-T001,P01-S01-T002 |
| STATE-001 | status allowlist {draft, approved} in Handler.do_PATCH | approved persisted in SQLite | P01-S01-T002 |
| ERR-001 | reject missing title/owner with DOMAIN_VALIDATION_FAILED | 400 response | P01-S01-T001 |
| ERR-002 | reject missing item with DOMAIN_NOT_FOUND | 404 response | P01-S01-T002 |
| ERR-003 | reject invalid status with DOMAIN_VALIDATION_FAILED | 400 response | P01-S01-T002 |
| INT-001 | verify script starts local server with temp SQLite/logs | run-golden-e2e JSON | P01-S01-T001,P01-S01-T002 |
| OBS-001 | JSON log domain_item_created | clean runtime logs | P01-S01-T001 |
| OBS-002 | JSON log domain_item_updated | clean runtime logs | P01-S01-T002 |
| OBS-003 | JSON log domain_validation_rejected | clean runtime logs | P01-S01-T001,P01-S01-T002 |

## 3. Verification Data Contract

| Data ID | Flow/Journey | Persona/Rol | Datos reales/proporcionados requeridos | Fuente de datos reales proporcionados | Reset/Cleanup | Refs lógicas | Slices/Journeys |
|---|---|---|---|---|---|---|---|
| VDATA-001 | J01,J02 | operador humano | title y owner reales/proporcionados | examples/golden-real-app/fixtures/real_user_payload.json | tempdir SQLite/logs por ejecución | AL-001,AL-002,CORE-001,CORE-002,DR-001,DR-002,EVAL-001,EVAL-002 | P01-S01-T001,P01-S01-T002 / J01,J02 |

## 4. Runtime logs

| Fuente | Comando | Debe estar limpio |
|---|---|---|
| app log | .claude/bin/check_runtime_logs.py --strict --json | sí, cero findings |
