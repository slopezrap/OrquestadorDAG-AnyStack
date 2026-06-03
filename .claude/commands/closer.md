---
description: Cierre manual de una slice ya verificada. Sólo corre después de /next-slice auto-verify o /verify-slice con VERIFY_OUTCOME=verified; genera report, baseline sync, commit, workflow Git y cleanup.
argument-hint: "<TASK_ID>|--task <TASK_ID>  (o terminal con CLAUDE_ACTIVE_TASK_ID exportado)"
---

# /closer

## Rule loading

Antes de ejecutar este comando, considera cargadas las reglas no-scoped de `.claude/rules/`. Si no ves esas reglas en contexto tras `/clear`, léelas explícitamente en este orden: `00-source-of-truth.md`, `01-non-negotiables.md`, `02-phase-execution.md`, `03-dev-loop.md`, `04-traceability.md`, `05-runtime-write-contract.md`.

## Propósito

Este comando es el único punto manual para invocar el subagente `closer` después de que una slice haya quedado verificada.

```text
/next-slice <TASK_ID>  -> implementación + verify automático -> verified_pending_close
/verify-slice <TASK_ID> -> recovery/verificación manual       -> verified_pending_close
/closer <TASK_ID>       -> report + baseline + commit + Git workflow + cleanup -> done
```

`/closer` no implementa, no verifica visualmente y no corrige producto. Si falta verificación, vuelve a `/verify-slice`. Si hay defecto de producto in-scope, vuelve a `debugger -> validator ‖ tester -> verify`.

## Production DAG mode

MODO DAG ACTIVO: production = explicit_dag.

Unidad cerrable = TASK_ID canónico del registry. No existe cierre por implicit selector ni por fase completa.

Todo Agent spawn desde `/closer` debe recibir `TASK_ID`, `CLAUDE_TASK_PACK` y el aviso production DAG mode. En este comando sólo se permite spawnear **un único** subagente `closer`.

## Root split obligatorio

- Lee `registry.json`, `runtime-state.json`, `PROGRESS.md`, `task-dag.*` desde `$CLAUDE_ORCHESTRATOR_ROOT/orchestrator-state/`.
- Lee/escribe handoff, evidence, report y task-pack desde la worktree activa (`./orchestrator-state/tasks/...`) cuando la slice corre en worktree.
- No registres follow-ups por errores mecánicos del orquestador: root stale, heading de handoff, checker/lint flake, cleanup omitido, PR abierta/queued o CI pendiente. Corrige, reintenta o bloquea; FU solo para trabajo real de producto fuera de scope.

## Paso 1 — Preflight

1. Resuelve `<TASK_ID>` desde argumento o `CLAUDE_ACTIVE_TASK_ID`.
2. Confirma checkout correcto:

```bash
./scripts/ensure-task-worktree.sh --check-current <TASK_ID>
```

En `pr-flow`, `/closer` debe correr desde el worktree/rama del TASK_ID; en `push-to-main`, desde `main`. Si estás en otro checkout, PARA.

3. Ejecuta el router mecánico:

```bash
./scripts/verify-slice-state.sh <TASK_ID> --json
```

Interpretación:

- `invoke_closer` -> continúa. Significa que validator/tester/verify están verdes y el handoff pasa contrato.
- `invoke_slice_verifier` -> PARA: falta verificación humana-real. Ejecuta `/verify-slice <TASK_ID>` o relanza `/next-slice <TASK_ID>` si la implementación aún no terminó.
- `invoke_debugger_or_register_followup` o `invoke_debugger` -> PARA: hay issues o estado `needs_debug`; vuelve al ciclo debugger/retest/verify.
- `wait_validator_tester` -> PARA: `/next-slice` no terminó validator/tester.
- `post_closer_done` -> no relances closer; resume que la task ya está `done`.
- `blocked` -> corrige el blocker mecánico o de producto indicado; no cierres por intuición.

## Paso 2 — Contratos de handoff

Valida siempre:

```bash
./scripts/check-handoff-contract.sh <TASK_ID> --require-ready-for-close --require-verify-slice --require-production-observability
```

Si la task toca UI, UX, journey, rutas, pantallas, VISUAL_CONTRACT_CHECK/visual contract, auth visible, navegación o `journey_refs`, valida además:

```bash
./scripts/check-handoff-contract.sh <TASK_ID> --require-ready-for-close --require-verify-slice --require-screen-journey-review --require-production-observability
```

Si el checker dice que hay código o artefactos productivos más nuevos que el bloque `## verify-slice`, PARA y relanza `/verify-slice <TASK_ID>` antes de cerrar.

Si el task pack declara `Domain rule refs`, inspecciona el handoff antes de spawnear `closer`: debe existir `DOMAIN_RULES_VERIFIED` o evidencia equivalente que cubra cada regla `DR-*` aplicable. Si falta, PARA y relanza `/verify-slice <TASK_ID>` con foco en esas reglas de dominio.

Además exige observabilidad productiva antes de cerrar: `REAL_USER_VERIFIED: yes`, `NO_STUB_DATA: yes`, `NO_STUB_DATA_USED: yes`, `HUMAN_REPRODUCTION: yes`, `UI_ACTIONS_VERIFIED` o `BUTTONS_AND_CONTROLS_CHECKED` cuando haya UI/UX, `RUNTIME_LOGS_REVIEWED`, `RUNTIME_LOGS_CHECKED: yes`, `ERROR_LOGS_STATUS: clean|no_errors`, `RUNTIME_LOG_ERRORS: 0`, `LOG_EVIDENCE`, `DOCKER_COMPOSE_PROJECT`, `DOCKER_PORTS_ALLOCATED: yes|not_applicable:<reason>` y `RANCHER_WORKER_LOGS_REVIEWED`/`RANCHER_WORKER_LOGS_CHECKED` limpio o `not_applicable:<reason>`. Si los logs browser/front/back/DB/worker/Docker/Rancher tienen errores, crashloops, exceptions, OOM, readiness/liveness failures, jobs fallidos o stacktraces, no cierres: vuelve a `/verify-slice <TASK_ID>` después de corregir y relanzar la verificación.

## Paso 3 — Spawn único de closer

Si los checks pasan, spawnea **un único** subagente `closer` con este contexto literal:

```text
TASK_ID: <TASK_ID>
CLAUDE_TASK_PACK: orchestrator-state/tasks/task-packs/<TASK_ID>.md
MODO DAG ACTIVO: production = explicit_dag.
cierra sólo el TASK_ID explícito.
El estado verificado previo es verified_pending_close; sólo closer puede pasar a done. Confirma en el report que la verificación fue humana-real, sin datos stub/fake, con logs runtime limpios, con Docker Compose project aislado de la slice, puertos host asignados por slice y con Rancher/worker logs limpios o justificados. Si el task pack declara Domain rule refs, confirma que las reglas DR-* aparecen cubiertas por DOMAIN_RULES_VERIFIED/evidencia real.
Las FU formales proposed del origin_task_id se meten en la PR, no bloquean este close.
Ejecuta report + sync baseline + git-add-slice + commit + workflow Git configurado mediante ./scripts/git-workflow.sh + `scripts/cleanup-slice-runtime.sh --task <TASK_ID> --apply --strict` + slice-clean + cleanup-worktrees + deferred cleanup. `git-add-slice` debe crear/stagear `orchestrator-state/tasks/lifecycle-events/<TASK_ID>.json`; no stagees `registry.json` ni crees commits manuales de sync post-close state. La limpieza runtime debe borrar contenedores/redes/volúmenes del Docker Compose project de la slice, imágenes locales/labelled creadas por ese project, liberar `orchestrator-state/dev-ports/<compose_project>.*` y ejecutar `verification.rancher.cleanup_cmd`/`observability.rancher_cleanup_cmd` si el proyecto creó workload/job Rancher por slice. El cleanup de worktrees debe ser hook-safe: no debe borrar la worktree activa del closer antes del SubagentStop; `active_deferred=1` es aceptable si no hay dirty/skipped y el cleanup imprimió `DEFERRED_CLEANUP_COMMAND` y dejó una petición en `cleanup-requests/`.
En pr-flow, done exige PR merged y root canónico sincronizado; PR abierta/queued = blocked mecánico, no FU.
```

Acepta cierre sólo si el trailer de `closer` trae exactamente:

```text
OUTCOME: committed
NEXT_STATUS: done
REPORT_READY: yes
BASELINE_SYNC_READY: yes
GIT_READY: yes
PUSH_READY: yes
GIT_WORKFLOW_READY: yes
RUNTIME_CLEANED: yes
WORKTREES_CLEANED: yes
```

Si `closer` devuelve `blocked` por PR pendiente, CI rojo, auto-merge no habilitado, cleanup dirty o root canónico dirty, no lances debugger salvo que el bloqueo sea un defecto de producto. Corrige el bloqueo mecánico y relanza `/closer <TASK_ID>`; la verificación existente en handoff sigue siendo válida si el código no cambió.

## Trailer final del comando

Resume al usuario:

```text
TASK_ID: <TASK_ID>
CLOSER_ACTION: invoked|blocked|already_done
REPORT_READY: yes|no
BASELINE_SYNC_READY: yes|no
GIT_READY: yes|no
PUSH_READY: yes|no
GIT_WORKFLOW_READY: yes|no
RUNTIME_CLEANED: yes|no
WORKTREES_CLEANED: yes|no
NEXT_ACTION: /next-slice | fix mechanical blocker | inspect PR/CI/runtime cleanup
```
