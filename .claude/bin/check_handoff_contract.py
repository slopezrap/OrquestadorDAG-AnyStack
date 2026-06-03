#!/usr/bin/env python3
"""Validate per-task handoff contract before verify/close.

This is intentionally small and text-based: handoffs are Markdown written by
agents, but closer depends on a few machine-readable result lines surviving
`/clear`. The chat trailer is not enough for close-time audit.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

try:
    from stack_profile import get_path as _stack_get_path, load_stack_profile as _load_stack_profile
except Exception:  # pragma: no cover
    _stack_get_path = None
    _load_stack_profile = None

from common import (
    find_task,
    handoff_path as _handoff_path_resolver,
    load_registry,
    task_write_set,
    workspace_relpath,
)

SECTION_RE = re.compile(r"^(?P<hashes>#{2,6})\s+(?P<title>.+?)\s*$")
KEY_RE = re.compile(r"^\s*-?\s*(?P<key>[A-Za-z][A-Za-z0-9_]*):\s*(?P<value>.*?)\s*$")
HEADING_KEY_RE = re.compile(r"^\s*-?\s*#{1,6}\s+(?P<key>[A-Za-z][A-Za-z0-9_]*):\s*(?P<value>.*?)\s*$")
CYCLE_SUFFIX_RE = re.compile(r"\s*\((?:cycle|ciclo)\s+\d+\)\s*$", re.IGNORECASE)

# Agents occasionally write machine-readable lines as markdown subheadings,
# e.g. ``### AGENT: validator`` under ``## Validator review``.  Treat
# those as fields in the current logical section, not as new sections.
# This keeps the checker robust without accepting arbitrary prose headings as
# contract fields.
MACHINE_HEADING_KEYS = {
    "AGENT",
    "TASK_ID",
    "TIMESTAMP",
    "MODE",
    "OUTCOME",
    "NEXT_STATUS",
    "HANDOFF",
    "EVIDENCE",
    "VERIFY_OUTCOME",
    "VERIFY_MODE",
    "RISK_LEVEL",
    "MCP_BROWSER",
    "FLUTTER_MCP_HEALTH",
    "SIMULATOR_DEVICE",
    "VISUAL_CHECK_METHOD",
    "MCP_CLIENT",
    "DATA_CONTRACT_ROWS",
    "DATA_SETUP",
    "PERSISTED_DATA_OBSERVED",
    "FLOWS_TESTED",
    "VALIDATION_TABLE",
    "FINDINGS",
    "BLOCKER_REASON",
    "BLOCKER_KIND",
    "USER_ACTION_REQUIRED",
    "JOURNEYS",
    "JOURNEY_VERIFY_OUTCOME",
    "MARGINAL_STATES_TESTED",
    "NEXT_ACTION_VERIFIED",
    "FOLLOWUP_ID",
    "FOLLOWUP_REQUIRED",
    "UI_ACTIONS_VERIFIED",
    "LLM_INPUT_ARTIFACTS",
    "DOMAIN_RULES_VERIFIED",
    "REAL_USER_VERIFIED",
    "NO_STUB_DATA",
    "RUNTIME_LOGS_REVIEWED",
    "RANCHER_WORKER_LOGS_REVIEWED",
    "ERROR_LOGS_STATUS",
    "DOCKER_COMPOSE_PROJECT",
    "DOCKER_PORTS_ALLOCATED",
    "NO_STUB_DATA_USED",
    "REAL_DATA_SOURCE",
    "HUMAN_REPRODUCTION",
    "BUTTONS_AND_CONTROLS_CHECKED",
    "RUNTIME_LOGS_CHECKED",
    "RANCHER_WORKER_LOGS_CHECKED",
    "RUNTIME_LOG_ERRORS",
    "LOG_EVIDENCE",
    "DATA_SOURCE_FILES",
    "LLM_DOCUMENT_EXTRACTION",
}


VALIDATOR_OUTCOMES = {"approved", "changes_requested", "blocked"}
TESTER_OUTCOMES = {"pass", "fail", "blocked"}
VERIFY_OUTCOMES = {"verified", "issues_found", "blocked"}
SCREEN_JOURNEY_OUTCOMES = {"approved", "changes_requested", "blocked"}

CONTRACT_SECTION_NAMES = {
    "validator review",
    "tester run",
    "verify-slice",
    "verify-journey",
    "revision-debugger",
    "debugger fix",
    "screen/journey review",
}
FOLLOWUP_ID_RE = re.compile(r"\bFU-[A-Za-z0-9_.:-]+\b")
FOLLOWUP_CANDIDATE_RE = re.compile(r"(?im)^\s*-?\s*(followup_candidate|FOLLOWUP_REQUIRED)\s*:\s*(yes|true|si|sí)\s*$")
VERIFY_BROWSER_ACCEPTED = {"chrome-devtools", "claude-in-chrome", "agent360-browser-mcp"}
VERIFY_MOBILE_MCP_ACCEPTED = {"dart", "flutter", "flutter-driver"}
VERIFY_MOBILE_VISUAL_METHODS = {"simulator", "emulator", "device", "ios-simulator", "android-emulator", "physical-device"}
SHARED_VISUAL_WRITE_SET_HINTS = (
    "/errors.ts", "/errors.tsx", "/errors.py", "/exceptions.py",
    "/auth/", "/chat/", "/security/", "/routes/", "/router/",
    "/navigation/", "/providers/", "/context/", "/store/",
)


# Auto verify is intentionally narrow. Slices touching UI, navigation, auth,
# shared frontend/domain files, or broad cross-feature modules need the human
# browser MCP gate so regressions that unit tests miss (e.g. deleted auth/chat
# error classes) are caught before closer.
AUTO_VERIFY_HUMAN_REQUIRED_EXTENSIONS = (".tsx", ".jsx", ".vue", ".svelte", ".dart")
AUTO_VERIFY_HUMAN_REQUIRED_TOKENS = (
    "errors.ts",
    "error.ts",
    "/error",
    "/errors",
    "router",
    "routes",
    "navigation",
    "layout",
    "provider",
    "providers",
    "auth",
    "mfa",
    "2fa",
    "forgot",
    "chat",
    "shared",
    "core",
)
AUTO_VERIFY_HUMAN_REQUIRED_KINDS = ("front", "frontend", "ui", "ux", "screen", "page", "route", "journey", "gate")


def _load_task_for_verify(task_id: str) -> dict[str, object] | None:
    try:
        return find_task(load_registry(), task_id)
    except Exception:
        return None


def _task_requires_human_browser_verify(task: dict[str, object] | None) -> tuple[bool, str]:
    if not task:
        return False, ""
    verify_mode = str(task.get("verify_mode") or task.get("verify") or "").strip().lower()
    if verify_mode and verify_mode not in {"auto", "low+auto", "automatic"}:
        return True, f"task verify_mode={verify_mode!r} is not auto"
    if task.get("route") or task.get("screen_route"):
        return True, "task declares a UI route/screen"
    if task.get("journey_refs"):
        return True, "task participates in a journey"
    haystack = " ".join(str(task.get(k) or "") for k in ("kind", "target", "title", "acceptance", "source_ref")).lower()
    if any(token in haystack for token in AUTO_VERIFY_HUMAN_REQUIRED_KINDS):
        return True, "task kind/title/target indicates UI/UX/frontend/journey work"
    for raw in task_write_set(task):
        path = raw.strip().lower().replace("\\", "/")
        if path.endswith(AUTO_VERIFY_HUMAN_REQUIRED_EXTENSIONS):
            return True, f"write_set touches browser UI file {raw!r}"
        if any(token in path for token in AUTO_VERIFY_HUMAN_REQUIRED_TOKENS):
            return True, f"write_set touches shared/auth/navigation file {raw!r}"
    return False, ""

_VERIFY_REQUIRED_WHEN_VERIFIED = (
    "DATA_CONTRACT_ROWS",
    "DATA_SETUP",
    "PERSISTED_DATA_OBSERVED",
    "FLOWS_TESTED",
    "EVIDENCE",
)

_PRODUCTION_OBSERVABILITY_FIELDS_WHEN_VERIFIED = (
    "NO_STUB_DATA_USED",
    "REAL_DATA_SOURCE",
    "HUMAN_REPRODUCTION",
    "BUTTONS_AND_CONTROLS_CHECKED",
    "RUNTIME_LOGS_CHECKED",
    "RANCHER_WORKER_LOGS_CHECKED",
    "RUNTIME_LOG_ERRORS",
    "LOG_EVIDENCE",
    "DOCKER_PORTS_ALLOCATED",
)



def _task_requires_human_visual(task_id: str) -> tuple[bool, str]:
    try:
        task = find_task(load_registry(), task_id)
    except Exception:
        return False, "registry_unavailable"
    if not task:
        return False, "task_not_found"
    risk = str(task.get("risk_level") or "").strip().lower()
    verify_mode = str(task.get("verify_mode") or "").strip().lower()
    if verify_mode == "human" or risk in {"medium", "high", "critical"}:
        return True, f"verify_mode={verify_mode or 'n/a'} risk_level={risk or 'n/a'}"
    if task.get("route") or task.get("screen_route") or task.get("journey_refs"):
        return True, "ui_or_journey_task"
    for raw in task.get("write_set") or []:
        path = (str(raw).replace("\\", "/").strip().lower())
        if not path.startswith("/"):
            path = "/" + path
        if any(hint in path for hint in SHARED_VISUAL_WRITE_SET_HINTS):
            return True, f"shared_visual_risk_write_set={raw}"
    return False, ""


def _heading_key_value(line: str) -> tuple[str, str] | None:
    match = HEADING_KEY_RE.match(line)
    if not match:
        return None
    key = match.group("key").strip()
    canonical = key.upper()
    if canonical not in MACHINE_HEADING_KEYS:
        return None
    return canonical, match.group("value").strip()

def _normalise_mcp_browser(value: str | None) -> str:
    raw = (value or "").strip().lower()
    raw = raw.replace("_", "-").replace(" ", "-")
    compact = raw.replace("-", "")
    if "agent360" in compact or raw in {"browser-mcp", "browsermcp", "browser-mcp-server"}:
        return "agent360-browser-mcp"
    # Agent360 is usually displayed by Claude Code as the MCP server name
    # `browser-mcp`; keep accepting that canonical runtime name.
    without_suffix = raw.replace("-mcp", "")
    if without_suffix == "browser":
        return "agent360-browser-mcp"
    if "chrome" in raw and "devtools" in raw:
        return "chrome-devtools"
    if "claude" in raw and "chrome" in raw:
        return "claude-in-chrome"
    return without_suffix



def _normalise_mcp_client(value: str | None) -> str:
    raw = (value or "").strip().lower().replace("_", "-").replace(" ", "-")
    if raw in {"dart", "dart-mcp", "dart-mcp-server", "dart-flutter", "dart-flutter-mcp"}:
        return "dart"
    if raw in {"flutter", "flutter-mcp", "flutter-mcp-server"}:
        return "flutter"
    if raw in {"flutter-driver", "flutterdriver", "integration-test", "integration-test-driver"}:
        return "flutter-driver"
    return raw


def _normalise_visual_method(value: str | None) -> str:
    raw = (value or "").strip().lower().replace("_", "-").replace(" ", "-")
    aliases = {
        "ios": "ios-simulator",
        "ios-sim": "ios-simulator",
        "android": "android-emulator",
        "android-device": "android-emulator",
        "physical": "physical-device",
        "phone": "device",
    }
    return aliases.get(raw, raw)


def _load_stack_profile_safe() -> dict[str, object]:
    if not _load_stack_profile:
        return {}
    try:
        return _load_stack_profile()
    except Exception:
        return {}


def _profile_value(profile: dict[str, object], dotted: str, default: object = "") -> object:
    if _stack_get_path:
        try:
            return _stack_get_path(profile, dotted, default)
        except Exception:
            return default
    cur: object = profile
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def _requires_flutter_mobile_verify(task_id: str) -> bool:
    profile = _load_stack_profile_safe()
    framework = str(_profile_value(profile, "frontend.framework", "") or "").strip().lower()
    language = str(_profile_value(profile, "frontend.language", "") or "").strip().lower()
    visual = _normalise_visual_method(str(_profile_value(profile, "verification.mobile.visual_check_method", "") or _profile_value(profile, "frontend.visual_check", "") or ""))
    mobile_client = _normalise_mcp_client(str(_profile_value(profile, "verification.mobile.mcp_client", "") or ""))
    task = _load_task_for_verify(task_id)
    task_text = ""
    if task:
        task_text = " ".join(str(task.get(k) or "") for k in ("kind", "target", "title", "acceptance", "route", "screen_route")).lower()
        task_text += " " + " ".join(str(x) for x in task.get("write_set") or []).lower()
    flutterish = framework == "flutter" or language == "dart" or mobile_client in VERIFY_MOBILE_MCP_ACCEPTED or "flutter" in task_text or ".dart" in task_text
    mobileish = visual in VERIFY_MOBILE_VISUAL_METHODS or any(token in task_text for token in ("simulator", "emulator", "device"))
    return bool(flutterish and mobileish)


def _missing_verified_field(value: str | None) -> bool:
    raw = (value or "").strip()
    if not raw:
        return True
    return raw.lower() in {"pending", "partial", "todo", "tbd", "unknown", "unavailable", "none", "n/a", "na", "-", "—"}


def _is_yes(value: str | None) -> bool:
    return (value or "").strip().lower() in {"yes", "true", "si", "sí", "human", "verified"}


def _is_clean_log_status(value: str | None) -> bool:
    raw = (value or "").strip().lower()
    return raw in {"clean", "yes", "no_errors", "no-errors", "pass", "passed"}


def _is_clean_or_not_applicable(value: str | None) -> bool:
    raw = (value or "").strip().lower()
    return _is_clean_log_status(raw) or raw.startswith("not_applicable:") or raw.startswith("no_rancher:") or raw.startswith("no_rancher_worker_declared")


def _affirmative(value: str | None) -> bool:
    raw = (value or "").strip().lower()
    return raw in {"yes", "true", "si", "sí", "ok", "passed", "pass"} or raw.startswith("yes:") or raw.startswith("ok:")


def _zero_errors(value: str | None) -> bool:
    raw = (value or "").strip().lower()
    if raw in {"0", "zero", "none", "no", "no_errors", "no errors", "clean"}:
        return True
    return bool(re.search(r"(^|\b)(0|zero)\s+(runtime\s+)?(log\s+)?errors?\b", raw))


def _has_unregistered_followup_candidate(text: str) -> bool:
    """Return True when a handoff says work needs FU but no FU id exists.

    In DAG-only flow, productive work outside the current TASK_ID must be a
    formal proposed FU before close. It must not remain as prose in validator,
    tester, debugger, verify-slice or screen/journey review sections.
    """
    if not FOLLOWUP_CANDIDATE_RE.search(text):
        return False
    if FOLLOWUP_ID_RE.search(text):
        return False
    if re.search(r"(?im)^\s*-?\s*FOLLOWUP_ID\s*:\s*FU-", text):
        return False
    return True


def _handoff_path(task_id: str) -> Path:
    # FW-024: per-slice files (handoff) live in workspace_root, which is the
    # per-TASK_ID worktree in pr-flow and the canonical repo in push-to-main.
    return _handoff_path_resolver(task_id)


def _canonical_section_name(raw: str) -> str:
    """Normalize agent-written handoff headings to the contract keys.

    Claude agents sometimes append cycle labels or use short headings, e.g.
    ``## validator`` and ``## validator (cycle 2)``. The contract should read
    the latest logical section, not fail on harmless heading decoration.
    """
    value = CYCLE_SUFFIX_RE.sub("", raw.strip().lower()).replace("_", " ")
    value = re.sub(r"\s+", " ", value).strip()
    compact = re.sub(r"[\s/_-]+", " ", value).strip()

    if compact.startswith("validator") or compact.startswith("validation"):
        return "validator review"
    if compact.startswith("tester") or compact.startswith("test run") or compact in {"tests", "test"}:
        return "tester run"
    if compact.startswith("verify slice") or compact.startswith("slice verifier"):
        return "verify-slice"
    if compact.startswith("verify journey"):
        return "verify-journey"
    if compact.startswith("revision debugger") or compact.startswith("revision debug"):
        return "revision-debugger"
    if compact.startswith("debugger") or compact.startswith("debug fix"):
        return "debugger fix"
    if "screen" in compact and "journey" in compact and "review" in compact:
        return "screen/journey review"
    return value




def _section_from_match(sec: re.Match[str]) -> str | None:
    name = _canonical_section_name(sec.group("title"))
    level = len(sec.group("hashes"))
    # H2 starts a new logical section even if this checker does not consume it
    # (e.g. Developer run). H3-H6 are often prose subheadings inside a section;
    # only promote them when they are known contract aliases.
    if level == 2 or name in CONTRACT_SECTION_NAMES:
        return name
    return None

def _display_path(path: Path) -> str:
    return workspace_relpath(path)


def _parse_sections(text: str) -> Dict[str, List[Tuple[str, str]]]:
    sections: Dict[str, List[Tuple[str, str]]] = {}
    current = "__preamble__"
    sections[current] = []
    for line in text.splitlines():
        heading_key = _heading_key_value(line)
        if heading_key:
            sections.setdefault(current, []).append(heading_key)
            continue
        sec = SECTION_RE.match(line)
        if sec:
            section_name = _section_from_match(sec)
            if section_name is None:
                continue
            current = section_name
            sections.setdefault(current, [])
            continue
        key = KEY_RE.match(line)
        if key:
            sections.setdefault(current, []).append((key.group("key"), key.group("value").strip()))
    return sections


def _section_order(text: str) -> List[Tuple[str, int]]:
    """Return canonical section names in file order with line numbers.

    Handoffs are append-only. A verified block must be newer than the
    latest debugger/validator/tester block; otherwise a prior verify may be
    stale after a fix/retest cycle.
    """
    order: List[Tuple[str, int]] = []
    for idx, line in enumerate(text.splitlines(), start=1):
        if _heading_key_value(line):
            continue
        sec = SECTION_RE.match(line)
        if sec:
            section_name = _section_from_match(sec)
            if section_name is not None:
                order.append((section_name, idx))
    return order


def _latest_section_line(order: List[Tuple[str, int]], name: str) -> int | None:
    wanted = name.lower()
    matches = [line for section, line in order if section == wanted]
    return matches[-1] if matches else None


def _latest(sections: Dict[str, List[Tuple[str, str]]], name: str) -> Dict[str, str]:
    """Return last key occurrence in a named section."""
    out: Dict[str, str] = {}
    for key, value in sections.get(name.lower(), []):
        out[key] = value
    return out


def _all_task_ids(sections: Dict[str, List[Tuple[str, str]]]) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for section, pairs in sections.items():
        for key, value in pairs:
            if key == "TASK_ID":
                found.append((section, value))
    return found


def validate(
    task_id: str,
    *,
    require_ready_for_close: bool,
    require_verify_slice: bool,
    require_screen_journey_review: bool = False,
    require_runtime_logs: bool = False,
    require_production_observability: bool = False,
) -> tuple[bool, list[str], dict[str, object]]:
    path = _handoff_path(task_id)
    errors: list[str] = []
    details: dict[str, object] = {"task_id": task_id, "handoff": _display_path(path)}
    if not path.exists():
        return False, [f"missing handoff: {_display_path(path)}"], details
    text = path.read_text(encoding="utf-8", errors="replace")
    sections = _parse_sections(text)
    order = _section_order(text)

    if _has_unregistered_followup_candidate(text):
        errors.append(
            "handoff contains followup_candidate/FOLLOWUP_REQUIRED=yes but no formal FOLLOWUP_ID; "
            "register it with ./scripts/register-followup-task.sh propose before close"
        )

    mismatches = [(sec, val) for sec, val in _all_task_ids(sections) if val and val != task_id and not val.startswith("<")]
    if mismatches:
        errors.append("handoff contains TASK_ID lines for another task: " + ", ".join(f"{sec}={val}" for sec, val in mismatches))

    validator = _latest(sections, "validator review")
    tester = _latest(sections, "tester run")
    verify = _latest(sections, "verify-slice")
    screen_review = _latest(sections, "screen/journey review")
    details["validator"] = validator
    details["tester"] = tester
    details["verify_slice"] = verify
    details["screen_journey_review"] = screen_review

    if require_ready_for_close:
        val_outcome = validator.get("OUTCOME")
        if not val_outcome:
            errors.append("missing Validator review OUTCOME line in handoff; chat trailer is not enough for closer")
        elif val_outcome not in VALIDATOR_OUTCOMES:
            errors.append(f"invalid Validator review OUTCOME={val_outcome!r}")
        elif val_outcome != "approved":
            errors.append(f"validator did not approve: OUTCOME={val_outcome}")

        tester_outcome = tester.get("OUTCOME")
        if not tester_outcome:
            errors.append("missing Tester run OUTCOME line in handoff; chat trailer is not enough for closer")
        elif tester_outcome not in TESTER_OUTCOMES:
            errors.append(f"invalid Tester run OUTCOME={tester_outcome!r}")
        elif tester_outcome != "pass":
            errors.append(f"tester did not pass: OUTCOME={tester_outcome}")

    if require_verify_slice:
        verify_outcome = verify.get("VERIFY_OUTCOME")
        if not verify:
            errors.append("missing ## verify-slice section in handoff")
        else:
            verify_tid = verify.get("TASK_ID")
            if not verify_tid:
                errors.append("missing verify-slice TASK_ID line in handoff")
            elif verify_tid != task_id and not verify_tid.startswith("<"):
                errors.append(f"verify-slice TASK_ID mismatch: {verify_tid} != {task_id}")
            if not verify_outcome:
                errors.append("missing verify-slice VERIFY_OUTCOME line in handoff")
            elif verify_outcome not in VERIFY_OUTCOMES:
                errors.append(f"invalid verify-slice VERIFY_OUTCOME={verify_outcome!r}")
            elif verify_outcome != "verified":
                errors.append(f"verify-slice not verified: VERIFY_OUTCOME={verify_outcome}")
            else:
                verify_mode = str(verify.get("VERIFY_MODE") or "human").strip().lower()
                if verify_mode == "auto":
                    risk = str(verify.get("RISK_LEVEL") or "low").strip().lower()
                    if risk != "low":
                        errors.append("auto verify-slice verified requires RISK_LEVEL: low")
                    requires_human, reason = _task_requires_human_browser_verify(_load_task_for_verify(task_id))
                    if requires_human:
                        errors.append(
                            "auto verify-slice is not allowed for UI/shared/auth/navigation/journey work; "
                            f"run /verify-slice with browser MCP. Reason: {reason}"
                        )
                    for key in ("DATA_CONTRACT_ROWS", "PERSISTED_DATA_OBSERVED", "FLOWS_TESTED", "EVIDENCE"):
                        if _missing_verified_field(verify.get(key)):
                            errors.append(f"missing auto verified verify-slice {key} line in handoff")
                    if require_runtime_logs or require_production_observability:
                        if not _is_yes(verify.get("REAL_USER_VERIFIED")):
                            errors.append("auto verify-slice must prove human-real reproduction: REAL_USER_VERIFIED must be yes")
                        if not _is_yes(verify.get("NO_STUB_DATA")):
                            errors.append("auto verify-slice must prove no stub/fake data: NO_STUB_DATA must be yes")
                        if not _is_clean_log_status(verify.get("ERROR_LOGS_STATUS")):
                            errors.append("auto verify-slice must prove clean logs: ERROR_LOGS_STATUS must be clean/no_errors")
                        if not _is_clean_or_not_applicable(verify.get("RANCHER_WORKER_LOGS_REVIEWED")):
                            errors.append("auto verify-slice must review Rancher worker logs or state not_applicable:<reason>")
                    if require_production_observability:
                        for key in _PRODUCTION_OBSERVABILITY_FIELDS_WHEN_VERIFIED:
                            if _missing_verified_field(verify.get(key)):
                                errors.append(f"missing auto production observability {key} line in handoff")
                        if not _is_yes(verify.get("NO_STUB_DATA_USED")):
                            errors.append("auto production observability requires NO_STUB_DATA_USED: yes")
                        if not _affirmative(verify.get("HUMAN_REPRODUCTION")):
                            errors.append("auto production observability requires HUMAN_REPRODUCTION: yes")
                        if not _is_clean_or_not_applicable(verify.get("BUTTONS_AND_CONTROLS_CHECKED")) and not _affirmative(verify.get("BUTTONS_AND_CONTROLS_CHECKED")):
                            errors.append("auto production observability requires BUTTONS_AND_CONTROLS_CHECKED: yes or not_applicable:<reason>")
                        if not _affirmative(verify.get("RUNTIME_LOGS_CHECKED")):
                            errors.append("auto production observability requires RUNTIME_LOGS_CHECKED: yes")
                        if not _is_clean_or_not_applicable(verify.get("RANCHER_WORKER_LOGS_CHECKED")):
                            errors.append("auto production observability requires RANCHER_WORKER_LOGS_CHECKED: yes or not_applicable:<reason>")
                        if not _zero_errors(verify.get("RUNTIME_LOG_ERRORS")):
                            errors.append("auto production observability requires RUNTIME_LOG_ERRORS: 0")
                        if not _is_clean_or_not_applicable(verify.get("DOCKER_PORTS_ALLOCATED")) and not _affirmative(verify.get("DOCKER_PORTS_ALLOCATED")):
                            errors.append("auto production observability requires DOCKER_PORTS_ALLOCATED: yes or not_applicable:<reason>")
                else:
                    if _requires_flutter_mobile_verify(task_id):
                        client = _normalise_mcp_client(verify.get("MCP_CLIENT"))
                        method = _normalise_visual_method(verify.get("VISUAL_CHECK_METHOD"))
                        browser = _normalise_mcp_browser(verify.get("MCP_BROWSER"))
                        if client not in VERIFY_MOBILE_MCP_ACCEPTED:
                            errors.append("verify-slice Flutter mobile requires accepted MCP_CLIENT: dart, flutter, or flutter-driver")
                        if method not in VERIFY_MOBILE_VISUAL_METHODS:
                            errors.append("verify-slice Flutter mobile requires VISUAL_CHECK_METHOD: simulator, emulator, or device")
                        if browser in VERIFY_BROWSER_ACCEPTED:
                            errors.append("verify-slice Flutter mobile must use Dart/Flutter MCP, not browser-only MCP; use MCP_CLIENT: dart|flutter|flutter-driver and MCP_BROWSER: not_applicable:flutter_mobile")
                        for key in ("DATA_CONTRACT_ROWS", "DATA_SETUP", "PERSISTED_DATA_OBSERVED", "FLOWS_TESTED", "EVIDENCE"):
                            if _missing_verified_field(verify.get(key)):
                                errors.append(f"missing verified mobile verify-slice {key} line in handoff")
                    else:
                        browser = _normalise_mcp_browser(verify.get("MCP_BROWSER"))
                        if browser not in VERIFY_BROWSER_ACCEPTED:
                            errors.append(
                                "verify-slice verified without accepted browser MCP: "
                                "MCP_BROWSER must be chrome-devtools, claude-in-chrome, or agent360-browser-mcp/browser-mcp"
                            )
                        for key in _VERIFY_REQUIRED_WHEN_VERIFIED:
                            if _missing_verified_field(verify.get(key)):
                                errors.append(f"missing verified verify-slice {key} line in handoff")
                    if require_runtime_logs or require_production_observability:
                        if not _is_yes(verify.get("REAL_USER_VERIFIED")):
                            errors.append("verify-slice must prove human-real reproduction: REAL_USER_VERIFIED must be yes")
                        if not _is_yes(verify.get("NO_STUB_DATA")):
                            errors.append("verify-slice must prove no stub/fake data: NO_STUB_DATA must be yes")
                        if not _is_clean_log_status(verify.get("ERROR_LOGS_STATUS")):
                            errors.append("verify-slice must prove clean logs: ERROR_LOGS_STATUS must be clean/no_errors")
                        if not _is_clean_or_not_applicable(verify.get("RANCHER_WORKER_LOGS_REVIEWED")):
                            errors.append("verify-slice must review Rancher worker logs or state not_applicable:<reason>")
                    if require_production_observability:
                        requires_human_ui, ui_reason = _task_requires_human_browser_verify(_load_task_for_verify(task_id))
                        if requires_human_ui and _missing_verified_field(verify.get("UI_ACTIONS_VERIFIED")):
                            errors.append(
                                "verify-slice must prove UI_ACTIONS_VERIFIED for human/UI work before closer"
                                + (f"; reason: {ui_reason}" if ui_reason else "")
                            )
                        for key in _PRODUCTION_OBSERVABILITY_FIELDS_WHEN_VERIFIED:
                            if _missing_verified_field(verify.get(key)):
                                errors.append(f"missing production observability {key} line in handoff")
                        if not _is_yes(verify.get("NO_STUB_DATA_USED")):
                            errors.append("production observability requires NO_STUB_DATA_USED: yes")
                        if not _affirmative(verify.get("HUMAN_REPRODUCTION")):
                            errors.append("production observability requires HUMAN_REPRODUCTION: yes")
                        if requires_human_ui:
                            if not _affirmative(verify.get("BUTTONS_AND_CONTROLS_CHECKED")):
                                errors.append("production observability requires BUTTONS_AND_CONTROLS_CHECKED: yes for UI/browser work")
                        elif not _is_clean_or_not_applicable(verify.get("BUTTONS_AND_CONTROLS_CHECKED")) and not _affirmative(verify.get("BUTTONS_AND_CONTROLS_CHECKED")):
                            errors.append("production observability requires BUTTONS_AND_CONTROLS_CHECKED: yes or not_applicable:<reason>")
                        if not _affirmative(verify.get("RUNTIME_LOGS_CHECKED")):
                            errors.append("production observability requires RUNTIME_LOGS_CHECKED: yes")
                        if not _is_clean_or_not_applicable(verify.get("RANCHER_WORKER_LOGS_CHECKED")):
                            errors.append("production observability requires RANCHER_WORKER_LOGS_CHECKED: yes or not_applicable:<reason>")
                        if not _zero_errors(verify.get("RUNTIME_LOG_ERRORS")):
                            errors.append("production observability requires RUNTIME_LOG_ERRORS: 0")
                        if not _is_clean_or_not_applicable(verify.get("DOCKER_PORTS_ALLOCATED")) and not _affirmative(verify.get("DOCKER_PORTS_ALLOCATED")):
                            errors.append("production observability requires DOCKER_PORTS_ALLOCATED: yes or not_applicable:<reason>")

            verify_line = _latest_section_line(order, "verify-slice")
            if verify_line is not None:
                for section_name, label in (
                    ("validator review", "Validator review"),
                    ("tester run", "Tester run"),
                    ("debugger fix", "Debugger fix"),
                    ("revision-debugger", "revision-debugger"),
                ):
                    latest_line = _latest_section_line(order, section_name)
                    if latest_line is not None and latest_line > verify_line:
                        errors.append(
                            f"stale verify-slice: latest {label} section at line {latest_line} "
                            f"is newer than verify-slice at line {verify_line}; rerun /verify-slice before closer"
                        )


    if require_screen_journey_review:
        if not screen_review:
            errors.append("missing ## Screen/Journey review section in handoff")
        else:
            review_tid = screen_review.get("TASK_ID")
            if not review_tid:
                errors.append("missing Screen/Journey review TASK_ID line in handoff")
            elif review_tid != task_id and not review_tid.startswith("<"):
                errors.append(f"Screen/Journey review TASK_ID mismatch: {review_tid} != {task_id}")
            review_outcome = screen_review.get("OUTCOME")
            if not review_outcome:
                errors.append("missing Screen/Journey review OUTCOME line in handoff")
            elif review_outcome not in SCREEN_JOURNEY_OUTCOMES:
                errors.append(f"invalid Screen/Journey review OUTCOME={review_outcome!r}")
            elif review_outcome != "approved":
                errors.append(f"screen/journey reviewer did not approve: OUTCOME={review_outcome}")
            verify_line = _latest_section_line(order, "verify-slice")
            review_line = _latest_section_line(order, "screen/journey review")
            if verify_line is not None and review_line is not None and review_line < verify_line:
                errors.append(
                    f"stale Screen/Journey review: review at line {review_line} is older than "
                    f"verify-slice at line {verify_line}; rerun screen-journey-reviewer"
                )
            for key in ("visual_contract_checked", "required_states_covered", "real_data_or_backend_used", "visual_evidence_present"):
                if key not in screen_review:
                    errors.append(f"missing Screen/Journey review {key} line in handoff")

    return not errors, errors, details


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate TASK_ID handoff before verify/close.")
    parser.add_argument("task_id")
    parser.add_argument("--require-ready-for-close", action="store_true", help="Require Validator review OUTCOME=approved and Tester run OUTCOME=pass.")
    parser.add_argument("--require-verify-slice", action="store_true", help="Require ## verify-slice with matching TASK_ID and VERIFY_OUTCOME=verified.")
    parser.add_argument("--require-screen-journey-review", action="store_true", help="Require ## Screen/Journey review with matching TASK_ID and OUTCOME=approved.")
    parser.add_argument("--require-runtime-logs", action="store_true", help="Require real-user/no-stub/log cleanliness fields in ## verify-slice.")
    parser.add_argument("--require-production-observability", action="store_true", help="Require full human-real + logs + Rancher/worker observability fields before closer.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    ok, errors, details = validate(
        args.task_id,
        require_ready_for_close=args.require_ready_for_close,
        require_verify_slice=args.require_verify_slice,
        require_screen_journey_review=args.require_screen_journey_review,
        require_runtime_logs=args.require_runtime_logs,
        require_production_observability=args.require_production_observability,
    )
    payload = {"ok": ok, "errors": errors, **details}
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if ok:
            print(f"Handoff contract OK — {args.task_id}")
        else:
            print(f"Handoff contract FAILED — {args.task_id}", file=sys.stderr)
            for err in errors:
                print(f"- {err}", file=sys.stderr)
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
