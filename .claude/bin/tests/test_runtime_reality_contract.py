from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class RuntimeRealityContractTests(unittest.TestCase):
    def test_all_subagents_use_1m_aliases_and_do_not_set_ultracode_frontmatter(self) -> None:
        for path in (ROOT / ".claude" / "agents").glob("*.md"):
            text = path.read_text(encoding="utf-8")
            self.assertNotRegex(text, r"(?m)^model:\s+(sonnet|opus)\s*$", path.name)
            self.assertNotRegex(text, r"(?m)^effort:\s*ultracode\s*$", path.name)
        claude_md = (ROOT / ".claude" / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("/effort ultracode", claude_md)
        self.assertIn("sonnet[1m]", claude_md)

    def test_verify_and_closer_require_real_data_human_actions_and_logs(self) -> None:
        verify = (ROOT / ".claude" / "commands" / "verify-slice.md").read_text(encoding="utf-8")
        closer = (ROOT / ".claude" / "commands" / "closer.md").read_text(encoding="utf-8")
        combined = verify + "\n" + closer
        for needle in [
            "docker compose -p <compose_project>",
            "DOCKER_PORTS_ALLOCATED",
            "check-runtime-logs.sh --task <TASK_ID> --mode check",
            "RANCHER_WORKER_LOGS_REVIEWED",
            "REAL_USER_VERIFIED",
            "NO_STUB_DATA",
            "NO_STUB_DATA_USED",
            "BUTTONS_AND_CONTROLS_CHECKED",
            "RUNTIME_LOG_ERRORS",
            "LLM_DOCUMENT_EXTRACTION",
        ]:
            self.assertIn(needle, combined)

    def test_stack_profiles_declare_observability_and_rancher_logs(self) -> None:
        for path in (ROOT / "docs" / "templates").glob("*/STACK_PROFILE.template.yaml"):
            text = path.read_text(encoding="utf-8")
            self.assertIn("verification:", text, path.name)
            self.assertIn("compose_project_template", text, path.name)
            self.assertIn("rancher:", text, path.name)
            self.assertIn("worker_logs_cmd", text, path.name)
            self.assertIn("observability:", text, path.name)
            self.assertIn("port_defaults:", text, path.name)
            self.assertIn("CLAUDE_FRONTEND_PORT", text, path.name)

    def test_next_wave_uses_task_slug_for_compose_project(self) -> None:
        sys.path.insert(0, str(ROOT / ".claude" / "bin"))
        import next_wave  # type: ignore

        cmd = next_wave._terminal_command("P01-S02-T003")
        self.assertIn("runtime_context.py", cmd)
        self.assertIn("COMPOSE_PROJECT_NAME", cmd)
        self.assertIn("P01-S02-T003", cmd)
        self.assertIn("CLAUDE_COMPOSE_PROJECT_NAME", cmd)
        self.assertIn("allocate_slice_ports.py", cmd)
        self.assertIn("CLAUDE_FRONTEND_PORT", cmd)
        parsed = subprocess.run(["bash", "-n", "-c", cmd], text=True, capture_output=True, timeout=10)
        self.assertEqual(parsed.returncode, 0, parsed.stderr)

    def test_no_shared_docker_stack_docs_remain(self) -> None:
        targets = [
            ROOT / "README.md",
            ROOT / "CHEATSHEET.md",
            ROOT / "docs" / "guides" / "CHEATSHEET.md",
            ROOT / "orquestador-explicado" / "scripts-git.html",
        ]
        stale = re.compile(r"Stack Docker compartido|todos los worktrees paralelos comparten|comparten el mismo stack Docker", re.I)
        for path in targets:
            self.assertIsNone(stale.search(path.read_text(encoding="utf-8")), str(path))


if __name__ == "__main__":
    unittest.main()
