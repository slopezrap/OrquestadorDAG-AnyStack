#!/usr/bin/env python3
"""Validate the derived task DAG against registry.json.

The source of truth is the Coverage Registry in the checklist. Bootstrap stores
its derived graph in registry.task_dag and orchestrator-state/memory/task-dag.*.
This script recomputes the graph from registry.tasks and reports drift, cycles,
unknown dependencies or stale matrices.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from bootstrap_source_of_truth import build_task_dag
from common import load_registry, memory_dir, now_iso, read_json


def _norm_edges(edges: list[list[str]] | list[tuple[str, str]] | None) -> list[list[str]]:
    out: list[list[str]] = []
    for edge in edges or []:
        if len(edge) == 2:
            out.append([str(edge[0]), str(edge[1])])
    return sorted(out)


def is_size_budget_warning(warning: str) -> bool:
    """Compatibility hook for the historical phase/step size-budget policy.

    The current policy removes artificial caps for phases, steps and slices. Large products are
    expected to declare every required task instead of compressing work to fit a
    numeric budget. This function remains so older tests/imports do not break.
    """
    return False


def validate_phase_budgets(registry: dict[str, Any]) -> list[str]:
    """Return no phase/step size warnings.

    The DAG validator now checks structural correctness only: dependencies,
    cycles, view drift and explicit-DAG metadata. Granularity is governed by
    traceability, write-set ownership and real verification, not by a hard or
    advisory count of tasks per phase/step.
    """
    _ = registry
    return []


def validate_dag_view_files(registry: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    stored = registry.get("task_dag") or {}
    task_dag_path = memory_dir() / "task-dag.json"
    if task_dag_path.exists():
        view = read_json(task_dag_path, {})
        for key in ("mode", "nodes", "edges", "adjacency_matrix", "topological_levels", "source_digest"):
            if view.get(key) != stored.get(key):
                warnings.append(f"task-dag.json view drift at {key}; rerun bootstrap_source_of_truth.py --refresh")
                break
    else:
        warnings.append("task-dag.json view missing; rerun bootstrap_source_of_truth.py --refresh")
    exec_path = memory_dir() / "execution-graph.json"
    if exec_path.exists():
        exec_view = read_json(exec_path, {})
        exec_dag = exec_view.get("task_dag") or {}
        if exec_dag.get("source_digest") != stored.get("source_digest"):
            warnings.append("execution-graph.json view drift from registry.task_dag; rerun bootstrap_source_of_truth.py --refresh")
    else:
        warnings.append("execution-graph.json view missing; rerun bootstrap_source_of_truth.py --refresh")
    return warnings


def validate_registry_dag(registry: dict[str, Any]) -> tuple[dict[str, Any], list[str], list[str]]:
    tasks = registry.get("tasks") or []
    warnings: list[str] = []
    errors: list[str] = []
    if not isinstance(tasks, list) or not tasks:
        errors.append("registry.tasks is empty; run bootstrap_source_of_truth.py --refresh after filling source-of-truth docs")
        return build_task_dag([]), warnings, errors

    recomputed = build_task_dag(tasks)
    errors.extend(recomputed.get("errors") or [])
    if recomputed.get("mode") != "explicit_dag":
        warnings.append("production DAG-only requires task_dag.mode=explicit_dag; fill Coverage Registry Depends on before opening workers")

    stored = registry.get("task_dag") or {}
    if not stored:
        warnings.append("registry.task_dag is missing; rerun bootstrap_source_of_truth.py --refresh")
    else:
        if stored.get("mode") != recomputed.get("mode"):
            errors.append(f"registry.task_dag.mode drift: stored={stored.get('mode')} recomputed={recomputed.get('mode')}")
        if stored.get("nodes") != recomputed.get("nodes"):
            errors.append("registry.task_dag.nodes drift from registry.tasks order")
        if _norm_edges(stored.get("edges")) != _norm_edges(recomputed.get("edges")):
            errors.append("registry.task_dag.edges drift from registry.tasks[].depends_on")
        if stored.get("adjacency_matrix") != recomputed.get("adjacency_matrix"):
            errors.append("registry.task_dag.adjacency_matrix drift from registry.tasks[].depends_on")
        if stored.get("topological_levels") != recomputed.get("topological_levels"):
            errors.append("registry.task_dag.topological_levels drift from registry.tasks[].depends_on")

    warnings.extend(validate_dag_view_files(registry))
    return recomputed, warnings, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate registry task DAG and derived adjacency matrix.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Return non-zero on structural warnings as well as errors")
    parser.add_argument("--enforce-size-budgets", action="store_true", help="Deprecated no-op: artificial phase/step size caps are removed")
    args = parser.parse_args()

    registry = load_registry()
    task_dag, warnings, errors = validate_registry_dag(registry)
    advisories = validate_phase_budgets(registry)
    enforce_size_budgets = False  # Current policy: no artificial phase/step caps.
    strict_warnings = list(warnings)
    result = {
        "ok": not errors and (not args.strict or not strict_warnings),
        "checked_at": now_iso(),
        "mode": task_dag.get("mode"),
        "node_count": len(task_dag.get("nodes") or []),
        "edge_count": len(task_dag.get("edges") or []),
        "wave_count": len(task_dag.get("topological_levels") or []),
        "warnings": strict_warnings,
        "advisories": [] if enforce_size_budgets else advisories,
        "size_budget_enforced": enforce_size_budgets,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        status = "OK" if result["ok"] else "INVALID"
        print(f"Task DAG: {status} mode={result['mode']} nodes={result['node_count']} edges={result['edge_count']} waves={result['wave_count']}")
        for warning in strict_warnings:
            print(f"WARNING: {warning}")
        for advisory in advisories:
            print(f"ADVISORY: {advisory}")
        for error in errors:
            print(f"ERROR: {error}")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
