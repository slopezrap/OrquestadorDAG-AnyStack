from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PY = ROOT / "scripts" / "cleanup_merged_pr_branches.py"
SCRIPT_SH = ROOT / "scripts" / "cleanup-merged-pr-branches.sh"

spec = importlib.util.spec_from_file_location("cleanup_merged_pr_branches", SCRIPT_PY)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def test_branch_safety_accepts_only_task_scoped_branches():
    assert mod.branch_is_task_scoped("dev/P04-S01-T008")
    assert mod.branch_is_task_scoped("feature/P04-S01-T008-ui")
    assert mod.branch_is_task_scoped("fix/auth-P04-S01-T008")
    assert not mod.branch_is_task_scoped("main")
    assert not mod.branch_is_task_scoped("develop")
    assert not mod.branch_is_task_scoped("dev/random-cleanup")
    assert not mod.branch_is_task_scoped("release/P04-S01-T008")


def test_choose_pr_deletes_only_merged_branch_with_matching_head_sha():
    prs = [{
        "number": 51,
        "state": "MERGED",
        "headRefName": "dev/P04-S01-T008",
        "headRefOid": "abc123",
        "baseRefName": "main",
        "url": "https://example.invalid/pr/51",
    }]
    decision = mod.choose_pr_decision("dev/P04-S01-T008", "abc123", prs, "main")
    assert decision.action == "delete"
    assert decision.pr_number == "51"


def test_choose_pr_skips_if_branch_moved_after_merge():
    prs = [{
        "number": 51,
        "state": "MERGED",
        "headRefName": "dev/P04-S01-T008",
        "headRefOid": "abc123",
        "baseRefName": "main",
        "url": "https://example.invalid/pr/51",
    }]
    decision = mod.choose_pr_decision("dev/P04-S01-T008", "def456", prs, "main")
    assert decision.action == "skip"
    assert decision.reason == "branch_moved_after_pr_merge"


def test_choose_pr_skips_open_or_closed_unmerged_prs():
    prs = [{
        "number": 52,
        "state": "OPEN",
        "headRefName": "dev/P04-S01-T009",
        "headRefOid": "abc123",
        "baseRefName": "main",
        "url": "https://example.invalid/pr/52",
    }]
    decision = mod.choose_pr_decision("dev/P04-S01-T009", "abc123", prs, "main")
    assert decision.action == "skip"
    assert decision.reason.startswith("pr_not_merged")


def test_choose_pr_skips_ambiguous_or_wrong_head_branch():
    prs = [{
        "number": 53,
        "state": "MERGED",
        "headRefName": "dev/P04-S01-T010-other",
        "headRefOid": "abc123",
        "baseRefName": "main",
        "url": "https://example.invalid/pr/53",
    }]
    decision = mod.choose_pr_decision("dev/P04-S01-T010", "abc123", prs, "main")
    assert decision.action == "skip"
    assert decision.reason == "no_pr_for_head_branch"


def test_cli_quiet_noops_outside_git(tmp_path):
    result = subprocess.run(["bash", str(SCRIPT_SH), "--apply", "--quiet"], cwd=tmp_path, text=True, capture_output=True, check=False, timeout=20)
    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_next_wave_invokes_safe_merged_remote_branch_cleanup():
    text = (ROOT / "scripts" / "next-wave.sh").read_text(encoding="utf-8")
    assert "cleanup-merged-pr-branches.sh" in text
    assert "CLAUDE_CLEAN_MERGED_PR_BRANCHES" in text


def _run(cmd: list[str], cwd: Path, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True, check=True, timeout=30)


def _git(cmd: list[str], cwd: Path) -> str:
    return _run(["git", *cmd], cwd).stdout.strip()


def _init_repo_with_origin(tmp_path: Path) -> Path:
    origin = tmp_path / "origin.git"
    repo = tmp_path / "repo"
    _run(["git", "init", "--bare", str(origin)], tmp_path)
    _run(["git", "clone", str(origin), str(repo)], tmp_path)
    _git(["checkout", "-b", "main"], repo)
    _git(["config", "user.email", "test@example.com"], repo)
    _git(["config", "user.name", "Test User"], repo)
    (repo / "README.md").write_text("init\n", encoding="utf-8")
    _git(["add", "README.md"], repo)
    _git(["commit", "-m", "init"], repo)
    _git(["push", "-u", "origin", "main"], repo)
    return repo


def _make_branch(repo: Path, branch: str, filename: str) -> None:
    _git(["checkout", "-b", branch, "main"], repo)
    (repo / filename).write_text(f"{branch}\n", encoding="utf-8")
    _git(["add", filename], repo)
    _git(["commit", "-m", f"feat: {branch}"], repo)
    _git(["push", "-u", "origin", branch], repo)
    _git(["checkout", "main"], repo)


def _write_fake_gh(bin_dir: Path, sha_by_branch: dict[str, str]) -> None:
    gh = bin_dir / "gh"
    gh_payload = json.dumps(sha_by_branch)
    gh.write_text(
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import sys\n"
        f"sha_by_branch = json.loads({gh_payload!r})\n"
        "args = sys.argv[1:]\n"
        "if args and args[0] == '--version':\n"
        "    print('gh version 9.9.9')\n"
        "    raise SystemExit(0)\n"
        "if args[:2] == ['pr', 'list']:\n"
        "    branch = ''\n"
        "    for idx, arg in enumerate(args):\n"
        "        if arg == '--head' and idx + 1 < len(args):\n"
        "            branch = args[idx + 1]\n"
        "            break\n"
        "    if branch == 'dev/P00-S01-T001':\n"
        "        print(json.dumps([{'number': 101, 'state': 'MERGED', 'headRefName': branch, 'headRefOid': sha_by_branch.get(branch, ''), 'baseRefName': 'main', 'mergedAt': '2026-05-14T00:00:00Z'}]))\n"
        "    elif branch == 'dev/P00-S01-T002':\n"
        "        print(json.dumps([{'number': 102, 'state': 'OPEN', 'headRefName': branch, 'headRefOid': sha_by_branch.get(branch, ''), 'baseRefName': 'main', 'mergedAt': None}]))\n"
        "    elif branch == 'dev/P00-S01-T003':\n"
        "        print(json.dumps([{'number': 103, 'state': 'MERGED', 'headRefName': branch, 'headRefOid': '0' * 40, 'baseRefName': 'main', 'mergedAt': '2026-05-14T00:00:00Z'}]))\n"
        "    else:\n"
        "        print('[]')\n"
        "    raise SystemExit(0)\n"
        "print('unexpected gh call', args, file=sys.stderr)\n"
        "raise SystemExit(2)\n",
        encoding="utf-8",
    )
    gh.chmod(0o755)


def test_cli_deletes_only_safe_merged_remote_branch(tmp_path, monkeypatch):
    repo = _init_repo_with_origin(tmp_path)
    _make_branch(repo, "dev/P00-S01-T001", "one.txt")
    _make_branch(repo, "dev/P00-S01-T002", "two.txt")
    _make_branch(repo, "dev/P00-S01-T003", "three.txt")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    sha_by_branch = {
        name: _git(["rev-parse", f"refs/remotes/origin/{name}"], repo)
        for name in ["dev/P00-S01-T001", "dev/P00-S01-T002", "dev/P00-S01-T003"]
    }
    _write_fake_gh(bin_dir, sha_by_branch)
    env = dict(**os.environ)
    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"

    result = _run(["bash", str(SCRIPT_SH), "--apply", "--verbose"], repo, env=env)
    combined = result.stdout + result.stderr
    assert "deleted merged PR branch: origin/dev/P00-S01-T001 PR #101" in combined
    assert "skip pr_not_merged_open: origin/dev/P00-S01-T002" in combined
    assert "skip branch_moved_after_pr_merge: origin/dev/P00-S01-T003" in combined
    remote_refs = _git(["ls-remote", "--heads", "origin"], repo)
    assert "refs/heads/dev/P00-S01-T001" not in remote_refs
    assert "refs/heads/dev/P00-S01-T002" in remote_refs
    assert "refs/heads/dev/P00-S01-T003" in remote_refs
