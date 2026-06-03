from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CHECKER = ROOT / ".claude" / "bin" / "check_runtime_logs.py"
WRAPPER = ROOT / "scripts" / "check-runtime-logs.sh"


class RuntimeLogCheckerTests(unittest.TestCase):
    def run_checker(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", "-S", str(CHECKER), *args],
            text=True,
            capture_output=True,
            check=False,
            timeout=20,
        )

    def test_clean_logs_pass_and_return_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            (logs / "app.log").write_text("server started\n0 errors\nrequest ok\n", encoding="utf-8")
            result = self.run_checker("--task", "P01-S02-T003", "--log-dir", str(logs), "--strict", "--json")
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["runtime_logs_clean"])
            self.assertEqual(payload["findings_count"], 0)

    def test_runtime_error_fails_strict_scan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            (logs / "worker.log").write_text("Traceback: worker crashed\n", encoding="utf-8")
            result = self.run_checker("--task", "P01-S02-T003", "--log-dir", str(logs), "--strict", "--json")
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["runtime_logs_clean"])
            self.assertGreaterEqual(payload["findings_count"], 1)

    def test_empty_strict_logs_fail_unless_explicitly_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "empty"
            logs.mkdir()
            result = self.run_checker("--task", "P01-S02-T003", "--log-dir", str(logs), "--strict", "--json")
            self.assertEqual(result.returncode, 2)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "no_logs")

            allowed = self.run_checker("--task", "P01-S02-T003", "--log-dir", str(logs), "--allow-empty", "--strict", "--json")
            self.assertEqual(allowed.returncode, 0, allowed.stderr + allowed.stdout)
            payload = json.loads(allowed.stdout)
            self.assertTrue(payload["runtime_logs_clean"])

    def test_wrapper_collects_dev_logs_and_uses_task_compose_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            (repo / ".claude" / "bin").mkdir(parents=True)
            (repo / "scripts").mkdir(parents=True)
            (repo / "orchestrator-state" / "dev-logs").mkdir(parents=True)
            shutil.copy2(CHECKER, repo / ".claude" / "bin" / "check_runtime_logs.py")
            shutil.copy2(ROOT / ".claude" / "bin" / "stack_profile.py", repo / ".claude" / "bin" / "stack_profile.py")
            shutil.copy2(ROOT / ".claude" / "bin" / "allocate_slice_ports.py", repo / ".claude" / "bin" / "allocate_slice_ports.py")
            shutil.copy2(ROOT / ".claude" / "bin" / "runtime_context.py", repo / ".claude" / "bin" / "runtime_context.py")
            shutil.copy2(WRAPPER, repo / "scripts" / "check-runtime-logs.sh")
            os.chmod(repo / "scripts" / "check-runtime-logs.sh", 0o755)
            (repo / "scripts" / "dev-restart.profile.sh").write_text("# neutral profile\n", encoding="utf-8")
            (repo / "orchestrator-state" / "dev-logs" / "app.log").write_text("worker idle\n0 errors\n", encoding="utf-8")
            result = subprocess.run(
                ["bash", "scripts/check-runtime-logs.sh", "--task", "P01-S02-T003", "--mode", "check", "--strict", "--json"],
                cwd=repo,
                text=True,
                capture_output=True,
                check=False,
                timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            payload = json.loads(result.stdout)
            self.assertTrue(payload["runtime_logs_clean"])
            self.assertTrue((repo / "orchestrator-state" / "tasks" / "evidence" / "P01-S02-T003" / "runtime-logs" / "runtime-log-check.json").exists())


if __name__ == "__main__":
    unittest.main()
