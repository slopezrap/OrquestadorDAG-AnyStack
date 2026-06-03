# Orchestrator state

This directory is intentionally outside `.claude/`.

Claude Code protects writes to `.claude/` even in autonomous modes, so this engine keeps `.claude/` static and writes all runtime state here:

- `memory/` — PROGRESS, decisions, risks, official-doc notes and derived graph views.
- `tasks/` — registry, runtime-state, work-items, task-packs, follow-up proposals, source-doc patches, handoffs, evidence, reports, ledger.
- `agent-memory/` — manual per-agent memory that survives `/clear` and app resets. `./scripts/next-wave.sh` auto-compacts `MEMORY.md` files above 250 lines, archiving originals under each agent `archive/` directory.
- `dev-logs/` — backend/frontend logs produced by `scripts/dev-restart.sh`.
- `hook-errors.log` — visible hook failures surfaced by SessionStart.

This directory is gitignored except for this README. Do not delete it during an app build. Use `./scripts/reset-for-new-project.sh` only when switching to a new app after replacing the source-of-truth pack.


## Deferred worktree cleanup

`cleanup-worktrees.sh` never removes the active Claude task worktree before `SubagentStop`. It records active deferrals in `orchestrator-state/tasks/cleanup-requests/<TASK_ID>.json`; `hook_finalize_deferred_cleanup.py`, `scripts/next-wave.sh`, and the next `ensure-task-worktree.sh` flush safe, inactive deferrals automatically.
