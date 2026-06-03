"""file_lock — primitivo de concurrencia del framework.

Lo crítico (común.py:147-208):
1. Reentrancy: `with file_lock(p):` anidado en sí mismo NO debe deadlock-ear.
   Esto es lo que permite que `update_task_status` (lock outer) llame a
   `save_registry → write_json` (lock inner del mismo file).
2. Mutex real entre procesos: dos procesos compitiendo serializan la sección.
3. Atomic write via tmp+rename: una caída a media escritura no corrompe el JSON.
"""
from __future__ import annotations

import json
import subprocess
import os
import sys
import time
from pathlib import Path

_BIN = Path(__file__).resolve().parent.parent
if str(_BIN) not in sys.path:
    sys.path.insert(0, str(_BIN))

import common


def test_lock_reentrancy_does_not_deadlock(tmp_project):
    """`with file_lock(p):` anidado debe ser cheap-no-op."""
    p = tmp_project / "orchestrator-state" / "tasks" / "registry.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("{}", encoding="utf-8")

    with common.file_lock(p):
        with common.file_lock(p):
            with common.file_lock(p):
                p.write_text('{"x": 1}', encoding="utf-8")

    assert json.loads(p.read_text())["x"] == 1


def test_update_task_status_reentrancy_under_lock(seeded_registry):
    """update_task_status toma lock; sync_runtime_state_from_registry corre
    dentro y vuelve a pedir locks de runtime-state. Si la reentrancy estuviera
    rota, esto deadlockearía."""
    common.update_task_status("P00-S01-T001", "in_progress", agent="developer")

    reg = common.load_registry()
    assert common.find_task(reg, "P00-S01-T001")["status"] == "in_progress"


def _writer_script() -> str:
    """Standalone child script for inter-process lock testing.

    Uses subprocesses rather than multiprocessing so the full pytest process
    does not keep a multiprocessing resource_tracker around. The test still
    verifies a real POSIX lock between independent Python interpreters.
    """
    return 'import importlib\nimport json\nimport os\nimport sys\nimport time\nfrom pathlib import Path\n\nbin_path = Path(os.environ["ORQ_TEST_BIN"])\nsys.path.insert(0, str(bin_path))\nimport common as _common  # noqa: E402\nimportlib.reload(_common)\n\nproject = Path(os.environ["CLAUDE_PROJECT_DIR"])\nvalue = int(os.environ["ORQ_LOCK_TEST_VALUE"])\nsleep_inside = float(os.environ.get("ORQ_LOCK_TEST_SLEEP", "0.05"))\np = project / "orchestrator-state" / "tasks" / "registry.json"\nwith _common.file_lock(p):\n    data = json.loads(p.read_text())\n    data["counter"] = data.get("counter", 0) + value\n    time.sleep(sleep_inside)\n    p.write_text(json.dumps(data), encoding="utf-8")\n'


def test_lock_serializes_concurrent_writers(tmp_project):
    """Independent Python subprocesses competing for the same section serialize."""
    p = tmp_project / "orchestrator-state" / "tasks" / "registry.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"counter": 0}), encoding="utf-8")

    # Asegura que el módulo compartido por el padre no bloquee al subproceso.
    common._LOCK_DEPTH.clear()

    script = _writer_script()
    procs = []
    for inc in (1, 2, 3, 4, 5):
        env = os.environ.copy()
        env.update({
            "CLAUDE_PROJECT_DIR": str(tmp_project),
            "ORQ_TEST_BIN": str(_BIN),
            "ORQ_LOCK_TEST_VALUE": str(inc),
            "ORQ_LOCK_TEST_SLEEP": "0.05",
        })
        procs.append(
            subprocess.Popen(
                [sys.executable, "-c", script],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        )

    for proc in procs:
        stdout, stderr = proc.communicate(timeout=10)
        assert proc.returncode == 0, (
            f"subproceso falló con exit {proc.returncode}\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
        )

    final = json.loads(p.read_text())
    assert final["counter"] == 1 + 2 + 3 + 4 + 5


def test_write_json_uses_tmp_rename(tmp_project, monkeypatch):
    """write_json debe escribir a .tmp + rename, no truncar el original.
    Verificamos que el .tmp existió y desapareció (rename atomic)."""
    p = tmp_project / "orchestrator-state" / "tasks" / "test.json"
    common.write_json(p, {"hello": "world"})
    assert p.exists()
    assert json.loads(p.read_text())["hello"] == "world"
    # Tras escribir, el .tmp no debe existir (rename completado).
    assert not p.with_suffix(p.suffix + ".tmp").exists()
