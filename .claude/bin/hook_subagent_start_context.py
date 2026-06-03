#!/usr/bin/env python3
"""SubagentStart hook - inject scoped DAG context into every subagent.

This hook is intentionally read-only. It cannot block subagent creation under
Claude Code's hook contract, so it front-loads the exact TASK_ID, task pack,
write contract, trailer schema and root-split reminders before the subagent's
first prompt.

Output format follows the official Claude Code hooks spec:

    {
      "hookSpecificOutput": {
        "hookEventName": "SubagentStart",
        "additionalContext": "<markdown>"
      }
    }
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    from common import (
        dag_worker_task_id,
        find_task,
        get_spawn_budget,
        get_spawn_count,
        handoff_path,
        load_registry,
        load_runtime_state,
        log_hook_error,
        project_root,
        task_pack_path,
        workspace_relpath,
    )
except Exception:  # pragma: no cover - defensive fallback for broken imports
    def dag_worker_task_id() -> str | None:  # type: ignore[no-redef]
        raw = (os.environ.get("CLAUDE_ACTIVE_TASK_ID") or os.environ.get("CLAUDE_TASK_ID") or "").strip()
        return raw or None

    def load_registry() -> dict[str, Any]:  # type: ignore[no-redef]
        return {}

    def load_runtime_state() -> dict[str, Any]:  # type: ignore[no-redef]
        return {}

    def find_task(registry: dict[str, Any], task_id: str | None) -> dict[str, Any] | None:  # type: ignore[no-redef]
        for item in registry.get("tasks", []) or []:
            if isinstance(item, dict) and item.get("id") == task_id:
                return item
        return None

    def get_spawn_budget() -> int:  # type: ignore[no-redef]
        return 20

    def get_spawn_count(task_id: str | None) -> int:  # type: ignore[no-redef]
        return 0

    def project_root() -> Path:  # type: ignore[no-redef]
        return Path.cwd()

    def task_pack_path(task_id: str | None) -> Path:  # type: ignore[no-redef]
        return Path("orchestrator-state/tasks/task-packs") / f"{task_id or 'unknown'}.md"

    def handoff_path(task_id: str | None) -> Path:  # type: ignore[no-redef]
        return Path("orchestrator-state/tasks/handoffs") / f"{task_id or 'unknown'}.md"

    def workspace_relpath(path: Path) -> str:  # type: ignore[no-redef]
        return path.as_posix()

    def log_hook_error(name: str, exc: BaseException) -> None:  # type: ignore[no-redef]
        return None

MAX_CHARS = 9000
NONE_VALUES = {"", "none", "null", "n/a", "na", "-", "--", "---", "_", "—"}


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, tuple):
        return [str(x).strip() for x in value if str(x).strip()]
    text = str(value).strip()
    if not text or text.lower() in NONE_VALUES:
        return []
    parts: list[str] = []
    for chunk in text.replace("\n", ",").replace(";", ",").split(","):
        item = chunk.strip()
        if item and item.lower() not in NONE_VALUES:
            parts.append(item)
    return parts or [text]


def _first_non_empty(mapping: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def _nested_first_non_empty(payload: dict[str, Any], keys: list[str]) -> Any:
    value = _first_non_empty(payload, keys)
    if value not in (None, "", [], {}):
        return value
    for container_key in ("parameters", "input", "metadata", "context"):
        nested = payload.get(container_key)
        if isinstance(nested, dict):
            value = _first_non_empty(nested, keys)
            if value not in (None, "", [], {}):
                return value
    return None


def _clip_items(items: list[str], *, limit: int = 12) -> str:
    if not items:
        return "not_declared"
    shown = items[:limit]
    suffix = "" if len(items) <= limit else f" (+{len(items) - limit} more)"
    return ", ".join(f"`{item}`" for item in shown) + suffix


def _safe_rel(path: Path) -> str:
    try:
        return workspace_relpath(path)
    except Exception:
        return path.as_posix()


def _load_contract() -> dict[str, Any]:
    try:
        path = project_root() / ".claude" / "orchestrator-contract.json"
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        try:
            log_hook_error("hook_subagent_start_context.contract", exc)
        except Exception:
            pass
        return {}


def _role_schema(contract: dict[str, Any], agent_type: str) -> dict[str, Any]:
    roles = ((contract.get("trailer_schema") or {}).get("roles") or {})
    spec = roles.get(agent_type)
    return spec if isinstance(spec, dict) else {}


def _write_contract(contract: dict[str, Any], agent_type: str) -> dict[str, Any]:
    writers = contract.get("agent_write_contract") or {}
    spec = writers.get(agent_type)
    return spec if isinstance(spec, dict) else {}


def _task_value(task: dict[str, Any], keys: list[str]) -> list[str]:
    return _as_list(_first_non_empty(task, keys))


def build_context(payload: dict[str, Any]) -> str:
    agent_type = str(_nested_first_non_empty(payload, ["agent_type", "subagent_type", "agent_name", "name", "agent"]) or "unknown").strip() or "unknown"
    agent_id = str(_nested_first_non_empty(payload, ["agent_id", "subagent_id", "id"]) or "unknown").strip() or "unknown"
    cwd = str(payload.get("cwd") or os.environ.get("PWD") or "").strip() or "unknown"
    task_id = (
        dag_worker_task_id()
        or str(_nested_first_non_empty(payload, ["task_id", "TASK_ID", "claude_active_task_id"]) or "").strip()
        or None
    )
    registry = load_registry() or {}
    runtime = load_runtime_state() or {}
    task = find_task(registry, task_id) if task_id else None
    contract = _load_contract()
    role = _role_schema(contract, agent_type)
    writer = _write_contract(contract, agent_type)

    explicit_dag = ((registry.get("task_dag") or {}).get("mode") or "explicit_dag")
    env_pack = (os.environ.get("CLAUDE_TASK_PACK") or "").strip()
    pack = task_pack_path(task_id) if task_id else None
    pack_display = env_pack or (_safe_rel(pack) if pack else "not_applicable")
    handoff_display = _safe_rel(handoff_path(task_id)) if task_id else "not_applicable"

    try:
        spawn_count = get_spawn_count(task_id)
    except Exception:
        spawn_count = 0
    try:
        spawn_budget = get_spawn_budget()
    except Exception:
        spawn_budget = 20

    lines: list[str] = [
        "## Subagent runtime context (auto-injected at subagent start)",
        f"- Agent type: `{agent_type}`",
        f"- Agent id: `{agent_id}`",
        f"- CWD: `{cwd}`",
        f"- DAG mode: `{explicit_dag}`; execution unit is the explicit `TASK_ID`.",
        f"- Active TASK_ID: `{task_id or 'not_set'}`",
        f"- Task pack: `{pack_display}`",
        f"- Handoff: `{handoff_display}`",
        f"- Spawns for active slice: {spawn_count}/{spawn_budget}",
        "- Root split: shared registry/runtime/memory live in the canonical repo; per-slice handoff/evidence/report/task-pack live in the active worktree checkout.",
    ]

    if task:
        title = str(task.get("title") or task.get("name") or "untitled")
        phase_id = str(task.get("phase_id") or "not_declared")
        step_id = str(task.get("step_id") or "not_declared")
        status = str(task.get("status") or "not_declared")
        lines.extend([
            "",
            "### Active task scope",
            f"- Title: {title}",
            f"- Phase/step/status: `{phase_id}` / `{step_id}` / `{status}`",
            f"- Depends on: {_clip_items(_task_value(task, ['depends_on', 'dependencies']))}",
            f"- Conflict groups: {_clip_items(_task_value(task, ['conflict_groups', 'conflict_group']))}",
            f"- Write set: {_clip_items(_task_value(task, ['write_set', 'write_paths']))}",
            f"- Allowed paths: {_clip_items(_task_value(task, ['allowed_paths', 'allowed_path']))}",
            f"- Journey refs: {_clip_items(_task_value(task, ['journey_refs', 'journeys']))}",
            f"- Domain rule refs: {_clip_items(_task_value(task, ['domain_rule_refs', 'domain_rules', 'domain_rule_refs_raw']))}",
            f"- Architecture refs: {_clip_items(_task_value(task, ['architecture_refs', 'arc42_refs', 'architecture_refs_raw']))}",
            f"- Application logic refs: {_clip_items(_task_value(task, ['application_logic_refs', 'application_logic_refs_raw']))}",
            f"- Core logic refs: {_clip_items(_task_value(task, ['core_logic_refs', 'core_logic_refs_raw']))}",
            f"- Permission refs: {_clip_items(_task_value(task, ['permission_refs', 'auth_refs', 'permission_refs_raw']))}",
            f"- State refs: {_clip_items(_task_value(task, ['state_refs', 'state_refs_raw']))}",
            f"- Failure refs: {_clip_items(_task_value(task, ['failure_refs', 'error_refs', 'failure_refs_raw']))}",
            f"- Integration refs: {_clip_items(_task_value(task, ['integration_refs', 'integration_refs_raw']))}",
            f"- UI refs: {_clip_items(_task_value(task, ['ui_refs', 'ui_refs_raw']))}",
            f"- Data refs: {_clip_items(_task_value(task, ['data_refs', 'data_refs_raw']))}",
            f"- Observability refs: {_clip_items(_task_value(task, ['observability_refs', 'audit_refs', 'observability_refs_raw']))}",
            f"- Evaluation refs: {_clip_items(_task_value(task, ['evaluation_refs', 'eval_refs', 'evaluation_refs_raw']))}",
            f"- Verify mode: `{_first_non_empty(task, ['verify_mode', 'verification_mode']) or 'not_declared'}`; risk level: `{_first_non_empty(task, ['risk_level', 'risk']) or 'not_declared'}`",
        ])
    elif task_id:
        lines.extend([
            "",
            "### Active task scope",
            f"- WARNING: `{task_id}` is set in the environment but was not found in `orchestrator-state/tasks/registry.json`.",
            "- Do not implement product changes until the registry/task pack mismatch is resolved.",
        ])
    else:
        lines.extend([
            "",
            "### Active task scope",
            "- No `CLAUDE_ACTIVE_TASK_ID` is pinned. Product-code agents must stop or return `OUTCOME: blocked` unless they are running an explicit bootstrap/planning workflow.",
        ])

    if role:
        lines.extend([
            "",
            "### Trailer contract for this agent",
            f"- Required keys: {_clip_items(_as_list(role.get('required_keys')))}",
            f"- Allowed OUTCOME values: {_clip_items(_as_list(role.get('outcome_values')))}",
            f"- Allowed NEXT_STATUS values: {_clip_items(_as_list(role.get('next_status_values')))}",
            f"- Info-only role: `{str(bool(role.get('info_only'))).lower()}`; mutates lifecycle: `{str(bool(role.get('mutates_registry_lifecycle'))).lower()}`; allowed to close task: `{str(bool(role.get('allowed_to_close_task'))).lower()}`",
            "- Final assistant message must include an explicit `CLAUDE_TRAILER:` block. Do not put inline comments on machine-readable trailer lines.",
        ])
    else:
        lines.extend([
            "",
            "### Trailer contract for this agent",
            f"- WARNING: agent type `{agent_type}` is not present in `.claude/orchestrator-contract.json` trailer schema.",
            "- Behave read-only and block rather than mutating lifecycle state without a contract.",
        ])

    if writer:
        lines.extend([
            "",
            "### Write contract for this agent",
            f"- May write: {_clip_items(_as_list(writer.get('may_write')), limit=10)}",
            f"- Must not write: {_clip_items(_as_list(writer.get('must_not_write')), limit=10)}",
        ])
    else:
        lines.extend([
            "",
            "### Write contract for this agent",
            f"- WARNING: no write contract found for `{agent_type}`. Default to read-only unless the prompt gives a stricter explicit command path.",
        ])

    lines.extend([
        "",
        "### Non-negotiable reminders",
        "- Do not edit `.claude/` static config, source-of-truth docs, registry/runtime JSON, or another task's artifacts during a normal app-building slice.",
        "- Do not broaden `write_set` silently. If scope drifts, record it in handoff and block or request source-of-truth correction.",
        "- Do not convert in-scope defects into follow-ups. Use debugger/retest/verify for in-scope defects; follow-ups are only for real out-of-scope work.",
        "- Verification must use real/provided data and runtime logs; never replace acceptance with stub/fake data.",
        "- Only `closer` may move a verified task to `done`, and only after report, baseline sync, Git workflow and cleanup gates pass.",
    ])

    # Surface a small amount of scheduler state without turning it into an implicit selector.
    if isinstance(runtime, dict):
        next_ready_phase = runtime.get("next_ready_phase_id") or "not_declared"
        next_ready_task = runtime.get("next_ready_task_id") or "not_declared"
        last_worker = runtime.get("last_worker") or "not_declared"
        lines.extend([
            "",
            "### Scheduler hints (read-only)",
            f"- Next ready hint: phase `{next_ready_phase}`, task `{next_ready_task}`",
            f"- Last worker: `{last_worker}`",
            "- These hints are not authority to switch tasks; keep the explicit active TASK_ID unless the command tells you otherwise.",
        ])

    return "\n".join(lines)[:MAX_CHARS]


def main() -> int:
    try:
        raw = sys.stdin.read()
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except Exception:
            payload = {}
        context = build_context(payload if isinstance(payload, dict) else {})
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SubagentStart",
                "additionalContext": context,
            }
        }, ensure_ascii=False))
    except Exception as exc:
        try:
            log_hook_error("hook_subagent_start_context", exc)
        except Exception:
            pass
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SubagentStart",
                "additionalContext": "",
            }
        }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
