from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


def test_doctor_fast_passes_and_reports_core_contracts():
    proc = subprocess.run(
        [sys.executable, "-B", "-S", ".claude/bin/orchestrator_doctor.py", "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["checks"]["agents"]["ok"] is True
    assert payload["checks"]["schemas"]["ok"] is True
    assert payload["checks"]["golden_fixture"]["ok"] is True
    assert payload["checks"]["runtime_reality_contract"]["ok"] is True
    assert payload["checks"]["no_artificial_slice_caps"]["ok"] is True


def test_schema_validator_accepts_runtime_log_check_sample(tmp_path):
    sample = tmp_path / "runtime-log-check.json"
    sample.write_text(json.dumps({
        "status": "pass",
        "task_id": "P01-S01-T001",
        "runtime_logs_clean": True,
        "files_scanned": ["orchestrator-state/tasks/evidence/P01-S01-T001/runtime-logs/app.log"],
        "files_count": 1,
        "findings_count": 0,
        "findings": [],
    }), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-B", "-S", ".claude/bin/validate_orchestrator_schemas.py", "--schema", ".claude/schemas/runtime-log-check.schema.json", "--instance", str(sample), "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["instance_validation"]["ok"] is True


def test_schema_validator_rejects_missing_required_runtime_log_field(tmp_path):
    sample = tmp_path / "runtime-log-check-bad.json"
    sample.write_text(json.dumps({
        "task_id": "P01-S01-T001",
        "runtime_logs_clean": True,
    }), encoding="utf-8")
    proc = subprocess.run(
        [sys.executable, "-B", "-S", ".claude/bin/validate_orchestrator_schemas.py", "--schema", ".claude/schemas/runtime-log-check.schema.json", "--instance", str(sample), "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )
    assert proc.returncode == 2
    payload = json.loads(proc.stdout)
    assert payload["instance_validation"]["ok"] is False
    assert any("findings_count" in err for err in payload["instance_validation"]["errors"])


def test_golden_real_app_e2e_passes():
    proc = subprocess.run(
        [sys.executable, "-B", "-S", "examples/golden-real-app/verify_golden_app.py", "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["status"] == "pass"
    assert payload["runtime_logs_clean"] is True
    assert payload["findings_count"] == 0
    assert payload["domain_rules_verified"] == ["DR-001", "DR-002"]
    assert "Create real record" in payload["ui_controls_checked"]
    assert "Refresh list" in payload["ui_controls_checked"]


def test_golden_source_of_truth_bootstrap_and_next_wave_pass():
    proc = subprocess.run(
        ["bash", "scripts/run-golden-e2e.sh", "--json"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=180,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert payload["app_e2e"]["runtime_logs_clean"] is True
    assert payload["orchestrator_bootstrap"]["tasks"] == 2
    assert payload["orchestrator_bootstrap"]["next_wave"]["ok"] is True
    assert payload["orchestrator_bootstrap"]["next_wave"]["dag_mode"] == "explicit_dag"
