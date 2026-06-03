from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ALLOC = ROOT / ".claude" / "bin" / "allocate_slice_ports.py"


class SlicePortAllocatorTests(unittest.TestCase):
    def _copy_minimal_allocator_repo(self, repo: Path) -> None:
        (repo / ".claude" / "bin").mkdir(parents=True)
        for name in ["allocate_slice_ports.py", "stack_profile.py", "runtime_context.py"]:
            (repo / ".claude" / "bin" / name).write_text((ROOT / ".claude" / "bin" / name).read_text(encoding="utf-8"), encoding="utf-8")
        (repo / "docs" / "source-of-truth").mkdir(parents=True)
        (repo / "docs" / "source-of-truth" / "STACK_PROFILE.yaml").write_text(
            """
profile_version: stack-profile-v1
runtime:
  port_strategy: auto-per-slice
  port_scan_span: 20
  port_defaults:
    frontend: 3010
    backend: 8010
    db: none
  port_env:
    frontend: CLAUDE_FRONTEND_PORT
    backend: CLAUDE_BACKEND_PORT
""",
            encoding="utf-8",
        )

    def test_allocates_distinct_free_ports_and_reuses_for_same_task(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self._copy_minimal_allocator_repo(repo)
            cmd = [sys.executable, "-B", "-S", str(repo / ".claude/bin/allocate_slice_ports.py"), "--root", str(repo), "--task", "P01-S02-T003", "--json"]
            first = subprocess.run(cmd, text=True, capture_output=True, check=True)
            payload = json.loads(first.stdout)
            self.assertEqual(payload["compose_project_name"], "p01-s02-t003")
            self.assertIn("frontend", payload["ports"])
            self.assertTrue((repo / "orchestrator-state" / "dev-ports" / "p01-s02-t003.env").exists())
            second = subprocess.run(cmd, text=True, capture_output=True, check=True)
            payload2 = json.loads(second.stdout)
            self.assertTrue(payload2["reused_existing_env"])
            self.assertEqual(payload["ports"], payload2["ports"])

    def test_allocator_checks_occupied_ports_before_assignment(self) -> None:
        with tempfile.TemporaryDirectory() as td, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            repo = Path(td)
            self._copy_minimal_allocator_repo(repo)
            sock.bind(("0.0.0.0", 3010))
            sock.listen(1)
            proc = subprocess.run(
                [sys.executable, "-B", "-S", str(repo / ".claude/bin/allocate_slice_ports.py"), "--root", str(repo), "--task", "P02-S01-T001", "--json"],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(proc.stdout)
            self.assertNotEqual(payload["ports"]["frontend"]["port"], 3010)
            self.assertGreaterEqual(payload["ports"]["frontend"]["port"], 3010)

    def test_next_wave_terminal_command_allocates_ports(self) -> None:
        sys.path.insert(0, str(ROOT / ".claude" / "bin"))
        import next_wave  # type: ignore

        cmd = next_wave._terminal_command("P01-S02-T003")
        self.assertIn("allocate_slice_ports.py", cmd)
        self.assertIn("CLAUDE_FRONTEND_PORT", cmd)
        parsed = subprocess.run(["bash", "-n", "-c", cmd], text=True, capture_output=True, timeout=10)
        self.assertEqual(parsed.returncode, 0, parsed.stderr)

    def test_allocator_uses_profile_compose_project_template_double_braces(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self._copy_minimal_allocator_repo(repo)
            profile = repo / "docs" / "source-of-truth" / "STACK_PROFILE.yaml"
            profile.write_text(profile.read_text(encoding="utf-8") + "\nverification:\n  docker:\n    compose_project_template: skinsync_{{task_slug}}\n", encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, "-B", "-S", str(repo / ".claude/bin/allocate_slice_ports.py"), "--root", str(repo), "--task", "P00-S02-T003", "--json"],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(payload["compose_project_name"], "skinsync_p00-s02-t003")
            self.assertTrue((repo / "orchestrator-state" / "dev-ports" / "p00-s02-t003.env").exists())

    def test_allocator_replaces_stale_existing_env_when_port_now_occupied(self) -> None:
        with tempfile.TemporaryDirectory() as td, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            repo = Path(td)
            self._copy_minimal_allocator_repo(repo)
            ports = repo / "orchestrator-state" / "dev-ports"
            ports.mkdir(parents=True)
            env = ports / "p02-s01-t002.env"
            env.write_text("export CLAUDE_ACTIVE_TASK_ID='P02-S01-T002'\nexport COMPOSE_PROJECT_NAME='p02-s01-t002'\nexport CLAUDE_COMPOSE_PROJECT_NAME='p02-s01-t002'\nexport CLAUDE_FRONTEND_PORT='3010'\nexport CLAUDE_BACKEND_PORT='8010'\n", encoding="utf-8")
            sock.bind(("0.0.0.0", 3010))
            sock.listen(1)
            proc = subprocess.run(
                [sys.executable, "-B", "-S", str(repo / ".claude/bin/allocate_slice_ports.py"), "--root", str(repo), "--task", "P02-S01-T002", "--json"],
                text=True,
                capture_output=True,
                check=True,
            )
            payload = json.loads(proc.stdout)
            self.assertFalse(payload["reused_existing_env"])
            self.assertNotEqual(payload["ports"]["frontend"]["port"], 3010)


if __name__ == "__main__":
    unittest.main()
