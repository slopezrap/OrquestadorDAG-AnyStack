#!/usr/bin/env python3
"""Validate static orchestrator JSON schemas and small evidence instances.

Stdlib-only by design: validates schema metadata plus the JSON-schema subset the
orchestrator uses for machine evidence contracts.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from common import project_root, workspace_relpath

REQUIRED_TOP_LEVEL = {"$schema", "$id", "title", "type"}


def _rel(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except Exception:
        return workspace_relpath(path)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_schema_files(root: Path | None = None) -> dict[str, Any]:
    root = (root or project_root()).resolve()
    schema_dir = root / ".claude" / "schemas"
    errors: list[str] = []
    warnings: list[str] = []
    schemas: dict[str, Any] = {}
    seen_ids: dict[str, str] = {}
    if not schema_dir.is_dir():
        return {"ok": False, "errors": [f"missing schema directory: {_rel(root, schema_dir)}"], "warnings": [], "schemas": {}}
    for path in sorted(schema_dir.glob("*.schema.json")):
        rel = _rel(root, path)
        try:
            data = _load_json(path)
        except Exception as exc:
            errors.append(f"{rel}: invalid JSON: {exc}")
            continue
        missing = sorted(REQUIRED_TOP_LEVEL - set(data))
        if missing:
            errors.append(f"{rel}: missing top-level keys: {', '.join(missing)}")
        sid = str(data.get("$id") or "").strip()
        if not sid:
            errors.append(f"{rel}: empty $id")
        elif sid in seen_ids:
            errors.append(f"{rel}: duplicate $id {sid!r}; first seen in {seen_ids[sid]}")
        else:
            seen_ids[sid] = rel
        if data.get("type") != "object":
            warnings.append(f"{rel}: top-level type is {data.get('type')!r}, expected object")
        for target in data.get("x-enforced-by") or []:
            if not isinstance(target, str) or not target.strip():
                errors.append(f"{rel}: invalid x-enforced-by entry {target!r}")
            elif not (root / target).exists():
                errors.append(f"{rel}: x-enforced-by target does not exist: {target}")
        schemas[rel] = {"id": sid, "title": data.get("title"), "required_count": len(data.get("required") or [])}
    if not schemas:
        errors.append(f"{_rel(root, schema_dir)}: no *.schema.json files found")
    return {"ok": not errors, "errors": errors, "warnings": warnings, "schemas": schemas, "checks": {"schema_count": len(schemas)}}


def _type_ok(expected: str, value: Any) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return True


def _validate(schema: dict[str, Any], value: Any, pointer: str, errors: list[str]) -> None:
    expected = schema.get("type")
    if isinstance(expected, str) and not _type_ok(expected, value):
        errors.append(f"{pointer}: expected {expected}, got {type(value).__name__}")
        return
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{pointer}: {value!r} not in enum {schema['enum']!r}")
    if isinstance(value, str) and schema.get("pattern") and not re.search(str(schema["pattern"]), value):
        errors.append(f"{pointer}: string does not match {schema['pattern']!r}")
    if isinstance(value, int) and not isinstance(value, bool) and "minimum" in schema and value < schema["minimum"]:
        errors.append(f"{pointer}: {value} below minimum {schema['minimum']}")
    if isinstance(value, dict):
        for key in schema.get("required") or []:
            if key not in value:
                errors.append(f"{pointer}: missing required key {key!r}")
        props = schema.get("properties") or {}
        allow_extra = schema.get("additionalProperties", True)
        for key, child in value.items():
            if key not in props:
                if allow_extra is False:
                    errors.append(f"{pointer}: additional property not allowed: {key!r}")
                continue
            if isinstance(props[key], dict):
                _validate(props[key], child, f"{pointer}/{key}", errors)
    if isinstance(value, list) and isinstance(schema.get("items"), dict):
        for i, item in enumerate(value):
            _validate(schema["items"], item, f"{pointer}/{i}", errors)


def validate_single_instance(root: Path, schema_path: Path, instance_path: Path) -> dict[str, Any]:
    schema_abs = schema_path if schema_path.is_absolute() else root / schema_path
    instance_abs = instance_path if instance_path.is_absolute() else root / instance_path
    try:
        schema = _load_json(schema_abs)
        instance = _load_json(instance_abs)
    except Exception as exc:
        return {"ok": False, "errors": [str(exc)], "schema": str(schema_path), "instance": str(instance_path)}
    errors: list[str] = []
    _validate(schema, instance, "#", errors)
    return {"ok": not errors, "errors": errors, "schema": _rel(root, schema_abs), "instance": _rel(root, instance_abs)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate orchestrator JSON schema contracts")
    parser.add_argument("--root", type=Path, default=None)
    parser.add_argument("--schema", type=Path, default=None)
    parser.add_argument("--instance", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve() if args.root else project_root()
    result = validate_schema_files(root)
    if args.schema or args.instance:
        if not args.schema or not args.instance:
            parser.error("--schema and --instance must be supplied together")
        inst = validate_single_instance(root, args.schema, args.instance)
        result["instance_validation"] = inst
        if not inst["ok"]:
            result["ok"] = False
            result["errors"].extend(inst["errors"])
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Orchestrator schemas OK" if result["ok"] else "Orchestrator schemas FAILED")
        for err in result["errors"]:
            print(f"- {err}")
        for warn in result["warnings"]:
            print(f"WARN: {warn}")
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
