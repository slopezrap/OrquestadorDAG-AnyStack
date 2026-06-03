#!/usr/bin/env python3
"""Resolve per-slice runtime names, Compose files and shell exports.

This helper centralizes rules that must be identical across next-wave,
check-runtime-logs, docker-hard-reset and cleanup-slice-runtime. In particular,
Docker Compose `-p` isolates objects but not host ports, and stack profiles may
use either `{task_slug}` or `{{task_slug}}` template syntax.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
from pathlib import Path
from typing import Any

BIN_DIR = Path(__file__).resolve().parent
import sys
if str(BIN_DIR) not in sys.path:
    sys.path.insert(0, str(BIN_DIR))
from stack_profile import load_stack_profile, get_path  # type: ignore  # noqa: E402

DEFAULT_COMPOSE_FILES = ["compose.yaml", "compose.yml", "docker-compose.yaml", "docker-compose.yml"]


def task_slug(task_id: str) -> str:
    cleaned = re.sub(r"[^a-z0-9_.-]+", "-", str(task_id).lower()).strip(".-_")
    cleaned = re.sub(r"-+", "-", cleaned)
    if not cleaned:
        cleaned = "orchestrator-slice"
    if not re.match(r"^[a-z0-9]", cleaned):
        cleaned = "p-" + cleaned
    return cleaned


def is_none_value(value: Any) -> bool:
    text = str(value if value is not None else "").strip().lower()
    return text in {"", "none", "null", "[]", "false", "off", "auto"}


def render_template(template: Any, *, task_id: str, slug: str) -> str:
    text = str(template if template is not None else "").strip()
    if is_none_value(text):
        text = "{task_slug}"
    replacements = {
        "task_slug": slug,
        "TASK_SLUG": slug,
        "task_id": task_id,
        "TASK_ID": task_id,
    }
    for key, value in replacements.items():
        text = re.sub(r"\{\{\s*" + re.escape(key) + r"\s*\}\}", value, text)
        text = text.replace("{" + key + "}", value)
        text = text.replace("${" + key + "}", value)
        text = re.sub(r"(?<![A-Za-z0-9_])\$" + re.escape(key) + r"\b", value, text)
    return text


def normalize_compose_project(value: str) -> str:
    raw = str(value or "").strip().lower()
    if "{" in raw or "}" in raw or "$task" in raw:
        raise ValueError(f"unresolved compose project template: {value!r}")
    cleaned = re.sub(r"[^a-z0-9_-]+", "-", raw).strip("-_")
    cleaned = re.sub(r"[-_]{2,}", lambda m: m.group(0)[0], cleaned)
    if not cleaned:
        cleaned = "orchestrator-slice"
    if not re.match(r"^[a-z0-9]", cleaned):
        cleaned = "p-" + cleaned
    return cleaned


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items = value
    elif isinstance(value, tuple):
        items = list(value)
    else:
        text = str(value).strip()
        if is_none_value(text):
            return []
        if text.startswith("[") and text.endswith("]"):
            body = text[1:-1].strip()
            if not body:
                return []
            items = [part.strip().strip("'\"") for part in body.split(",")]
        elif "," in text:
            items = [part.strip() for part in text.split(",")]
        else:
            items = [text]
    out: list[str] = []
    for item in items:
        text = str(item).strip().strip("'\"")
        if text and not is_none_value(text) and text not in out:
            out.append(text)
    return out


def profile_compose_project_template(profile: dict[str, Any]) -> Any:
    return get_path(profile, "verification.docker.compose_project_template", "{task_slug}")


def profile_compose_files(profile: dict[str, Any]) -> tuple[list[str], bool]:
    candidates: list[str] = []
    explicit = False
    for dotted in (
        "verification.docker.compose_file",
        "verification.docker.compose_files",
        "runtime.compose_file",
        "runtime.compose_files",
        "runtime.docker_compose_file",
        "runtime.docker_compose_files",
    ):
        raw = get_path(profile, dotted, None)
        if raw is not None and not isinstance(raw, (list, tuple, dict)) and is_none_value(raw) and str(raw).strip().lower() != "auto":
            # An explicit `none` means this stack does not use Docker Compose.
            return [], False
        values = _as_list(raw)
        if values:
            explicit = True
            candidates.extend(values)
    if not candidates:
        candidates = list(DEFAULT_COMPOSE_FILES)
    if candidates == DEFAULT_COMPOSE_FILES:
        explicit = False
    out: list[str] = []
    for item in candidates:
        if item not in out:
            out.append(item)
    return out, explicit


def resolve(root: Path, task_id: str, *, workspace_root: Path | None = None, project: str | None = None) -> dict[str, Any]:
    root = root.resolve()
    workspace = (workspace_root or root).resolve()
    profile = load_stack_profile(root)
    slug = task_slug(task_id)
    if project:
        compose_project = normalize_compose_project(render_template(project, task_id=task_id, slug=slug))
    else:
        template = profile_compose_project_template(profile)
        compose_project = normalize_compose_project(render_template(template, task_id=task_id, slug=slug))
    configured_files, compose_files_explicit = profile_compose_files(profile)
    resolved_files: list[dict[str, Any]] = []
    existing_files: list[str] = []
    for rel in configured_files:
        rendered = render_template(rel, task_id=task_id, slug=slug)
        path = Path(rendered)
        abs_path = path if path.is_absolute() else workspace / path
        record = {
            "configured": rel,
            "path": str(path),
            "abs_path": str(abs_path),
            "exists": abs_path.is_file(),
        }
        resolved_files.append(record)
        if record["exists"]:
            # Keep a workspace-relative path for docker compose -f when possible.
            try:
                existing_files.append(str(abs_path.relative_to(workspace)))
            except ValueError:
                existing_files.append(str(abs_path))
    return {
        "task_id": task_id,
        "task_slug": slug,
        "compose_project_name": compose_project,
        "root": str(root),
        "workspace_root": str(workspace),
        "compose_files_configured": configured_files,
        "compose_files_explicit": compose_files_explicit,
        "compose_files": resolved_files,
        "existing_compose_files": existing_files,
        "first_compose_file": existing_files[0] if existing_files else "",
        "profile_source": profile.get("_source", "unknown"),
    }


def shell_exports(ctx: dict[str, Any]) -> str:
    existing = ":".join(ctx.get("existing_compose_files") or [])
    configured = ":".join(str(item) for item in (ctx.get("compose_files_configured") or []))
    lines = [
        f"export CLAUDE_ACTIVE_TASK_ID={shlex.quote(str(ctx['task_id']))}",
        f"export TASK_ID={shlex.quote(str(ctx['task_id']))}",
        f"export TASK_SLUG={shlex.quote(str(ctx['task_slug']))}",
        f"export COMPOSE_PROJECT_NAME={shlex.quote(str(ctx['compose_project_name']))}",
        f"export CLAUDE_COMPOSE_PROJECT_NAME={shlex.quote(str(ctx['compose_project_name']))}",
        f"export CLAUDE_RUNTIME_COMPOSE_FILES={shlex.quote(existing)}",
        f"export CLAUDE_RUNTIME_COMPOSE_FILES_CONFIGURED={shlex.quote(configured)}",
        f"export CLAUDE_COMPOSE_FILE={shlex.quote(str(ctx.get('first_compose_file') or ''))}",
        f"export CLAUDE_COMPOSE_FILE_EXISTS={shlex.quote('yes' if ctx.get('first_compose_file') else 'no')}",
        f"export CLAUDE_RUNTIME_COMPOSE_FILES_EXPLICIT={shlex.quote('yes' if ctx.get('compose_files_explicit') else 'no')}",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve runtime context for one orchestrator TASK_ID")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--workspace-root", type=Path)
    parser.add_argument("--task", "--task-id", dest="task_id", required=True)
    parser.add_argument("--project", help="explicit compose project template/name")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--print-env", action="store_true")
    args = parser.parse_args()
    try:
        ctx = resolve(args.root, args.task_id, workspace_root=args.workspace_root, project=args.project)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.print_env:
        print(shell_exports(ctx), end="")
    else:
        print(json.dumps(ctx, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
