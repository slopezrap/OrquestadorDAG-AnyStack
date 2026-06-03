from __future__ import annotations

import sys
from pathlib import Path

_BIN = Path(__file__).resolve().parent.parent
if str(_BIN) not in sys.path:
    sys.path.insert(0, str(_BIN))

import check_task_dag as dag  # noqa: E402


def _registry_with_step_count(count: int) -> dict:
    tasks = []
    for i in range(1, count + 1):
        tasks.append({
            "id": f"P00-S02-T{i:03d}",
            "phase_id": "P00",
            "step_id": "P00-S02",
            "depends_on": [],
        })
    return {"tasks": tasks}


def test_large_step_task_counts_have_no_artificial_warning():
    assert dag.validate_phase_budgets(_registry_with_step_count(16)) == []
    assert dag.validate_phase_budgets(_registry_with_step_count(100)) == []


def test_no_artificial_size_budget_warning_classifier():
    assert dag.is_size_budget_warning("P00: 100 tasks exceeds max 20") is False


def test_large_phase_does_not_make_valid_dag_structurally_invalid():
    reg = _registry_with_step_count(100)
    recomputed, warnings, errors = dag.validate_registry_dag({
        "tasks": reg["tasks"],
        "task_dag": dag.build_task_dag(reg["tasks"]),
    })
    assert recomputed["mode"] == "explicit_dag"
    assert errors == []
    assert all("exceeds max" not in w for w in warnings)


def test_deprecated_size_budget_env_does_not_reintroduce_caps(monkeypatch):
    reg = _registry_with_step_count(100)
    monkeypatch.setenv("CLAUDE_DAG_ENFORCE_SIZE_BUDGETS", "1")
    recomputed, warnings, errors = dag.validate_registry_dag({
        "tasks": reg["tasks"],
        "task_dag": dag.build_task_dag(reg["tasks"]),
    })
    advisories = dag.validate_phase_budgets(reg)
    assert recomputed["mode"] == "explicit_dag"
    assert errors == []
    assert advisories == []
    assert all("exceeds max" not in w for w in warnings)
