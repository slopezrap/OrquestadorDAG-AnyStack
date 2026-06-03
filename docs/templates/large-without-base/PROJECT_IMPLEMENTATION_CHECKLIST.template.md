# {{APP_NAME}} — Implementation Checklist

## Screen/Journey Lane Redactor Contract

- No modeles la app como `backend/API primero`, luego `frontend`, y `UX polish` al final. Esa separación rompe la pantalla aunque los tests pasen.
- Cada pantalla importante debe nacer de una **screen/journey lane**: contrato de pantalla + contrato API/datos + implementación conectada + estados UX obligatorios + verificación del journey.
- Las slices de API/backend pueden existir separadas sólo si son foundation real o contrato técnico que alimenta una pantalla/journey nombrado en `Journey refs`.
- Criterio de cierre de pantalla: datos reales/proporcionados conectados front -> back -> DB, estados `loading`, `empty`, `error_network`, `error_validation`, `permission_denied` cuando aplique, `success`, navegación/next action, responsive básico y accesibilidad básica.
- Granularidad: crea tantas slices como hagan falta para cerrar cada pantalla/journey lane verificable de punta a punta. No hagas una slice por botón/componente pequeño; tampoco cierres una pantalla sólo porque compila.
- Defectos dentro de la pantalla actual van por `validator/tester -> debugger -> retest`. Sólo crea FU si falta trabajo nuevo fuera de scope: pantalla, endpoint, tabla, journey, contrato de datos reales o decisión humana no declarada.

> Este fichero es la **fuente ejecutable** para `.claude/bin/bootstrap_source_of_truth.py`.
> ChatGPT debe devolverlo ya rellenado, sin `.template`, con prefijo real:
> `{{APP_PREFIX}}_IMPLEMENTATION_CHECKLIST.md`.
>
> Perfil sin existing baseline: esta checklist construye la app grande desde cero con el stack declarado en `STACK_PROFILE.yaml`.
>
> Regla clave: **un slice oficial = una unidad verificable**. No usar "sub-slices" narrativos. Si algo necesita seguimiento, debe tener su propio `Slice ID` en el Coverage Registry.

> Perfil: **large-without-base**. App grande nueva desde cero; AnyStack permitido vía `STACK_PROFILE.yaml`, sin asumir ningún framework salvo que el perfil lo declare.

---

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


## Modelo Phase / Step / Slice para generar una app completa

- **Phase** = milestone o módulo de producto con sentido para la visión global; no es un lote arbitrario de tareas.
- **Step** = lane coherente dentro de la phase: pantalla/journey lane, módulo de dominio, foundation lane o contrato API que alimenta una pantalla nombrada.
- **Slice/Task** = unidad ejecutable y verificable por un worker, con `Depends on`, `Write set`, `Conflict group`, `Journey refs` y `Verify mínimo` claros.
- Granularidad sana: una phase agrupa milestones/módulos coherentes y un step agrupa lanes relacionadas. No dividas ni fusiones por números; divide cuando mezcle lanes no relacionadas, pierda trazabilidad, tenga ownership distinto o bloquee paralelismo real.
- Mantén visión de app: cada slice debe conectar con una feature, endpoint, tabla, journey o foundation real; nada de slices decorativas.
- Sustituye todos los ejemplos por el dominio real de la app. Si falta un dato real para verificar, bloquea o registra follow-up; no inventes cargas no proporcionadas ni datos de relleno.

## 🔗 Contrato de Cableado — léelo ANTES de generar el Coverage Registry

> Este documento es el **CONSUMIDOR FINAL** de `instrucciones.md` + `*_TECHNICAL_GUIDE.md`. El bootstrap (`.claude/bin/bootstrap_source_of_truth.py`) lee el Coverage Registry y genera `orchestrator-state/tasks/work-items/*.yaml` desde ahí. Lo que NO esté aquí, NO se construye — punto.
>
> **Wires ENTRANTES** (cada item de los otros 2 docs DEBE convertirse en ≥1 slice aquí):
>
> | Tipo de slice (Coverage Registry) | Origen en `instrucciones.md`              | Origen en `*_TECHNICAL_GUIDE.md`                  |
> |-----------------------------------|--------------------------------------------|----------------------------------------------------|
> | `db` (migración)                  | §3.1 motor (entities)                     | §10.3 tabla + §6.3 entity                          |
> | `api` (endpoint)                  | §3.1 motor / §3.2 feature                 | §6.2 endpoint                                      |
> | `frontend` (screen/page)                  | §3.2 feature                              | §6.1 ruta + §6.3 DTO/modelo frontend                          |
> | `ai` (agent / graph / tool / reference retrieval) | §3.1 motor (componente AI)                | §10.4 pieza AI + smoke                             |
> | `journey` (e2e multi-pantalla)    | §3.6 + §3.7 fila de la matriz             | §6.1 + §6.2 (componen el flujo)                    |
> | `library` (intro de lib)          | §11.0 USAR/DEFERRED                       | §2.0 fila técnica                                  |
> | `setup` / `gate`                  | §4 milestones / phase gates               | §13 milestones técnicos                            |
>
> **Cableado VISIBLE en cada slice**: el Coverage Registry incluye `Journey refs`, `Pantalla/Ruta`, `Endpoint`, `Tablas DB`, `Origen-Instr`, `Origen-TechGuide`, `Domain rule refs`, `Architecture refs`, `Application logic refs`, `Core logic refs`, `Permission refs`, `State refs`, `Failure refs`, `Integration refs`, `UI refs`, `Data refs`, `Observability refs`, `Evaluation refs`, `Conflict group` y `Write set`. El bootstrap copia este recurso a `registry.json`, `work-items/*.yaml` y `task-packs/<TASK_ID>.md`, de modo que `planner`, `developer`, `validator` y `tester` trabajan con el mismo mapa front→back→DB sin depender de memoria global.
>
> **Regla de oro**: cero slices huérfanos (sin origen claro) y cero items huérfanos en los otros 2 docs (sin slice aquí). Si un endpoint está en `§6.2` pero no tiene slice → bug silencioso. Si un slice está aquí pero no tiene origen → drift inverso (slice inventado).
>
> **Cómo saber si está bien cableado**: ejecuta mentalmente la verificación final "Final wiring verification" al final del doc.

---

# Canonical Coverage Registry — Dynamic Slice Registry

El orquestador funciona mejor cuando el CHECKLIST declara primero los slices canónicos y luego desarrolla los steps. El bootstrap lee todas las tablas cuyo primer encabezado sea exactamente `Slice ID`.

## Granularity policy

Usa esta política para generar los slices dinámicamente desde `instrucciones.md` + `TECHNICAL_GUIDE.md`:

| Tipo de trabajo | Granularidad recomendada | Ejemplo bueno | Ejemplo malo |
|---|---|---|---|
| Endpoint backend | 1 endpoint verificable por slice cuando tiene schema/use case/repository/test/curl/logs propios | `POST /api/v1/{{resource}}` | `Todo el dominio completo` |
| DB/migration | 1 migración coherente por slice; puede agrupar tablas que nacen juntas y se verifican juntas | `0007_result_tables.py` | `Toda la DB de la app` |
| AI | 1 tool / prompt / graph / agent verificable por slice; endpoint + graph juntos solo si es trivial | `{{domain_process_graph}} smoke` | `Todo el motor AI/dominio` |
| Frontend | 1 ruta/page completa por slice, con estados loading/empty/error/success | `{{ResultPage}}` o equivalente | `Todas las pantallas` |
| Integración | 1 journey end-to-end por slice si solo conecta piezas ya construidas | `J1 upload→result→result e2e` | `Toda la app e2e` |
| Config externa | 1 proveedor/servicio externo declarado por slice | `{{provider}} config` | `Configurar todos los servicios externos y probar todo` |

Reglas prácticas:

- Divide si el slice mezcla criterios de aceptación independientes, ownership distintos, write sets incompatibles o verificaciones que deberían poder fallar de forma aislada.
- Divide si toca más de 4 zonas fuertes a la vez: DB + backend + AI + frontend + infra.
- Une si una tarea no tiene verificación independiente.
- Cada `Slice ID` debe tener `Acceptance mínimo` y `Verify mínimo` específicos de esa fila.
- `Verify mínimo` debe referenciar datos reales/proporcionados del `TECHNICAL_GUIDE §Verification Data Contract` cuando la slice sea verificable por UI/API; no cierres con mocks decorativos.
- Las fases ejecutables nunca deben depender de checkboxes genéricos: la tabla de Registry manda y los headings son solo guía humana.
- Para una app grande nueva: genera todos los slices necesarios para cubrir completamente pantallas, endpoints, tablas, reglas de dominio, integraciones y journeys. Divide por milestones/lanes cuando mejore trazabilidad, ownership o paralelismo real.

## Canonical Coverage Registry — OBLIGATORIO

> ChatGPT debe generar las filas reales. Mantén las columnas exactamente con estos nombres mínimos para DAG, paralelismo seguro y cableado: `Slice ID`, `Tipo`, `Target`, `Step`, `Product increment`, `Build state`, `Risk level`, `Verify mode`, `Depends on`, `Conflict group`, `Write set`, `Journey refs`, `Pantalla/Ruta`, `Endpoint`, `Tablas DB`, `Origen-Instr`, `Origen-TechGuide`, `Acceptance mínimo`, `Verify mínimo`, `Domain rule refs`, `Architecture refs`, `Application logic refs`, `Core logic refs`, `Permission refs`, `State refs`, `Failure refs`, `Integration refs`, `UI refs`, `Data refs`, `Observability refs`, `Evaluation refs`.
> Puedes añadir más columnas (`Path`, `Provider`, `Widget`, `Migración`, etc.). El bootstrap seguirá funcionando si la primera columna sigue siendo `Slice ID` (parser por header dict — columnas extra se ignoran sin romper). `Depends on` es obligatorio en TODAS las filas: usa `—` sólo para roots reales que no necesitan predecesor verificable. Omitir `Depends on` es error operativo en `production = explicit_dag`; no existe fallback sano a dependencias implícitas.
>
> 🧭 **DAG / paralelismo**: `Depends on` es la source-of-truth de dependencias entre slices. Usa `—` para roots; usa `TASK_ID`, rangos (`P03-S02-T001..T004`), step refs (`P03-S02`), phase refs (`P03`) o `previous`. El bootstrap deriva la matriz en `orchestrator-state/memory/task-dag.json`; NO escribas una matriz manual aquí.
>
> 🧱 **Versionado acumulativo**: `Product increment` identifica si la fila pertenece a `v0`, `v1`, `v2`, etc. `Build state` indica si el slice ya está construido (`done`) o si pertenece al incremento activo (`planned`/`ready`). Para un producto grande, no borres filas antiguas: conserva `v0`/`done` y añade las nuevas filas de `vN`; eso permite que ChatGPT mantenga contexto completo sin obligar al orquestador a reconstruir lo ya cerrado.
>
> 🧱 **Serialización segura**: `Conflict group` y `Write set` son guardrails de concurrencia. Dos slices pueden tener `Depends on` libre y aun así NO deben correr juntas si pisan el mismo router, state handler, migración, API client, manifiestos de dependencias, workflow o ficheros compartidos. Usa grupos estables (`db:migrations`, `api:auth`, `front:dashboard`, `router`, `theme`, `release`) y patrones de ficheros esperados (`<frontend_module_root>/**/router*`, `<backend_module_root>/**`, manifiestos/lockfiles). `/next-wave` serializa automáticamente los conflictos y `claim_task.py` bloquea claims manuales conflictivos.
>
> 🧩 **Follow-ups en producción**: si durante `validator`, `tester`, `/verify-slice` o `/verify-journey` aparece trabajo real que no estaba contemplado, NO se deja como nota suelta. Se crea propuesta con `register-followup-task.sh propose` y, si el usuario la aprueba, se promueve a una fila real en `Runtime Follow-up Coverage Registry` con `Depends on`, `Conflict group`, `Write set`, journey, UX y verificación real/proporcionada. Así futuros `bootstrap --refresh` no pierden el trabajo añadido.
>
> 🔗 **Columnas de cableado recomendadas** (`Origen-Instr` + `Origen-TechGuide`): visibles en cada fila para que el `planner` resuelva sin adivinanzas qué motor / feature / endpoint / tabla origina el slice. Sintaxis libre tipo `§3.1#resource-analyzer` o `§6.2#POST-/api/v1/{{resource}}`. Mantén el formato `<sección>#<slug>` para facilitar grep.

| Slice ID | Tipo | Target | Step | Product increment | Build state | Risk level | Verify mode | Depends on | Conflict group | Write set | Journey refs | Pantalla/Ruta | Endpoint | Tablas DB | Origen-Instr | Origen-TechGuide | Acceptance mínimo | Verify mínimo | Domain rule refs | Architecture refs | Application logic refs | Core logic refs | Permission refs | State refs | Failure refs | Integration refs | UI refs | Data refs | Observability refs | Evaluation refs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P00-S01-T001 | setup | Bootstrap repo + env | Step 0.1 | v1 | planned | low | auto | — | setup:bootstrap | `.env.example`; `scripts/**`; `<backend_module_root>/**/health*` | — | — | `GET /health` | — | §1.1 | §3#dev-restart | proyecto compila; `.env.example` completo; scripts base ejecutables | `./scripts/setup-from-scratch.sh --check` | {{DOMAIN_RULE_REFS}} | {{ARCHITECTURE_REFS_OR_—}} | {{AL_REFS_OR_—}} | {{CORE_REFS_OR_—}} | {{AUTH_REFS_OR_—}} | {{STATE_REFS_OR_—}} | {{ERR_REFS_OR_—}} | {{INT_REFS_OR_—}} | {{UI_REFS_OR_—}} | {{DATA_REFS_OR_—}} | {{OBS_REFS_OR_—}} | {{EVAL_REFS_OR_—}} |
| P02-S01-T001 | db | `0001_{{domain}}` | Step 2.1 | v1 | planned | medium | auto | P00-S01-T001 | db:migrations, db:{{table}} | `<migrations_dir>/*{{table}}*`; `<backend_module_root>/**/{{table}}*` | J1 | — | — | `{{table}}` | §3.1#{{component}} | §10.3#{{table}} + §6.3#{{Entity}} | migración up/down; FK cascade; índices en queries críticas | `{{db_migrate_up_down_cmd}}` | {{DOMAIN_RULE_REFS}} | {{ARCHITECTURE_REFS_OR_—}} | {{AL_REFS_OR_—}} | {{CORE_REFS_OR_—}} | {{AUTH_REFS_OR_—}} | {{STATE_REFS_OR_—}} | {{ERR_REFS_OR_—}} | {{INT_REFS_OR_—}} | {{UI_REFS_OR_—}} | {{DATA_REFS_OR_—}} | {{OBS_REFS_OR_—}} | {{EVAL_REFS_OR_—}} |
| P02-S02-T001 | api | `POST /api/v1/{{resource}}` | Step 2.2 | v1 | planned | medium | human | P02-S01-T001 | api:{{resource}} | `<backend_module_root>/**/{{resource}}*`; `<backend_tests_root>/**/{{resource}}*` | J1 | `{{Resource}}CreatePage /{{resource}}/new` | `POST /api/v1/{{resource}}` | `{{table}}` | §3.1#{{component}} | §6.2#POST-/api/v1/{{resource}} | schema/DTO tipado; use case; repository; integration test; logs BEFORE/AFTER/ERROR | `{{backend_integration_test_cmd}} {{resource}}_create` + curl con datos reales/proporcionados | {{DOMAIN_RULE_REFS}} | {{ARCHITECTURE_REFS_OR_—}} | {{AL_REFS_OR_—}} | {{CORE_REFS_OR_—}} | {{AUTH_REFS_OR_—}} | {{STATE_REFS_OR_—}} | {{ERR_REFS_OR_—}} | {{INT_REFS_OR_—}} | {{UI_REFS_OR_—}} | {{DATA_REFS_OR_—}} | {{OBS_REFS_OR_—}} | {{EVAL_REFS_OR_—}} |
| P02-S04-T001 | ai | `{{graph}}_smoke` | Step 2.4 | v1 | planned | medium | auto | P02-S02-T001 | ai:{{graph}} | `<backend_module_root>/**/{{graph}}*`; `<backend_tests_root>/**/{{graph}}*` | J1 | — | internal/no-front | `{{ai_table}}` | §3.1#{{component-AI}} | §10.4#{{graph}} | componente compila; smoke determinista con doubles permitidos solo para servicios externos; logs por nodo | `{{backend_ai_test_cmd}} {{graph}}_smoke` | {{DOMAIN_RULE_REFS}} | {{ARCHITECTURE_REFS_OR_—}} | {{AL_REFS_OR_—}} | {{CORE_REFS_OR_—}} | {{AUTH_REFS_OR_—}} | {{STATE_REFS_OR_—}} | {{ERR_REFS_OR_—}} | {{INT_REFS_OR_—}} | {{UI_REFS_OR_—}} | {{DATA_REFS_OR_—}} | {{OBS_REFS_OR_—}} | {{EVAL_REFS_OR_—}} |
| P02-S00-T001 | library | intro `<paquete-X>` en dependency manifest | Step 2.0 | v1 | planned | low | auto | P00-S01-T001 | dependency:{{paquete}} | dependency manifest; lockfile; primer consumidor | — | primer consumidor | — | — | §11.0#{{área}} | §2.0#{{paquete}} | lib instalada; primer consumidor refactorizado; lockfile actualizado | `{{backend_dependency_install_cmd}} && {{backend_test_cmd}} {{first_consumer_test_selector}}` | {{DOMAIN_RULE_REFS}} | {{ARCHITECTURE_REFS_OR_—}} | {{AL_REFS_OR_—}} | {{CORE_REFS_OR_—}} | {{AUTH_REFS_OR_—}} | {{STATE_REFS_OR_—}} | {{ERR_REFS_OR_—}} | {{INT_REFS_OR_—}} | {{UI_REFS_OR_—}} | {{DATA_REFS_OR_—}} | {{OBS_REFS_OR_—}} | {{EVAL_REFS_OR_—}} |
| P03-S01-T001 | frontend | `/{{resource}}/new` `{{Resource}}CreatePage` | Step 3.1 | v1 | planned | medium | human | P02-S02-T001 | front:{{resource}}, router | `<frontend_module_root>/**/{{resource}}*`; `<frontend_tests_root>/**/{{resource}}*`; router/config | J1 | `{{Resource}}CreatePage /{{resource}}/new` | `POST /api/v1/{{resource}}` | — | §3.2#{{feature}} | §6.1#/{{resource}}/new | page con design system; validación inline; seis estados UI; state handler wired; next action | `/verify-slice` en la superficie real declarada con backend real y datos proporcionados | {{DOMAIN_RULE_REFS}} | {{ARCHITECTURE_REFS_OR_—}} | {{AL_REFS_OR_—}} | {{CORE_REFS_OR_—}} | {{AUTH_REFS_OR_—}} | {{STATE_REFS_OR_—}} | {{ERR_REFS_OR_—}} | {{INT_REFS_OR_—}} | {{UI_REFS_OR_—}} | {{DATA_REFS_OR_—}} | {{OBS_REFS_OR_—}} | {{EVAL_REFS_OR_—}} |
| P03-S02-T001 | journey | `J1` e2e happy path | Step 3.2 | v1 | planned | high | human | P03-S01-T001 | journey:J1 | `orchestrator-state/tasks/evidence/journeys/J1/**` | J1 | `{{route_sequence}}` | `{{endpoint_sequence}}` | `{{tables}}` | §3.6#J1 + §3.7#J1 | §6.1 + §6.2 | flujo multi-pantalla real; datos persistidos; next action visible; estados marginales reproducidos | `/verify-journey J1` | {{DOMAIN_RULE_REFS}} | {{ARCHITECTURE_REFS_OR_—}} | {{AL_REFS_OR_—}} | {{CORE_REFS_OR_—}} | {{AUTH_REFS_OR_—}} | {{STATE_REFS_OR_—}} | {{ERR_REFS_OR_—}} | {{INT_REFS_OR_—}} | {{UI_REFS_OR_—}} | {{DATA_REFS_OR_—}} | {{OBS_REFS_OR_—}} | {{EVAL_REFS_OR_—}} |


>>> MODELO: reemplaza las filas de ejemplo por TODAS las filas reales del proyecto.
>>>
>>> 🔗 **Cableado obligatorio por fila**: rellena `Journey refs`, `Pantalla/Ruta`, `Endpoint`, `Tablas DB`, `Origen-Instr`, `Origen-TechGuide`, `Domain rule refs`, `Architecture refs`, `Application logic refs`, `Core logic refs`, `Permission refs`, `State refs`, `Failure refs`, `Integration refs`, `UI refs`, `Data refs`, `Observability refs`, `Evaluation refs`, `Conflict group` y `Write set` en cada fila apuntando al elemento real o `—` cuando no aplique. El contenido se copia al task-pack y guía las escrituras del agente. Si una celda productiva quedaría vacía, el slice probablemente no debería existir. Excepción: filas `setup` puras del Phase 0 pueden apuntar a `§1.1` o `§3` genéricos.
>>>
>>> 🧭 **Dependencias DAG obligatorias**: rellena `Depends on` en TODAS las filas. Usa `—` solo cuando el slice pueda ejecutarse como raíz de su phase/wave. No uses dependencias decorativas: una dependencia debe significar que el output del predecessor es necesario para verificar este slice.
>>>
>>> 🧱 **Guardrails de concurrencia obligatorios**: rellena `Conflict group` y `Write set` en TODAS las filas. Si dos slices tocan el mismo router, state handler, migración, workflow, manifiestos de dependencias, API client, theme o fichero compartido, deben compartir `Conflict group` o solaparse en `Write set`. Si la aceptación menciona `docker-compose.yml`, `docker-compose.yaml`, `compose.yaml`, `Dockerfile*`, `.env.example`, `.github/workflows/**` o lockfiles, esos paths exactos deben aparecer en `Write set`/`allowed_paths` con grupo `infra:*`/`ci:*`. Usa `read-only` o `—` solo para slices que no escriben código compartido.
>>>
>>> 🔗 **No dejes slices huérfanos**:
>>> - Cada endpoint de `TECHNICAL_GUIDE §6.2` → slice `api` con columna `Endpoint` igual a `METHOD /path`, y consumidor front/journey declarado si no es interno.
>>> - Cada tabla de `§10.3` → slice `db`.
>>> - Cada pieza AI de `§10.4` → slice `ai` con smoke.
>>> - Cada ruta/pantalla frontend de `§6.1` → slice `frontend` (o `journey` si solo existe como integración), con columna `Pantalla/Ruta` que incluya Page + ruta.
>>> - Cada lib USAR/DEFERRED de `instrucciones §11.0` + `§2.0` → slice `library` que la introduce en deps.
>>> - Cada journey de `instrucciones §3.7` → slice(s) que cubren las pantallas + endpoint final con `journey` ID en columna `Journey refs`.

---

# Phase 0 — Bootstrap / foundation propia

> Construir scaffold propio: backend/frontend/DB según `STACK_PROFILE.yaml`, design system, health checks, scripts, reset/carga de datos reales proporcionados y tests base.


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

## Step 0.1 — Project bootstrap

- [ ] Confirmar perfil `large-without-base`: app grande desde cero, sin arrastrar `docs/product-baseline/`.
- [ ] Instanciar estructura de repo según `STACK_PROFILE.yaml` y limpiar placeholders.
- [ ] Crear scaffold backend/frontend en los module roots declarados.
- [ ] `.env.example` completo sin secretos reales.
- [ ] Scripts base ejecutables: `setup-from-scratch.sh`, `dev-restart.sh`, `run-all-tests.sh`.
- [ ] `scripts/dev-restart.sh` implementa `--soft`, `--check`, `--reset`.

## Step 0.2 — DB foundation

- [ ] DB local/cloud configurada según `STACK_PROFILE.yaml`.
- [ ] Conexión DB real declarada por `STACK_PROFILE.yaml` configurada cuando aplique.
- [ ] Migraciones reversibles con la herramienta declarada por el stack cuando aplique.
- [ ] Health/readiness endpoints declarados por el stack funcionan cuando existan.

## Step 0.3 — Frontend foundation

- [ ] Frontend compila/arranca con el comando declarado.
- [ ] Router/navigation, theme/tokens, shared widgets e i18n inicial listos si aplican.
- [ ] `/showcase` visible en la superficie real declarada con design system profesional.

## Step 0.4 — Phase 0 gate

- [ ] Backend lint definido en `STACK_PROFILE.yaml` zero.
- [ ] backend type-check/lint zero.
- [ ] `{{frontend_analyze_cmd}}` zero si el stack lo declara.
- [ ] Tests unitarios/integración de Phase 0 verdes.
- [ ] PROGRESS.md actualizado.

---

# Phase 1 — Identity / base capabilities

> App nueva sin baseline: construir identidad/cuenta/administración solo si esta app lo declara en source-of-truth; no hay capacidades heredadas.

## Step 1.1 — Identity/state handler configuration

- [ ] Método de identidad/acceso declarado configurado, si aplica.
- [ ] Proveedores externos configurados sólo si el source-of-truth los declara.
- [ ] Redirect/callback URLs o equivalente documentados según superficie real.

## Step 1.2 — Identity/API slices

- [ ] Para cada endpoint auth declarado en el registry: schema, use case, repository/client, router, tests, curl y logs.
- [ ] La estrategia de sesión/token cumple el contrato de seguridad del stack y no expone secretos en cliente.

## Step 1.3 — Identity/frontend slices

- [ ] Pantallas/flujo de identidad declarado implementado, si aplica.
- [ ] Identity state handler, redirects y error states.

## Step 1.4 — Phase 1 gate

- [ ] 4 métodos de login funcionales si están en scope.
- [ ] Admin user configurado para pruebas.
- [ ] Tests acumulados Phase 0-1 verdes.
- [ ] PROGRESS.md actualizado.

---

# Phase 2 — MOTOR resources feeding named screens/journeys

> Aquí se construye el valor de la app. Sin UI final salvo herramientas de smoke. Cada componente del motor de `instrucciones.md §3.1` debe tener slices en el Coverage Registry.

> 🔗 **CABLEADO de Phase 2** — los steps aquí son **agrupadores narrativos** del registry; los slices reales (con `Origen-Instr` / `Origen-TechGuide` cableados) viven en el Coverage Registry de arriba. Para CADA componente del motor declarado en `instrucciones.md §3.1`:
>
> - 1 slice `db` por tabla nueva → cablea a `§10.3#<tabla>` + `§6.3#<Entity>`.
> - 1 slice `api` por endpoint del componente → cablea a `§6.2#<METHOD-/path>`.
> - 1 slice `ai` por agent / graph / deep_agent / tool / reference-data loader (con smoke test) → cablea a `§10.4#<pieza>`.
> - Slices `library` para libs no instaladas todavía → cablean a `§11.0#<área>` + `§2.0#<paquete>`.
>
> Si un componente del motor en `§3.1` no tiene NINGÚN slice aquí, no existe en código. Si un slice aquí no apunta a un componente real de `§3.1`, drift inverso.

>>> MODELO: generar todos los steps reales que requiera el producto. Cada step agrupa slices del registry, pero NO sustituye al registry.

## Step 2.1 — Data model and migrations

- [ ] Implementar las migraciones declaradas en TECHNICAL_GUIDE §10.3 y en el Coverage Registry.
- [ ] Cada migración tiene up/down probado.
- [ ] FKs, índices y constraints reflejan invariantes del dominio.

## Step 2.2 — Domain + repositories + use cases

- [ ] Entities de dominio puras.
- [ ] Repository interfaces en domain.
- [ ] SQLAlchemy models e implementations en infrastructure.
- [ ] Use cases con tests unitarios y logs BEFORE/AFTER/ERROR.

## Step 2.3 — API endpoints

- [ ] Cada endpoint de TECHNICAL_GUIDE §6.2 tiene slice propio o justificación explícita de agrupación.
- [ ] Schemas/DTOs de validación tipados.
- [ ] Identity/rate limit/audit log según criticidad.
- [ ] Integration tests contra DB/servicio real con datos proporcionados.
- [ ] Curl reproducible.

## Step 2.4 — AI components, if any

- [ ] Tools/prompts/agents/graphs/deep_agents declarados en TECHNICAL_GUIDE §10.4.
- [ ] Tests deterministas con test double del servicio externo o equivalente.
- [ ] Smoke command real para cada graph/agent.
- [ ] official-docs-researcher verifica versiones/imports antes de implementar.

## Step 2.5 — Phase 2 gate

- [ ] Todo endpoint del motor responde por curl con payload realista.
- [ ] DB contiene filas verificables.
- [ ] Logs sin PII/secrets.
- [ ] Tests backend acumulados verdes.
- [ ] PROGRESS.md actualizado.

---

# Phase 3 — SCREEN/JOURNEY LANES / Frontend UX

> Cada feature de `instrucciones.md §3.2` se expone visualmente. Cada ruta de TECHNICAL_GUIDE §6.1 debe tener slice propio o formar parte de un journey slice claramente declarado.

> 🔗 **CABLEADO de Phase 3** — los steps aquí agrupan slices del registry. Para CADA feature de `instrucciones.md §3.2`:
>
> - 1 slice `frontend` por pantalla → cablea a `§3.2#<feature>` + `§6.1#<ruta>`.
> - Cada slice `frontend` cubre los 6 estados marginales explícitamente: loading / empty / error_network / error_validation / permission_denied / success.
> - 1 slice `journey` por flujo end-to-end de `instrucciones.md §3.7` → cablea a `§3.6#<JID>` + `§3.7#<JID>`. Solo se construye CUANDO todas las pantallas y endpoints del flujo ya tienen slice y están cerrados.
>
> Si una feature de `§3.2` no tiene NINGÚN slice `frontend` aquí, no se construye pantalla. Si un journey de `§3.7` no tiene slice `journey` aquí, `/verify-journey` no tiene cómo lanzarse.

>>> MODELO: generar phases/lanes reales por milestone/pantalla/módulo. No apliques topes artificiales: si el producto necesita muchas slices, decláralas todas. Divide una phase o step por pantalla/journey lane/módulo independiente cuando eso mantenga visión de aplicación, ownership claro y paralelismo real.

## Step 3.1 — Primary route/pages

- [ ] Pages principales con design system propio/declarado.
- [ ] State management declarado conectado al API client.
- [ ] Estados loading, empty, error_network, error_validation, permission_denied, success.
- [ ] Next action después de cada success.

## Step 3.2 — Journey integration

- [ ] Cada journey J1+ de instrucciones §3.7 se puede recorrer en la superficie real declarada.
- [ ] Back behavior, deep links y empty/error states verificados.
- [ ] `/verify-journey JXXX` preparado para cada journey.

## Step 3.3 — Phase 3 gate

- [ ] `{{frontend_analyze_cmd}}` zero si el stack lo declara.
- [ ] Widget tests verdes.
- [ ] E2E/smoke la superficie real declarada para cada milestone.
- [ ] Screenshots/evidence guardados en handoff.
- [ ] PROGRESS.md actualizado.

---

# Phase 4 — Hardening specific to this app

## Step 4.1 — Security, observability and performance

- [ ] Audit actions específicas del dominio.
- [ ] Rate limits en endpoints caros.
- [ ] Métricas y logs del motor.
- [ ] Performance smoke sobre dataset real proporcionado por el usuario/equipo.

## Step 4.2 — Phase 4 gate

- [ ] Tests acumulados verdes.
- [ ] Security checks sin findings críticos.
- [ ] PROGRESS.md actualizado.

---

# Phase 5 — Release

## Step 5.1 — Build and release readiness

- [ ] `{{frontend_build_cmd}}` OK si el stack lo declara.
- [ ] Docker/backend build OK si aplica.
- [ ] Env vars documentadas.
- [ ] Rollback plan específico si aplica.

## Step 5.2 — Final acceptance

- [ ] Todos los journeys verificados.
- [ ] All tests green.
- [ ] README de app actualizado.
- [ ] Tag/release preparado.

---

# Final wiring verification — OBLIGATORIO

> 🔗 **Antes de devolverme este CHECKLIST, recorre TODA esta verificación**. Esta es la última red de seguridad: si algún wire falla aquí, llega roto al bootstrap, al `planner` y al pipeline.

## A. Wires ENTRANTES — todo identifier de los otros docs tiene slice

### A.1 Desde `instrucciones.md`

- [ ] Cada **componente del motor** de `§3.1` tiene slice(s) suficientes de datos/API/core/AI según aplique.
- [ ] Cada **AL-* / caso de uso** aparece en `Application logic refs` de al menos una fila.
- [ ] Cada **CORE-* / motor especializado** aparece en `Core logic refs` y tiene `Evaluation refs`.
- [ ] Cada **DR-* / AUTH-* / STATE-* / ERR-* / INT-* / DATA-* / OBS-* / EVAL-*` declarado tiene al menos una slice o justificación explícita.
- [ ] Cada **feature** de `§3.2` tiene 1+ slice de screen/journey lane si es visible.
- [ ] Cada **journey** de `§3.7` referencia slices existentes en columna `Slices`.
- [ ] Cada **milestone** de `§4` agrupa slices reales.
- [ ] Cada **decisión USAR / DEFERRED** de `§11.0` tiene 1 slice `library` que la introduce en deps.

### A.2 Desde `*_TECHNICAL_GUIDE.md`

- [ ] Cada **lib USAR / DEFERRED** de `§2.0` tiene slice `library`.
- [ ] Cada **ruta** de `§6.1` tiene slice `frontend` o aparece como paso de un slice `journey`.
- [ ] Cada **endpoint** de `§6.2` tiene slice `api` propio o agrupación justificada.
- [ ] Cada **entity** de `§6.3` tiene tabla/store o declara explícitamente que no persiste.
- [ ] Cada **tabla** de `§10.3` tiene slice `db`.
- [ ] Cada **agent / graph / deep_agent / tool / reference-data loader** de `§10.4` tiene slice `ai` o de core logic con test/evidencia.
- [ ] Cada fila del **Verification Data Contract §6.5** se usa por uno o más journeys/slices.

## B. Wires SALIENTES — cada slice tiene origen real

Recorre cada fila del Coverage Registry y verifica:

- [ ] Tiene `Origen-Instr` rellenado y la sección apuntada existe en `instrucciones.md`.
- [ ] Tiene `Origen-TechGuide` rellenado y la sección apuntada existe en `*_TECHNICAL_GUIDE.md`.
- [ ] Tiene `Depends on`; usa `—` sólo para roots reales.
- [ ] Tiene `Conflict group` estable y `Write set` concreto.
- [ ] Tiene `Acceptance mínimo` verificable.
- [ ] Tiene `Verify mínimo` ejecutable con datos reales/proporcionados o comando determinista.
- [ ] Si es visible, tiene `Journey refs`, `Pantalla/Ruta`, `UI refs` y estados UX.
- [ ] Si es endpoint, tiene `Endpoint`, `AUTH-*`, `ERR-*`, `DATA-*` y consumidor declarado si aplica.
- [ ] Si es datos/schema, tiene `Tablas DB`, `DATA-*`, constraints y migración/schema.
- [ ] Si es core logic, tiene `CORE-*` y `EVAL-*`.
- [ ] Si es integración, tiene `INT-*`, idempotencia y failure behavior.
- [ ] Si es sensible, mutable o core, tiene `Observability refs`.

## C. Wires de la Journey Coverage Matrix (`instrucciones.md §3.7`)

Para CADA fila de la matriz:

- [ ] Tiene pantallas o evidencia no-UI declarada.
- [ ] Cada endpoint de la celda existe en `TECHNICAL_GUIDE §6.2`.
- [ ] Cada tabla de la celda existe en `TECHNICAL_GUIDE §10.3`.
- [ ] La columna `Slices` se expande a `Slice ID`s reales del Coverage Registry.
- [ ] Aparece 1 slice `journey` con ese `JID` en columna `Journey refs` y verify `/verify-journey JXXX` si es journey visible.
- [ ] Separadores correctos: `→` en pantallas, coma + espacio en endpoints/tablas/estado/slices, `\|` para pipes literales, sentinels `(none)` o `—` para celdas sin contenido.

## D. Drift checks — cero tolerancia

- [ ] **Cero `>>> MODELO:`** restantes en el fichero filled.
- [ ] **Cero referencias** a `Slice ID`s que no existan.
- [ ] **Cero referencias** a secciones de `instrucciones.md` o `TECHNICAL_GUIDE` que no existan.
- [ ] **Coverage Registry header** sigue empezando exactamente por `| Slice ID |`.
- [ ] DAG production explícito: `./scripts/check-task-dag.sh --strict` retorna 0.
- [ ] Wiring estricto: `./scripts/check-wiring-contract.sh --strict --require-new-template-columns` retorna 0.

## Production hardening actual

Usa source-of-truth acumulativo de app nueva (`v1`, luego `v2`, ...), `Risk level`, `Verify mode`, phases/steps/journeys completos sin topes artificiales y verify con datos reales/proporcionados. Ejecuta bootstrap + check-task-dag + check-journey-matrix + check-wiring-contract antes de waves.
