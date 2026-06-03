# Guía: generar el source-of-truth pack con ChatGPT en modo DAG explícito

Esta guía explica cómo usar ChatGPT para rellenar los cinco documentos canónicos que después ingiere el orquestador:

```text
docs/source-of-truth/instrucciones.md
docs/source-of-truth/<APP>_TECHNICAL_GUIDE.md
docs/source-of-truth/<APP>_IMPLEMENTATION_CHECKLIST.md
docs/source-of-truth/UX_CONTRACT.md
docs/source-of-truth/STACK_PROFILE.yaml
```

El objetivo es que el bootstrap genere un grafo DAG explícito, no el modo sin dependencias explícitas, y que la aplicación se construya por **screen/journey lanes** con datos reales/proporcionados.

## 1. Qué debe recibir ChatGPT

Entrega a ChatGPT estos ficheros como contexto común:

```text
docs/prompts/PROMPT_SOURCE_OF_TRUTH_DAG.md
README.md
CHEATSHEET.md
```

Después elige exactamente un perfil y entrega sus cinco templates:

```text
docs/templates/minimal/instrucciones.template.md
docs/templates/minimal/PROJECT_TECHNICAL_GUIDE.template.md
docs/templates/minimal/PROJECT_IMPLEMENTATION_CHECKLIST.template.md
docs/templates/minimal/UX_CONTRACT.template.md
docs/templates/minimal/STACK_PROFILE.template.yaml
```

```text
docs/templates/large-without-base/instrucciones.template.md
docs/templates/large-without-base/PROJECT_TECHNICAL_GUIDE.template.md
docs/templates/large-without-base/PROJECT_IMPLEMENTATION_CHECKLIST.template.md
docs/templates/large-without-base/UX_CONTRACT.template.md
docs/templates/large-without-base/STACK_PROFILE.template.yaml
```

```text
docs/templates/large-with-base/instrucciones.template.md
docs/templates/large-with-base/PROJECT_TECHNICAL_GUIDE.template.md
docs/templates/large-with-base/PROJECT_IMPLEMENTATION_CHECKLIST.template.md
docs/templates/large-with-base/UX_CONTRACT.template.md
docs/templates/large-with-base/STACK_PROFILE.template.yaml
```

Usa `minimal` para apps pequeñas desde cero. Usa `large-without-base` para productos grandes desde cero. Usa `large-with-base` sólo cuando exista un producto real ya construido en `docs/product-baseline/`; si no existe baseline real, no lo inventes y usa `large-without-base`.

Si usas `large-with-base`, entrega también el baseline real disponible:

```text
docs/product-baseline/instrucciones.md
docs/product-baseline/*_TECHNICAL_GUIDE.md
docs/product-baseline/*_IMPLEMENTATION_CHECKLIST.md
docs/product-baseline/UX_CONTRACT.md
docs/product-baseline/STACK_PROFILE.yaml
docs/product-baseline/BASELINE_MANIFEST.json
```

Además, dale el contexto real de la app: usuarios, problema, valor, V1, milestones, integraciones externas, datos sensibles, pantallas necesarias, reglas de negocio, restricciones legales, datos reales disponibles y prioridades. Las reglas de negocio estables deben entrar como `Domain Logic Contract` dentro de `instrucciones.md` con IDs `DR-*`; no añadas un sexto documento obligatorio para dominio.

Los docs que entregue ChatGPT son **acumulativos**, no diferenciales sueltos: conservan filas ya construidas (`Build state=done`) y añaden nuevas filas con `Build state=planned`. En apps nuevas, todo empieza normalmente como `Product increment=v1` y `Build state=planned`.

## Qué NO se rellena con ChatGPT

No generes `.claude/schemas/` ni entregues `.claude/schemas/*.json`, salidas de `orchestrator-doctor`, reportes de golden E2E ni artefactos de `orchestrator-state/` como si fueran source-of-truth de producto. Esos ficheros pertenecen al framework o se derivan durante bootstrap/verify.

La golden app no fija el stack. La golden app de `examples/golden-real-app/` es una referencia de contrato AnyStack: la implementación incluida usa Python/SQLite por ser portable en CI, pero una app Flutter/React/Node/Python/Java/Go se modela igual a través de los cinco docs y de los comandos reales declarados en `STACK_PROFILE.yaml`.

## 2. Entrega por fases, no todo de golpe

Pide a ChatGPT que entregue los documentos uno a uno:

1. `instrucciones.md`.
2. `<APP>_TECHNICAL_GUIDE.md`.
3. `<APP>_IMPLEMENTATION_CHECKLIST.md`.
4. `UX_CONTRACT.md`.
5. `STACK_PROFILE.yaml`.

No aceptes el siguiente documento hasta revisar el anterior. El checklist es crítico para DAG porque contiene el `Canonical Coverage Registry`; `UX_CONTRACT.md` es crítico para que las pantallas no se cierren sólo por compilar; `STACK_PROFILE.yaml` evita asumir framework, paths o comandos por costumbre.

## 3. Regla que activa el modo DAG DAG explícito

El modo DAG se activa solo si el Coverage Registry del checklist contiene una columna de dependencias con uno de estos nombres:

```text
Depends on
Dependencies
Deps
After
Blocked by
Dependencias
```

La plantilla estándar usa `Depends on`. Todas las filas deben rellenarla:

```text
—                         root real, no tiene predecessor
P02-S01-T001              depende de una task exacta
P02-S01-T001..T004        depende de un rango de tasks del mismo step
P02-S01                   depende de todas las tasks de un step
P02                       depende de todas las tasks de una phase
previous                  conserva orden local cuando no se puede paralelizar
```

Si la columna falta, el bootstrap crea `bootstrap error: missing dependency column`. Si la columna existe pero todo usa `previous`, será DAG explícito pero sin ahorro útil.

## 4. Columnas mínimas del Coverage Registry

El checklist debe incluir esta tabla con la primera columna exacta `Slice ID` y estas columnas mínimas en este orden:

```text
Slice ID
Tipo
Target
Step
Product increment
Build state
Risk level
Verify mode
Depends on
Conflict group
Write set
Journey refs
Pantalla/Ruta
Endpoint
Tablas DB
Origen-Instr
Origen-TechGuide
Acceptance mínimo
Verify mínimo
Domain rule refs
Application logic refs
Core logic refs
Permission refs
State refs
Failure refs
Integration refs
UI refs
Data refs
Observability refs
Evaluation refs
```

Estas columnas permiten que el planner construya el task pack sin adivinar:

- `Risk level` y `Verify mode` deciden la profundidad del gate: `/next-slice` encadena verificación siempre que validator/tester pasen; sólo slices `low + auto`, deterministas y sin cierre de journey pueden usar el helper estrecho `/auto-verify-slice`.
- `Depends on` alimenta la matriz de adyacencia del DAG.
- `Conflict group` y `Write set` evitan paralelizar slices que comparten ficheros, routers, state handlers, migraciones, workflows o dependencias globales.
- `Journey refs` conecta slices con journeys.
- `Pantalla/Ruta`, `Endpoint` y `Tablas DB` evitan pantallas, endpoints o tablas huérfanas.
- `Domain rule refs` conecta cada slice con reglas `DR-*`.
- `Application logic refs` conecta cada slice con casos de uso `AL-*`.
- `Core logic refs` conecta cada slice con lógica central `CORE-*`: algoritmo, motor de precios, ranking, matching, scoring o cualquier motor especializado.
- `Permission refs`, `State refs` y `Failure refs` obligan a pensar permisos, estados/transiciones y errores antes de implementar.
- `Integration refs`, `UI refs`, `Data refs`, `Observability refs` y `Evaluation refs` se rellenan cuando la slice toca integraciones, pantallas, datos persistentes, auditoría o evaluación determinista.

## 4.b Contratos lógicos genéricos

Los cinco documentos source-of-truth siguen siendo los mismos. No añadas un sexto documento. La lógica adicional se expresa con IDs trazables dentro de esos documentos:

```text
DR-*       Domain Logic / reglas de dominio
AL-*       Application Logic / casos de uso internos
CORE-*     Core Logic / algoritmo, motor central o lógica especializada
AUTH-*     Permission Logic / permisos y acceso
STATE-*    State Logic / estados y transiciones
ERR-*      Failure Logic / errores y recuperación
INT-*      Integration Logic / integraciones y efectos externos
UI-*       UI Logic / comportamiento de pantalla
DATA-*     Data Logic / ciclo de vida de datos
OBS-*      Observability Logic / auditoría y trazabilidad
EVAL-*     Evaluation Logic / evaluación determinista
```

Cadena mental esperada:

```text
Journey -> Application Logic -> Core Logic -> Domain Rules -> Permissions -> State -> Errors -> Data/Integrations -> UI -> Audit -> Verify
```

`CORE-*` es deliberadamente genérico: puede describir un algoritmo financiero, un motor de precios, un ranking de papers, una recomendación, un matching, un cálculo de rutas o cualquier lógica central especializada. El registry sólo referencia IDs; el detalle vive en `instrucciones.md` y se aterriza técnicamente en el Technical Guide.
- `Origen-Instr` y `Origen-TechGuide` apuntan a las secciones exactas de los otros dos docs.
- `Acceptance mínimo` y `Verify mínimo` se convierten en checklist ejecutable de cada task.

## 5. Cómo diseñar dependencias y conflictos para paralelizar bien

Usa dependencias reales, no decorativas. Una task debe depender de otra solo si necesita su output para implementarse o verificarse. Usa `Conflict group`/`Write set` para otro problema distinto: dos tasks pueden ser independientes en el DAG, pero no deben ejecutarse a la vez si pisan los mismos ficheros o recursos globales.

Patrón recomendado:

```text
P00 roots en paralelo: scaffold, design tokens, scripts dev cuando no pisan los mismos ficheros.
P01 identidad/datos base: secuencial donde haya migraciones o contratos compartidos.
P02 motor: migraciones root -> endpoints/use cases en paralelo -> AI/tools/reference retrieval que dependan de contratos.
P03 front: pantallas dependen de endpoints que consumen; pantallas independientes pueden ir en paralelo.
Journey slices: dependen de todas las pantallas/endpoints que componen el journey.
P04 harden: depende de journeys críticos.
P05 release: depende de P04.
```


Patrón de conflictos recomendado:

```text
Migraciones del stack: Conflict group = db:migrations; Write set = <migrations_root>/**
Router frontend declarado:     Conflict group = router;        Write set = {{frontend_router_path}}
Theme/design:       Conflict group = theme;         Write set = {{frontend_theme_root}}/**
Deps del stack declarado: Conflict group = dependencies;  Write set = <dependency_manifest>; <lockfile>
Workflow CI:        Conflict group = ci;            Write set = .github/workflows/**
```

`/next-wave` usa esos campos para proponer solo terminales seguros. `claim_task.py` repite la validación para que un claim manual no pueda pisar una task ya activa.

Para un join, declara todos los predecessors:

```text
| P03-S04-T001 | journey | J101 e2e | Step 3.4 | P03-S01-T001, P03-S02-T001, P03-S03-T001 | J101 | ... |
```

El orquestador no desbloquea ese nodo hasta que **todos** esos predecessors estén `done`.

## 6. Cableado endpoint/front/journey

Cada endpoint de `TECHNICAL_GUIDE §6.2` debe estar en el checklist como slice `api`, o debe declarar que es `internal/no-front`, `webhook`, `job`, `admin-only` o similar.

Cada endpoint con consumidor UI debe aparecer en al menos una ruta de `TECHNICAL_GUIDE §6.1` o en un journey de `instrucciones.md §3.7`.

Cada ruta de `TECHNICAL_GUIDE §6.1` debe especificar:

```text
ruta del router declarado
Page/Widget
Auth
Journey refs
Endpoints consumidos
Estado cliente/state handler
Estados UI obligatorios: loading, empty, error_network, error_validation, permission_denied, success
Next action
Slice ID
```

Estos campos UX no son decorativos: el planner los copia al task pack y `check-wiring-contract.sh --strict --require-new-template-columns` los valida para que una pantalla no llegue al developer sin journey, endpoint, estados o siguiente acción.

Cada journey debe cruzar dos o más pantallas y referenciar rutas, endpoints, tablas y slices existentes.

## 7. Copiar los documentos al sitio canónico

Cuando los cinco documentos estén aceptados, guárdalos aquí:

```text
docs/source-of-truth/instrucciones.md
docs/source-of-truth/<PROJECT>_TECHNICAL_GUIDE.md
docs/source-of-truth/<PROJECT>_IMPLEMENTATION_CHECKLIST.md
```

Debe haber exactamente un `instrucciones.md`, un `*_TECHNICAL_GUIDE.md` y un `*_IMPLEMENTATION_CHECKLIST.md` en `docs/source-of-truth/`.

## 8. Ingesta y checks obligatorios

Ejecuta:

```bash
python3 -B -S .claude/bin/bootstrap_source_of_truth.py --validate-only
python3 -B -S .claude/bin/bootstrap_source_of_truth.py --refresh
./scripts/check-task-dag.sh --strict
./scripts/check-journey-matrix.sh --strict
./scripts/check-wiring-contract.sh --strict --require-new-template-columns
```

Resultado esperado para DAG explícito:

```text
Source-of-truth contract is valid.
Bootstrapped project prefix: <PROJECT>
Task DAG: OK mode=explicit_dag nodes=<N> edges=<E> waves=<W>
Journey matrix coherent — <J> journeys validadas, 0 drifts
Wiring contract coherent — <R> routes, <E> endpoints, <T> registry rows, <J> journeys
```

Si ves `bootstrap error: missing dependency column`, vuelve al checklist y añade/rellena `Depends on`.

## 9. Qué genera el bootstrap

El bootstrap escribe estado derivado, no fuente de verdad:

```text
orchestrator-state/tasks/registry.json              fuente runtime canónica: tasks[] + task_dag.source_digest
orchestrator-state/tasks/runtime-state.json         estado runtime
orchestrator-state/tasks/work-items/*.yaml          work items por task
orchestrator-state/memory/task-dag.json             vista derivada: adjacency_index + adjacency_matrix + levels
orchestrator-state/memory/task-dag.md               vista derivada: waves legibles
orchestrator-state/memory/execution-graph.json      vista derivada: grafo de journeys/slices/docs
orchestrator-state/memory/PROGRESS.md               snapshot vivo inicial
```

No edites estos ficheros a mano salvo para debug. Si cambia el orden del DAG, edita el Coverage Registry y vuelve a ejecutar bootstrap. `check-task-dag --strict` compara las vistas contra `registry.task_dag.source_digest` para detectar refreshes incompletos.

## 10. Ejecutar en terminales como Airflow

Pide la wave actual:

```bash
./scripts/next-wave.sh --limit 4
```

El script imprime comandos copy/paste de este estilo:

```bash
BOOTSTRAP_ROOT="${CLAUDE_ORCHESTRATOR_ROOT:-$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)}" && ROOT="$(bash "$BOOTSTRAP_ROOT/scripts/ensure-task-worktree.sh" --print-root)" && WT="$(bash "$ROOT/scripts/ensure-task-worktree.sh" P02-S03-T001)" && cd "$WT" && PACK="$WT/orchestrator-state/tasks/task-packs/P02-S03-T001.md" && if [ ! -f "$PACK" ]; then PACK="$ROOT/orchestrator-state/tasks/task-packs/P02-S03-T001.md"; fi && export CLAUDE_ORCHESTRATOR_ROOT="$ROOT" CLAUDE_WORKTREE_ROOT="$WT" CLAUDE_ACTIVE_TASK_ID=P02-S03-T001 CLAUDE_TASK_PACK="$PACK" && echo 'Ahora ejecuta en Claude Code: claude --agent main-orchestrator --permission-mode bypassPermissions "/next-slice P02-S03-T001"'
```

Abre un terminal por task ready. En cada terminal:

```bash
export CLAUDE_ACTIVE_TASK_ID=<TASK_ID> CLAUDE_TASK_PACK=orchestrator-state/tasks/task-packs/<TASK_ID>.md
# dentro de Claude Code:
/next-slice <TASK_ID>
```

`/next-slice` hace el claim atómico después del plan humano. El planner enriquece `orchestrator-state/tasks/task-packs/<TASK_ID>.md`. Developer, official-docs-researcher, validator, tester y debugger deben leer ese pack por `TASK_ID`.

## 11. Cierre de cada nodo

El cierre correcto de una task en el flujo actual es:

```text
/next-slice <TASK_ID>
  -> planner
  -> developer (+ official-docs-researcher si aplica)
  -> validator || tester
  -> debugger loop si falla
  -> tester pass
  -> /verify-slice automático
  -> hard reset + datos reales/proporcionados + UI humana + logs + DR-*
  -> verified_pending_close

/closer <TASK_ID>  # manual, lo escribe el usuario
  -> report + baseline sync
  -> commit atómico y workflow Git configurado (`./scripts/git-workflow.sh`)
  -> runtime cleanup Docker/Rancher de la slice (`cleanup-slice-runtime.sh`)
  -> slice-clean
  -> cleanup-worktrees + deferred cleanup
  -> task done
  -> successors desbloqueados si todos sus deps están done y no hay conflicto activo
```

`/next-slice` no spawnea `closer`. El closer no debe marcar `done` sin handoff, validator pass, tester pass y `VERIFY_OUTCOME: verified` o waiver explícito. En el flujo normal, `tester pass -> ready_for_close`, `slice-verifier verified -> verified_pending_close`, y sólo `/closer` manual puede invocar `closer committed -> done`. El bloque `## verify-slice` debe incluir evidencia humana-real: datos reales/proporcionados, sin stubs, botones/controles revisados, logs runtime/Rancher limpios cuando apliquen, `DOMAIN_RULES_VERIFIED` para reglas `DR-*` y prueba visual según superficie: browser MCP para web/browser o Dart/Flutter MCP con simulador/emulador/dispositivo para Flutter mobile. Si el push falla, falta `RUNTIME_CLEANED: yes` o quedan worktrees sucios, el cierre queda bloqueado.

## 12. Phase gate antes de avanzar

Al terminar una phase, ejecuta:

```bash
./scripts/phase-gate.sh P03
# o, si quieres verificar Git además:
./scripts/phase-gate.sh P03 --require-git-clean
```

El gate exige que todas las tasks de la phase estén `done`, que sus reports/evidence/handoffs existan, que no queden `pending_journey_verifications`, y que los journeys cerrados por esa phase estén `verified` o `waived`. Si falla, no abras la siguiente phase aunque el DAG tenga nodos ready.

## 13. DAG explícito obligatorio

Missing dependency column:

```text
Coverage Registry sin Depends on
bootstrap => bootstrap error: missing dependency column (bloqueo operativo)
una sola cadena secuencial
/next-slice sin TASK_ID específico
```

DAG explícito:

```text
Coverage Registry con Depends on relleno
bootstrap => mode=explicit_dag
/next-wave lista nodos ready
varios terminales pueden ejecutar nodos independientes
joins esperan a todos sus predecessors
```

Ambos modos comparten los mismos agentes, hooks, quality gates, memoria y closer. El DAG solo cambia el scheduling y añade packs por task para evitar corrupción entre terminales.


## Contrato de datos reales para verificación

Al rellenar el `TECHNICAL_GUIDE`, incluye la sección `Verification Data Contract`. Cada journey/flow verificable debe declarar persona/rol, datos reales/proporcionados, carga de datos reales/proporcionados permitida, reset/cleanup y slices vinculados. `/verify-slice` y `/verify-journey` usan esa sección: los mocks solo valen para unit tests o edge cases marcados como `synthetic-edge-case`, no para cerrar slices productivas.


## Production hardening actual

Usa source-of-truth acumulativo baseline+vN, `Risk level`, `Verify mode`, phases/steps/journeys completos sin topes artificiales y verify con datos reales/proporcionados. Ejecuta bootstrap + check-task-dag + check-journey-matrix + check-wiring-contract antes de waves.


## Contrato front→back→DB en cada fila

Al generar el checklist, cada slice productiva debe poder ejecutarse sin adivinar contexto: la fila debe declarar journey, pantalla/ruta, endpoint, tablas, origen funcional, origen técnico, write set, conflict group, acceptance y verify con datos reales/proporcionados. El bootstrap copia estos campos a `work-items/*.yaml` y al `task-pack`; si falta el contrato, los agentes deben bloquear o registrar follow-up.

## Runtime logs, Rancher workers y datos humanos reales

En `STACK_PROFILE.yaml` declara cómo levantar, resetear, observar y limpiar el runtime real. Si hay Docker Compose, el project name debe derivarse del `TASK_ID` (`docker compose -p <compose_project>`) para aislar contenedores/redes/volúmenes entre worktrees paralelos, y los puertos host deben salir de `runtime.port_defaults` + `CLAUDE_*_PORT` para que el allocator detecte puertos ocupados/reservados y asigne libres por slice. Declara también `verification.docker.compose_file` cuando el compose real no está en la raíz; el runtime resolver acepta `{task_slug}` y `{{task_slug}}` en `compose_project_template`. Al cerrar, `scripts/cleanup-slice-runtime.sh --task <TASK_ID> --apply --strict` debe poder borrar sólo recursos de esa slice: contenedores/redes/volúmenes del Compose project, imágenes locales/labelled creadas por ese project y reservas `dev-ports`. Si hay Rancher/Kubernetes/worker/colas, añade el comando real para capturar logs del worker, el cleanup de workloads/jobs creados por la slice y marca si los logs son obligatorios para verificar slices que tocan jobs, colas, IA, PDFs o procesos asíncronos.

`/verify-slice` no debe cerrar con datos inventados. Para PDFs/documentos/LLM, el source-of-truth debe declarar artefactos reales/proporcionados, hashes o rutas, pipeline esperado y campos persistidos observables. El agente debe pasar esos artefactos por el flujo real del producto y registrar evidencia; no vale pegar al LLM un texto inventado.


### Flutter mobile verify-slice

Si `STACK_PROFILE.yaml` declara `frontend.framework: flutter` y `frontend.visual_check: simulator|emulator|device`, `/verify-slice` debe usar siempre el Dart/Flutter MCP real: `MCP_CLIENT: dart` (o `flutter`/`flutter-driver`) y `VISUAL_CHECK_METHOD: simulator|emulator|device`. Para Flutter web sigue siendo válido `MCP_BROWSER: chrome-devtools|claude-in-chrome|agent360-browser-mcp|browser-mcp`. No cierres una slice mobile con una verificación sólo web. Configuración MCP recomendada: `claude mcp add --transport stdio dart -- dart mcp-server`.
