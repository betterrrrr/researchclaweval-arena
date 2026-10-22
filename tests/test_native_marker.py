#!/usr/bin/env python3
"""Native-log-marker check tests — self-executing assertions (no pytest needed).

Run directly:  python3 tests/test_native_marker.py
Shells out to scripts/check_native_marker.sh over fixture logs in a temp
dir, asserting PASS/FAIL behavior (rules §5.5).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = ROOT / "scripts" / "check_native_marker.sh"


def run_check(log: Path, marker: str | None = None) -> subprocess.CompletedProcess:
    argv = ["bash", str(CHECK), str(log)]
    if marker is not None:
        argv.append(marker)
    return subprocess.run(argv, capture_output=True, text=True)


def test_marker_present_passes() -> None:
    with tempfile.TemporaryDirectory() as td:
        log = Path(td) / "e2e.log"
        log.write_text("[runner] run id: 01-framework-topic-20261022T000000\nMYFRAMEWORK_NATIVE\n", encoding="utf-8")
        r = run_check(log)
        assert r.returncode == 0, f"marker present must pass:\n{r.stdout}{r.stderr}"
        assert "PASS" in r.stdout


def test_marker_missing_fails() -> None:
    with tempfile.TemporaryDirectory() as td:
        log = Path(td) / "e2e.log"
        log.write_text("[runner] run id: 01-framework-topic-20261022T000000\n", encoding="utf-8")
        r = run_check(log)
        assert r.returncode != 0, "marker missing must fail"
        assert "PASS" not in r.stdout
        assert "not found" in r.stderr


def test_missing_log_fails() -> None:
    with tempfile.TemporaryDirectory() as td:
        r = run_check(Path(td) / "nope.log")
        assert r.returncode != 0, "missing log must fail"


def test_custom_marker_override() -> None:
    with tempfile.TemporaryDirectory() as td:
        log = Path(td) / "e2e.log"
        log.write_text("[runner] run id: 01-framework-topic-20261022T000000\nMY_OTHER_MARKER\n", encoding="utf-8")
        r = run_check(log, "MY_OTHER_MARKER")
        assert r.returncode == 0, "custom marker must pass when supplied"
        r = run_check(log)  # default marker must not match
        assert r.returncode != 0, "default marker must not match a custom one"


def main() -> None:
    tests = [test_marker_present_passes, test_marker_missing_fails, test_missing_log_fails, test_custom_marker_override]
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
    print("test_native_marker: ALL PASS")


if __name__ == "__main__":
    main()