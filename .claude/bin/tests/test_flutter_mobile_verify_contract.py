from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TASK_ID = "P00-S01-T001"


def _seed_flutter_mobile(tmp_path: Path) -> None:
    tasks_dir = tmp_path / "orchestrator-state" / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    registry = {
        "tasks": [{
            "id": TASK_ID,
            "title": "Flutter mobile screen",
            "kind": "flutter",
            "target": "Mobile screen",
            "status": "verified_pending_close",
            "risk_level": "medium",
            "verify_mode": "human",
            "write_set": ["app/lib/features/home/home_page.dart"],
            "route": "HomePage",
            "journey_refs": ["J001"],
        }],
        "phases": [], "journeys": [], "task_dag": {"mode": "explicit_dag"},
    }
    (tasks_dir / "registry.json").write_text(json.dumps(registry), encoding="utf-8")
    sot = tmp_path / "docs" / "source-of-truth"
    sot.mkdir(parents=True, exist_ok=True)
    (sot / "STACK_PROFILE.yaml").write_text("""
profile_version: stack-profile-v1
frontend:
  language: dart
  framework: flutter
  visual_check: simulator
verification:
  mobile:
    enabled: true
    mcp_client: dart
    visual_check_method: simulator
    simulator_required: true
    device_selector: ios-simulator
""".strip()+"\n", encoding="utf-8")


def _handoff(tmp_path: Path, visual: str) -> None:
    handoff = tmp_path / "orchestrator-state" / "tasks" / "handoffs" / f"{TASK_ID}.md"
    handoff.parent.mkdir(parents=True, exist_ok=True)
    handoff.write_text(f"""# Handoff {TASK_ID}

## Validator review
- TASK_ID: {TASK_ID}
- OUTCOME: approved

## Tester run
- TASK_ID: {TASK_ID}
- OUTCOME: pass

## verify-slice
- TASK_ID: {TASK_ID}
- AGENT: slice-verifier
{visual}
- VERIFY_OUTCOME: verified
- DATA_CONTRACT_ROWS: VDC-MOBILE-001
- DATA_SETUP: provided mobile fixture loaded
- PERSISTED_DATA_OBSERVED: backend record mob-001 persisted
- FLOWS_TESTED: simulator tap-through happy path and validation error
- EVIDENCE: orchestrator-state/tasks/evidence/{TASK_ID}/verify-mobile-simulator.md
- REAL_USER_VERIFIED: yes
- NO_STUB_DATA: yes
- NO_STUB_DATA_USED: yes
- REAL_DATA_SOURCE: provided fixture VDC-MOBILE-001
- HUMAN_REPRODUCTION: yes: simulator driven via Dart MCP
- UI_ACTIONS_VERIFIED: mobile tap submit, validation, back navigation
- BUTTONS_AND_CONTROLS_CHECKED: yes
- RUNTIME_LOGS_CHECKED: yes
- RUNTIME_LOGS_REVIEWED: flutter logs/backend logs checked
- ERROR_LOGS_STATUS: clean
- RUNTIME_LOG_ERRORS: 0
- LOG_EVIDENCE: orchestrator-state/tasks/evidence/{TASK_ID}/runtime-logs/runtime-log-check.json
- DOCKER_PORTS_ALLOCATED: not_applicable:flutter_simulator_no_published_host_ports
- RANCHER_WORKER_LOGS_CHECKED: not_applicable:no_rancher_worker
- RANCHER_WORKER_LOGS_REVIEWED: not_applicable:no_rancher_worker
- DOMAIN_RULES_VERIFIED: not_applicable:no_domain_refs
""", encoding="utf-8")


def _run(tmp_path: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CLAUDE_PROJECT_DIR"] = str(tmp_path)
    env["CLAUDE_ORCHESTRATOR_ROOT"] = str(tmp_path)
    return subprocess.run([
        sys.executable, "-B", "-S", str(ROOT / ".claude/bin/check_handoff_contract.py"), TASK_ID,
        "--require-ready-for-close", "--require-verify-slice", "--require-production-observability", "--json",
    ], cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)


def test_flutter_mobile_accepts_dart_mcp_client_and_simulator(tmp_path: Path) -> None:
    _seed_flutter_mobile(tmp_path)
    _handoff(tmp_path, "- MCP_BROWSER: not_applicable:flutter_mobile\n- MCP_CLIENT: dart\n- VISUAL_CHECK_METHOD: simulator\n- SIMULATOR_DEVICE: ios-simulator\n- FLUTTER_MCP_HEALTH: passed")
    result = _run(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr


def test_flutter_mobile_rejects_browser_only_verification(tmp_path: Path) -> None:
    _seed_flutter_mobile(tmp_path)
    _handoff(tmp_path, "- MCP_BROWSER: chrome-devtools\n- VISUAL_CHECK_METHOD: simulator")
    result = _run(tmp_path)
    assert result.returncode == 2
    payload = json.loads(result.stdout)
    joined = "\n".join(payload["errors"])
    assert "MCP_CLIENT" in joined
    assert "Dart/Flutter MCP" in joined
