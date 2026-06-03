---
description: Verificación humana-real post-slice en modo DAG. Hard reset, navegador MCP, datos reales/proporcionados, logs front/back/DB y tabla de validación. Deja la slice en verified_pending_close; el cierre lo invoca el usuario con /closer.
argument-hint: "<TASK_ID>|--task <TASK_ID>  (o terminal con CLAUDE_ACTIVE_TASK_ID exportado)"
---

# /verify-slice

## Rule loading

Antes de ejecutar este comando, considera cargadas las reglas no-scoped de `.claude/rules/`. Si no ves esas reglas en contexto tras `/clear`, léelas explícitamente en este orden: `00-source-of-truth.md`, `01-non-negotiables.md`, `02-phase-execution.md`, `03-dev-loop.md`, `04-traceability.md`, `05-runtime-write-contract.md`.

## Production DAG mode — recordatorio obligatorio

MODO DAG ACTIVO: production = explicit_dag.

Unidad verificable = TASK_ID canónico del registry. No existe modo DAG-disabled improvisado. La ausencia de `Depends on` es error operativo, no fallback. Usa TASK_ID explícito por argumento o `CLAUDE_ACTIVE_TASK_ID`; si falta, para.

Todo Agent spawn desde verify-slice debe recibir TASK_ID, CLAUDE_TASK_PACK y el aviso production DAG mode. Usa exactamente `CLAUDE_TASK_PACK=orchestrator-state/tasks/task-packs/<TASK_ID>.md`. Esto incluye `slice-verifier`, `screen-journey-reviewer`, `debugger`, `validator` y `tester`. `closer` queda reservado al comando manual `/closer`.

Antes de verificar, confirma el checkout correcto:

```bash
./scripts/ensure-task-worktree.sh --check-current <TASK_ID>
```

En `pr-flow`, `/verify-slice` debe correr desde el worktree/rama del TASK_ID; en `push-to-main`, desde `main`. Si estás en otro checkout, PARA: no verifiques una rama distinta a la que implementó el developer.

## Root split obligatorio

- Lee `registry.json`, `runtime-state.json`, `PROGRESS.md`, `task-dag.*` desde `$CLAUDE_ORCHESTRATOR_ROOT/orchestrator-state/`.
- Lee/escribe handoff, evidence, report y task-pack desde la worktree activa (`./orchestrator-state/tasks/...`) cuando la slice corre en worktree.
- No registres follow-ups por errores mecánicos del orquestador: root stale, heading de handoff, checker/lint flake, cleanup omitido, PR abierta/queued o CI pendiente. Corrige, reintenta o bloquea; FU solo para trabajo real de producto fuera de scope.

## Flujo mecánico

```text
tester pass / validator approved
→ verify-slice-state router
→ slice-verifier                 # hard reset + reproducción humana + ## verify-slice + trailer
→ screen-journey-reviewer        # sólo si aplica UI/journey/visual contract
→ verified_pending_close          # fin de /verify-slice
→ /closer <TASK_ID>               # usuario invoca report + commit + workflow Git configurado + cleanup
→ done sólo si closer prueba commit/push/merge/cleanup
```

El estado intermedio correcto después del verify es `verified_pending_close`, no `done`. Sólo `closer` puede mover la task a `done`.

## Paso 1 — Reconstrucción de contexto

1. Resuelve `<TASK_ID>` desde argumento o `CLAUDE_ACTIVE_TASK_ID`.
2. Lee task pack `orchestrator-state/tasks/task-packs/<TASK_ID>.md`.
3. Lee handoff `orchestrator-state/tasks/handoffs/<TASK_ID>.md`.
4. Lee registry/runtime/PROGRESS desde root canónico, no desde snapshot viejo de worktree.
5. Si el pack no existe o no menciona el TASK_ID, bloquea antes de spawnear nada.

## Paso 2.5 — Router mecánico de estado

Ejecuta siempre antes de spawnear nada, y repítelo después de `slice-verifier`, `debugger`/retest o un `closer` blocked:

```bash
./scripts/verify-slice-state.sh <TASK_ID> --json
```

Acciones:

- `invoke_slice_verifier` → sigue al Paso 4.
- `invoke_closer` → la slice ya está verificada y lista para cierre manual; salta al Paso 6 para validar precondiciones y mostrar `/closer <TASK_ID>`. No spawnees `closer` desde `/verify-slice`.
- `invoke_debugger_or_register_followup` → sigue al Paso 5.
- `invoke_debugger` → spawnea `debugger`, luego `validator` y `tester` en paralelo, y relanza `/verify-slice <TASK_ID>`.
- `wait_validator_tester` → no hagas verify todavía.
- `post_closer_done` → no relances closer/debugger; resume estado.
- `blocked` → corrige el blocker mecánico; no crees FU de producto por ruido.

Regla dura: `/verify-slice` NO invoca closer; `closer` no se invoca desde `/verify-slice`. Cuando el helper devuelve `invoke_closer`, interprétalo como `ready_for_manual_closer`. `slice-verifier` sólo se invoca cuando devuelve `invoke_slice_verifier`.


## Verificación humana-real obligatoria

`/verify-slice` no es sólo un router de estados. El router decide CUÁNDO lanzar `slice-verifier`, pero `slice-verifier` debe ejecutar el contrato humano-real antiguo:

- Hard reset del entorno: parar servicios propios, reset DB, migraciones, datos base reales/proporcionados y datos específicos del slice desde `Verification Data Contract`.
- Reproducción real como usuario mediante el MCP visual aceptado para la superficie: web/browser usa Chrome DevTools MCP aislado como opción primaria, fallback 2 Claude-in-Chrome, fallback 3 Agent360 Browser MCP (`browser-mcp`); Flutter mobile usa Dart/Flutter MCP (`MCP_CLIENT: dart|flutter|flutter-driver`) con `VISUAL_CHECK_METHOD: simulator|emulator|device`.
- Si la app usa Docker Compose, el reset debe aislarse por slice con `docker compose -p <compose_project>` (`P01-S02-T003` → `p01-s02-t003`). Isolation por slice/project name, no por worktree. Además, antes de levantar servicios debe ejecutar el allocator de puertos (`allocate-slice-ports.sh` o `check-runtime-logs.sh`) para detectar puertos host ocupados y exportar `CLAUDE_FRONTEND_PORT`, `CLAUDE_BACKEND_PORT`, `CLAUDE_DB_PORT`, etc.; `-p` no evita colisiones de puertos host por sí solo.
- Observación de logs browser/front + back + DB + worker/queue + Docker Compose + Rancher/Kubernetes worker cuando el stack lo declare.
- Evidencia en `orchestrator-state/tasks/evidence/<TASK_ID>/verify-*` y `runtime-logs/runtime-log-check.json`.
- Tabla visible para el usuario con URL, qué probar, descripción, resultado esperado, observado y pasa/no pasa. Debe cubrir botones/controles afectados: click real, efecto visible, llamada real si aplica, persistencia y estados disabled/loading/error.
- Si la slice procesa PDFs/documentos/entradas LLM, usa artefactos reales/proporcionados, registra ruta/hash en `LLM_INPUT_ARTIFACTS`/`DATA_SOURCE_FILES`, ejecuta el pipeline real de producto y verifica `LLM_DOCUMENT_EXTRACTION`/persistencia. No sustituyas esto por pegar texto inventado a Claude.
- Bloque `## verify-slice` en handoff con `VERIFY_OUTCOME: verified|issues_found|blocked`.

El MCP visual es obligatorio para el gate humano. Debe ser **usable**, no sólo aparecer listado. Para web/browser, MCPs aceptados: `chrome-devtools`, `claude-in-chrome` y `agent360-browser-mcp`/`browser-mcp`. Política de elección web: intenta primero Chrome DevTools aislado (`--isolated` o `scripts/chrome-devtools-isolated-session.sh --task <TASK_ID>` + `--browser-url`), también para login/MFA si puede abrir una sesión visible por `TASK_ID`; si Chrome DevTools no está usable o no puede completar la sesión humana requerida, prueba `claude-in-chrome`; si tampoco responde, prueba Agent360 Browser MCP (`browser-mcp`). Para Flutter mobile, MCPs aceptados: `MCP_CLIENT: dart|flutter|flutter-driver` con `VISUAL_CHECK_METHOD: simulator|emulator|device`; registra `MCP_BROWSER: not_applicable:flutter_mobile`. Si Chrome DevTools MCP falla por lock del profile, diagnostica con `bash scripts/chrome-mcp-doctor.sh || true`, imprime instrucciones de aislamiento con `bash scripts/chrome-devtools-isolated-session.sh --task <TASK_ID>`, cambia a claude-in-chrome y después a Agent360 sólo si están realmente usables, o bloquea con `BLOCKER_REASON: browser_mcp_unavailable` + `MCP_DIAGNOSTIC`. Si Flutter mobile no tiene Dart/Flutter MCP usable, bloquea con `BLOCKER_REASON: flutter_mobile_mcp_unavailable` + acción requerida. Si los MCP están listados pero sus llamadas fallan, no hagas fallback a `curl` como cierre humano: dile al usuario que conecte/reinicie un MCP aceptado y relance `/verify-slice <TASK_ID>`. Si uno de los MCP ya completó la reproducción humana, no repitas con otro sólo porque otro esté roto.

`slice-verifier` tiene `maxTurns: 130` para absorber reproducción humana real con MCP web/mobile. No amplíes el budget de spawns ni el `spawn_budget` global para esto: el límite de 20 subagentes por slice sigue igual. El agente debe hacer preflight corto, usar el MCP usable elegido y reservar margen para evidencia + tabla + handoff + trailer. Si el MCP está roto o el scope visual excede la slice, debe bloquear limpio con `VERIFY_OUTCOME: blocked` y `BLOCKER_REASON: mcp_budget_exhausted_or_scope_too_large` o el diagnóstico MCP correspondiente; no quedar `partial` ni relanzarse en bucle.

Antes de spawnear `slice-verifier`, escribe skeleton persistente para evitar estados parciales por interrupción:

```bash
./scripts/init-verify-slice-handoff.sh <TASK_ID>
```

Ese skeleton debe quedar sobrescrito lógicamente por un bloque final append-only del subagente. Si el subagente se interrumpe y no hay bloque final ni trailer, vuelve a lanzar `slice-verifier` con prompt focalizado `write-first skeleton already exists; finish visual MCP verification or write blocked`.

## Paso 3.5 — Runtime reset/log helper

Antes de lanzar `slice-verifier`, prepara el contrato mecánico que debe usar:

```bash
./scripts/check-runtime-logs.sh --task <TASK_ID> --mode hard-reset
```

Este helper usa el profile de runtime y los comandos declarados por la app. En apps Docker, el proyecto de compose por defecto es el TASK_ID en minúsculas (`p01-s02-t003`), y además genera `orchestrator-state/dev-ports/<compose_project>.env` con puertos host libres. Así dos worktrees paralelos no comparten contenedores/volúmenes ni chocan por publicar el mismo puerto. Si el stack no usa Docker o no tiene compose file, el helper lo deja como `skipped` y `slice-verifier` debe usar `scripts/dev-restart.sh --reset`/comandos documentados. Si Rancher worker logs están marcados como requeridos y no hay comando, bloquea con `BLOCKER_REASON: rancher_worker_logs_not_configured`.

Durante y después de la reproducción humana, `slice-verifier` debe ejecutar:

```bash
./scripts/check-runtime-logs.sh --task <TASK_ID> --mode check --strict --json
```

Si el resultado JSON no tiene `runtime_logs_clean: true`, vuelve a debugger/retest si el error es corregible dentro del `TASK_ID`, o bloquea por entorno/comando faltante. No conviertas errores de logs en follow-up salvo que realmente falte cobertura fuera de scope en source-of-truth.

## Paso 4 — Spawn de `slice-verifier`

`slice-verifier` tiene un budget de tool-uses algo mayor (`maxTurns: 130`) porque la verificación humana MCP web/mobile consume más llamadas. No amplíes el budget de spawns ni lances varios verificadores para compensar MCP roto: el agente debe escribir primero el skeleton, hacer preflight corto del MCP aceptado para la superficie y sólo después probar fallbacks acotados.

Sólo si `verify-slice-state` devuelve `invoke_slice_verifier`, primero ejecuta `./scripts/init-verify-slice-handoff.sh <TASK_ID>` y luego spawnea **un único** subagente `slice-verifier` con este contexto literal:

```text
TASK_ID: <TASK_ID>
CLAUDE_TASK_PACK: orchestrator-state/tasks/task-packs/<TASK_ID>.md
MODO DAG ACTIVO: production = explicit_dag.
Unidad verificable = TASK_ID canónico del registry.
Hard reset obligatorio con datos reales/proporcionados del Verification Data Contract. Si hay Docker Compose, usa aislamiento por slice (`docker compose -p <compose_project>`) y puertos host asignados por slice (`CLAUDE_*_PORT`), preferiblemente vía `./scripts/check-runtime-logs.sh --task <TASK_ID> --mode hard-reset`; si hay Rancher/worker declarado, sus logs son parte del gate.
Primero confirma que un MCP aceptado está usable con una llamada mínima. Para web/browser, Orden obligatorio de preferencia: 1) Chrome DevTools MCP aislado, 2) Claude-in-Chrome MCP, 3) Agent360 Browser MCP (`browser-mcp`). Usa Chrome DevTools también para MFA/2FA/CAPTCHA/sesión real si puede abrir una sesión visible por `TASK_ID`; si no puede completar esa sesión humana, pasa a claude-in-chrome y después a Agent360. Si Chrome DevTools MCP falla por profile lock, ejecuta `bash scripts/chrome-mcp-doctor.sh || true`, imprime aislamiento con `bash scripts/chrome-devtools-isolated-session.sh --task <TASK_ID>` y prueba los fallbacks en ese orden sólo si están realmente conectados. Para Flutter mobile, usa Dart/Flutter MCP (`dart|flutter|flutter-driver`) con simulador/emulador/device; si no está usable, escribe ## verify-slice con `VERIFY_OUTCOME: blocked`, `BLOCKER_REASON: flutter_mobile_mcp_unavailable`, `MCP_DIAGNOSTIC` y `USER_ACTION_REQUIRED`.
Presupuesto: `slice-verifier` tiene `maxTurns: 130` para acomodar MCP visual web/mobile. Úsalo para hard reset + navegación real + logs/evidence, no para reintentos infinitos. Máximo 2 intentos cortos por MCP candidato; si el MCP sigue roto, el scope visual excede la slice o se agota el margen, escribe `VERIFY_OUTCOME: blocked` con `BLOCKER_REASON: mcp_budget_exhausted_or_scope_too_large` y acción requerida en vez de quedar partial.
Reproduce como usuario humano con el MCP visual aceptado: navegador MCP para web/browser o Dart/Flutter MCP para Flutter mobile; toca todos los botones/controles afectados por la slice, verifica enabled/disabled, loading, empty, validation, permission y error states, y confirma persistencia real por backend/DB/worker. Vigila logs browser/front/back/DB/worker/Docker/Rancher. Ejecuta `./scripts/check-runtime-logs.sh --task <TASK_ID> --mode check --strict --json` y, si la slice toca worker/cola/Rancher, exige logs del worker Rancher o bloquea con `BLOCKER_REASON: missing_rancher_worker_logs_contract`. Guarda evidencia verify-* + runtime-logs/runtime-log-check.json y devuelve una tabla: URL | Qué probar | Descripción | Resultado esperado | Resultado observado | Pasa?. Si el task pack declara Domain rule refs, verifica explícitamente esas reglas DR-* con datos reales/proporcionados y escribe DOMAIN_RULES_VERIFIED con la lista cubierta o una razón not_applicable por regla.
Escribe ## verify-slice final en el handoff.
No invoques closer; no hagas commit; no marques done.
```

Debe emitir:

```text
CLAUDE_TRAILER:
TASK_ID: <TASK_ID>
OUTCOME: verified|issues_found|blocked
NEXT_STATUS: verified_pending_close|needs_debug|blocked
HANDOFF: orchestrator-state/tasks/handoffs/<TASK_ID>.md
EVIDENCE: orchestrator-state/tasks/evidence/<TASK_ID>/
VERIFY_OUTCOME: verified|issues_found|blocked
```

Mapeo obligatorio:

- `verified` → `verified_pending_close`.
- `issues_found` → `needs_debug`.
- `blocked` → `blocked`.

Cuando vuelva, ejecuta otra vez `./scripts/verify-slice-state.sh <TASK_ID> --json`. Si devuelve `invoke_closer`, sigue al Paso 6 sin spawnear `closer`. Si devuelve `invoke_debugger_or_register_followup`, sigue al Paso 5. Si devuelve `blocked` con `VERIFY_OUTCOME: blocked` por MCP/entorno, PARA y muestra al usuario el `USER_ACTION_REQUIRED`; no spawnees closer ni debugger. Si el trailer se pierde, revisa el handoff: el agente debe haber escrito al menos el skeleton `## verify-slice` con `VERIFY_OUTCOME: pending`. Si hay sección final verified y el checker pasa, puedes continuar por el helper; si sólo hay skeleton pending o no hay evidencia, relanza `slice-verifier` una sola vez con prompt enfocado en `write-first skeleton already exists; finish visual MCP verification or write blocked`. Si vuelve a no escribir handoff, bloquea como fallo mecánico.

## Paso 5 — Si `slice-verifier` reporta issues

No preguntes al usuario para decidir el siguiente paso:

- Defecto dentro del `TASK_ID`/Write set → spawnea `debugger` con findings exactos, `TASK_ID`, `CLAUDE_TASK_PACK` y root split. Después lanza `validator` y `tester` en paralelo. Si pasan, relanza `/verify-slice <TASK_ID>` desde hard reset.
- Trabajo real fuera de scope pero aceptación actual verificada → registra FU formal `proposed` con `origin_task_id=<TASK_ID>`, `triage.scope_classification` y `triage.why_not_debugger`; después relanza `slice-verifier` o corrige el handoff para que `VERIFY_OUTCOME: verified` refleje que la aceptación actual sí pasa.
  Usa `/register-followup propose ... --scope-classification <out_of_scope|missing_coverage|...> --why-not-debugger <razón>`; sin esos campos no cierres la PR con deuda ambigua.
- Problema mecánico del orquestador/ambiente → corrige/reintenta o bloquea. No crees follow-up de producto.

Nunca uses el reset completo `debugger → validator+tester → verify-slice` cuando el diagnóstico dice “sólo falta closer” y validator/tester/verify ya están correctos. En ese caso ve al Paso 6.

## Paso 5.2 — Screen/Journey review condicional antes de /closer

HTML preview/docs visuales son referencia/evidencia, no source-of-truth.

Si la task toca UI, UX, journey, rutas, pantallas, VISUAL_CONTRACT_CHECK/visual contract, auth visible, navegación o `journey_refs`, spawnea **un único** `screen-journey-reviewer` después de `slice-verifier` y antes de dejar la slice lista para `/closer`.

Contexto obligatorio:

```text
TASK_ID: <TASK_ID>
CLAUDE_TASK_PACK: orchestrator-state/tasks/task-packs/<TASK_ID>.md
MODO DAG ACTIVO: production = explicit_dag.
Revisa UX_CONTRACT, Technical Guide, Checklist, handoff, verify-slice y evidencia.
Si el problema cabe en TASK_ID/Write set: OUTCOME=changes_requested; needs_debugger=yes; NO FU.
Si falta trabajo/datos/contrato fuera de scope: OUTCOME=blocked; followup_candidate=yes; why_not_debugger obligatorio.
```

Luego valida:

```bash
./scripts/check-handoff-contract.sh <TASK_ID> --require-ready-for-close --require-verify-slice --require-screen-journey-review --require-production-observability
```

Si `OUTCOME: changes_requested`, va a debugger/retest. Si `blocked` por FU real fuera de scope y la aceptación actual sigue verificada, registra FU `proposed` y continúa; si no puedes decidir, bloquea.

## Paso 5.bis — Journey-closing

Si esta slice cierra journeys, usa `python3 -B -S .claude/bin/list_journey_closures.py <TASK_ID> --json` antes de closer para que el cierre sepa qué journeys debe clasificar.

- Si el journey se verificó inline y el handoff contiene `## verify-journey` con `JOURNEY_VERIFY_OUTCOME: verified`, el closer debe emitir `JOURNEY_VERIFIED_INLINE: <JID>`.
- Si no puede verificarse inline automáticamente, el closer debe emitir `JOURNEY_PENDING_VERIFY: <JID>`.
- En DAG-only, pending journey bloquea sólo tasks que referencian ese journey, no todo el grafo.

## Paso 6 — Preparar cierre manual

Si el task pack declara `Domain rule refs`, comprueba antes del cierre que `## verify-slice` contiene `DOMAIN_RULES_VERIFIED` con las reglas `DR-*` aplicables, o una justificación explícita por regla no aplicable. Si faltan reglas de dominio, relanza `slice-verifier` con foco en esas reglas; no dejes la slice lista para `/closer` sólo con pruebas técnicas genéricas.

Cuando el handoff tiene validator approved + tester pass + `## verify-slice` con `VERIFY_OUTCOME: verified`, valida las precondiciones que usará `/closer`:

```bash
./scripts/check-handoff-contract.sh <TASK_ID> --require-ready-for-close --require-verify-slice --require-production-observability
```

Si pasa, **no spawnees `closer`**. Resume la verificación y pide al usuario que ejecute el comando manual:

```text
/closer <TASK_ID>
```

El usuario debe invocar `/closer <TASK_ID>` después de revisar tu resumen. Si el helper ya devolvía `invoke_closer` por una verificación previa, no repitas hard reset ni navegador; sólo confirma que el handoff sigue vigente y deja el cierre manual preparado. Si aparece un cambio de código posterior al bloque verify, el handoff checker debe bloquear por stale verify y debes relanzar `/verify-slice <TASK_ID>` antes de permitir `/closer`.

## Trailer final del comando

Como comando, resume lo ocurrido al usuario. Los trailers de estado los emiten los subagentes (`slice-verifier`, `screen-journey-reviewer`, `debugger`, `validator`, `tester`) y los consume el hook bajo lock. `closer` emitirá su trailer sólo cuando el usuario ejecute `/closer`.

Incluye en la respuesta final la tabla producida por `slice-verifier` o un resumen fiel de ella:

| URL | Qué probar | Descripción | Resultado esperado | Resultado observado | Pasa? |
|-----|------------|-------------|--------------------|---------------------|-------|

Y debajo:

- MCP usado: web (`MCP_BROWSER`) o Flutter mobile (`MCP_CLIENT`, `VISUAL_CHECK_METHOD`, `SIMULATOR_DEVICE`, `FLUTTER_MCP_HEALTH`) | blocked.
- Filas del Verification Data Contract usadas.
- Datos reales/proporcionados cargados.
- Datos persistidos observados.
- Logs front/back/DB revisados.
- Reglas de dominio `DR-*` verificadas (`DOMAIN_RULES_VERIFIED`) si el task pack declara `Domain rule refs`.
- `REAL_USER_VERIFIED: yes`, `NO_STUB_DATA: yes`, `NO_STUB_DATA_USED: yes`, `HUMAN_REPRODUCTION: yes`, `RUNTIME_LOGS_CHECKED: yes`, `ERROR_LOGS_STATUS: clean`, `RUNTIME_LOG_ERRORS: 0`, `DOCKER_COMPOSE_PROJECT: <project>`, `DOCKER_PORTS_ALLOCATED: yes|not_applicable:<reason>` y `RANCHER_WORKER_LOGS_REVIEWED`/`RANCHER_WORKER_LOGS_CHECKED` limpio o `not_applicable:<reason>`.
- Si hubo PDF/documento/LLM input: `LLM_INPUT_ARTIFACTS`, `DATA_SOURCE_FILES` y `LLM_DOCUMENT_EXTRACTION` con ruta/hash, pipeline ejecutado y resultado persistido/observado.

Luego añade:

```text
TASK_ID: <TASK_ID>
VERIFY_ACTION: <acción del router>
CLOSER_ACTION: user_required|not_ready|already_done
FOLLOWUPS_PROPOSED: <FU IDs o none>
NEXT_ACTION: /closer <TASK_ID> | debugger/retest | fix mechanical blocker | /next-slice
```


### Flutter mobile verify-slice

Si `STACK_PROFILE.yaml` declara `frontend.framework: flutter` y `frontend.visual_check: simulator|emulator|device`, `/verify-slice` debe usar siempre el Dart/Flutter MCP real: `MCP_CLIENT: dart` (o `flutter`/`flutter-driver`) y `VISUAL_CHECK_METHOD: simulator|emulator|device`. Para Flutter web sigue siendo válido `MCP_BROWSER: chrome-devtools|claude-in-chrome|agent360-browser-mcp|browser-mcp`. No cierres una slice mobile con una verificación sólo web. Configuración MCP recomendada: `claude mcp add --transport stdio dart -- dart mcp-server`.
