#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
APP = HERE / "app.py"
FIXTURE = HERE / "fixtures" / "real_user_payload.json"
LOG_CHECKER = ROOT / ".claude" / "bin" / "check_runtime_logs.py"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def request(method: str, url: str, payload: dict[str, object] | None = None) -> tuple[int, str, dict[str, object] | None]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            text = resp.read().decode("utf-8")
            parsed = json.loads(text) if resp.headers.get_content_type() == "application/json" else None
            return resp.status, text, parsed
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8")
        parsed = json.loads(text) if text.startswith("{") else None
        return exc.code, text, parsed


def wait_for_health(base: str, timeout_s: float = 10.0) -> None:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            status, _, payload = request("GET", base + "/health")
            if status == 200 and payload and payload.get("ok") is True:
                return
        except Exception:
            pass
        time.sleep(0.1)
    raise RuntimeError("golden app did not become healthy")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Golden Real App E2E verification")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    port = args.port or free_port()
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="orq-golden-app-") as tmp:
        work = Path(tmp)
        db = work / "golden.sqlite3"
        log = work / "golden.log"
        env = os.environ.copy()
        env.update({"GOLDEN_DB": str(db), "GOLDEN_LOG": str(log), "GOLDEN_PORT": str(port), "PYTHONDONTWRITEBYTECODE": "1"})
        proc = subprocess.Popen([sys.executable, "-B", "-S", str(APP)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        try:
            base = f"http://127.0.0.1:{port}"
            wait_for_health(base)
            status, html, _ = request("GET", base + "/")
            if status != 200 or "Create real record" not in html or "Refresh list" not in html:
                raise AssertionError("human UI controls not present")
            status, _, created = request("POST", base + "/api/v1/items", fixture)
            if status != 201 or not created or "item" not in created:
                raise AssertionError(f"create failed: {status} {created}")
            item = created["item"]  # type: ignore[index]
            item_id = int(item["id"])  # type: ignore[index]
            if item["title"] != fixture["title"] or item["owner"] != fixture["owner"]:  # type: ignore[index]
                raise AssertionError("created item does not match provided fixture")
            status, _, invalid = request("POST", base + "/api/v1/items", {"title": "", "owner": fixture["owner"]})
            if status != 400 or not invalid or invalid.get("code") != "DOMAIN_VALIDATION_FAILED":
                raise AssertionError("DR-001 validation did not reject empty title")
            status, _, updated = request("PATCH", base + f"/api/v1/items/{item_id}", {"status": "approved"})
            if status != 200 or not updated or updated["item"]["status"] != "approved":  # type: ignore[index]
                raise AssertionError("DR-002 state transition failed")
            with sqlite3.connect(db) as conn:
                row = conn.execute("SELECT title, owner, status FROM items WHERE id=?", (item_id,)).fetchone()
            if row != (fixture["title"], fixture["owner"], "approved"):
                raise AssertionError(f"SQLite persistence mismatch: {row}")
            log_result = subprocess.run([sys.executable, "-B", "-S", str(LOG_CHECKER), "--task", "P01-S01-T001", "--scan-file", str(log), "--strict", "--json"], text=True, capture_output=True, timeout=20, check=False)
            if log_result.returncode != 0:
                raise AssertionError("runtime logs are not clean: " + log_result.stdout + log_result.stderr)
            log_payload = json.loads(log_result.stdout)
            result = {
                "status": "pass",
                "real_data_source": str(FIXTURE.relative_to(ROOT)),
                "ui_controls_checked": ["Create real record", "Refresh list"],
                "domain_rules_verified": ["DR-001", "DR-002"],
                "runtime_logs_clean": log_payload["runtime_logs_clean"],
                "findings_count": log_payload["findings_count"],
            }
            print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else "GOLDEN_E2E: PASS")
            return 0
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
