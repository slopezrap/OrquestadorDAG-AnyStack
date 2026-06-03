# {{APP_NAME}} Technical Guide — minimal DAG

## Screen/Journey Lane Redactor Contract

- No modeles la app como `backend/API primero`, luego `frontend`, y `UX polish` al final. Esa separación rompe la pantalla aunque los tests pasen.
- Cada pantalla importante debe nacer de una **screen/journey lane**: contrato de pantalla + contrato API/datos + implementación conectada + estados UX obligatorios + verificación del journey.
- Las slices de API/backend pueden existir separadas sólo si son foundation real o contrato técnico que alimenta una pantalla/journey nombrado en `Journey refs`.
- Criterio de cierre de pantalla: datos reales/proporcionados conectados front -> back -> DB, estados `loading`, `empty`, `error_network`, `error_validation`, `permission_denied` cuando aplique, `success`, navegación/next action, responsive básico y accesibilidad básica.
- Granularidad: crea tantas slices como hagan falta para cerrar cada pantalla/journey lane verificable de punta a punta. No hagas una slice por botón/componente pequeño; tampoco cierres una pantalla sólo porque compila.
- Defectos dentro de la pantalla actual van por `validator/tester -> debugger -> retest`. Sólo crea FU si falta trabajo nuevo fuera de scope: pantalla, endpoint, tabla, journey, contrato de datos reales o decisión humana no declarada.

> Perfil: **minimal**. Guía técnica suficiente para que planner/developer/tester no adivinen contratos.

## Cadena lógica obligatoria de la app

Rellena cada documento siguiendo esta cadena. No es una lista decorativa: cada eslabón debe poder referenciarse desde el `Canonical Coverage Registry` y desde los task-packs del orquestador.

```text
Journey -> Application Logic -> Core Logic -> Domain Rules
        -> Permissions -> State -> Errors -> Data -> Integrations -> UI -> Audit -> Verify
```

- `Journey` (`J-*`): recorrido real del usuario, con pantallas, acciones y estado final observable.
- `Application Logic` (`AL-*`): caso de uso interno que coordina entradas, permisos, reglas, estado, datos, integraciones y salida visible.
- `Core Logic` (`CORE-*`): algoritmo, motor central, workflow especializado, cálculo, scoring, ranking, matching, recomendador o lógica crítica del producto. Si no aplica, decláralo como `NO APLICA` con razón; no lo omitas.
- `Domain Rules` (`DR-*`): invariantes del negocio que nunca deben romperse.
- `Permissions` (`AUTH-*`): quién puede hacer qué, sobre qué recurso, cuándo se permite y cuándo se deniega.
- `State` (`STATE-*`): estados válidos, transiciones válidas y transiciones prohibidas.
- `Errors` (`ERR-*`): fallos esperados, comportamiento, mensaje visible, impacto en estado, retry/idempotencia y recovery.
- `Data` (`DATA-*`): ciclo de vida de datos, creación, mutación, borrado, retención, ownership y restricciones.
- `Integrations` (`INT-*`): sistemas externos/internos, side effects, idempotencia, retry, timeouts y comportamiento en fallo.
- `UI` (`UI-*`): comportamiento exacto de pantalla ante loading, empty, error, permission denied, success, datos reales y next action.
- `Audit` (`OBS-*`): eventos, logs, campos obligatorios, evidencia y trazabilidad.
- `Verify` (`EVAL-*` y `Verify mínimo`): cómo se demuestra con datos reales/proporcionados que la slice funciona.

Regla: si una slice menciona un eslabón de la cadena, debe citar su ID en la columna correspondiente del registry. Si no aplica, usa `—` con sentido; no dejes celdas vacías.


## Architecture Blueprint overlay (arc42 / `A42-*`)

Además de la cadena lógica, documenta la arquitectura con un overlay inspirado en arc42. No es un sexto documento obligatorio: vive repartido entre `instrucciones.md`, `*_TECHNICAL_GUIDE.md`, `STACK_PROFILE.yaml`, `UX_CONTRACT.md` y el `Canonical Coverage Registry`.

`A42-*` captura lo que la cadena lógica no debe perder: objetivos de arquitectura, restricciones, contexto/scope, estrategia de solución, building blocks, runtime view, deployment view, conceptos transversales, decisiones, requisitos de calidad, riesgos/deuda y glosario.

Usa estos IDs canónicos cuando apliquen:

| A42 ID | arc42 section | Qué debe contener | Dónde se aterriza |
|---|---|---|---|
| A42-01 | Introduction and Goals | objetivos, stakeholders, drivers y quality goals top | `instrucciones.md` + `TECHNICAL_GUIDE §1` |
| A42-02 | Constraints | restricciones técnicas, organizativas, legales, UX, datos y stack | `instrucciones.md` + `STACK_PROFILE.yaml` |
| A42-03 | Context and Scope | límites del sistema, actores externos, APIs externas, sistemas vecinos | `instrucciones.md` + `TECHNICAL_GUIDE §3/§6` |
| A42-04 | Solution Strategy | decisiones arquitectónicas principales y trade-offs | `TECHNICAL_GUIDE` + ADRs |
| A42-05 | Building Block View | módulos, capas, componentes, bounded contexts, paquetes y ownership | `TECHNICAL_GUIDE` |
| A42-06 | Runtime View | escenarios dinámicos, journeys técnicos, secuencias y flujos críticos | `TECHNICAL_GUIDE` + `UX_CONTRACT` |
| A42-07 | Deployment View | entornos, runtime, contenedores, workers, DB, cloud/local y puertos | `STACK_PROFILE.yaml` + `TECHNICAL_GUIDE` |
| A42-08 | Crosscutting Concepts | auth, logging, error handling, idempotencia, caching, i18n, seguridad | `TECHNICAL_GUIDE` + contratos `AUTH/ERR/OBS` |
| A42-09 | Architecture Decisions | ADRs reales con alternativas y consecuencias | `TECHNICAL_GUIDE` ADR section |
| A42-10 | Quality Requirements | escenarios de calidad: performance, seguridad, mantenibilidad, usabilidad | `instrucciones.md` + `EVAL-*` |
| A42-11 | Risks and Technical Debt | riesgos conocidos, deuda aceptada, mitigaciones y seguimiento | `instrucciones.md` + checklist hardening |
| A42-12 | Glossary | glosario técnico y de dominio que evita ambigüedad | `instrucciones.md` + `TECHNICAL_GUIDE` |

Regla: cada slice que implemente o verifique una decisión arquitectónica, componente transversal, despliegue, runtime crítico, quality scenario, riesgo o ADR debe citar sus `A42-*` en `Architecture refs`. Si no aplica, usa `—`; no dejes celdas vacías.


## 0. Architecture Blueprint Matrix (arc42 / `A42-*`)

> Esta matriz aterriza el overlay arc42 en decisiones técnicas concretas. Debe estar sincronizada con `instrucciones.md §3.1.10`, `STACK_PROFILE.yaml`, ADRs y `Architecture refs` del Coverage Registry.

| A42 ID | arc42 section | Technical realization | Modules / files / services | Runtime/deployment impact | Quality scenario / verification | ADR / risk link | Slice refs |
|---|---|---|---|---|---|---|---|
| A42-01 | Introduction and Goals | {{TECH_GOALS_REALIZATION}} | {{TECH_GOAL_MODULES}} | {{TECH_GOAL_RUNTIME_IMPACT}} | {{TECH_GOAL_VERIFY}} | {{ADR_OR_RISK_01}} | {{SLICE_IDS_01}} |
| A42-02 | Constraints | {{TECH_CONSTRAINT_REALIZATION}} | {{TECH_CONSTRAINT_MODULES}} | {{TECH_CONSTRAINT_RUNTIME_IMPACT}} | {{TECH_CONSTRAINT_VERIFY}} | {{ADR_OR_RISK_02}} | {{SLICE_IDS_02}} |
| A42-03 | Context and Scope | {{TECH_CONTEXT_REALIZATION}} | {{TECH_CONTEXT_MODULES}} | {{TECH_CONTEXT_RUNTIME_IMPACT}} | {{TECH_CONTEXT_VERIFY}} | {{ADR_OR_RISK_03}} | {{SLICE_IDS_03}} |
| A42-04 | Solution Strategy | {{TECH_SOLUTION_STRATEGY}} | {{TECH_SOLUTION_MODULES}} | {{TECH_SOLUTION_RUNTIME_IMPACT}} | {{TECH_SOLUTION_VERIFY}} | {{ADR_OR_RISK_04}} | {{SLICE_IDS_04}} |
| A42-05 | Building Block View | {{TECH_BUILDING_BLOCKS}} | {{TECH_BUILDING_BLOCK_MODULES}} | {{TECH_BUILDING_BLOCK_RUNTIME_IMPACT}} | {{TECH_BUILDING_BLOCK_VERIFY}} | {{ADR_OR_RISK_05}} | {{SLICE_IDS_05}} |
| A42-06 | Runtime View | {{TECH_RUNTIME_SCENARIOS}} | {{TECH_RUNTIME_MODULES}} | {{TECH_RUNTIME_IMPACT}} | {{TECH_RUNTIME_VERIFY}} | {{ADR_OR_RISK_06}} | {{SLICE_IDS_06}} |
| A42-07 | Deployment View | {{TECH_DEPLOYMENT_TOPOLOGY}} | {{TECH_DEPLOYMENT_FILES}} | {{ENVIRONMENTS_AND_PORTS}} | {{DEPLOY_VERIFY}} | {{ADR_OR_RISK_07}} | {{SLICE_IDS_07}} |
| A42-08 | Crosscutting Concepts | {{TECH_CROSSCUTTING}} | {{CROSSCUTTING_MODULES}} | {{CROSSCUTTING_RUNTIME_IMPACT}} | {{CROSSCUTTING_VERIFY}} | {{ADR_OR_RISK_08}} | {{SLICE_IDS_08}} |
| A42-09 | Architecture Decisions | {{ADR_SUMMARY}} | {{ADR_FILES_OR_SECTION}} | {{ADR_RUNTIME_IMPACT}} | {{ADR_VERIFY}} | ADR-001+ | {{SLICE_IDS_09}} |
| A42-10 | Quality Requirements | {{QUALITY_SCENARIOS_TECH}} | {{QUALITY_TEST_MODULES}} | {{QUALITY_RUNTIME_IMPACT}} | {{QUALITY_VERIFY}} | {{ADR_OR_RISK_10}} | {{SLICE_IDS_10}} |
| A42-11 | Risks and Technical Debt | {{RISK_TECH_DEBT}} | {{RISK_AFFECTED_MODULES}} | {{RISK_RUNTIME_IMPACT}} | {{RISK_VERIFY_OR_MONITOR}} | {{RISK_IDS}} | {{SLICE_IDS_11}} |
| A42-12 | Glossary | {{TECH_GLOSSARY}} | {{GLOSSARY_DOC_LOCATIONS}} | {{GLOSSARY_RUNTIME_IMPACT_OR_NO_APLICA}} | {{GLOSSARY_VERIFY}} | {{ADR_OR_RISK_12}} | {{SLICE_IDS_12}} |

Rellenado obligatorio:

- No escribas frases genéricas como “arquitectura modular” sin módulos, archivos o servicios concretos.
- `A42-05` debe poder convertirse en carpetas/módulos/slices.
- `A42-06` debe describir escenarios runtime que el tester/verifier pueda ejecutar o simular.
- `A42-07` debe estar alineado con `STACK_PROFILE.yaml`.
- `A42-10` debe enlazar con `EVAL-*` o comandos de verificación medibles.
- `A42-11` debe producir slices de hardening/follow-up cuando el riesgo no pueda cerrarse en el MVP.

## 1. Stack

La fuente única del stack es `STACK_PROFILE.yaml`. Resume aquí solo las decisiones de arquitectura que derivan de ese perfil:

- Frontend: `{{frontend.framework}}` en `{{frontend.module_root}}`.
- Backend: `{{backend.framework}}` en `{{backend.module_root}}`.
- DB: `{{db.engine}}`.
- Auth: {{AUTH_MODE}}.
- Comandos: frontend `{{frontend.test_cmd}}`, backend `{{backend.test_cmd}}`, migración `{{db.migrate_cmd}}`.

## 2. Contrato front -> back -> DB

### 2.1 Rutas/pantallas nuevas

| Ruta | Page | Auth | Journey refs | Endpoints consumidos | Estado cliente/provider | Estados UI obligatorios | Next action | Slice ID | Descripción |
|---|---|---|---|---|---|---|---|---|---|
| {{ROUTE_1}} | {{PAGE_1}} | {{AUTH}} | J1 | {{ENDPOINT_1}} | {{PROVIDER_1}} | loading, empty, error_network, error_validation, success | {{NEXT_ACTION_1}} | {{SLICE_UI_1}} | {{DESC_1}} |
| {{ROUTE_2_OPCIONAL}} | {{PAGE_2}} | {{AUTH}} | J1 | {{ENDPOINT_2}} | {{PROVIDER_2}} | loading, empty, error_network, success | {{NEXT_ACTION_2}} | {{SLICE_UI_2}} | {{DESC_2}} |

### 2.2 Endpoints API nuevos

| Method | Path | Request | Response | Auth | Errors | Consumidor front/journey | Tablas/side effects | Slice ID |
|---|---|---|---|---|---|---|---|---|
| {{METHOD_1}} | {{PATH_1}} | {{REQUEST_1}} | {{RESPONSE_1}} | {{AUTH}} | 400, 401, 500 | {{PAGE_1}} / J1 | {{TABLE_1}} | {{SLICE_API_1}} |
| {{METHOD_2_OPCIONAL}} | {{PATH_2}} | {{REQUEST_2}} | {{RESPONSE_2}} | {{AUTH}} | 400, 401, 404, 500 | {{PAGE_2}} / J1 | {{TABLE_2}} | {{SLICE_API_2}} |

### 2.3 Modelos / tablas

| Tabla | Campos mínimos | Índices / constraints | Slices |
|---|---|---|---|
| {{TABLE_1}} | {{FIELDS_1}} | {{CONSTRAINTS_1}} | {{SLICE_DB_1}} |

### 2.4 Domain Rules Implementation Matrix

> Cada `DR-*` declarado en `instrucciones.md` debe aparecer aquí y en `Domain rule refs` del Coverage Registry cuando una slice lo implemente o verifique.

| Rule ID | Enforced in | Endpoint | DB constraint | Service/use case | Front UX | Test/fixture | Slice ID |
|---|---|---|---|---|---|---|---|
| DR-001 | backend + db + frontend | {{ENDPOINT_1}} | {{DOMAIN_DB_CONSTRAINT_001}} | {{DOMAIN_USECASE_001}} | {{DOMAIN_UX_001}} | {{DOMAIN_TEST_001}} | {{SLICE_API_1}} |
| DR-002 | backend + frontend | {{ENDPOINT_2}} | {{DOMAIN_DB_CONSTRAINT_002}} | {{DOMAIN_USECASE_002}} | {{DOMAIN_UX_002}} | {{DOMAIN_TEST_002}} | {{SLICE_UI_1}} |

### 12.0.1 Application/Core Logic Implementation Matrix

> Esta matriz aterriza `AL-*` y `CORE-*` en servicios, módulos, jobs, endpoints y tests. La lógica especializada no debe quedar sólo narrada en instrucciones.

| Ref ID | Implemented in | Entry point | Inputs/outputs typed | Transactions/idempotency | Tests/evidence | Slice ID |
|---|---|---|---|---|---|---|
| AL-001 | {{APPLICATION_SERVICE_001}} | {{ENTRYPOINT_001}} | {{DTO_OR_SCHEMA_001}} | {{TX_IDEMPOTENCY_001}} | {{AL_TEST_001}} | {{AL_SLICE_001}} |
| CORE-001 | {{CORE_MODULE_001}} | {{CORE_FUNCTION_001}} | {{CORE_TYPES_001}} | {{CORE_REPRODUCIBILITY_001}} | {{CORE_TEST_001}} | {{CORE_SLICE_001}} |

### 12.0.2 Policy, State, Failure, Integration and Audit Matrix

| Ref ID | Enforcement location | Endpoint/route/job | Storage/side effect | User-visible behavior | Test/evidence | Slice ID |
|---|---|---|---|---|---|---|
| AUTH-001 | {{AUTH_ENFORCEMENT_001}} | {{AUTH_SURFACE_001}} | {{AUTH_STORAGE_001}} | {{AUTH_UX_001}} | {{AUTH_TEST_001}} | {{AUTH_SLICE_001}} |
| STATE-001 | {{STATE_ENFORCEMENT_001}} | {{STATE_SURFACE_001}} | {{STATE_STORAGE_001}} | {{STATE_UX_001}} | {{STATE_TEST_001}} | {{STATE_SLICE_001}} |
| ERR-001 | {{ERR_ENFORCEMENT_001}} | {{ERR_SURFACE_001}} | {{ERR_STATE_STORAGE_001}} | {{ERR_UX_001}} | {{ERR_TEST_001}} | {{ERR_SLICE_001}} |
| INT-001 | {{INT_ENFORCEMENT_001}} | {{INT_SURFACE_001}} | {{INT_SIDE_EFFECT_001}} | {{INT_UX_001}} | {{INT_TEST_001}} | {{INT_SLICE_001}} |
| DATA-001 | {{DATA_ENFORCEMENT_001}} | {{DATA_SURFACE_001}} | {{DATA_STORAGE_001}} | {{DATA_UX_001}} | {{DATA_TEST_001}} | {{DATA_SLICE_001}} |
| OBS-001 | {{OBS_ENFORCEMENT_001}} | {{OBS_SURFACE_001}} | {{OBS_STORAGE_001}} | {{OBS_UX_001}} | {{OBS_TEST_001}} | {{OBS_SLICE_001}} |
| EVAL-001 | {{EVAL_ENFORCEMENT_001}} | {{EVAL_SURFACE_001}} | {{EVAL_ARTIFACT_001}} | {{EVAL_VISIBLE_RESULT_001}} | {{EVAL_TEST_001}} | {{EVAL_SLICE_001}} |

## 3. Verification Data Contract

| Flow/Journey | Persona/Rol | Datos reales/proporcionados requeridos | Fuente de datos reales proporcionados | Reset/Cleanup | Slices/Journeys |
|---|---|---|---|---|---|
| J1 | {{PERSONA}} | {{REAL_DATA}} | {{FIXTURE_CMD}} | {{RESET_CMD}} | {{SLICE_IDS}} / J1 |

## 4. Testing mínimo

| Capa | Comando | Evidencia esperada |
|---|---|---|
| API | {{API_TEST_CMD}} | tests verdes con DB real con datos proporcionados |
| Frontend | {{frontend.test_cmd}} | UI states y provider conectados |
| Verify | /verify-slice + /verify-journey J1 | front -> back -> DB observado |

## Final self-review before delivery

- [ ] Cada `J-*` referencia `AL-*`, `CORE-*` si aplica, `DR-*`, `AUTH-*`, `STATE-*`, `ERR-*`, `UI-*`, `DATA-*`, `OBS-*` y `EVAL-*`.
- [ ] Cada slice tiene `Depends on`, `Conflict group`, `Write set`, `Acceptance mínimo` y `Verify mínimo`.
- [ ] Cada pantalla tiene loading, empty, error, permission denied si aplica, success y next action.
- [ ] Cada flujo tiene datos reales/proporcionados para verificación.
- [ ] No quedan placeholders, IDs rotos ni secciones vacías.


## Verification Data Implementation Matrix

Define cómo se implementan los datos reales/proporcionados declarados en `instrucciones.md`. El objetivo es que `/verify-slice` pueda levantar la app, cargar datos válidos y comprobar front -> back -> DB/logs sin inventar fixtures decorativos.

| Data Fixture ID | Implemented by | Command/path | Tables/files/external accounts | Reset behavior | Used by journeys | Used by CORE/EVAL | Evidence |
|---|---|---|---|---|---|---|---|
| VDATA-001 | {{{{script_or_manual_setup}}}} | {{{{seed_or_import_cmd}}}} | DATA-001 | idempotent reset | J-001 | CORE-001/EVAL-001 | DB row + log + screenshot |

Rules:

- [ ] Seed/import scripts are idempotent.
- [ ] Test credentials/secrets are not committed.
- [ ] External accounts/files are named as provided inputs or blockers.
- [ ] Data freshness/staleness rules are implemented when relevant.
- [ ] Evidence paths are compatible with `orchestrator-state/tasks/evidence/<TASK_ID>/`.


## Technical final self-review

Before delivering the filled `*_TECHNICAL_GUIDE.md`, ChatGPT must fix these issues in-place:

- [ ] Every route in `UX_CONTRACT.md` exists in the route/screen section.
- [ ] Every endpoint used by a journey or screen has method, path, request, response, auth, errors and tests.
- [ ] Every `AL-*` and `CORE-*` has an implementation home: service/module/job/worker/endpoint.
- [ ] Every `STATE-*` transition is enforced server-side or explicitly justified.
- [ ] Every `ERR-*` has API error shape and user-visible mapping.
- [ ] Every `INT-*` has timeout, retry, idempotency and audit behavior.
- [ ] Every `DATA-*` has schema/table/file/store lifecycle and retention/delete behavior.
- [ ] Every `OBS-*` has log/audit event name and required fields.
- [ ] Every `EVAL-*` has deterministic command/test/evidence.
- [ ] Every technical item that needs work has a slice in the Coverage Registry.
