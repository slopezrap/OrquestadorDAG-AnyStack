#!/usr/bin/env python3
"""Allocate per-slice host ports before Docker Compose starts.

`docker compose -p <compose_project>` isolates container names, volumes and networks, but
host ports are still global on the developer machine. This helper makes the
orchestrator safe for parallel worktrees by assigning stable, free host ports per
TASK_ID and exporting them as environment variables consumed by compose/dev
profiles.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import socket
import sys
from contextlib import closing
from pathlib import Path
from typing import Any

try:
    import fcntl  # type: ignore
except Exception:  # pragma: no cover - non-POSIX fallback
    fcntl = None  # type: ignore

# Keep import local/repo-relative so the helper works from copied worktrees.
BIN_DIR = Path(__file__).resolve().parent
if str(BIN_DIR) not in sys.path:
    sys.path.insert(0, str(BIN_DIR))
from stack_profile import load_stack_profile, get_path  # type: ignore  # noqa: E402
from runtime_context import task_slug, resolve as resolve_runtime_context  # type: ignore  # noqa: E402

DEFAULT_PORT_DEFAULTS = {
    "frontend": 3000,
    "backend": 8000,
    "api": 8080,
    "db": 5432,
    "worker": 9000,
}
DEFAULT_PORT_ENV = {
    "frontend": "CLAUDE_FRONTEND_PORT",
    "backend": "CLAUDE_BACKEND_PORT",
    "api": "CLAUDE_API_PORT",
    "db": "CLAUDE_DB_PORT",
    "worker": "CLAUDE_WORKER_PORT",
}



def is_free_port(port: int) -> bool:
    """Return True only when a TCP host port can be bound on localhost."""
    if port <= 0 or port > 65535:
        return False
    # Binding on 0.0.0.0 catches the normal Docker Compose host-port conflict.
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
        try:
            sock.bind(("0.0.0.0", port))
        except OSError:
            return False
    return True


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    text = str(value).strip().lower()
    if not text or text in {"none", "null", "false", "off", "auto"}:
        return None
    if re.fullmatch(r"\d+", text):
        num = int(text)
        return num if num > 0 else None
    return None


def _dict_or_empty(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def load_port_contract(root: Path) -> tuple[dict[str, int], dict[str, str], int]:
    profile = load_stack_profile(root)
    profile_defaults = _dict_or_empty(get_path(profile, "runtime.port_defaults", {}))
    profile_env = _dict_or_empty(get_path(profile, "runtime.port_env", {}))
    scan_span = _to_int(get_path(profile, "runtime.port_scan_span", 2000)) or 2000
    if scan_span < 20:
        scan_span = 20
    defaults: dict[str, int] = {}
    for key, default_port in {**DEFAULT_PORT_DEFAULTS, **profile_defaults}.items():
        port = _to_int(default_port)
        if port:
            defaults[str(key).strip().lower()] = port
    env_names: dict[str, str] = {}
    for key in defaults:
        candidate = profile_env.get(key) or DEFAULT_PORT_ENV.get(key) or f"CLAUDE_{re.sub(r'[^A-Z0-9]+', '_', key.upper()).strip('_')}_PORT"
        env_names[key] = str(candidate).strip() or f"CLAUDE_{key.upper()}_PORT"
    return defaults, env_names, scan_span


def parse_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key:
            out[key] = value
    return out


def existing_reserved_ports(ports_dir: Path, current_env_file: Path) -> set[int]:
    reserved: set[int] = set()
    for env_path in sorted(ports_dir.glob("*.env")):
        if env_path.resolve() == current_env_file.resolve():
            continue
        for value in parse_env_file(env_path).values():
            if re.fullmatch(r"\d+", str(value)):
                reserved.add(int(value))
    return reserved



def port_appears_owned_by_compose_project(port: int, compose_project: str) -> bool:
    """Best-effort check: an occupied port is acceptable only if Docker shows it
    as published by a container labelled with this compose project. If Docker is
    unavailable or output cannot prove ownership, return False.
    """
    if not compose_project:
        return False
    try:
        import subprocess
        proc = subprocess.run(
            [
                "docker",
                "ps",
                "--filter",
                f"label=com.docker.compose.project={compose_project}",
                "--format",
                "{{.Ports}}",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
    except Exception:
        return False
    if proc.returncode != 0:
        return False
    pattern = re.compile(rf"(?:0\.0\.0\.0|127\.0\.0\.1|\[::\])?:{port}->|:{port}->")
    return bool(pattern.search(proc.stdout or ""))

def candidate_ports(base: int, slug: str, key: str, span: int) -> list[int]:
    # Try the human-friendly default first when free; otherwise use a stable
    # hashed offset and then scan deterministically through the slice range.
    digest = hashlib.sha256(f"{slug}:{key}".encode("utf-8")).hexdigest()
    offset = int(digest[:8], 16) % span
    candidates = [base]
    for idx in range(span):
        port = base + ((offset + idx) % span)
        if port not in candidates and port <= 65535:
            candidates.append(port)
    return candidates


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\\''") + "'"


def write_outputs(env_file: Path, json_file: Path, *, task_id: str, slug: str, compose_project: str, ports: dict[str, int], env_names: dict[str, str], reused: bool) -> dict[str, Any]:
    env_file.parent.mkdir(parents=True, exist_ok=True)
    json_file.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Auto-generated by .claude/bin/allocate_slice_ports.py",
        "# Runtime-only. Do not commit.",
        f"export CLAUDE_ACTIVE_TASK_ID={shell_quote(task_id)}",
        f"export TASK_SLUG={shell_quote(slug)}",
        f"export COMPOSE_PROJECT_NAME={shell_quote(compose_project)}",
        f"export CLAUDE_COMPOSE_PROJECT_NAME={shell_quote(compose_project)}",
        f"export CLAUDE_PORT_ENV_FILE={shell_quote(str(env_file))}",
    ]
    by_name: dict[str, Any] = {}
    for key in sorted(ports):
        env_name = env_names[key]
        port = ports[key]
        lines.append(f"export {env_name}={shell_quote(str(port))}")
        lines.append(f"export CLAUDE_{re.sub(r'[^A-Z0-9]+', '_', key.upper()).strip('_')}_URL={shell_quote(f'http://localhost:{port}')}")
        by_name[key] = {"env": env_name, "port": port, "url": f"http://localhost:{port}"}
    env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    payload = {
        "task_id": task_id,
        "task_slug": slug,
        "compose_project_name": compose_project,
        "env_file": str(env_file),
        "ports": by_name,
        "reused_existing_env": reused,
    }
    json_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def allocate(root: Path, task_id: str, *, env_file: Path | None = None, force: bool = False) -> dict[str, Any]:
    root = root.resolve()
    slug = task_slug(task_id)
    ports_dir = root / "orchestrator-state" / "dev-ports"
    env_file = env_file or (ports_dir / f"{slug}.env")
    json_file = env_file.with_suffix(".json")
    lock_file = ports_dir / ".port-allocation.lock"
    ports_dir.mkdir(parents=True, exist_ok=True)
    with lock_file.open("a+") as lock_handle:
        if fcntl is not None:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        existing = parse_env_file(env_file)
        if existing and not force:
            # Reuse stable ports for this slice. During hard reset those ports may
            # already be held by the same compose project before `down` runs.
            defaults, env_names, _ = load_port_contract(root)
            ports: dict[str, int] = {}
            for key, env_name in env_names.items():
                value = existing.get(env_name)
                if value and re.fullmatch(r"\d+", value):
                    ports[key] = int(value)
            runtime_ctx = resolve_runtime_context(root, task_id)
            compose_project = existing.get("CLAUDE_COMPOSE_PROJECT_NAME") or existing.get("COMPOSE_PROJECT_NAME") or str(runtime_ctx.get("compose_project_name") or slug)
            if ports:
                occupied_by_other = [
                    port for port in ports.values()
                    if not is_free_port(port) and not port_appears_owned_by_compose_project(port, compose_project)
                ]
                if not occupied_by_other:
                    return write_outputs(env_file, json_file, task_id=task_id, slug=slug, compose_project=compose_project, ports=ports, env_names=env_names, reused=True)
                # Stale env: keep same task stable only if ports are free or owned
                # by this compose project. Otherwise allocate fresh ports.
        defaults, env_names, scan_span = load_port_contract(root)
        reserved = existing_reserved_ports(ports_dir, env_file)
        ports: dict[str, int] = {}
        for key, base in defaults.items():
            # Explicit environment variables win. They are trusted operator input.
            env_name = env_names[key]
            explicit = os.environ.get(env_name)
            explicit_port = _to_int(explicit)
            if explicit_port:
                ports[key] = explicit_port
                reserved.add(explicit_port)
                continue
            selected: int | None = None
            for candidate in candidate_ports(base, slug, key, scan_span):
                if candidate in reserved:
                    continue
                if is_free_port(candidate):
                    selected = candidate
                    break
            if selected is None:
                raise RuntimeError(f"no free port found for {key} near base {base} within span {scan_span}")
            ports[key] = selected
            reserved.add(selected)
        runtime_ctx = resolve_runtime_context(root, task_id)
        compose_project = os.environ.get("CLAUDE_COMPOSE_PROJECT_NAME") or os.environ.get("COMPOSE_PROJECT_NAME") or str(runtime_ctx.get("compose_project_name") or slug)
        return write_outputs(env_file, json_file, task_id=task_id, slug=slug, compose_project=compose_project, ports=ports, env_names=env_names, reused=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Allocate free host ports for a per-slice Docker/dev environment")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--task", "--task-id", dest="task_id", required=True)
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--force", action="store_true", help="ignore a previous allocation for this task and pick again")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--print-env", action="store_true", help="print source-able shell exports")
    args = parser.parse_args()
    try:
        result = allocate(args.root, args.task_id, env_file=args.env_file, force=args.force)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.print_env:
        print(Path(result["env_file"]).read_text(encoding="utf-8"), end="")
    else:
        print(f"PORT_ALLOCATION: task={result['task_id']} project={result['compose_project_name']} env={result['env_file']}")
        for key, info in result["ports"].items():
            print(f"  {key}: {info['env']}={info['port']} {info['url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
