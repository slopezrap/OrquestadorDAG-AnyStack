from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def test_stop_hook_resolves_canonical_root_from_sibling_worktree(tmp_path: Path) -> None:
    settings = json.loads((ROOT / ".claude/settings.json").read_text(encoding="utf-8"))
    command = settings["hooks"]["Stop"][0]["hooks"][0]["command"]
    canonical = tmp_path / "MaSer-Beauty"
    worktree = tmp_path / "MaSer-Beauty-worktrees" / "P00-S04-T001"
    (canonical / ".claude" / "bin").mkdir(parents=True)
    worktree.mkdir(parents=True)
    hook = canonical / ".claude" / "bin" / "hook_finalize_deferred_cleanup.py"
    hook.write_text('import os; print("ROOT=" + os.environ.get("CLAUDE_ORCHESTRATOR_ROOT", ""))\n', encoding="utf-8")
    env = os.environ.copy()
    env.pop("CLAUDE_ORCHESTRATOR_ROOT", None)
    env["CLAUDE_PROJECT_DIR"] = str(worktree)
    result = subprocess.run(command, shell=True, cwd=worktree, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
    assert result.returncode == 0, result.stderr
    assert f"ROOT={canonical}" in result.stdout
