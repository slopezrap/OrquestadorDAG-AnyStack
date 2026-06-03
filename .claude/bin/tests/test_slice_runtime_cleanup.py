from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "cleanup-slice-runtime.sh"


def test_cleanup_slice_runtime_dry_run_without_compose_is_safe(tmp_path: Path) -> None:
    result = subprocess.run(
        ["bash", str(SCRIPT), "--task", "P01-S02-T003", "--dry-run", "--json"],
        cwd=tmp_path,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["task_id"] == "P01-S02-T003"
    assert payload["compose_project"] == "p01-s02-t003"
    assert payload["applied"] is False
    assert payload["runtime_cleaned"] == "yes"
    assert payload["docker_runtime_cleaned"].startswith("not_applicable:")


def test_cleanup_slice_runtime_releases_per_slice_port_files(tmp_path: Path) -> None:
    port_dir = tmp_path / "orchestrator-state" / "dev-ports"
    port_dir.mkdir(parents=True)
    (port_dir / "p01-s02-t003.env").write_text("CLAUDE_FRONTEND_PORT=3100\n", encoding="utf-8")
    (port_dir / "p01-s02-t003.json").write_text("{}\n", encoding="utf-8")
    result = subprocess.run(
        ["bash", str(SCRIPT), "--task", "P01-S02-T003", "--apply", "--json"],
        cwd=tmp_path,
        env={"CLAUDE_ORCHESTRATOR_ROOT": str(tmp_path), "PATH": "/usr/bin:/bin"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["runtime_cleaned"] == "yes"
    assert payload["dev_ports_released"] == "yes"
    assert not (port_dir / "p01-s02-t003.env").exists()
    assert not (port_dir / "p01-s02-t003.json").exists()


def test_cleanup_slice_runtime_never_uses_global_docker_prune() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "docker system prune" not in text
    assert "docker image prune" not in text
    assert "docker volume prune" not in text
    assert "--rmi all" not in text.split("Usage:", 1)[0]


def _copy_runtime_helpers(repo: Path) -> None:
    (repo / ".claude" / "bin").mkdir(parents=True)
    for name in ["stack_profile.py", "runtime_context.py"]:
        (repo / ".claude" / "bin" / name).write_text((ROOT / ".claude" / "bin" / name).read_text(encoding="utf-8"), encoding="utf-8")


def test_cleanup_resolves_double_brace_project_and_profile_compose_file(tmp_path: Path) -> None:
    _copy_runtime_helpers(tmp_path)
    compose = tmp_path / "infra" / "compose" / "docker-compose.dev.yml"
    compose.parent.mkdir(parents=True)
    compose.write_text("services:\n  db:\n    image: postgres:16\n", encoding="utf-8")
    sot = tmp_path / "docs" / "source-of-truth"
    sot.mkdir(parents=True)
    (sot / "STACK_PROFILE.yaml").write_text(
        """
profile_version: stack-profile-v1
verification:
  docker:
    compose_project_template: "skinsync_{{task_slug}}"
    compose_file: "infra/compose/docker-compose.dev.yml"
    cleanup_remove_images: "none"
""",
        encoding="utf-8",
    )
    fakebin = tmp_path / "fakebin"
    fakebin.mkdir()
    log = tmp_path / "docker.log"
    docker = fakebin / "docker"
    docker.write_text(
        f"""#!/usr/bin/env bash
printf '%s\\n' "$*" >> {str(log)!r}
case "$1" in
  compose) exit 0 ;;
  ps) exit 0 ;;
  network) exit 0 ;;
  volume) exit 0 ;;
  images) exit 0 ;;
  rmi|rm) exit 0 ;;
  *) exit 0 ;;
esac
""",
        encoding="utf-8",
    )
    docker.chmod(0o755)
    env = {
        "CLAUDE_ORCHESTRATOR_ROOT": str(tmp_path),
        "CLAUDE_WORKTREE_ROOT": str(tmp_path),
        "PATH": f"{fakebin}:/usr/bin:/bin",
    }
    result = subprocess.run(
        ["bash", str(SCRIPT), "--task", "P00-S02-T003", "--apply", "--strict", "--json"],
        cwd=tmp_path,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["runtime_cleaned"] == "yes"
    assert payload["compose_project"] == "skinsync_p00-s02-t003"
    docker_log = log.read_text(encoding="utf-8")
    assert "compose -p skinsync_p00-s02-t003 -f infra/compose/docker-compose.dev.yml down -v --remove-orphans" in docker_log
    assert "skinsync_{" not in docker_log


def test_cleanup_releases_prefixed_and_legacy_dev_port_files(tmp_path: Path) -> None:
    _copy_runtime_helpers(tmp_path)
    sot = tmp_path / "docs" / "source-of-truth"
    sot.mkdir(parents=True)
    (sot / "STACK_PROFILE.yaml").write_text(
        """
profile_version: stack-profile-v1
verification:
  docker:
    compose_project_template: "skinsync_{{task_slug}}"
    compose_file: none
""",
        encoding="utf-8",
    )
    port_dir = tmp_path / "orchestrator-state" / "dev-ports"
    port_dir.mkdir(parents=True)
    for stem in ["skinsync_p00-s02-t003", "p00-s02-t003"]:
        (port_dir / f"{stem}.env").write_text("export CLAUDE_ACTIVE_TASK_ID='P00-S02-T003'\n", encoding="utf-8")
        (port_dir / f"{stem}.json").write_text("{}\n", encoding="utf-8")
    result = subprocess.run(
        ["bash", str(SCRIPT), "--task", "P00-S02-T003", "--apply", "--json"],
        cwd=tmp_path,
        env={"CLAUDE_ORCHESTRATOR_ROOT": str(tmp_path), "CLAUDE_WORKTREE_ROOT": str(tmp_path), "PATH": "/usr/bin:/bin"},
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["compose_project"] == "skinsync_p00-s02-t003"
    assert payload["dev_ports_released"] == "yes"
    assert not any(port_dir.glob("*.env"))
    assert not any(port_dir.glob("*.json"))
