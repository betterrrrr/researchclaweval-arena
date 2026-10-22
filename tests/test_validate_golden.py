#!/usr/bin/env python3
"""Golden-run gate tests — self-executing assertions (no pytest needed).

Run directly:  python3 tests/test_validate_golden.py

The golden run tree under templates/submission/golden_tdc_admet_tox is a
frozen, complete, legal TDC-ADMET-Tox handoff. The audit must accept it
(regression against the audit itself) and must reject it when logs live
inside the workspace instead of the run root (docs/rules.md §5.2).
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scoring" / "validate_tdc_admet_tox_run.py"
GOLDEN = ROOT / "templates" / "submission" / "golden_tdc_admet_tox"


def run_validator(target: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--run-root", str(target), "--stage", "framework"],
        capture_output=True,
        text=True,
    )


def test_golden_passes() -> None:
    r = run_validator(GOLDEN)
    assert r.returncode == 0, f"golden must pass, rc={r.returncode}:\n{r.stdout}{r.stderr}"
    payload = json.loads(r.stdout)
    assert payload["status"] == "passed"
    assert payload["experiment_count"] == 2
    assert payload["workspace"].endswith("/workspace"), "audit must report the workspace path"


def test_logs_must_be_at_run_root() -> None:
    with tempfile.TemporaryDirectory() as td:
        target = Path(td)
        shutil.copytree(GOLDEN, target, dirs_exist_ok=True)
        shutil.rmtree(target / "logs")
        (target / "workspace" / "logs").mkdir(parents=True)
        (target / "workspace" / "logs" / "fake.log").write_text("not the run-root log\n")
        r = run_validator(target)
        assert r.returncode != 0, "logs inside the workspace must not satisfy the audit"
        assert "logs directory is empty" in r.stdout


def test_resource_budget_anchor_matches_golden() -> None:
    anchors = json.loads((ROOT / "scoring" / "resource_budget.anchors.json").read_text(encoding="utf-8"))
    trace = json.loads((GOLDEN / "workspace" / "experiment_trace.json").read_text(encoding="utf-8"))
    assert trace["resource_budget"] == anchors["topics"]["tdc_admet_tox"]


def test_golden_log_is_tracked() -> None:
    # .gitignore has a bare "logs/" rule; if it ever swallows the golden run's
    # log again, clean CI checkouts lose logs/e2e.log and both this suite and
    # scripts/selfcheck_tdc.sh fail on a tree that is green locally.
    r = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--error-unmatch",
         "templates/submission/golden_tdc_admet_tox/logs/e2e.log"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, f"golden logs/e2e.log must be tracked, not git-ignored:\n{r.stderr}"


def main() -> None:
    tests = [
        test_golden_passes,
        test_logs_must_be_at_run_root,
        test_resource_budget_anchor_matches_golden,
        test_golden_log_is_tracked,
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
    print("test_validate_golden: ALL PASS")


if __name__ == "__main__":
    main()