# {{APP_NAME}} — Instrucciones minimal DAG

## Screen/Journey Lane Redactor Contract

- No modeles la app como `backend/API primero`, luego `frontend`, y `UX polish` al final. Esa separación rompe la pantalla aunque los tests pasen.
- Cada pantalla importante debe nacer de una **screen/journey lane**: contrato de pantalla + contrato API/datos + implementación conectada + estados UX obligatorios + verificación del journey.
- Las slices de API/backend pueden existir separadas sólo si son foundation real o contrato técnico que alimenta una pantalla/journey nombrado en `Journey refs`.
- Criterio de cierre de pantalla: datos reales/proporcionados conectados front -> back -> DB, estados `loading`, `empty`, `error_network`, `error_validation`, `permission_denied` cuando aplique, `success`, navegación/next action, responsive básico y accesibilidad básica.
- Granularidad: crea tantas slices como hagan falta para cerrar cada pantalla/journey lane verificable de punta a punta. No hagas una slice por botón/componente pequeño; tampoco cierres una pantalla sólo porque compila.
- Defectos dentro de la pantalla actual van por `validator/tester -> debugger -> retest`. Sólo crea FU si falta trabajo nuevo fuera de scope: pantalla, endpoint, tabla, journey, contrato de datos reales o decisión humana no declarada.

> Perfil: **minimal**. Usa este template para una app pequeña sin existing baseline. Debe producir una app real/MVP de producción con todas las phases, tasks y journeys reales necesarios, siempre con `mode=explicit_dag`.
>
> Este documento define negocio, UX y journeys. Debe cablearse con `<APP>_TECHNICAL_GUIDE.md` y `<APP>_IMPLEMENTATION_CHECKLIST.md`.

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

## 1. Identidad

- **Nombre**: {{APP_NAME}}
- **Problema de negocio**: {{PROBLEMA_CONCRETO}}
- **Usuario objetivo**: {{USUARIO_OBJETIVO}}
- **Resultado visible del MVP**: {{RESULTADO_VISIBLE}}
- **Métrica de éxito**: {{METRICA}}

## 2. Alcance minimal

### 2.1 Features

Declara solo features reales del MVP. Para cada feature, define pantalla, acción principal y dato persistido.

| Feature ID | Feature | Pantalla/Ruta | Endpoint principal | Tabla/side effect | Valor para usuario |
|---|---|---|---|---|---|
| F1 | {{FEATURE_1}} | {{PAGE_1}} {{ROUTE_1}} | {{ENDPOINT_1}} | {{TABLE_1}} | {{VALOR_1}} |
| F2 | {{FEATURE_2_OPCIONAL}} | {{PAGE_2}} {{ROUTE_2}} | {{ENDPOINT_2}} | {{TABLE_2}} | {{VALOR_2}} |

### 2.1.1 Domain Logic Contract

> La lógica de dominio canónica vive aquí, dentro de `instrucciones.md`. No añadas un sexto documento obligatorio. El Technical Guide debe aterrizar estas reglas en `Domain Rules Implementation Matrix` y el Checklist debe referenciarlas en `Domain rule refs`.

#### Glosario de dominio

| Término | Definición | No confundir con |
|---|---|---|
| {{DOMAIN_TERM_1}} | {{DOMAIN_DEFINITION_1}} | {{NOT_THIS_1}} |

#### Entidades de dominio

| Entity | Descripción | Estado/lifecycle | Owner | Reglas asociadas |
|---|---|---|---|---|
| {{DOMAIN_ENTITY_1}} | {{DOMAIN_ENTITY_DESCRIPTION_1}} | {{DOMAIN_STATES_1}} | {{DOMAIN_OWNER_1}} | DR-001 |

#### Reglas de dominio

| Rule ID | Regla | Tipo | Aplica a | Fuente/razón | Error esperado | Verificación |
|---|---|---|---|---|---|---|
| DR-001 | {{DOMAIN_RULE_001}} | invariant | {{DOMAIN_ENTITY_1}}, {{ENDPOINT_1}} | F1 / J1 | {{DOMAIN_ERROR_001}} | {{DOMAIN_VERIFY_001}} |
| DR-002 | {{DOMAIN_RULE_002}} | authorization/state/calculation | {{DOMAIN_ENTITY_1}}, {{ENDPOINT_2}} | F2 / J1 | {{DOMAIN_ERROR_002}} | {{DOMAIN_VERIFY_002}} |

#### Máquinas de estado / lifecycle

| Entity | Estados válidos | Transiciones válidas | Transiciones prohibidas |
|---|---|---|---|
| {{DOMAIN_ENTITY_1}} | {{VALID_STATES_1}} | {{VALID_TRANSITIONS_1}} | {{FORBIDDEN_TRANSITIONS_1}} |

#### Casos límite de dominio

| Case ID | Descripción | Resultado esperado | Datos reales/proporcionados |
|---|---|---|---|
| DC-001 | {{DOMAIN_EDGE_CASE_001}} | {{DOMAIN_EDGE_RESULT_001}} | {{DOMAIN_EDGE_DATA_001}} |

### 2.1.2 Application Logic Contract

> La lógica de aplicación describe los casos de uso internos que coordinan entradas, permisos, reglas, estado, datos, integraciones y salida visible. IDs `AL-*`.

| AL ID | Caso de uso | Trigger | Actor | Preconditions | Pasos internos | Outputs | Refs |
|---|---|---|---|---|---|---|---|
| AL-001 | {{APP_USE_CASE_001}} | {{TRIGGER_001}} | {{ACTOR_001}} | {{PRECONDITIONS_001}} | {{STEPS_001}} | {{OUTPUTS_001}} | DR-001, CORE-001, AUTH-001, STATE-001, ERR-001 |

### 2.1.3 Core Logic Contract

> La lógica central es el motor especializado de la app: algoritmo, scoring, pricing, matching, ranking, recomendador, cálculo, workflow crítico o cualquier núcleo que no deba quedar implícito. IDs `CORE-*`.

| Core ID | Nombre | Propósito | Inputs | Parámetros | Algoritmo / pasos | Outputs | Verificación mínima |
|---|---|---|---|---|---|---|---|
| CORE-001 | {{CORE_NAME_001}} | {{CORE_PURPOSE_001}} | {{CORE_INPUTS_001}} | {{CORE_PARAMS_001}} | {{CORE_STEPS_001}} | {{CORE_OUTPUTS_001}} | {{CORE_VERIFY_001}} |

### 2.1.4 Permission Logic Contract

| Auth ID | Actor | Resource | Action | Allowed when | Denied when | Error |
|---|---|---|---|---|---|---|
| AUTH-001 | {{ACTOR_001}} | {{RESOURCE_001}} | {{ACTION_001}} | {{ALLOW_CONDITION_001}} | {{DENY_CONDITION_001}} | 401/403 {{ERROR_CODE_001}} |

### 2.1.5 State Logic Contract

| State ID | Entity / process | Estados válidos | Transiciones válidas | Transiciones prohibidas | Verificación |
|---|---|---|---|---|---|
| STATE-001 | {{STATE_ENTITY_001}} | {{STATE_VALUES_001}} | {{STATE_TRANSITIONS_001}} | {{STATE_FORBIDDEN_001}} | {{STATE_VERIFY_001}} |

### 2.1.6 Failure Logic Contract

| Error ID | Scenario | Expected behavior | User message | State change | Retry? | Applies to |
|---|---|---|---|---|---|---|
| ERR-001 | {{FAILURE_SCENARIO_001}} | {{FAILURE_BEHAVIOR_001}} | {{FAILURE_MESSAGE_001}} | {{FAILURE_STATE_CHANGE_001}} | {{RETRY_POLICY_001}} | AL-001, J1 |

### 2.1.7 Data and Observability Logic

| ID | Tipo | Qué debe quedar definido | Retención / evidencia | Applies to |
|---|---|---|---|---|
| DATA-001 | data lifecycle | {{DATA_CREATION_MUTATION_DELETION_001}} | {{DATA_RETENTION_001}} | AL-001 |
| OBS-001 | audit/trace | {{AUDIT_EVENT_001}} | {{AUDIT_FIELDS_001}} | AL-001, CORE-001 |
| EVAL-001 | evaluation | {{EVAL_CRITERIA_001}} | {{EVAL_EVIDENCE_001}} | CORE-001 |

### 2.2 Fuera de alcance

- {{FUERA_1}}
- {{FUERA_2}}




#### 3.1.10 Architecture Blueprint Contract (`A42-*` / arc42 overlay)

> Esta sección evita que la arquitectura quede repartida en frases sueltas. Usa `A42-*` para conectar decisiones arquitectónicas con slices, quality scenarios, deployment, runtime y riesgos. No dupliques `AL-*` ni `CORE-*`: aquí explicas el marco arquitectónico que permite implementarlos sin ambigüedad.

| A42 ID | arc42 section | Decisión / contenido concreto | Drivers / constraints | Impacto en módulos/slices | Quality scenario / verify | Riesgo si se ignora |
|---|---|---|---|---|---|---|
| A42-01 | Introduction and Goals | {{ARCH_GOALS_AND_STAKEHOLDERS}} | {{ARCH_DRIVERS_01}} | {{ARCH_SLICE_IMPACT_01}} | {{ARCH_VERIFY_01}} | {{ARCH_RISK_01}} |
| A42-02 | Constraints | {{TECH_ORG_LEGAL_CONSTRAINTS}} | {{ARCH_DRIVERS_02}} | {{ARCH_SLICE_IMPACT_02}} | {{ARCH_VERIFY_02}} | {{ARCH_RISK_02}} |
| A42-03 | Context and Scope | {{SYSTEM_BOUNDARIES_AND_EXTERNALS}} | {{ARCH_DRIVERS_03}} | {{ARCH_SLICE_IMPACT_03}} | {{ARCH_VERIFY_03}} | {{ARCH_RISK_03}} |
| A42-04 | Solution Strategy | {{SOLUTION_STRATEGY}} | {{ARCH_DRIVERS_04}} | {{ARCH_SLICE_IMPACT_04}} | {{ARCH_VERIFY_04}} | {{ARCH_RISK_04}} |
| A42-05 | Building Block View | {{BUILDING_BLOCKS_AND_OWNERSHIP}} | {{ARCH_DRIVERS_05}} | {{ARCH_SLICE_IMPACT_05}} | {{ARCH_VERIFY_05}} | {{ARCH_RISK_05}} |
| A42-06 | Runtime View | {{RUNTIME_SCENARIOS_AND_SEQUENCES}} | {{ARCH_DRIVERS_06}} | {{ARCH_SLICE_IMPACT_06}} | {{ARCH_VERIFY_06}} | {{ARCH_RISK_06}} |
| A42-07 | Deployment View | {{DEPLOYMENT_ENVIRONMENTS_AND_TOPOLOGY}} | {{ARCH_DRIVERS_07}} | {{ARCH_SLICE_IMPACT_07}} | {{ARCH_VERIFY_07}} | {{ARCH_RISK_07}} |
| A42-08 | Crosscutting Concepts | {{CROSSCUTTING_CONCEPTS}} | {{ARCH_DRIVERS_08}} | {{ARCH_SLICE_IMPACT_08}} | {{ARCH_VERIFY_08}} | {{ARCH_RISK_08}} |
| A42-09 | Architecture Decisions | {{ADR_SUMMARY_AND_DECISION_AREAS}} | {{ARCH_DRIVERS_09}} | {{ARCH_SLICE_IMPACT_09}} | {{ARCH_VERIFY_09}} | {{ARCH_RISK_09}} |
| A42-10 | Quality Requirements | {{QUALITY_SCENARIOS}} | {{ARCH_DRIVERS_10}} | {{ARCH_SLICE_IMPACT_10}} | {{ARCH_VERIFY_10}} | {{ARCH_RISK_10}} |
| A42-11 | Risks and Technical Debt | {{RISKS_AND_TECH_DEBT}} | {{ARCH_DRIVERS_11}} | {{ARCH_SLICE_IMPACT_11}} | {{ARCH_VERIFY_11}} | {{ARCH_RISK_11}} |
| A42-12 | Glossary | {{ARCH_GLOSSARY_TERMS}} | {{ARCH_DRIVERS_12}} | {{ARCH_SLICE_IMPACT_12}} | {{ARCH_VERIFY_12}} | {{ARCH_RISK_12}} |

Rellenado obligatorio:

- Cada `A42-*` debe decir qué decisiones o restricciones reales impone sobre la app.
- Cada `A42-*` que afecte implementación debe aparecer en `Architecture refs` de al menos una slice.
- `A42-04`, `A42-05`, `A42-06`, `A42-07`, `A42-08` y `A42-10` no deben quedar genéricos en apps grandes.
- Si una sección arc42 no aplica, escribe `NO APLICA` con motivo y explica qué evidencia lo demuestra.
- Las decisiones con alternativas reales deben convertirse en ADRs en el Technical Guide; `A42-09` solo las resume y enlaza.

## Verification Data Contract

> El orquestador no puede cerrar slices ni journeys con datos inventados, decorativos o mocks como sustituto de datos reales/proporcionados. Esta sección define qué datos necesita cada flujo para poder verificarse.

| Data Set ID | Flow/Journey | Persona/Rol | Datos reales/proporcionados requeridos | Fuente | Seed/reset command | Cleanup | Evidence expected | Related refs |
|---|---|---|---|---|---|---|---|---|
| VDATA-001 | J1 / {{PRIMARY_FLOW}} | {{ROLE_001}} | {{REAL_OR_PROVIDED_DATA_001}} | {{USER_PROVIDED_FILE_OR_SANDBOX_OR_DB_SEED}} | {{SEED_OR_RESET_CMD_001}} | {{CLEANUP_001}} | {{SCREENSHOT_LOG_DB_ROW_001}} | J1, AL-001, CORE-001, DATA-001, OBS-001, EVAL-001 |

Rellenado obligatorio:

- Cada journey `J-*` debe tener al menos una fila `VDATA-*`.
- Cada `CORE-*` que calcule, clasifique, recomiende, rankee, genere o decida algo debe tener dataset/fixture verificable y `EVAL-*`.
- Cada integración externa debe declarar sandbox, credenciales de test, evento de prueba o bloqueo explícito si no existe entorno verificable.
- Cada estado de error crítico debe tener dato/caso capaz de reproducirlo.
- Si faltan datos reales/proporcionados, no inventes valores: marca el flujo como bloqueado por datos y crea la slice/follow-up correspondiente.


## 3. Journey Coverage Matrix

> La matriz es canónica. No inventes journeys de una sola pantalla salvo que sean realmente end-to-end. Declara todos los journeys reales necesarios para cubrir el MVP sin topes artificiales.

| ID | Milestone | Pantallas/Screens | Acciones/Actions | Endpoints | Tablas/Tables | Estado cliente/Client state | Slices | Verificación/Verification |
|---|---|---|---|---|---|---|---|---|
| J1 | M1 | {{PAGE_SEQUENCE}} | {{USER_ACTIONS}} | `{{ENDPOINT_SEQUENCE}}` | `{{TABLES}}` | `{{CLIENT_STATE}}` | `{{SLICE_IDS}}` | `/verify-journey J1` |

## 4. Milestones

| Milestone | Objetivo | Criterio visible | Journeys |
|---|---|---|---|
| M1 | MVP usable | usuario completa J1 con datos reales/proporcionados | J1 |

## 5. Reglas de verificación real

- El verify debe usar datos reales/proporcionados persistidos.
- No cierres con mocks decorativos, datos inventados o datos no persistidos.
- Si faltan datos para edge cases, el usuario/equipo debe proporcionarlos o la verificación queda bloqueada/follow-up.

## Final self-review before delivery

- [ ] Cada `J-*` referencia `AL-*`, `CORE-*` si aplica, `DR-*`, `AUTH-*`, `STATE-*`, `ERR-*`, `UI-*`, `DATA-*`, `OBS-*` y `EVAL-*`.
- [ ] Cada slice tiene `Depends on`, `Conflict group`, `Write set`, `Acceptance mínimo` y `Verify mínimo`.
- [ ] Cada pantalla tiene loading, empty, error, permission denied si aplica, success y next action.
- [ ] Cada flujo tiene datos reales/proporcionados para verificación.
- [ ] No quedan placeholders, IDs rotos ni secciones vacías.



## Final source-of-truth self-review

Antes de entregar el `instrucciones.md` rellenado, ChatGPT debe revisar quirúrgicamente y corregir in-place:

- [ ] Cada `J-*` tiene `AL-*` asociado.
- [ ] Cada `AL-*` tiene pasos internos, preconditions, outputs y refs a `DR-*`, `AUTH-*`, `STATE-*`, `ERR-*`, `DATA-*`, `OBS-*` cuando aplique.
- [ ] Cada `CORE-*` describe inputs, parámetros, algoritmo/pasos, outputs, errores y `EVAL-*`.
- [ ] Cada `DR-*` está aplicado por al menos un `AL-*` o slice.
- [ ] Cada `AUTH-*` define allowed when y denied when.
- [ ] Cada `STATE-*` define estados válidos y transiciones prohibidas.
- [ ] Cada `ERR-*` define comportamiento, mensaje visible, impacto en estado y retry/recovery.
- [ ] Cada `INT-*` define sistema externo, idempotencia, timeout/retry y fallo.
- [ ] Cada `DATA-*` define creación, mutación, borrado/retención y owner.
- [ ] Cada `OBS-*` define evento, cuándo se emite y campos mínimos.
- [ ] Cada `EVAL-*` define cómo se comprueba el `CORE-*` con datos reproducibles.
- [ ] No quedan placeholders sin resolver, IDs duplicados ni referencias a IDs inexistentes.
