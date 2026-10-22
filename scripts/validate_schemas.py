#!/usr/bin/env python3
"""JSON-schema validation for the repository schemas (stdlib-only).

Implements the small, self-contained subset of JSON Schema (draft 2020-12)
that the schemas under schemas/ actually use: type, const, enum, pattern,
minLength / minimum / maximum / minItems / maxItems / uniqueItems, required,
properties / additionalProperties, items (single schema) and local $ref into
"$defs". No third-party dependency (CONTRIBUTING.md — glue stays stdlib).

Usage:
  python3 scripts/validate_schemas.py --manifest  FILE
  python3 scripts/validate_schemas.py --provenance FILE
  python3 scripts/validate_schemas.py --trace      FILE
  python3 scripts/validate_schemas.py --all-repo        # the templates shipped in this repo

All modes print one JSON payload on stdout and exit 0 (passed) or 1
(failed), per the scoring CLI conventions (docs/scorer-contracts.md).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ADAPTER_SCHEMA = ROOT / "schemas" / "adapter.schema.json"
RUNS_SCHEMA = ROOT / "schemas" / "runs.schema.json"
MANIFEST = ROOT / "templates" / "example-adapter" / "manifest.json"
GOLDEN = ROOT / "templates" / "submission" / "golden_tdc_admet_tox"


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def collect_errors(instance: object, schema: object, path: str, defs: dict) -> list[str]:
    errors: list[str] = []
    if not isinstance(schema, dict):
        return errors

    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            errors.append(f"{path}: unsupported $ref: {ref}")
            return errors
        resolved = defs.get(ref.split("/")[-1])
        if resolved is None:
            errors.append(f"{path}: unknown $def: {ref}")
            return errors
        errors.extend(collect_errors(instance, resolved, path, defs))
        return errors

    schema_type = schema.get("type")
    if schema_type is not None:
        if not matches_type(instance, schema_type):
            errors.append(f"{path}: expected {schema_type}, got {type(instance).__name__}")
            return errors

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value {instance!r} not in enum {schema['enum']}")

    if isinstance(instance, str):
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append(f"{path}: string does not match {schema['pattern']!r}")
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: below minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: above maximum {schema['maximum']}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append(f"{path}: more than {schema['maxItems']} items")
        if schema.get("uniqueItems") and len(set(map(json.dumps, instance))) != len(instance):
            errors.append(f"{path}: items are not unique")
        if "items" in schema:
            for index, item in enumerate(instance):
                errors.extend(collect_errors(item, schema["items"], f"{path}[{index}]", defs))

    if isinstance(instance, dict):
        properties = schema.get("properties")
        if isinstance(properties, dict):
            for key, value in instance.items():
                subschema = properties.get(key)
                if subschema is not None:
                    errors.extend(collect_errors(value, subschema, f"{path}.{key}", defs))
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")
        if schema.get("additionalProperties") is False and properties is not None:
            for key in instance:
                if key not in properties:
                    errors.append(f"{path}: unexpected property {key!r}")
    return errors


def matches_type(instance: object, schema_type: object) -> bool:
    if isinstance(schema_type, list):
        return any(matches_type(instance, item) for item in schema_type)
    schema_type = str(schema_type)
    if schema_type == "object":
        return isinstance(instance, dict)
    if schema_type == "array":
        return isinstance(instance, list)
    if schema_type == "string":
        return isinstance(instance, str)
    if schema_type == "boolean":
        return isinstance(instance, bool)
    if schema_type == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if schema_type == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if schema_type == "null":
        return instance is None
    return False


def validate(schema_path: Path, def_name: str | None, data_path: Path) -> tuple[bool, list[str]]:
    schema = load_json(schema_path)
    instance = load_json(data_path)
    defs = schema.get("$defs", {}) if isinstance(schema, dict) else {}
    if def_name is not None:
        target = defs.get(def_name)
        if target is None:
            return False, [f"schema {schema_path.name} has no $def {def_name!r}"]
        errors = collect_errors(instance, target, "$", defs)
    else:
        errors = collect_errors(instance, schema, "$", defs)
    return not errors, errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("Usage:")[0].strip())
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--provenance", type=Path)
    parser.add_argument("--trace", type=Path)
    parser.add_argument("--all-repo", action="store_true")
    args = parser.parse_args(argv)

    checks: list[tuple[str, Path, str | None, Path]] = []
    if args.all_repo:
        checks = [
            ("manifest", ADAPTER_SCHEMA, None, MANIFEST),
            ("provenance", RUNS_SCHEMA, "provenance", GOLDEN / "PROVENANCE.json"),
            ("trace", RUNS_SCHEMA, "trace", GOLDEN / "workspace" / "experiment_trace.json"),
        ]
    else:
        if args.manifest:
            checks.append(("manifest", ADAPTER_SCHEMA, None, args.manifest))
        if args.provenance:
            checks.append(("provenance", RUNS_SCHEMA, "provenance", args.provenance))
        if args.trace:
            checks.append(("trace", RUNS_SCHEMA, "trace", args.trace))
    if not checks:
        parser.error("pass one of --manifest / --provenance / --trace / --all-repo")

    results: dict[str, list[str]] = {}
    failed = False
    for name, schema_path, def_name, data_path in checks:
        ok, errors = validate(schema_path, def_name, data_path)
        results[name] = errors
        if not ok:
            failed = True

    if failed:
        print(
            json.dumps(
                {"status": "failed", "errors": {name: errors for name, errors in results.items() if errors}},
                ensure_ascii=True,
                indent=2,
            )
        )
        return 1
    print(json.dumps({"status": "passed", "checks": sorted(results)}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())