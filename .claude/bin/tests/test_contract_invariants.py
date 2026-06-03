from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_trailer_schema_is_single_enum_source():
    contract = json.loads((ROOT / ".claude/orchestrator-contract.json").read_text(encoding="utf-8"))
    roles = contract["trailer_schema"]["roles"]
    assert roles, "trailer_schema.roles must exist"
    assert "outcome" + "_enums" not in contract
    assert "next_status" + "_enums" not in contract
    assert "outcome" + "_enums_source" not in contract
    assert "next_status" + "_enums_source" not in contract
    for role, spec in roles.items():
        assert isinstance(spec.get("outcome_values"), list), f"{role} missing outcome_values list"
        assert isinstance(spec.get("next_status_values"), list), f"{role} missing next_status_values list"


def test_trailer_agent_classes_are_derived_from_schema_only():
    contract = json.loads((ROOT / ".claude/orchestrator-contract.json").read_text(encoding="utf-8"))
    trailers = contract.get("trailers", {})
    assert "lifecycle_agents" not in trailers
    assert "info_only_agents" not in trailers
    roles = contract["trailer_schema"]["roles"]
    lifecycle = {role for role, spec in roles.items() if spec.get("mutates_registry_lifecycle")}
    info_only = {role for role, spec in roles.items() if spec.get("info_only")}
    assert "developer" in lifecycle
    assert "tester" in lifecycle
    assert "closer" in lifecycle
    assert "validator" in info_only
    assert "screen-journey-reviewer" in info_only


def test_agent_prompts_reference_existing_schema_roles():
    contract = json.loads((ROOT / ".claude/orchestrator-contract.json").read_text(encoding="utf-8"))
    valid_roles = set(contract["trailer_schema"]["roles"].keys())
    for agent_path in (ROOT / ".claude/agents").glob("*.md"):
        text = agent_path.read_text(encoding="utf-8")
        for m in re.finditer(r"trailer_schema\.roles\.([\w-]+)", text):
            assert m.group(1) in valid_roles, f"{agent_path.name} cita rol inexistente: {m.group(1)}"


def test_claude_md_agent_count_matches_filesystem():
    claude_md = (ROOT / ".claude/CLAUDE.md").read_text(encoding="utf-8")
    declared = int(re.search(r"Total:\s*(\d+)\s*agents", claude_md).group(1))
    actual = len(list((ROOT / ".claude/agents").glob("*.md")))
    assert declared == actual, f"CLAUDE.md dice {declared} agentes, hay {actual} ficheros"

def test_closer_done_guardrails_are_consistent_across_contract_sections():
    contract = json.loads((ROOT / ".claude/orchestrator-contract.json").read_text(encoding="utf-8"))
    source_of_truth = contract["trailers"]["closer_done_requires"]
    trailer_schema = contract["trailer_schema"]["closer_done_requires"]
    closer_required_keys = set(contract["trailer_schema"]["roles"]["closer"]["required_keys"])
    assert source_of_truth == trailer_schema
    assert "GIT_WORKFLOW_READY" in closer_required_keys
    assert "RUNTIME_CLEANED" in closer_required_keys
    assert "WORKTREES_CLEANED" in closer_required_keys
    for required in [
        "OUTCOME: committed",
        "NEXT_STATUS: done",
        "REPORT_READY: yes",
        "BASELINE_SYNC_READY: yes",
        "GIT_READY: yes",
        "PUSH_READY: yes",
        "GIT_WORKFLOW_READY: yes",
        "RUNTIME_CLEANED: yes",
        "WORKTREES_CLEANED: yes",
    ]:
        assert required in source_of_truth


def test_verify_policy_documents_browser_and_flutter_mobile_mcp_contracts():
    contract = json.loads((ROOT / ".claude/orchestrator-contract.json").read_text(encoding="utf-8"))
    verify_policy = contract["verify_policy"]
    assert {"chrome-devtools", "claude-in-chrome", "agent360-browser-mcp", "browser-mcp"}.issubset(
        set(verify_policy["accepted_browser_mcps"])
    )
    assert {"dart", "flutter", "flutter-driver"}.issubset(set(verify_policy["accepted_mobile_mcps"]))
    assert {"simulator", "emulator", "device"}.issubset(set(verify_policy["mobile_visual_check_methods"]))
    assert "browser/mobile MCP" in json.dumps(contract, ensure_ascii=False)




def test_agent_prompts_integrate_flutter_mobile_verify_policy_cleanly():
    agents_dir = ROOT / ".claude/agents"
    for name in ["main-orchestrator.md", "slice-verifier.md", "closer.md"]:
        text = (agents_dir / name).read_text(encoding="utf-8")
        assert "### Flutter mobile verify-slice" not in text, f"{name} has an appended mobile policy block"
        assert "MCP browser obligatorio" not in text, f"{name} still documents verify as browser-only"
    verifier = (agents_dir / "slice-verifier.md").read_text(encoding="utf-8")
    assert "Visual MCP obligatorio" in verifier
    assert "MCP_CLIENT: dart|flutter|flutter-driver" in verifier
    assert "VISUAL_CHECK_METHOD: simulator|emulator|device" in verifier
    assert "el usuario ejecutará `/closer <TASK_ID>` manualmente" in verifier
    main = (agents_dir / "main-orchestrator.md").read_text(encoding="utf-8")
    assert "Dart/Flutter MCP obligatorio" in main
    assert "MCP visual" in main
    closer = (agents_dir / "closer.md").read_text(encoding="utf-8")
    assert "Mobile verification evidence gate" in closer
    assert "MCP_CLIENT: dart|flutter|flutter-driver" in closer
