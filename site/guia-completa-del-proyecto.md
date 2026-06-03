# Guía completa del proyecto OrquestadorDAG AnyStack

Este documento explica el proyecto de forma integral: qué problema resuelve, cómo se organiza, qué hace cada carpeta, qué hace cada tipo de fichero, cómo fluye una tarea por el DAG, cómo intervienen los agentes, qué validan los scripts y qué debe tocarse o no tocarse durante el uso normal.

La idea central es sencilla, pero el sistema está diseñado con muchas protecciones: este repositorio no es una aplicación final, sino un marco de trabajo para construir aplicaciones de forma gobernada con Claude Code. El repositorio convierte una especificación funcional y técnica en una cola de tareas atómicas, ordenadas por dependencias, ejecutadas por slices y cerradas con evidencias reales.

---

## 1. Definición corta

OrquestadorDAG AnyStack es un orquestador de desarrollo asistido por Claude Code. Su objetivo es transformar un conjunto de documentos fuente en un flujo de implementación controlado por DAG.

En la práctica, hace esto:

```text
Documentos fuente del producto
        ↓
Bootstrap del orquestador
        ↓
Registry de tareas y contratos derivados
        ↓
Waves de tareas listas
        ↓
Slices aisladas por TASK_ID
        ↓
Implementación, validación, pruebas y verificación real
        ↓
Cierre con reporte, baseline, Git workflow y limpieza
```

El sistema intenta evitar cuatro problemas típicos de desarrollo con agentes:

1. Que el agente implemente sin una fuente de verdad clara.
2. Que se mezclen muchas tareas en una sola intervención.
3. Que se marque como terminado algo que no fue verificado con datos reales.
4. Que el estado del proyecto se rompa por ediciones manuales, ramas sucias o cierres incompletos.

---

## 2. Modelo mental del repositorio

El proyecto se entiende mejor separando tres capas:

```text
.claude/
  Configuración estática del orquestador.
  Define reglas, agentes, comandos, hooks, skills, schemas y contratos.

orchestrator-state/
  Estado runtime generado durante el trabajo.
  Contiene registry, memoria, handoffs, reports, evidencias, logs y estado de tareas.

docs/source-of-truth/
  Entrada canónica del producto que se quiere construir.
  Contiene los documentos fuente que alimentan el bootstrap.
```

La regla principal es:

```text
.claude/ define cómo trabaja el sistema.
orchestrator-state/ registra qué está pasando.
docs/source-of-truth/ define qué producto se debe construir.
```

El framework no debe improvisar producto desde la conversación. Debe leer la especificación, derivar tareas y ejecutar solo lo que el DAG permite.

---

## 3. Flujo operativo completo

El flujo esperado es el siguiente:

```text
1. Se preparan los documentos en docs/source-of-truth/.
2. Se ejecuta el bootstrap.
3. Se genera orchestrator-state/tasks/registry.json.
4. Se consulta la wave actual con /next-wave.
5. Se abre una terminal por tarea lista cuando procede.
6. Se ejecuta /next-slice TASK_ID.
7. El planner prepara contexto y alcance.
8. El developer implementa solo esa slice.
9. Validator y tester revisan en paralelo.
10. Si hay fallo, debugger corrige lo mínimo.
11. verify-slice valida la slice contra aplicación real.
12. closer cierra manualmente: report, baseline, commit, Git workflow y limpieza.
13. La tarea pasa a done solo al final del cierre.
```

La separación entre implementación y cierre es deliberada. Una tarea implementada no es una tarea terminada. Una tarea con tests verdes tampoco es necesariamente una tarea terminada. En este sistema, una tarea está terminada cuando está verificada, reportada, integrada, sincronizada y limpia.

---

## 4. Los cinco documentos source-of-truth

El framework espera cinco entradas canónicas dentro de `docs/source-of-truth/`.

```text
instrucciones.md
*_IMPLEMENTATION_CHECKLIST.md
*_TECHNICAL_GUIDE.md
STACK_PROFILE.yaml
UX_CONTRACT.md
```

### 4.1 `instrucciones.md`

Define la intención del producto, restricciones del usuario, objetivos funcionales, prioridades, exclusiones y criterio general de éxito.

Sirve para responder preguntas como:

```text
¿Qué quiere construir el usuario?
¿Qué no debe construir el sistema?
¿Qué restricciones explícitas existen?
¿Qué comportamiento es obligatorio aunque no sea técnico?
```

### 4.2 `*_IMPLEMENTATION_CHECKLIST.md`

Es la lista estructurada de trabajo. Debe contener fases, slices, criterios de aceptación, dependencias, riesgos, evidencias requeridas y cobertura funcional.

Es especialmente importante porque de aquí se derivan muchas tareas del DAG.

Campos conceptuales relevantes:

```text
Task ID
Phase
Depends on
Conflict group
Write set
Acceptance criteria
Verify mode
Risk level
Journey refs
Endpoint refs
Table refs
Domain rule refs
```

### 4.3 `*_TECHNICAL_GUIDE.md`

Describe arquitectura técnica, módulos, decisiones de implementación, servicios, datos, contratos, endpoints, integraciones, colas, jobs, librerías y restricciones de infraestructura.

Sirve para que el developer no invente arquitectura durante una slice.

### 4.4 `STACK_PROFILE.yaml`

Declara el stack real del proyecto. Permite que el orquestador sea AnyStack y no dependa de un framework concreto.

Puede declarar cosas como:

```text
backend framework
frontend framework
mobile framework
module roots
commands de dev/test/lint
database
ports
Docker profile
design token enforcer
browser/mobile verification mode
Git workflow
```

Los scripts usan este fichero para saber qué comandos ejecutar y qué rutas inspeccionar.

### 4.5 `UX_CONTRACT.md`

Define journeys, pantallas, flujos de usuario, estados visuales, navegación, accesibilidad, mensajes, errores, empty states, loading states y coherencia visual.

Es clave para no limitar la verificación a tests de backend. Si una slice afecta la experiencia de usuario, debe poder validarse en navegador o móvil real.

---

## 5. Bootstrap: convertir documentos en sistema operativo de tareas

El bootstrap es el paso que transforma documentación en artefactos ejecutables.

El script principal es:

```text
.claude/bin/bootstrap_source_of_truth.py
```

Los wrappers humanos están en:

```text
scripts/setup-from-scratch.sh
scripts/reset-for-new-project.sh
```

y las skills relacionadas son:

```text
.claude/skills/bootstrap-source-of-truth-project/SKILL.md
.claude/skills/validate-source-of-truth-contract/SKILL.md
```

Durante el bootstrap se generan o actualizan artefactos como:

```text
orchestrator-state/tasks/registry.json
orchestrator-state/tasks/work-items/
orchestrator-state/tasks/task-packs/
orchestrator-state/memory/
docs/product-baseline/
contratos API derivados
vistas de DAG
índices de reglas de dominio
```

El bootstrap no debe ser una edición creativa de la especificación. Debe derivar estructura desde los documentos fuente y bloquear cuando falten datos críticos.

---

## 6. DAG y ejecución por waves

El proyecto usa DAG porque las tareas tienen dependencias explícitas. No todas las tareas pueden ejecutarse al mismo tiempo.

Una tarea puede estar lista si:

```text
sus dependencias están done
no entra en conflicto con otra tarea activa
su phase está permitida
no hay gates previos bloqueando
su estado runtime permite reclamarla
```

La wave actual se obtiene con:

```text
/next-wave
```

o con:

```text
scripts/next-wave.sh
```

El comando no implementa nada. Solo calcula tareas listas, conflictos, dependencias, comandos sugeridos y límites de concurrencia.

---

## 7. Slice: unidad mínima de trabajo

Una slice es una tarea DAG ejecutable de forma aislada. El identificador operativo es `TASK_ID`.

Cada slice debe tener:

```text
alcance claro
criterios de aceptación
write set
conflict group
dependencias
modo de verificación
riesgo
journeys o endpoints afectados
handoff runtime
evidencias esperadas
```

La slice se ejecuta con:

```text
/next-slice TASK_ID
```

La regla de oro es:

```text
Una terminal, una slice, un TASK_ID.
```

El sistema favorece worktrees por tarea para evitar que varias slices se pisen entre sí.

---

## 8. Estados de tarea

El sistema usa estados runtime para controlar el avance. Los nombres exactos pueden ampliarse según el contrato, pero el flujo conceptual es:

```text
pending
  ↓
ready
  ↓
claimed
  ↓
in_progress
  ↓
validator_tester_pending
  ↓
ready_for_verification
  ↓
verified_pending_close
  ↓
done
```

Estados de recuperación o bloqueo:

```text
needs_debug
blocked
waived
reopened
revised
```

El estado `done` no se debe escribir a mano. Debe producirlo el cierre correcto.

---

## 9. Cierre real de una tarea

El cierre lo hace:

```text
/closer TASK_ID
```

El cierre comprueba y ejecuta tareas como:

```text
validar que la slice fue verificada
generar reporte de cierre
sincronizar product baseline
preparar commit
correr Git workflow configurado
sincronizar lifecycle events
limpiar worktree y runtime auxiliar
marcar la tarea como done
```

El agente responsable es:

```text
.claude/agents/closer.md
```

La skill wrapper está en:

```text
.claude/skills/closer/SKILL.md
```

El cierre es manual y explícito porque concentra efectos importantes: Git, baseline, limpieza y estado runtime definitivo.

---

## 10. Raíz del repositorio

### `README.md`

Explica el propósito del framework, el flujo de uso, la separación entre source-of-truth y runtime state, y los comandos principales.

Es la entrada para un humano que abre el repositorio por primera vez.

### `CHEATSHEET.md`

Resumen operativo de comandos. Sirve para recordar el flujo sin leer todos los documentos largos.

### `.gitignore`

Evita que se suban artefactos temporales, caches y otros residuos de ejecución.

### `.github/workflows/`

Contiene workflows CI para validar el framework, ejecutar auditorías, schemas, doctor y pruebas de referencia.

### `examples/`

Contiene ejemplos ejecutables o fixtures de referencia. El más importante es `examples/golden-real-app/`.

### `orquestador-explicado/`

Contiene una explicación visual en HTML sobre DAG, agentes, hooks, scripts, estados y buenas prácticas.

### `site/`

Contiene material documental publicable o navegable. Este documento vive aquí porque explica el proyecto completo desde el punto de vista de operación, arquitectura y mantenimiento.

---

## 11. Carpeta `.claude/`

La carpeta `.claude/` es la configuración estática del sistema. No es estado de producto.

Contiene:

```text
CLAUDE.md
settings.json
settings.local.example.json
orchestrator-contract.json
agents/
commands/
skills/
rules/
bin/
schemas/
git-workflows/
enforcers/
```

### 11.1 `.claude/CLAUDE.md`

Es la instrucción global del repositorio para Claude Code.

Define:

```text
quién orquesta
cómo se interpretan las slices
qué se puede tocar
qué no se puede tocar
cómo se usan los agentes
cómo se verifica
cómo se cierra
cómo se usa orchestrator-state
cómo se separa raíz canónica de worktree
```

Su función es impedir que Claude trabaje como un asistente genérico. Debe comportarse como el orquestador del framework.

### 11.2 `.claude/settings.json`

Configura comportamiento de Claude Code dentro del proyecto.

Aspectos importantes:

```text
agente principal
modo de permisos
hooks
comandos de guardia
inyección de contexto
captura de trailers
registro de ledger
limpieza al parar
```

Hooks relevantes:

```text
PreToolUse
PostToolUse
SubagentStart
SubagentStop
SessionStart
Stop
```

El hook `SubagentStart` inyecta contexto al subagente al arrancar. No cierra tareas ni cambia lifecycle. Su función es entregar al agente información sobre TASK_ID, scope, write set, conflict group, contrato de trailers y reglas runtime antes de que actúe.

### 11.3 `.claude/settings.local.example.json`

Ejemplo de configuración local no compartida. Sirve para que cada usuario adapte detalles de entorno sin alterar la configuración común del repositorio.

### 11.4 `.claude/orchestrator-contract.json`

Es el contrato machine-readable del orquestador.

Define vocabulario y reglas para:

```text
agentes
roles
outcomes
trailers
permisos conceptuales de escritura
estados de tarea
handoffs
follow-ups
verify modes
journey gates
política de cierre
separación entre estático y runtime
```

Este fichero es clave porque permite que scripts y auditorías comprueben que los agentes no inventan resultados ni estados.

---

## 12. Agentes

Los agentes viven en:

```text
.claude/agents/
```

Cada fichero define un rol especializado. Los agentes se invocan desde comandos, skills o por el main orchestrator cuando el flujo lo requiere.

### `main-orchestrator`

Es el agente principal de sesión. Coordina el DAG, decide qué subagentes usar, respeta el estado runtime y evita saltarse gates.

No es un worker de slice. Es el controlador.

### `planner`

Prepara el contexto de una tarea lista. Lee registry, task pack, source-of-truth, progreso y dependencias.

Debe producir un contexto implementable, no código.

### `developer`

Implementa una única tarea aprobada. Debe respetar el write set, los criterios de aceptación, la arquitectura y el task pack.

No debe ampliar alcance salvo que el contrato de la tarea lo permita.

### `validator`

Revisa calidad, arquitectura, seguridad, alcance, integración y contrato. Es una revisión informativa pero obligatoria dentro del flujo.

Debe detectar desviaciones antes de cierre.

### `tester`

Ejecuta pruebas reales. Debe comprobar backend, frontend, logs, DB o cualquier runtime declarado por el stack profile.

No debe sustituir pruebas reales por afirmaciones.

### `debugger`

Actúa cuando validator, tester o verifier detectan un fallo. Debe hacer la corrección mínima necesaria y devolver la slice al flujo.

No es un segundo developer libre.

### `slice-verifier`

Verifica la slice contra aplicación real. Usa navegador o móvil cuando aplica, datos reales/proporcionados, journeys y evidencias.

Es el gate previo al cierre.

### `screen-journey-reviewer`

Revisa UX, pantallas, journeys, copy visual, estados y coherencia de navegación cuando una slice afecta experiencia de usuario.

### `closer`

Finaliza una slice verificada. Genera reporte, sincroniza baseline, ejecuta Git workflow, limpia y marca done.

Es el único agente que debe cerrar definitivamente una tarea.

### `official-docs-researcher`

Consulta documentación oficial cuando hay riesgo de APIs, frameworks, SDKs, proveedores, despliegue o comportamientos cambiantes.

Su trabajo reduce alucinaciones técnicas antes de implementar.

### `document-analyzer`

Analiza y normaliza los documentos source-of-truth durante bootstrap o cuando cambian documentos fuente.

### `project-architect`

Convierte intención y guía técnica en contrato arquitectónico ejecutable.

### `task-planner`

Convierte checklist, fases y pasos en tareas atómicas con dependencias, aceptación, riesgos y evidencia.

### `deployer`

Planifica o ejecuta despliegues cuando el DAG declara una tarea de deployment.

---

## 13. Comandos slash

Los comandos viven en:

```text
.claude/commands/
```

Son procedimientos humanos e invocables desde Claude Code.

### `/next-wave`

Lista la wave actual. Muestra tareas listas, dependencias, conflictos y comandos para trabajar en paralelo.

No implementa.

### `/next-slice TASK_ID`

Arranca una slice. Reclama tarea, prepara contexto, llama a planner, developer, validator, tester, debugger si hace falta y deja la slice lista para verificar o cerrar según resultado.

### `/verify-slice TASK_ID`

Verifica una slice ya implementada con app real. Puede requerir navegador, móvil, datos reales, logs y evidencias.

No cierra.

### `/auto-verify-slice TASK_ID`

Verifica automáticamente slices de bajo riesgo mediante comandos deterministas.

Debe usarse solo cuando el verify mode lo permite.

### `/verify-journey JOURNEY_ID`

Valida un journey completo de extremo a extremo. Se usa cuando las slices que componen un journey ya están cerradas.

### `/closer TASK_ID`

Cierre manual de una slice verificada.

### `/phase-gate PHASE_ID`

Comprueba que una fase está cerrada antes de avanzar. Valida tareas done, journeys, evidencias y estado Git si aplica.

### `/register-followup`

Convierte un hallazgo real en una propuesta formal de follow-up.

### `/promote-followup`

Promueve follow-ups aprobados a tareas DAG reales.

### `/revise-slice TASK_ID`

Reabre una slice concreta para corregir issues sin inventar una tarea paralela descontrolada.

### `/slice-maintain`

Ejecuta mantenimiento entre slices: limpieza conservadora, compactación de memoria o mantenimiento de agent memory.

---

## 14. Skills

Las skills viven en:

```text
.claude/skills/
```

Hay dos grupos:

```text
skills operativas originales
skills wrapper equivalentes a comandos slash
```

Las skills permiten que el orquestador use procedimientos reutilizables. En este proyecto están configuradas con:

```text
disable-model-invocation: false
```

Eso permite que el orquestador pueda invocarlas cuando el flujo lo requiera. Aun así, las skills que envuelven comandos deben seguir leyendo el comando correspondiente como procedimiento autoritativo.

### Skills operativas

```text
bootstrap-source-of-truth-project
build-task-pack
close-task
deploy-k8s
dev-loop
dev-verify
official-docs-check
phase-execution
validate-source-of-truth-contract
write-handoff
```

Estas skills representan tareas repetibles del framework: bootstrap, task packs, cierre, despliegue, dev loop, verificación, documentación oficial, ejecución por fase y handoff.

### Skills wrapper de comandos

```text
next-wave
next-slice
verify-slice
auto-verify-slice
verify-journey
closer
phase-gate
register-followup
promote-followup
revise-slice
slice-maintain
```

Estas skills delegan en los comandos slash equivalentes para evitar duplicar lógica. Su objetivo es permitir que tanto el humano como el orquestador puedan entrar por una interfaz moderna sin perder el procedimiento original.

---

## 15. Rules

Las reglas viven en:

```text
.claude/rules/
```

Son documentos normativos que definen cómo se debe comportar el sistema.

### `00-source-of-truth.md`

Define los documentos obligatorios, la autoridad de cada uno y las reglas para derivar tareas.

### `01-non-negotiables.md`

Define requisitos irrenunciables: calidad, seguridad, pruebas reales, no mocks como sustituto, logs limpios y ausencia de trabajo simulado.

### `02-phase-execution.md`

Explica cómo ejecutar por fases y slices, cómo respetar gates y cómo avanzar sin romper el DAG.

### `03-dev-loop.md`

Define cómo arrancar, reiniciar y verificar runtime local.

### `04-traceability.md`

Define trazabilidad, handoffs, evidencias, journeys, trailers, lifecycle y memoria.

### `05-runtime-write-contract.md`

Define qué puede escribir cada parte del sistema, dónde vive el estado runtime y cómo se protege la raíz canónica.

---

## 16. Hooks

Los hooks viven en `.claude/settings.json` y ejecutan scripts dentro de `.claude/bin/`.

### `PreToolUse`

Se ejecuta antes de herramientas sensibles. Sirve para controlar presupuesto de subagentes y proteger escrituras.

Scripts relacionados:

```text
.claude/bin/hook_spawn_budget.py
.claude/bin/hook_write_scope_guard.py
```

### `PostToolUse`

Registra actividad después de herramientas.

Script relacionado:

```text
.claude/bin/hook_update_ledger.py
```

### `SubagentStart`

Inyecta contexto a cada subagente cuando arranca.

Script relacionado:

```text
.claude/bin/hook_subagent_start_context.py
```

Entrega información como:

```text
TASK_ID activo
scope de tarea
write set
conflict group
journeys afectados
reglas de dominio
verify mode
contrato de trailers
contrato de escritura
recordatorios operativos
```

### `SubagentStop`

Captura el resultado final del subagente y valida trailers/outcomes.

Script relacionado:

```text
.claude/bin/hook_capture_subagent_stop.py
```

### `SessionStart`

Inyecta contexto global al arrancar una sesión.

Script relacionado:

```text
.claude/bin/hook_session_context.py
```

### `Stop`

Ejecuta tareas de cierre o limpieza diferida.

Script relacionado:

```text
.claude/bin/hook_finalize_deferred_cleanup.py
```

---

## 17. Scripts internos en `.claude/bin/`

Esta carpeta contiene la lógica principal del orquestador.

### Generación y lectura de estado

```text
bootstrap_source_of_truth.py
common.py
runtime_context.py
stack_profile.py
```

`bootstrap_source_of_truth.py` genera el registry y artefactos derivados.

`common.py` concentra utilidades compartidas.

`runtime_context.py` carga estado runtime para comandos, hooks y agentes.

`stack_profile.py` lee valores de `STACK_PROFILE.yaml`.

### DAG y planificación

```text
next_wave.py
claim_task.py
check_task_dag.py
inspect_task_state.py
check_phase_gate.py
```

Estos scripts calculan readiness, reclaman tareas, detectan ciclos, validan dependencias y verifican gates de fase.

### Contratos funcionales

```text
check_wiring_contract.py
check_journey_matrix.py
check_handoff_contract.py
generate_api_contracts.py
list_journey_closures.py
```

Estos scripts comprueban que endpoints, journeys, handoffs y contratos derivados siguen siendo coherentes.

### Verificación

```text
init_verify_slice_handoff.py
verify_slice_state.py
auto_verify_slice.py
check_runtime_logs.py
```

Preparan handoff de verificación, validan estado, ejecutan verificación automática cuando procede y revisan logs.

### Follow-ups y lifecycle

```text
register_followup_task.py
sync_lifecycle_events.py
sync_product_baseline.py
```

Gestionan hallazgos fuera de scope, sincronizan eventos tras merge y actualizan baseline del producto.

### Git y runtime

```text
runtime_git_guard.py
allocate_slice_ports.py
run_tests_async.py
reset_orchestrator_state.py
```

Protegen Git/runtime, asignan puertos por slice, ejecutan tests asíncronos y resetean estado del orquestador cuando se empieza otro producto.

### Hooks

```text
hook_capture_subagent_stop.py
hook_docs_discrepancy_check.py
hook_finalize_deferred_cleanup.py
hook_session_context.py
hook_spawn_budget.py
hook_subagent_start_context.py
hook_update_ledger.py
hook_write_scope_guard.py
```

Implementan la capa de enforcement conectada a Claude Code.

### Tests internos

```text
.claude/bin/tests/
```

Contiene pruebas unitarias y de integración del framework.

---

## 18. Schemas

Los schemas viven en:

```text
.claude/schemas/
```

Sirven para validar JSON y contratos runtime.

### `domain-rule-index.schema.json`

Valida el índice de reglas de dominio derivado de source-of-truth.

### `orchestrator-doctor-result.schema.json`

Valida la salida del doctor del orquestador.

### `runtime-log-check.schema.json`

Valida resultados de análisis de logs runtime.

### `stack-profile.schema.json`

Valida `STACK_PROFILE.yaml`.

### `task-record.schema.json`

Valida registros de tareas dentro del registry.

### `verify-slice-handoff.schema.json`

Valida handoff de verificación de slice.

---

## 19. Git workflows

Los workflows Git viven en:

```text
.claude/git-workflows/
```

### `push-to-main.sh`

Flujo simple para integrar directamente en main cuando el proyecto lo permite.

### `pr-flow.sh`

Flujo mediante branch, push, PR, merge, sincronización de main y limpieza. Es el flujo más estricto.

### `git-flow.sh`

Flujo alternativo para equipos que usan ramas de integración.

El workflow real se declara en el stack profile o configuración asociada.

---

## 20. Enforcers

Los enforcers viven en:

```text
.claude/enforcers/
```

### `design_tokens_v1/`

Define reglas para enforcement visual basado en tokens. Es independiente del framework frontend concreto.

### `design_tokens_v1.sh`

Dispatcher que lee `STACK_PROFILE.yaml` y elige scanner según framework frontend.

Soporta de forma general:

```text
Flutter/Dart
React/Next/Vite/TypeScript
SwiftUI como punto de extensión
none como no-op explícito
```

### `none.sh`

Enforcer vacío. Se usa cuando el stack declara que no quiere enforcement de design tokens.

---

## 21. `orchestrator-state/`

Esta carpeta contiene estado vivo. En un repositorio limpio está casi vacía, pero durante ejecución se llena.

Estructura conceptual:

```text
orchestrator-state/
  memory/
  tasks/
  agent-memory/
  dev-logs/
  hook-errors.log
```

### `orchestrator-state/tasks/`

Contiene registry, task packs, work-items, handoffs, reports y evidencias por tarea.

Fichero central:

```text
orchestrator-state/tasks/registry.json
```

Este fichero no debe editarse manualmente. Debe generarse y actualizarse por scripts controlados.

### `orchestrator-state/memory/`

Memoria runtime global. Puede contener progreso, decisiones, lifecycle events y resúmenes de ejecución.

### `orchestrator-state/agent-memory/`

Memoria específica por agente. Permite compactar contexto sin perder trazabilidad útil.

### `orchestrator-state/dev-logs/`

Logs generados durante dev loop, pruebas y verificaciones.

### `orchestrator-state/README.md`

Explica el rol de esta carpeta y advierte que no debe borrarse a mano durante un proyecto activo.

---

## 22. `scripts/`

La carpeta `scripts/` expone wrappers para humanos, CI y comandos de shell. Muchos scripts delegan en `.claude/bin/`.

### Bootstrap y setup

```text
setup-from-scratch.sh
reset-for-new-project.sh
```

Preparan o reinician el marco de ejecución para un producto.

### DAG y waves

```text
next-wave.sh
phase-gate.sh
check-task-dag.sh
inspect-task-state.sh
```

Calculan waves, validan DAG, inspeccionan tareas y bloquean avance de fase si algo no está cerrado.

### Contratos y matriz funcional

```text
check-journey-matrix.sh
check-wiring-contract.sh
check-handoff-contract.sh
check-progress-updated.sh
check-worktree-deps-visible.sh
```

Validan journeys, wiring, handoffs, progreso y visibilidad de dependencias desde worktrees.

### Verificación

```text
auto-verify-slice.sh
verify-slice-state.sh
journey-closures.sh
update-journey-verification.sh
check-runtime-logs.sh
```

Gestionan verificación por slice, verificación por journey, cierres funcionales y logs.

### Dev runtime

```text
dev-restart.sh
dev-restart.profile.sh
docker-hard-reset.sh
cleanup-slice-runtime.sh
allocate-slice-ports.sh
chrome-devtools-isolated-session.sh
chrome-mcp-doctor.sh
```

Arrancan o reinician runtime local, asignan puertos, limpian recursos de slice y preparan sesiones de navegador aisladas.

### Git y worktrees

```text
ensure-task-worktree.sh
git-add-slice.sh
git-workflow.sh
sync-main-before-wave.sh
runtime-git-guard.sh
check-git-identity.sh
check-staged-deletions.sh
cleanup-worktrees.sh
cleanup-closed-task-worktrees.sh
cleanup-deferred-worktrees.sh
cleanup-deferred-worktrees-loop.sh
cleanup-zombie-task-worktrees.sh
cleanup-merged-pr-branches.sh
configure-github-pr-cleanup.sh
```

Gestionan worktrees por tarea, staging de slice, workflows Git, limpieza conservadora y seguridad contra borrados accidentales.

### Follow-ups y baseline

```text
register-followup-task.sh
sync-product-baseline.sh
sync-lifecycle-events.sh
```

Crean follow-ups formales y sincronizan baseline/lifecycle tras cierres.

### Calidad, auditoría y CI local

```text
validate-orchestrator-schemas.sh
orchestrator-doctor.sh
run-all-tests.sh
run-golden-e2e.sh
smoke-template-profiles.py
audit-agent-reality.py
audit-agent-trailer-vocabulary.py
audit-template-screen-journey-redactor.py
audit-orchestrator-refactor-consistency.py
check-design-tokens.sh
check_design_tokens.py
check_web_design_tokens.py
```

Validan schemas, salud del framework, golden app, plantillas, coherencia de agentes, vocabulario de trailers y design tokens.

### Mantenimiento de memoria

```text
compact-agent-memory.py
slice-clean.sh
```

Compactan memoria por agente y limpian artefactos de slice.

---

## 23. `docs/`

La carpeta `docs/` contiene documentación fuente, plantillas y guías.

### `docs/source-of-truth/`

Debe contener los cinco documentos canónicos del producto activo.

En un framework limpio puede estar vacía salvo `.gitkeep`.

### `docs/templates/`

Contiene plantillas para crear los cinco documentos source-of-truth.

Perfiles:

```text
minimal
large-without-base
large-with-base
```

Cada perfil incluye:

```text
instrucciones.template.md
PROJECT_IMPLEMENTATION_CHECKLIST.template.md
PROJECT_TECHNICAL_GUIDE.template.md
STACK_PROFILE.template.yaml
UX_CONTRACT.template.md
```

### `docs/prompts/`

Contiene prompts para generar documentos source-of-truth con ChatGPT.

Fichero principal:

```text
PROMPT_SOURCE_OF_TRUTH_DAG.md
```

### `docs/guides/`

Contiene guías operativas para humanos.

```text
CHATGPT_DAG_SOURCE_OF_TRUTH_GUIDE.md
CHEATSHEET.md
MCP_BROWSER_VERIFY.md
```

### `docs/product-baseline/`

No es fuente inicial. Es el baseline acumulado del producto construido, sincronizado durante cierres.

### `docs/reports/`

Contiene plantillas o reportes de smoke/checks.

---

## 24. `examples/`

La carpeta `examples/` contiene fixtures y ejemplos de referencia.

### `examples/golden-real-app/`

Es una app pequeña de referencia para demostrar que el framework puede validar algo real.

Comprueba:

```text
servidor real
base de datos real
endpoint real
UI real
reglas de dominio
logs limpios
```

Es útil para CI y para comprobar que cambios en el framework no rompen el flujo base.

---

## 25. `site/`

La carpeta `site/` contiene documentación explicativa y material publicable.

### `site/diagrams/`

Diagramas Markdown sobre arquitectura, comandos, flujo DAG y outcomes.

### `site/html-site/`

Sitio HTML estático con páginas sobre comandos, flujo, negocio, outcomes, stack, templates y terminales.

### `site/guia-completa-del-proyecto.md`

Este documento. Explica cómo encajan todas las piezas del framework.

---

## 26. `orquestador-explicado/`

Contiene documentación HTML adicional orientada a explicar el framework visualmente.

Páginas relevantes:

```text
index.html
agentes.html
buenas-practicas.html
dag.html
flujo.html
hooks-locks.html
maquina-estados.html
scripts-git.html
```

Sirve para entender el sistema sin leer todos los ficheros técnicos.

---

## 27. Contrato de escritura

El proyecto separa rutas por autoridad.

### Se puede escribir durante ejecución normal

```text
orchestrator-state/
docs/product-baseline/
docs/reports/
archivos dentro del write set de la slice
```

### No se debe editar manualmente durante una slice

```text
.claude/
docs/source-of-truth/
orchestrator-state/tasks/registry.json
artefactos derivados críticos
```

### Por qué existe esta regla

Si una slice cambia el sistema que la gobierna, se pierde trazabilidad. Por eso el framework distingue entre trabajar en producto y modificar el propio orquestador.

---

## 28. Follow-ups

Un follow-up es trabajo detectado durante una slice que no pertenece al alcance actual.

El sistema distingue:

```text
bug in-scope
  Se arregla dentro de la misma slice.

hallazgo out-of-scope
  Se registra como follow-up.

hallazgo crítico
  Puede bloquear nuevas waves hasta promoverse, resolverse o quedar explícitamente aceptado.
```

Comandos:

```text
/register-followup
/promote-followup
```

Scripts:

```text
scripts/register-followup-task.sh
.claude/bin/register_followup_task.py
```

---

## 29. Verificación real

El framework insiste en verificación real.

Eso significa:

```text
no sustituir ejecución por razonamiento
no usar mocks como prueba final si el contrato pide datos reales
no cerrar sin logs/evidencia cuando aplica
no decir pass si no se ejecutó el flujo
```

La verificación puede incluir:

```text
navegador MCP
móvil MCP
HTTP real
DB real
capturas
logs front/back
journeys completos
pruebas automatizadas
evidencia manual estructurada
```

---

## 30. Product baseline

El product baseline es una fotografía mantenida del producto construido.

Vive en:

```text
docs/product-baseline/
```

Se actualiza durante cierre, no durante implementación normal.

Sirve para saber qué existe realmente en el producto tras cierres ya integrados.

---

## 31. Journey gates

Un journey puede cruzar varias slices. Por eso no siempre basta con verificar una slice aislada.

El flujo conceptual es:

```text
slice A done
slice B done
slice C done
  ↓
/verify-journey JOURNEY_ID
  ↓
journey cerrado
```

Esto evita que cada pieza funcione por separado, pero el flujo completo falle.

---

## 32. Worktrees

El proyecto usa worktrees para aislar tareas.

Scripts relevantes:

```text
scripts/ensure-task-worktree.sh
scripts/cleanup-worktrees.sh
scripts/cleanup-closed-task-worktrees.sh
scripts/cleanup-zombie-task-worktrees.sh
```

La idea es:

```text
cada TASK_ID trabaja en su espacio
cada rama contiene su slice
el cierre integra de forma controlada
la limpieza no borra trabajo sucio ni único
```

---

## 33. Git workflow

El cierre no termina en commit local solamente. Dependiendo del workflow configurado, puede implicar PR, merge, sincronización de main y limpieza.

El flujo más estricto es:

```text
feature branch
commit de slice
push
PR
merge
sync main
cleanup branch/worktree
runtime state done
```

La regla conceptual es:

```text
PR abierto no equivale a tarea done.
```

---

## 34. Qué debe hacer un humano al usarlo

### Para empezar un producto

```text
1. Rellenar docs/source-of-truth/ con los cinco documentos.
2. Ejecutar bootstrap.
3. Ejecutar doctor y schemas.
4. Consultar /next-wave.
5. Trabajar por TASK_ID.
```

### Para trabajar una tarea

```text
1. Abrir entorno de slice.
2. Exportar TASK_ID si el flujo lo pide.
3. Ejecutar /next-slice TASK_ID.
4. Revisar resultado.
5. Ejecutar /verify-slice si hace falta.
6. Ejecutar /closer TASK_ID cuando esté verificada.
```

### Para cerrar una fase

```text
1. Comprobar que las tareas están done.
2. Comprobar journeys relevantes.
3. Ejecutar /phase-gate.
4. Avanzar solo si no hay bloqueos.
```

---

## 35. Qué no debe hacer un humano

No conviene hacer esto:

```text
editar registry.json a mano
marcar tareas done manualmente
borrar orchestrator-state durante un producto activo
editar source-of-truth para tapar un fallo de implementación
cerrar sin verifier
hacer commit global con cambios fuera de write set
borrar worktrees sucios con comandos destructivos
convertir un bug in-scope en follow-up para avanzar rápido
```

El framework existe precisamente para evitar esos atajos.

---

## 36. Cómo se comprueba la salud del framework

Comandos útiles:

```text
bash scripts/orchestrator-doctor.sh --json
bash scripts/validate-orchestrator-schemas.sh --json
bash scripts/check-task-dag.sh
bash scripts/check-journey-matrix.sh
bash scripts/check-wiring-contract.sh
bash scripts/run-golden-e2e.sh
bash scripts/run-all-tests.sh
```

Auditorías:

```text
python3 -B -S scripts/audit-agent-reality.py
python3 -B -S scripts/audit-agent-trailer-vocabulary.py
python3 -B -S scripts/audit-template-screen-journey-redactor.py
python3 -B -S scripts/audit-orchestrator-refactor-consistency.py
```

Estas comprobaciones ayudan a detectar drift entre documentación, agentes, contratos, schemas y scripts.

---

## 37. Lectura de una slice por dentro

Una slice típica tiene esta información distribuida:

```text
registry.json
  estado, deps, conflict groups, write set, metadata

work-item
  descripción operativa de la tarea

task-pack
  contexto enriquecido para planner/developer

handoff
  lo que developer, validator, tester, debugger y verifier dejan registrado

report
  evidencia final generada por closer

lifecycle events
  eventos aplicados o reaplicados tras merge
```

El objetivo es que cualquier persona pueda reconstruir qué pasó, quién actuó, qué se verificó y por qué se cerró.

---

## 38. Relación entre comandos, skills y scripts

El proyecto tiene tres niveles de entrada:

```text
Comando slash
  Procedimiento humano/orquestador en .claude/commands/.

Skill
  Procedimiento reutilizable en .claude/skills/.
  En los wrappers, delega en el comando slash correspondiente.

Script
  Implementación ejecutable en .claude/bin/ o scripts/.
```

Ejemplo:

```text
/next-wave
  ↓
.claude/commands/next-wave.md
  ↓
.claude/skills/next-wave/SKILL.md puede delegar ahí
  ↓
scripts/next-wave.sh
  ↓
.claude/bin/next_wave.py
```

Esta separación permite que el procedimiento sea legible y la lógica dura sea comprobable.

---

## 39. Por qué el framework es AnyStack

No asume React, Flutter, Django, FastAPI, Rails, Laravel o Kubernetes por defecto.

El stack real se declara en:

```text
STACK_PROFILE.yaml
```

Y los scripts consultan ese perfil para decidir:

```text
qué comando arranca backend
qué comando arranca frontend
qué tests correr
qué rutas mirar
qué puertos usar
qué verifier aplicar
qué enforcement visual activar
qué Git workflow ejecutar
```

Por eso el orquestador puede adaptarse a varios tipos de proyecto.

---

## 40. Resumen final

El repositorio es un sistema de control para desarrollo con agentes. Sus piezas encajan así:

```text
docs/source-of-truth/
  Define el producto.

.claude/
  Define el sistema que gobierna a Claude Code.

.claude/bin/ y scripts/
  Ejecutan validaciones, bootstrap, gates, Git y runtime.

orchestrator-state/
  Guarda estado vivo, evidencias y memoria.

examples/
  Comprueba que el framework funciona con una app real mínima.

site/ y orquestador-explicado/
  Documentan el sistema para humanos.
```

La promesa del proyecto es:

```text
menos improvisación
más trazabilidad
menos cierres falsos
más verificación real
mejor paralelización
menos conflictos entre agentes
```

Para mantener esa promesa, hay que respetar tres reglas:

```text
1. El producto se define en source-of-truth.
2. El trabajo se ejecuta por TASK_ID.
3. Nada está done hasta que closer lo cierra correctamente.
```
