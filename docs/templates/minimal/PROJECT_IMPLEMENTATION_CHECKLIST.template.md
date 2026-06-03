# {{APP_NAME}} Implementation Checklist — minimal DAG

## Screen/Journey Lane Redactor Contract

- No modeles la app como `backend/API primero`, luego `frontend`, y `UX polish` al final. Esa separación rompe la pantalla aunque los tests pasen.
- Cada pantalla importante debe nacer de una **screen/journey lane**: contrato de pantalla + contrato API/datos + implementación conectada + estados UX obligatorios + verificación del journey.
- Las slices de API/backend pueden existir separadas sólo si son foundation real o contrato técnico que alimenta una pantalla/journey nombrado en `Journey refs`.
- Criterio de cierre de pantalla: datos reales/proporcionados conectados front -> back -> DB, estados `loading`, `empty`, `error_network`, `error_validation`, `permission_denied` cuando aplique, `success`, navegación/next action, responsive básico y accesibilidad básica.
- Granularidad: crea tantas slices como hagan falta para cerrar cada pantalla/journey lane verificable de punta a punta. No hagas una slice por botón/componente pequeño; tampoco cierres una pantalla sólo porque compila.
- Defectos dentro de la pantalla actual van por `validator/tester -> debugger -> retest`. Sólo crea FU si falta trabajo nuevo fuera de scope: pantalla, endpoint, tabla, journey, contrato de datos reales o decisión humana no declarada.

> Perfil: **minimal**. El `Canonical Coverage Registry` es la fuente del DAG. Declara todas las tasks y phases necesarias, con dependencias reales. El bootstrap debe terminar en `mode=explicit_dag`, siempre `explicit_dag`.


## Modelo Phase / Step / Slice para generar una app completa

- **Phase** = milestone o módulo de producto con sentido para la visión global; no es un lote arbitrario de tareas.
- **Step** = lane coherente dentro de la phase: pantalla/journey lane, módulo de dominio, foundation lane o contrato API que alimenta una pantalla nombrada.
- **Slice/Task** = unidad ejecutable y verificable por un worker, con `Depends on`, `Write set`, `Conflict group`, `Journey refs` y `Verify mínimo` claros.
- Granularidad sana: una phase agrupa milestones/módulos coherentes y un step agrupa lanes relacionadas. No dividas ni fusiones por números; divide cuando mezcle lanes no relacionadas, pierda trazabilidad, tenga ownership distinto o bloquee paralelismo real.
- Mantén visión de app: cada slice debe conectar con una feature, endpoint, tabla, journey o foundation real; nada de slices decorativas.
- Sustituye todos los ejemplos por el dominio real de la app. Si falta un dato real para verificar, bloquea o registra follow-up; no inventes cargas no proporcionadas ni datos de relleno.

## Canonical Coverage Registry

| Slice ID | Tipo | Target | Step | Product increment | Build state | Risk level | Verify mode | Depends on | Conflict group | Write set | Journey refs | Pantalla/Ruta | Endpoint | Tablas DB | Origen-Instr | Origen-TechGuide | Acceptance mínimo | Verify mínimo | Domain rule refs | Architecture refs | Application logic refs | Core logic refs | Permission refs | State refs | Failure refs | Integration refs | UI refs | Data refs | Observability refs | Evaluation refs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P00-S01-T001 | db | {{MIGRATION_OR_SCHEMA_CHANGE}} | Step 0.1 | v1 | planned | low | auto | — | db:migrations | {{db_migration_write_set}}; {{backend_test_write_set}} | — | — | — | {{TABLE_1}} | §2.1 | §2.3#{{TABLE_1}} | migración/schema y constraints | {{db.migrate_cmd}} && {{backend.test_cmd}} | {{DOMAIN_RULE_REFS}} | {{ARCHITECTURE_REFS_OR_—}} | {{AL_REFS_OR_—}} | {{CORE_REFS_OR_—}} | {{AUTH_REFS_OR_—}} | {{STATE_REFS_OR_—}} | {{ERR_REFS_OR_—}} | {{INT_REFS_OR_—}} | {{UI_REFS_OR_—}} | {{DATA_REFS_OR_—}} | {{OBS_REFS_OR_—}} | {{EVAL_REFS_OR_—}} |
| P01-S01-T001 | api | {{ENDPOINT_1}} | Step 1.1 | v1 | planned | medium | human | P00-S01-T001 | api:{{DOMAIN}} | {{backend.module_root}}/**/{{DOMAIN}}*; {{backend_test_write_set}} | J1 | {{PAGE_1}} {{ROUTE_1}} | {{ENDPOINT_1}} | {{TABLE_1}} | §3#J1 | §2.2#{{ENDPOINT_1}} | endpoint real con DB y auth | {{backend.test_cmd}} | {{DOMAIN_RULE_REFS}} | {{ARCHITECTURE_REFS_OR_—}} | {{AL_REFS_OR_—}} | {{CORE_REFS_OR_—}} | {{AUTH_REFS_OR_—}} | {{STATE_REFS_OR_—}} | {{ERR_REFS_OR_—}} | {{INT_REFS_OR_—}} | {{UI_REFS_OR_—}} | {{DATA_REFS_OR_—}} | {{OBS_REFS_OR_—}} | {{EVAL_REFS_OR_—}} |
| P02-S01-T001 | frontend | {{PAGE_1}} | Step 2.1 | v1 | planned | medium | human | P01-S01-T001 | front:{{DOMAIN}}, navigation | {{frontend.module_root}}/**/{{DOMAIN}}*; {{frontend_test_write_set}}; {{frontend_navigation_write_set}} | J1 | {{PAGE_1}} {{ROUTE_1}} | {{ENDPOINT_1}} | — | §3#J1 | §2.1#{{ROUTE_1}} | estados UI y provider conectados | /verify-slice con datos reales/proporcionados | {{DOMAIN_RULE_REFS}} | {{ARCHITECTURE_REFS_OR_—}} | {{AL_REFS_OR_—}} | {{CORE_REFS_OR_—}} | {{AUTH_REFS_OR_—}} | {{STATE_REFS_OR_—}} | {{ERR_REFS_OR_—}} | {{INT_REFS_OR_—}} | {{UI_REFS_OR_—}} | {{DATA_REFS_OR_—}} | {{OBS_REFS_OR_—}} | {{EVAL_REFS_OR_—}} |
| P03-S01-T001 | journey | J1 e2e | Step 3.1 | v1 | planned | high | human | P02-S01-T001 | journey:{{DOMAIN}} | orchestrator-state/tasks/journey-handoffs/** | J1 | {{PAGE_SEQUENCE}} | {{ENDPOINT_SEQUENCE}} | {{TABLES}} | §3#J1 | §3 Verification Data Contract | J1 verificado de punta a punta | /verify-journey J1 | {{DOMAIN_RULE_REFS}} | {{ARCHITECTURE_REFS_OR_—}} | {{AL_REFS_OR_—}} | {{CORE_REFS_OR_—}} | {{AUTH_REFS_OR_—}} | {{STATE_REFS_OR_—}} | {{ERR_REFS_OR_—}} | {{INT_REFS_OR_—}} | {{UI_REFS_OR_—}} | {{DATA_REFS_OR_—}} | {{OBS_REFS_OR_—}} | {{EVAL_REFS_OR_—}} |

## Phase 0 — Data foundation
#
## Step 0.0 — Architecture blueprint / arc42 foundation

- [ ] Rellenar `A42-01..A42-12` con decisiones concretas de la app, no texto genérico.
- [ ] Confirmar que `A42-03` define límites del sistema e integraciones vecinas.
- [ ] Confirmar que `A42-04` y `A42-05` explican estrategia y building blocks antes de crear slices de código.
- [ ] Confirmar que `A42-06` enlaza runtime scenarios con journeys, `AL-*` y `CORE-*`.
- [ ] Confirmar que `A42-07` coincide con `STACK_PROFILE.yaml` y runtime per-slice.
- [ ] Confirmar que `A42-08` cubre auth, error handling, idempotencia, logging y observabilidad.
- [ ] Confirmar que `A42-10` enlaza quality scenarios con `EVAL-*` o verify mínimo medible.
- [ ] Confirmar que riesgos `A42-11` tienen mitigación, slice de hardening o follow-up explícito.
- [ ] Cada slice que implemente arquitectura transversal debe citar `Architecture refs`.

## Step 0.1 — Schema
- [ ] P00-S01-T001

## Phase 1 — J1 screen/journey lane
### Step 1.1 — Contrato API que alimenta la pantalla J1
- [ ] P01-S01-T001

## Phase 2 — J1 connected screen lane
### Step 2.1 — Pantalla conectada + estados UX
- [ ] P02-S01-T001

## Phase 3 — J1 journey verification gate
### Step 3.1 — Verify e2e
- [ ] P03-S01-T001

## Runtime Follow-up Coverage Registry

> Append-only. ChatGPT lo deja vacío. El orquestador añade filas aquí si QA descubre trabajo nuevo.


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


## Final self-review before delivery

- [ ] Cada `J-*` referencia `AL-*`, `CORE-*` si aplica, `DR-*`, `AUTH-*`, `STATE-*`, `ERR-*`, `UI-*`, `DATA-*`, `OBS-*` y `EVAL-*`.
- [ ] Cada slice tiene `Depends on`, `Conflict group`, `Write set`, `Acceptance mínimo` y `Verify mínimo`.
- [ ] Cada pantalla tiene loading, empty, error, permission denied si aplica, success y next action.
- [ ] Cada flujo tiene datos reales/proporcionados para verificación.
- [ ] No quedan placeholders, IDs rotos ni secciones vacías.


## Dependencias DAG obligatorias

`Depends on` es obligatorio en todas las filas. Usa `—` sólo para roots reales. Si una fila omite `Depends on`, el source-of-truth está mal formado para `production = explicit_dag`.

## Logic coverage self-review

- [ ] Cada slice tiene `Depends on`, `Conflict group`, `Write set` y `Verify mínimo`.
- [ ] Cada slice visible referencia `Journey refs`, `Application logic refs`, `UI refs` y datos reales/proporcionados.
- [ ] Cada slice con lógica central referencia `Core logic refs` y `Evaluation refs`.
- [ ] Cada slice con permisos/estado/errores referencia `Permission refs`, `State refs` y `Failure refs`.
