from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AGENTS = ROOT / ".claude" / "agents"


def _frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    data: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"')
    return data


def test_agent_prompts_keep_canonical_trailer_as_final_section() -> None:
    for path in sorted(AGENTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        assert "## Production DAG trailer vocabulary" in text, path
        tail = text.split("## Production DAG trailer vocabulary", 1)[1]
        headings_after = [line for line in tail.splitlines()[1:] if line.startswith("#")]
        assert headings_after == [], f"{path} has sections after canonical trailer: {headings_after}"


def test_agent_prompts_have_layout_discipline_and_no_nested_root_split() -> None:
    for path in sorted(AGENTS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        assert "## Prompt layout discipline" in text, path
        assert "### Root split obligatorio" not in text, path
        assert "### Flutter mobile verify-slice" not in text, path


def test_validator_remains_info_only_in_frontmatter() -> None:
    text = (AGENTS / "validator.md").read_text(encoding="utf-8")
    fm = _frontmatter(text)
    assert "close-task" not in fm.get("skills", "")
    assert "write-handoff" in fm.get("skills", "")
    assert "does not close or mutate task.status" in fm.get("description", "")


def test_mobile_verifier_wording_is_browser_and_mobile() -> None:
    verifier = (AGENTS / "slice-verifier.md").read_text(encoding="utf-8")
    assert "browser/mobile MCP verification gate" in _frontmatter(verifier).get("description", "")
    assert "## Visual MCP obligatorio: web o mobile" in verifier
    assert "MCP_CLIENT: dart" in verifier
    assert "VISUAL_CHECK_METHOD: simulator" in verifier

    closer = (AGENTS / "closer.md").read_text(encoding="utf-8")
    assert "## Mobile verification evidence gate" in closer
    assert "MCP_CLIENT: dart" in closer
