#!/usr/bin/env python3
"""Global health check for OrquestadorDAG AnyStack."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from common import canonical_source_docs_dir, project_root, workspace_relpath
from validate_orchestrator_schemas import validate_schema_files

EXPECTED_AGENTS = {
    "main-orchestrator", "planner", "developer", "validator", "tester", "debugger",
    "slice-verifier", "screen-journey-reviewer", "closer", "official-docs-researcher",
    "document-analyzer", "project-architect", "task-planner", "deployer",
}
REQUIRED_COMMANDS = {
    "next-wave.md", "next-slice.md", "verify-slice.md", "closer.md", "phase-gate.md",
    "verify-journey.md", "register-followup.md", "promote-followup.md", "revise-slice.md",
    "slice-maintain.md", "auto-verify-slice.md",
}
REQUIRED_FILES = [
    "README.md", "CHEATSHEET.md", ".claude/CLAUDE.md", ".claude/orchestrator-contract.json",
    ".claude/bin/bootstrap_source_of_truth.py", ".claude/bin/check_handoff_contract.py",
    ".claude/bin/check_runtime_logs.py", ".claude/bin/allocate_slice_ports.py", ".claude/bin/runtime_context.py", ".claude/bin/verify_slice_state.py",
    ".claude/bin/orchestrator_doctor.py", ".claude/bin/validate_orchestrator_schemas.py",
    "scripts/next-wave.sh", "scripts/check-runtime-logs.sh", "scripts/docker-hard-reset.sh", "scripts/allocate-slice-ports.sh",
    "scripts/cleanup-slice-runtime.sh", "scripts/orchestrator-doctor.sh", "scripts/run-golden-e2e.sh", "scripts/validate-orchestrator-schemas.sh",
]
STALE_CAP_PATTERNS = [
    r"phase\s*<=\s*20", r"step\s*<=\s*15", r"20\s*[-–]\s*60\s+slices",
    r"20\s*[-–]\s*50\s+slices", r"3\s*[-–]\s*8\s+tasks", r"2\s*[-–]\s*4\s+phases",
    r"1\s*[-–]\s*2\s+journeys", r"6\s*[-–]\s*12\s+slices", r"NUNCA\s+m[aá]s\s+de\s+6\s+journeys",
]


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except Exception:
        return workspace_relpath(path)


def _check(ok: bool, details: Any = None) -> dict[str, Any]:
    return {"ok": bool(ok), "details": details}


def _run(cmd: list[str], root: Path, timeout: int = 60) -> dict[str, Any]:
    proc = subprocess.run(cmd, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, check=False)
    return {"ok": proc.returncode == 0, "returncode": proc.returncode, "stdout": proc.stdout[-5000:], "stderr": proc.stderr[-5000:]}


def _source_docs_state(root: Path) -> tuple[str, list[Path]]:
    sot = canonical_source_docs_dir(root)
    if not sot.exists():
        return "missing", []
    docs = sorted([p for p in sot.iterdir() if p.is_file() and p.name != ".gitkeep"])
    if not docs:
        return "framework_clean", []
    return "present", docs


def doctor(*, root: Path | None = None, require_source_of_truth: bool = False, run_static: bool = False, deep: bool = False) -> dict[str, Any]:
    root = (root or project_root()).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, Any] = {}

    missing_files = [rel for rel in REQUIRED_FILES if not (root / rel).exists()]
    checks["required_files"] = _check(not missing_files, {"missing": missing_files})
    errors.extend([f"missing required file: {rel}" for rel in missing_files])

    obsolete_claude_scripts = root / ".claude" / "scripts"
    checks["no_obsolete_claude_scripts_dir"] = _check(not obsolete_claude_scripts.exists(), {"path": ".claude/scripts"})
    if obsolete_claude_scripts.exists():
        errors.append("obsolete .claude/scripts directory must not exist")

    agents_dir = root / ".claude" / "agents"
    agent_names = sorted(p.stem for p in agents_dir.glob("*.md")) if agents_dir.is_dir() else []
    missing_agents = sorted(EXPECTED_AGENTS - set(agent_names))
    extra_agents = sorted(set(agent_names) - EXPECTED_AGENTS)
    model_errors: list[str] = []
    for path in sorted(agents_dir.glob("*.md")) if agents_dir.is_dir() else []:
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"(?m)^model:\s+(opus|sonnet)\s*$", text):
            model_errors.append(f"{_rel(root, path)} uses non-1M alias")
        if re.search(r"(?m)^effort:\s*ultracode\s*$", text, re.I):
            model_errors.append(f"{_rel(root, path)} sets session-only effort ultracode in subagent frontmatter")
    checks["agents"] = _check(not missing_agents and not extra_agents and not model_errors, {
        "count": len(agent_names), "missing": missing_agents, "extra": extra_agents, "model_errors": model_errors,
    })
    errors.extend([f"missing agent: {name}" for name in missing_agents])
    errors.extend([f"unexpected agent: {name}" for name in extra_agents])
    errors.extend(model_errors)

    command_names = sorted(p.name for p in (root / ".claude" / "commands").glob("*.md"))
    missing_commands = sorted(REQUIRED_COMMANDS - set(command_names))
    checks["commands"] = _check(not missing_commands, {"count": len(command_names), "missing": missing_commands})
    errors.extend([f"missing command: {name}" for name in missing_commands])

    schema_result = validate_schema_files(root)
    checks["schemas"] = _check(schema_result["ok"], {"schema_count": len(schema_result.get("schemas") or {}), "errors": schema_result["errors"]})
    errors.extend([f"schema: {err}" for err in schema_result["errors"]])
    warnings.extend([f"schema: {warn}" for warn in schema_result["warnings"]])

    golden_files = [
        "examples/golden-real-app/app.py", "examples/golden-real-app/verify_golden_app.py",
        "examples/golden-real-app/fixtures/real_user_payload.json", "examples/golden-real-app/source-of-truth/instrucciones.md",
        "examples/golden-real-app/source-of-truth/GOLDEN_REAL_APP_TECHNICAL_GUIDE.md",
        "examples/golden-real-app/source-of-truth/GOLDEN_REAL_APP_IMPLEMENTATION_CHECKLIST.md",
        "examples/golden-real-app/source-of-truth/UX_CONTRACT.md", "examples/golden-real-app/source-of-truth/STACK_PROFILE.yaml",
    ]
    missing_golden = [rel for rel in golden_files if not (root / rel).exists()]
    checks["golden_fixture"] = _check(not missing_golden, {"missing": missing_golden})
    errors.extend([f"missing golden fixture file: {rel}" for rel in missing_golden])

    state, docs = _source_docs_state(root)
    checks["source_of_truth"] = _check(state == "present" or not require_source_of_truth, {"state": state, "files": [_rel(root, p) for p in docs]})
    if require_source_of_truth and state != "present":
        errors.append("source-of-truth docs required but docs/source-of-truth has no product files")
    if state == "present":
        result = _run([sys.executable, "-B", "-S", ".claude/bin/bootstrap_source_of_truth.py", "--validate-only", "--json"], root, 120)
        checks["bootstrap_validate_only"] = result
        if not result["ok"]:
            errors.append("bootstrap --validate-only failed")

    stale_hits: list[str] = []
    scan_roots = [root / "docs" / "templates", root / "docs" / "prompts", root / "docs" / "guides", root / "README.md", root / "CHEATSHEET.md"]
    for scan_root in scan_roots:
        paths = [scan_root] if scan_root.is_file() else sorted(scan_root.rglob("*.md")) if scan_root.exists() else []
        for path in paths:
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern in STALE_CAP_PATTERNS:
                if re.search(pattern, text, re.I):
                    stale_hits.append(f"{_rel(root, path)} matches {pattern}")
    checks["no_artificial_slice_caps"] = _check(not stale_hits, stale_hits)
    errors.extend([f"stale artificial cap: {hit}" for hit in stale_hits])

    runtime_needles = ["REAL_USER_VERIFIED", "NO_STUB_DATA_USED", "HUMAN_REPRODUCTION", "RUNTIME_LOG_ERRORS", "RANCHER_WORKER_LOGS_CHECKED", "DOMAIN_RULES_VERIFIED", "LLM_DOCUMENT_EXTRACTION", "DOCKER_PORTS_ALLOCATED", "RUNTIME_CLEANED", "cleanup-slice-runtime"]
    runtime_docs = "\n".join((root / rel).read_text(encoding="utf-8", errors="replace") for rel in [".claude/commands/verify-slice.md", ".claude/commands/closer.md", ".claude/agents/slice-verifier.md", ".claude/agents/closer.md"] if (root / rel).exists())
    missing_runtime = [needle for needle in runtime_needles if needle not in runtime_docs]
    checks["runtime_reality_contract"] = _check(not missing_runtime, {"missing": missing_runtime})
    errors.extend([f"runtime reality contract missing {needle}" for needle in missing_runtime])

    port_docs = "\n".join(
        (root / rel).read_text(encoding="utf-8", errors="replace")
        for rel in ["README.md", "CHEATSHEET.md", "docs/guides/CHATGPT_DAG_SOURCE_OF_TRUTH_GUIDE.md", ".claude/commands/verify-slice.md"]
        if (root / rel).exists()
    )
    port_needles = ["CLAUDE_FRONTEND_PORT", "allocate-slice-ports", "puertos host", "compose_file"]
    missing_port_docs = [needle for needle in port_needles if needle not in port_docs]
    stack_templates_missing_ports = []
    for template in sorted((root / "docs" / "templates").glob("*/STACK_PROFILE.template.yaml")):
        text = template.read_text(encoding="utf-8", errors="replace")
        if "port_defaults:" not in text or "CLAUDE_FRONTEND_PORT" not in text:
            stack_templates_missing_ports.append(_rel(root, template))
    checks["per_slice_port_contract"] = _check(not missing_port_docs and not stack_templates_missing_ports, {"missing_docs": missing_port_docs, "templates_missing": stack_templates_missing_ports})
    errors.extend([f"per-slice port contract missing doc token: {needle}" for needle in missing_port_docs])
    errors.extend([f"STACK_PROFILE template missing port contract: {rel}" for rel in stack_templates_missing_ports])

    cleanup_docs = "\n".join(
        (root / rel).read_text(encoding="utf-8", errors="replace")
        for rel in ["README.md", "CHEATSHEET.md", "docs/guides/CHEATSHEET.md", ".claude/commands/closer.md", ".claude/agents/closer.md"]
        if (root / rel).exists()
    )
    cleanup_needles = ["cleanup-slice-runtime.sh", "RUNTIME_CLEANED", "rancher_cleanup_cmd", "--strict"]
    missing_cleanup_docs = [needle for needle in cleanup_needles if needle not in cleanup_docs]
    checks["slice_runtime_cleanup_contract"] = _check(not missing_cleanup_docs, {"missing_docs": missing_cleanup_docs})
    errors.extend([f"slice runtime cleanup contract missing doc token: {needle}" for needle in missing_cleanup_docs])

    if run_static:
        py_files = [str(p) for p in sorted((root / ".claude" / "bin").glob("*.py"))] + [str(p) for p in sorted((root / "scripts").glob("*.py"))]
        checks["py_compile"] = _run([sys.executable, "-B", "-S", "-m", "py_compile", *py_files], root, 120)
        if not checks["py_compile"]["ok"]:
            errors.append("py_compile failed")
        checks["validate_schemas"] = _run(["bash", "scripts/validate-orchestrator-schemas.sh", "--json"], root, 60)
        if not checks["validate_schemas"]["ok"]:
            errors.append("validate-orchestrator-schemas failed")
    if deep and (root / "scripts" / "run-golden-e2e.sh").exists():
        checks["golden_e2e"] = _run(["bash", "scripts/run-golden-e2e.sh", "--json"], root, 180)
        if not checks["golden_e2e"]["ok"]:
            errors.append("golden E2E failed")

    return {"ok": not errors, "errors": errors, "warnings": warnings, "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run OrquestadorDAG global health checks")
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--require-source-of-truth", action="store_true")
    parser.add_argument("--run-static", action="store_true")
    parser.add_argument("--deep", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = doctor(root=args.root, require_source_of_truth=args.require_source_of_truth, run_static=args.run_static, deep=args.deep)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Orchestrator doctor OK" if result["ok"] else "Orchestrator doctor FAILED", file=sys.stdout if result["ok"] else sys.stderr)
        for err in result["errors"]:
            print(f"- {err}", file=sys.stderr)
        for warn in result["warnings"]:
            print(f"WARN: {warn}")
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
