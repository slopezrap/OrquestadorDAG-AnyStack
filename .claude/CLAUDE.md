# Five-file source-of-truth execution index — AnyStack Production DAG Edition

## CRITICAL — This is a REAL PRODUCTION product

- Not a prototype, not a mockup, not a demo.
- All code is PRODUCTION-QUALITY from day 1: real validations, real error handling, real security.
- All data flows are REAL: real API calls, real DB queries, real auth.
- All tests verify REAL behavior. No fake data, no hardcoded responses, no "TODO: implement later".
- E2E tests hit real backend + real DB. If a test passes without real services, it is not valid.

## Source of truth

The project is governed by the canonical source-of-truth set in `docs/source-of-truth/`:

1. `instrucciones.md` — goals, scope, business rules and Journey Coverage Matrix.
2. `*_IMPLEMENTATION_CHECKLIST.md` — phases, steps, Coverage Registry and DAG fields.
3. `*_TECHNICAL_GUIDE.md` — architecture, contracts, endpoints, DB and verification data contract.
4. `STACK_PROFILE.yaml` — stack-specific paths, commands, visual-token enforcer and Git workflow.
5. `UX_CONTRACT.md` — personas, screen inventory, UI states and UX verification rules.

If any source-of-truth file is missing, duplicated, stale or contradictory — stop and repair the contract first.

## Main-thread orchestrator invariant

This project is controlled by `main-orchestrator` as the Claude Code main session agent. `.claude/settings.json` sets `agent: main-orchestrator`, and explicit worker commands must use `claude --agent main-orchestrator --permission-mode bypassPermissions`. Do not run plain `claude` and then invoke `main-orchestrator` as a child subagent; child subagents cannot orchestrate other subagents.

Do not add `tools:` or `disallowedTools:` to `.claude/agents/main-orchestrator.md`. Omitting `tools` is intentional: the main orchestrator inherits all available tools from the main session, including MCP tools and `Agent`. Any `tools:` list becomes an allowlist and can silently remove new tools/MCPs needed by the DAG controller.

## Phases are variable by source-of-truth (source-of-truth dependent, MiniNotes/minimal examples=3)

0. **Scaffold + Design System** — backend + DB + frontend running, design tokens ready, showcase page.
1. **Auth + Data Foundation** — login/register on real backend + DB, protected routes, real/provided verification data setup.
2. **Core Features (the motor)** — each feature = complete screen (backend + frontend + tests + visual check).
3. **Complete Features** — secondary features, settings, admin, edge cases.
4. **Harden** — security, error handling, responsive, accessibility, Docker, performance.
5. **Release** — production build, deploy docs, rollback.

Every phase produces a VISIBLE, FUNCTIONAL, VERIFIABLE deliverable. Never build in the dark.

## Per-slice chain — max 20 spawns, parallelism first

```text
── /next-slice pipeline (implementación + verify automático; NO cierre) ──
1. planner                               (planning, context curation and technical analysis)
2. developer (+ official-docs-researcher only when needed)
                                          official-docs-researcher runs only for new/uncertain
                                          external APIs, libraries, security, AI/RAG/MCP, streaming,
                                          DB/deploy behavior or planner `NEEDS_OFFICIAL_DOCS: yes`.
                                          When invoked, ask 1–5 concrete questions and use
                                          Context7/MCP/cache before official WebFetch/WebSearch.
3. validator ‖ tester                    [PARALLEL — one message, two Agent calls]
4. debugger                              [if tester fails OR validator requests changes → back to step 3]
   ── if validator/tester are green, continue automatically into verify ──
5. verify-slice contract                 hard reset + real/provided data + human-real web/mobile MCP reproduction
   ├─ slice-verifier                     writes ## verify-slice + evidence + trailer
   ├─ if task frontend/ux/journey/gate or VISUAL_CONTRACT_CHECK:
   │   screen-journey-reviewer info-only before manual /closer
   │   ├─ approved → continue
   │   ├─ changes_requested → debugger/retest, NO FU
   │   └─ blocked → FU triaged only if missing work/data/contract is out of scope
   ├─ VERIFY_OUTCOME: verified + MCP/data/evidence complete
   │   ├─ task.status = verified_pending_close
   │   └─ §5.bis if the slice closes journey(s) → ask the user:
   │       ├─ "ahora"  → verify-journey INLINE with the already loaded environment
   │       │            append ## verify-journey to the same handoff
   │       └─ "aparte" → /closer later emits JOURNEY_PENDING_VERIFY and frontier defers only that journey
   └─ VERIFY_OUTCOME: issues_found → debugger → back to validator/tester/verify

── user-controlled close ──
6. /closer <TASK_ID>                     evidence/report + baseline sync + commit + configured Git workflow
                                          pre-check rejects without verified ## verify-slice
                                          for screen/journey requires approved Screen/Journey review
                                          if ## verify-journey verified exists, closer emits
                                          JOURNEY_VERIFIED_INLINE instead of JOURNEY_PENDING_VERIFY
   └─ post-push: cleanup-slice-runtime + slice-clean + cleanup-worktrees + deferred cleanup if the active worktree is still in use
```

`closer` NUNCA commitea código sin un bloque `## verify-slice` completo con `VERIFY_OUTCOME: verified`, modalidad MCP válida (`MCP_BROWSER` para web/browser o `MCP_CLIENT` + `VISUAL_CHECK_METHOD` para Flutter mobile), datos/evidencia y flujos probados (procedente del subagente `slice-verifier` dentro de `/next-slice` auto-verify o `/verify-slice` recovery; `/auto-verify-slice` sólo aplica a slices `low+auto` no journey) o sin waiver explícito `VERIFY_WAIVED: <motivo>` firmado por el usuario. Esto garantiza que no hay commits de código sin verificación real y trazable. El estado intermedio correcto es `verified_pending_close`; sólo `closer` puede mover a `done`, y sólo lo invoca el comando manual `/closer`.

`/verify-journey <JID>` sigue existiendo como **command de rescate manual** — para waivers, re-verificaciones aisladas, debug post-mortem, o casos donde el usuario eligió "aparte" en §5.bis. En el flujo normal, el journey se verifica inline en el tramo verify y este command queda dormido.

**Resiliente a `/clear`**: `/verify-slice` y `/closer` reconstruyen TODO desde disco (PROGRESS.md, runtime-state, registry, handoff, TECHNICAL_GUIDE). El flujo normal intenta verificar automáticamente dentro de `/next-slice`; si el contexto se queda corto o interrumpes con `/clear`, relanza `/verify-slice <TASK_ID>` y después `/closer <TASK_ID>`.

## DAG wave mode — production explicit DAG

Production mode is `explicit_dag`. The bootstrap materializes DAG mode when the Coverage Registry in `*_IMPLEMENTATION_CHECKLIST.md` contains a dependency column named `Depends on`, `Dependencies`, `Deps`, `After`, `Blocked by` or `Dependencias`. In that case, each row is a node and the dependency cell is the source-of-truth adjacency list. If the dependency column is missing, do not open workers; repair the Coverage Registry and refresh. Blank / `—` means a root node. Accepted refs: full `TASK_ID`, ranges (`P03-S02-T001..T004`), step refs (`P03-S02`), phase refs (`P03`), or `previous`.

Derived graph artifacts:

```text
orchestrator-state/memory/task-dag.json   adjacency_index + adjacency_matrix + levels
orchestrator-state/memory/task-dag.md     human-readable waves
orchestrator-state/tasks/registry.json    task_dag copy used by planner/checks
```

The matrix is derived, not authored. To change ordering or parallelism, edit only the Coverage Registry `Depends on`, `Conflict group` and `Write set` cells and rerun `bootstrap_source_of_truth.py --refresh` + `scripts/check-task-dag.sh --strict`. `Depends on` controls DAG readiness; `Conflict group`/`Write set` control safe same-wave scheduling.

For large products, the Coverage Registry is cumulative: `Product increment` labels `v0`, `v1`, `v2`, ... and `Build state` keeps already-built rows at `done` while new rows remain `planned`. This preserves full product context without rebuilding closed increments.

Parallel execution uses separate terminals, not extra agent types. Run `/next-wave` to list ready independent tasks, then start one terminal per selected task with both `CLAUDE_ACTIVE_TASK_ID=<TASK_ID>` and `CLAUDE_TASK_PACK=orchestrator-state/tasks/task-packs/<TASK_ID>.md`, then run `/next-slice <TASK_ID>` from the printed command. For pr-flow, the command first creates/enters the per-TASK_ID worktree so all subagents see the same branch. The task environment is critical: hooks use `CLAUDE_ACTIVE_TASK_ID` for spawn budget, ledger, session context and SubagentStop accounting; agents use the per-task pack so memory remains scoped to the correct slice. `CLAUDE_ACTIVE_TASK_ID` + `CLAUDE_TASK_PACK` are the only DAG task authority.

All existing gates still apply in each node: planner writes/enriches `orchestrator-state/tasks/task-packs/<TASK_ID>.md`, developer + official-docs-researcher run with that pack, validator + tester read that same pack, debugger loops on the same `TASK_ID`, then verify-slice contract, manual `/closer`, journey verification. A task is promotable only when every `depends_on` predecessor is `done`; a task is claimable only when no DAG task conflicts via `Conflict group`/`Write set`; the planner still respects phase order, phase gates and pending journey blocks.

## Canonical root vs task worktree

In `pr-flow` and `git-flow`, every slice runs in its own task worktree, but shared DAG truth remains in the canonical repo root. Use this split consistently:

- Shared scheduler/state truth: `$CLAUDE_ORCHESTRATOR_ROOT/orchestrator-state/tasks/registry.json`, `runtime-state.json`, `memory/PROGRESS.md`, `memory/task-dag.*`, `memory/execution-graph.json`. Do not infer operational truth from `./orchestrator-state` inside a task worktree; it can be partial or stale.
- Slice artifacts to commit: `./orchestrator-state/tasks/handoffs/<TASK_ID>.md`, `evidence/<TASK_ID>/`, `reports/<TASK_ID>.md`, `task-packs/<TASK_ID>.md`. These live in the active worktree for PR/Gitflow and are staged by `./scripts/git-add-slice.sh <TASK_ID>`.
- False follow-ups are worse than a blocked close. Do not create or promote follow-ups for mechanical noise: stale root reads, handoff heading variants, checker mismatch, CI/tooling flake, or missed cleanup. Fix/retry/block; follow-ups are only for real product work outside the current slice scope.

## Central runtime contract

`.claude/orchestrator-contract.json` is the compact machine-readable index for what each agent may write, which files are generated core state, what trailer fields are required, and which UX fields must reach every UI task pack. Human guidance lives in `.claude/rules/05-runtime-write-contract.md`, but it is not a runtime policy source. Hooks enforce code + `orchestrator-contract.json`; they do not parse `.claude/rules/*.md` as runtime policy. If you edit rules/agents/contract during a live Claude session, restart or `/clear` before relying on the new instructions so agents and hooks do not reason from different context snapshots.

Use this to keep prompts shorter: agents do not need to rediscover write policy. They load the contract, then write only their own slice artifacts. In DAG mode every artifact containing a `TASK_ID` must match `CLAUDE_ACTIVE_TASK_ID`; hooks enforce that mechanically.

`docs/product-baseline/` is the built baseline snapshot for the next ChatGPT planning pass. Closer runs `./scripts/sync-product-baseline.sh sync --version <increment> --task <TASK_ID>` after verified `/verify-slice` handoff and before commit so existing baseline + v1 + v2 context is never lost.

## Agents

Total: 14 agents. Per slice max 20 spawns (steps above). Bootstrap-only: `document-analyzer`, `project-architect`, `task-planner`. Phase 5 only: `deployer`. Verify-slice agents: `slice-verifier` (lifecycle, `maxTurns: 130` because web/mobile MCP verification can be tool-use heavy) and `screen-journey-reviewer` (info-only).

Manual-memory agents: `planner`, `developer`, `validator`, `debugger`, `slice-verifier`, `official-docs-researcher`, `project-architect`, `screen-journey-reviewer`, plus `task-planner` for bootstrap learnings. Memory is stored in `orchestrator-state/agent-memory/<agent>/MEMORY.md`; `.claude/` stays static.

Task worktree isolation is session-level, not subagent-level: `/next-wave` moves pr-flow worker terminals into a per-TASK_ID worktree before `claude --agent main-orchestrator` starts. Do not add `isolation: worktree` to lifecycle subagents; validator/tester/debugger/closer must inspect the same checkout.

## Rules

Note: the repeated "Startup obligatorio del agente" block in agent prompts is intentional. Claude Code does not currently provide a shared include primitive for subagent prompts, so each agent repeats the same startup contract to avoid runtime drift.


All project-wide non-negotiables live in `.claude/rules/`:

- `00-source-of-truth.md` — the source-of-truth contract.
- `01-non-negotiables.md` — production quality, tests real, logging, security, a11y, DRY/KISS/YAGNI, docs, file size, deps, DB, API contract.
- `02-phase-execution.md` — variable source-of-truth phases and the per-slice pipeline.
- `03-dev-loop.md` — dev servers, per-slice verification.
- `04-traceability.md` — handoffs, registry, close conditions, hooks.
- `05-runtime-write-contract.md` — centralized runtime write contract, DAG task scope, protected generated state, UX task-pack requirements.

Claude Code loads unscoped `.claude/rules/*.md` at session start. Subagents have isolated prompts, so every agent prompt also contains an explicit startup step to read the six rule files and `.claude/orchestrator-contract.json` directly before acting. If a rule appears to be ignored, read the rule file path explicitly and continue from disk, not from memory.

## Hooks

Six hook event groups are wired in `settings.json`, backed by eight scripts. They are intentionally small and capped with conservative timeouts:

- `PreToolUse` on `Agent` → `hook_spawn_budget.py`. Enforces the mechanical max-20-spawns-per-slice budget. On the 21st Agent call it returns `permissionDecision: deny`, so the invariant is code-enforced instead of cultural.
- `PreToolUse` on `Write|Edit|MultiEdit|NotebookEdit` → `hook_write_scope_guard.py` first, then `hook_docs_discrepancy_check.py`. The write-scope guard blocks DAG-corrupting writes: static `.claude/` edits during app execution, cross-task handoff/evidence/report/task-pack writes, source-of-truth edits while a TASK_ID is active, and direct edits to generated core state. The docs-discrepancy hook then warns about unresolved official-doc notes. If `orchestrator-state/memory/official-doc-notes/` has unresolved notes, it injects a visible warning so Claude reconciles before continuing. It is non-blocking by design; MCP/browser tools are excluded by the matcher.
- `PostToolUse` on `Write|Edit|MultiEdit|Bash|NotebookEdit` → `hook_update_ledger.py`. Logs Write/Edit/MultiEdit/NotebookEdit events to local `orchestrator-state/tasks/ledger.jsonl` and Bash events to local `orchestrator-state/tasks/bash-ledger.jsonl`; in DAG worker terminals records are scoped to `CLAUDE_ACTIVE_TASK_ID`. Both ledgers are runtime-only/ignored by Git so Bash hooks cannot dirty the repository after the closer's atomic commit/push.
- `SubagentStart` → `hook_subagent_start_context.py`. Emits task-scoped `additionalContext` before each subagent starts: active `TASK_ID`, task pack, declared scope, write set, conflict groups, logic refs, verify mode and trailer/write-contract reminders. It injects context only; it does not mutate lifecycle state.
- `SubagentStop` → `hook_capture_subagent_stop.py`. Parses the final `CLAUDE_TRAILER:` block (`TASK_ID` / `OUTCOME` / `NEXT_STATUS` / `HANDOFF` / `EVIDENCE` / `REPORT`), increments spawn counters, and syncs `registry.json` + `runtime-state.json` under ordered locks. If the trailer is missing or partial, it writes a visible error; it does not silently drop state. In DAG worker terminals, a trailer with a different `TASK_ID` is logged as a scope mismatch and cannot mutate another node.
- `SessionStart` → `hook_session_context.py`. Emits `additionalContext` with the project state, unresolved docs discrepancies, spawn counts, and recent hook errors.
- `Stop` → `hook_finalize_deferred_cleanup.py`. Flushes deferred, inactive worktree cleanups after the active Claude session has safely stopped. It does not remove the current working directory while Claude is still running.

Root resolution is split deliberately: orchestrator state writes resolve to the canonical main repo, while product verification commands resolve to the current task worktree via `CLAUDE_WORKTREE_ROOT`/cwd. Hook failures write a timestamped entry to `orchestrator-state/hook-errors.log`; the SessionStart hook surfaces recent entries at restart so corruption is visible instead of silent. Do not delete the active task worktree before SubagentStop runs; cleanup must report `active_deferred=1` rather than removing Claude's current cwd.

## Mutable state policy

`.claude/` is static Claude Code configuration: agents, skills, commands, rules, hooks and settings. Runtime writes go outside it:

- `orchestrator-state/memory/` — PROGRESS, architecture contract, decisions, risks, official-doc notes. DAG-only mode uses TASK_ID + task-pack, not task/implicit selector files.
- `orchestrator-state/tasks/` — registry, runtime-state, work-items, per-task packs, handoffs, evidence, reports, local ledger.
- `orchestrator-state/agent-memory/` — manual Reflexion-style memory per agent.
- `orchestrator-state/hook-errors.log` — visible hook failures.

Do not create hidden runtime folders such as `.orchestrator/`. The only hidden configuration directory in this project is `.claude/`.

## Commands

- `/next-wave` — lista la wave DAG actual y los TASK_ID ready paralelizables sin conflictos declarados; no implementa ni spawnea. Imprime exports copy/paste para `CLAUDE_ACTIVE_TASK_ID` + `CLAUDE_TASK_PACK`, `COMPOSE_PROJECT_NAME` por slice y `CLAUDE_*_PORT` libres cuando hay runtime local.
- `/next-slice` — arranca la siguiente slice con gate de aprobación, pipeline completo y verificación automática post-slice. NO invoca `closer`; si todo está verified deja `verified_pending_close` y muestra `/closer <TASK_ID>` como siguiente acción.
- `/verify-slice` — recovery/verificación humana-real con hard reset + datos reales/proporcionados + logs vivos. Spawnea `slice-verifier`; si deja `verified_pending_close`, NO invoca closer y muestra `/closer <TASK_ID>`. Si encuentra issues, orquesta `debugger/retest`. Resiliente al `/clear`.
- `/closer <TASK_ID>` — cierre manual tras verify: report, baseline sync, commit, workflow Git configurado y cleanup. Es el único comando que invoca el subagente `closer`.
- `/revise-slice <TASK_ID> "motivo"` — reabre una slice canónica sin cambiar el DAG ni crear IDs temporales; corrige, revalida, deja verified_pending_close y requiere `/closer` correctivo.
- `/phase-gate <PHASE_ID>` — valida que la phase está realmente cerrada antes de abrir la siguiente: tasks done, reports/evidence/handoffs, journeys verified/waived y Git limpio opcional.
- `/register-followup propose|waive|list` — registra/waivea hallazgos reales de validator/tester/verify como propuestas YAML.
- `/promote-followup <FU_ID>` — promoción segura vía main-orchestrator: convierte una FU aprobada en task DAG persistente en source-of-truth + registry + work-items.
- `./scripts/sync-product-baseline.sh status|sync` — mantiene `docs/product-baseline/` como snapshot construido acumulativo para el siguiente incremento. `sync` requiere handoff verificado salvo migración manual explícita con `--allow-unverified`.
- `/verify-journey <JID>` — gate humano end-to-end **a nivel journey** (multi-pantalla, no por slice). Se lanza tras el `closer` de la ÚLTIMA slice de un journey declarado en la Journey Coverage Matrix de `instrucciones.md` (sección Journey Coverage Matrix; el bootstrap la localiza por nombre, no por número). `pending_journey_verifications[]` difiere solo las tasks que referencian esos journeys. No existe modo alternativo de journey gate en DAG-only. Hard reset + datos reales/proporcionados consolidados + reproducción del flujo entero + estados marginales (empty/error/permission/back/deep_link) + next action. Resiliente al `/clear`.
- `/slice-maintain clean|compact|compact-agent-memory` — mantenimiento entre slices, compactación de PROGRESS.md y compactación lossless de memorias de agentes. `./scripts/next-wave.sh` auto-compacta memorias de agentes >250 líneas antes de calcular la wave.

Recommended order when closing a slice: `/next-slice <TASK_ID>` implements and verifies automatically → user reviews summary → `/closer <TASK_ID>` → `/slice-maintain clean` → `/clear` → `/next-slice`. If interrupted, use `/verify-slice <TASK_ID>` before `/closer`.

## Follow-ups formales

Si aparece trabajo real fuera del TASK_ID actual, no se deja en el handoff como nota suelta. Validator/tester/debugger/verify crean propuesta con `register-followup-task.sh propose`; el closer incluye esas propuestas en el report/commit/PR y no pregunta al usuario para cerrar. El main-orchestrator promueve o waivea después con decisión humana. Las propuestas `high|critical|blocker` bloquean nuevas waves y claims hasta resolverse, no el PR de la slice que las originó.

## PROGRESS.md

- `orchestrator-state/memory/PROGRESS.md` is the live project snapshot.
- `developer` updates it after EVERY slice.
- After `/clear`: read PROGRESS.md FIRST before any other action.
- All subagents' first read on start.
- PROGRESS.md is a DERIVED artifact — the five source-of-truth docs remain the authority when present; the five source-of-truth docs are mandatory for production.

## Entry points

- Start: `claude --agent main-orchestrator --permission-mode bypassPermissions`.
- Bootstrap: run `python3 -B -S .claude/bin/bootstrap_source_of_truth.py --validate-only` and then `python3 -B -S .claude/bin/bootstrap_source_of_truth.py --refresh`.
- Slice: `/next-slice`.
- Verify: `/verify-slice`.
- Maintain: `/slice-maintain clean` or `/slice-maintain compact`.

## Operating priorities

1. Validate the source-of-truth contract.
2. Backend lint + frontend lint must pass at all times.
3. Consult official frontend AND backend framework docs before implementation.
4. Execute only dependency-ready tasks.
5. After each slice: verify backend health + verify in browser + run ALL tests.
6. Require handoff, validator approval, tester pass, full `VERIFY_OUTCOME: verified` from `slice-verifier` (`verified_pending_close`), closer baseline sync + commit + push before `done`, and (when the slice closes a journey) `JOURNEY_VERIFY_OUTCOME: verified` from inline `/verify-slice` or `/verify-journey` before dependent journey tasks continue.
7. Keep context small. Daily read = `PROGRESS.md` + per-task pack (`orchestrator-state/tasks/task-packs/<TASK_ID>.md`). Use only the per-task pack for the current `TASK_ID`. Agent `MEMORY.md` files above 250 lines are compacted automatically by `./scripts/next-wave.sh`; do not ask a subagent to compact its own memory.

## Compact instructions

During compaction preserve:

- current phase and task IDs + task status,
- source document paths,
- `orchestrator-state/memory/PROGRESS.md` path (read FIRST after compaction),
- frontend dev server status + URL,
- backend server status (running, port, health),
- database status (migrations applied, real/provided verification data loaded when required),
- unresolved discrepancies with official docs,
- active risks, blockers, last test results.

**`/slice-maintain compact` (compactación operativa de PROGRESS.md)** se ejecuta solo bajo gate humano y con verificación post-compact obligatoria: snapshot previo, promoción append-only de decisions+risks a sus ficheros canónicos, preservación de TODOS los commit SHAs, UUIDs seed, must-carry bullets, last N slices verbatim. Si la verificación post-compact detecta que algún elemento crítico falta en el resultado, restaura desde snapshot y aborta. **Nunca pierde información crítica.**


## Deferred worktree cleanup

`cleanup-worktrees.sh` never removes the active Claude task worktree before `SubagentStop`. It records active deferrals in `orchestrator-state/tasks/cleanup-requests/<TASK_ID>.json`; `hook_finalize_deferred_cleanup.py`, `scripts/next-wave.sh`, and the next `ensure-task-worktree.sh` flush safe, inactive deferrals automatically.


## Claude Code model/session guidance

Use only Claude Code documented model aliases or full model IDs; do not invent model names. `model: opus[1m]`/`model: sonnet[1m]` are documented Claude Code aliases for 1M context when the account/provider supports them. Do not set `effort: ultracode` inside subagents: Claude Code treats ultracode as a session-only setting. For especially hard orchestrator work, the user may run `/effort ultracode` in the main session before starting `/next-slice`; subagents keep their declared model/effort unless Claude Code session policy overrides them.

## Framework self-checks

Before packaging or after editing the orchestrator itself, run the global doctor and the golden app smoke:

```bash
./scripts/orchestrator-doctor.sh --json
./scripts/orchestrator-doctor.sh --run-static --json
./scripts/run-golden-e2e.sh --json
```

The golden app is intentionally small but real: it starts an HTTP server, writes to SQLite, uses a provided fixture, checks visible controls, verifies DR-* domain rules, and scans runtime logs. It exists to catch regressions that unit tests and Markdown reviews can miss.

Do not replace this with stub data, mocked persistence, fake browser evidence, or invented LLM/PDF outputs. If the product is deployed with Docker/Rancher/worker processes, `/verify-slice` must capture and check those logs before a slice can be considered verified.
