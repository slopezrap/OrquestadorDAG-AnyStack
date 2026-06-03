#!/usr/bin/env python3
"""Scan runtime logs captured during verify-slice.

The checker is stack-agnostic: scripts/check-runtime-logs.sh collects logs from
Docker Compose, app profiles and/or Rancher/K8s commands, then this program
flags production-style errors that must not be ignored before /closer.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

ERROR_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("fatal", re.compile(r"\b(fatal|panic|segmentation fault|core dumped)\b", re.I)),
    ("exception", re.compile(r"\b(unhandled exception|uncaught exception|traceback|stacktrace|stack trace)\b", re.I)),
    ("runtime_error", re.compile(r"\b(error|errored|failed|failure)\b", re.I)),
    ("http_5xx", re.compile(r"\b(500|501|502|503|504)\b.*\b(GET|POST|PUT|PATCH|DELETE|/api|http)\b|\b(Internal Server Error|Bad Gateway|Service Unavailable)\b", re.I)),
    ("network", re.compile(r"\b(ECONNREFUSED|ECONNRESET|EADDRINUSE|ETIMEDOUT|ENOTFOUND)\b", re.I)),
    ("container", re.compile(r"\b(CrashLoopBackOff|ImagePullBackOff|ErrImagePull|OOMKilled|Back-off restarting failed container)\b", re.I)),
    ("k8s_probe", re.compile(r"\b(Liveness probe failed|Readiness probe failed|Error syncing pod|FailedScheduling)\b", re.I)),
]
DEFAULT_IGNORE_PATTERNS = [
    re.compile(r"\b(no errors?|0 errors?|errors?=0|error_count[=:]0)\b", re.I),
    re.compile(r"\b(error boundary|error page|error state|error_validation|error_network)\b", re.I),
    re.compile(r"\bexpected error\b", re.I),
]
LOG_SUFFIXES = {".log", ".txt", ".jsonl", ".out", ".err"}


def iter_log_files(log_dir: Path | None, extra_files: list[Path]) -> Iterable[Path]:
    seen: set[Path] = set()
    if log_dir:
        if log_dir.is_file():
            seen.add(log_dir.resolve())
            yield log_dir
        elif log_dir.exists():
            for path in sorted(log_dir.rglob("*")):
                if path.is_file() and path.suffix.lower() in LOG_SUFFIXES:
                    resolved = path.resolve()
                    if resolved not in seen:
                        seen.add(resolved)
                        yield path
    for path in extra_files:
        if path.is_file():
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield path


def load_allowlist(path: Path | None) -> list[re.Pattern[str]]:
    patterns = list(DEFAULT_IGNORE_PATTERNS)
    if not path or not path.is_file():
        return patterns
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            patterns.append(re.compile(line, re.I))
        except re.error:
            patterns.append(re.compile(re.escape(line), re.I))
    return patterns


def tail_lines(path: Path, limit: int) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return [f"<unable to read {path}: {exc}>"]
    if limit <= 0 or len(lines) <= limit:
        return lines
    return lines[-limit:]


def scan(log_dir: Path | None, *, scan_files: list[Path], allowlist_path: Path | None, tail: int, allow_empty: bool) -> dict[str, object]:
    allowlist = load_allowlist(allowlist_path)
    files = list(iter_log_files(log_dir, scan_files))
    findings: list[dict[str, object]] = []
    for path in files:
        for idx, line in enumerate(tail_lines(path, tail), start=1):
            if not line.strip() or any(pattern.search(line) for pattern in allowlist):
                continue
            for label, pattern in ERROR_PATTERNS:
                if pattern.search(line):
                    findings.append({"file": str(path), "line": idx, "category": label, "text": line.strip()[:1000]})
                    break
    if findings:
        status, clean = "errors_found", False
    elif files or allow_empty:
        status, clean = "pass", True
    else:
        status, clean = "no_logs", False
    return {
        "status": status,
        "log_dir": str(log_dir) if log_dir else "",
        "files_scanned": [str(path) for path in files],
        "files_count": len(files),
        "findings_count": len(findings),
        "findings": findings,
        "runtime_logs_clean": clean,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan captured runtime logs for production-blocking errors.")
    parser.add_argument("--log-dir", type=Path, default=None, help="Directory or file containing captured logs")
    parser.add_argument("--scan-file", action="append", type=Path, default=[], help="Additional explicit log file to scan")
    parser.add_argument("--allow-empty", action="store_true", help="Treat empty logs as clean only for explicit non-runtime/neutral framework checks")
    parser.add_argument("--task", default="", help="TASK_ID for diagnostics")
    parser.add_argument("--tail", type=int, default=1200)
    parser.add_argument("--allowlist", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    if not args.log_dir and not args.scan_file and not args.allow_empty:
        parser.error("--log-dir or --scan-file is required unless --allow-empty is set")
    payload = scan(args.log_dir, scan_files=list(args.scan_file), allowlist_path=args.allowlist, tail=args.tail, allow_empty=args.allow_empty)
    payload["task_id"] = args.task
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"RUNTIME_LOGS_CLEAN: {'yes' if payload['runtime_logs_clean'] else 'no'}")
        print(f"LOG_FILES_SCANNED: {payload['files_count']}")
        for finding in payload["findings"]:  # type: ignore[index]
            print(f"- {finding['category']} {finding['file']}:{finding['line']}: {finding['text']}")
    if args.strict and not payload["runtime_logs_clean"]:
        return 2
    if payload["findings_count"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
