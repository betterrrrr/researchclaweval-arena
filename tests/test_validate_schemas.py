#!/usr/bin/env python3
"""Schema-validation tests — self-executing assertions (no pytest needed).

Run directly:  python3 tests/test_validate_schemas.py
Shells out to scripts/validate_schemas.py over the repo's own schema +
template files (and a mutated copy), asserting red/green behavior.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_schemas.py"
MANIFEST = ROOT / "templates" / "example-adapter" / "manifest.json"
PROVENANCE = ROOT / "templates" / "submission" / "golden_tdc_admet_tox" / "PROVENANCE.json"
TRACE = ROOT / "templates" / "submission" / "golden_tdc_admet_tox" / "workspace" / "experiment_trace.json"


def run_validator(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(VALIDATOR), *args], capture_output=True, text=True)


def test_all_repo_passes() -> None:
    r = run_validator("--all-repo")
    assert r.returncode == 0, f"--all-repo must pass:\n{r.stdout}{r.stderr}"
    assert json.loads(r.stdout)["status"] == "passed"


def test_manifest_passes() -> None:
    r = run_validator("--manifest", str(MANIFEST))
    assert r.returncode == 0, f"manifest must validate:\n{r.stdout}{r.stderr}"


def test_broken_manifest_fails() -> None:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "manifest.json"
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        payload["framework_id"] = "0"  # violates ^[0-9]{2}$|^NN$
        path.write_text(json.dumps(payload), encoding="utf-8")
        r = run_validator("--manifest", str(path))
        assert r.returncode != 0, "a one-digit framework_id must fail"
        assert "framework_id" in r.stdout, r.stdout


def test_provenance_golden_passes() -> None:
    r = run_validator("--provenance", str(PROVENANCE))
    assert r.returncode == 0, f"golden PROVENANCE must validate:\n{r.stdout}{r.stderr}"


def test_broken_provenance_fails() -> None:
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "PROVENANCE.json"
        payload = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        del payload["model"]  # model is required (rules §4, docs §5.2)
        path.write_text(json.dumps(payload), encoding="utf-8")
        r = run_validator("--provenance", str(path))
        assert r.returncode != 0, "missing model must fail"
        assert "model" in r.stdout, r.stdout


def test_trace_golden_passes() -> None:
    r = run_validator("--trace", str(TRACE))
    assert r.returncode == 0, f"golden trace must validate:\n{r.stdout}{r.stderr}"


def main() -> None:
    tests = [
        test_all_repo_passes,
        test_manifest_passes,
        test_broken_manifest_fails,
        test_provenance_golden_passes,
        test_broken_provenance_fails,
        test_trace_golden_passes,
    ]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL {t.__name__}: {e}")
    if failures:
        print(f"{failures} test(s) failed")
        sys.exit(1)
    print("test_validate_schemas: ALL PASS")


if __name__ == "__main__":
    main()