#!/usr/bin/env python3
"""Runner template smoke tests — self-executing assertions (no pytest needed).

Run directly:  python3 tests/test_runner_smoke.py

Shells out to scripts/runner/my_framework_wrapper.sh with a minimal fake
framework, asserting the runner injects the WORKSPACE env var and composes
prompt.txt + logs/e2e.log at the documented locations (docs/rules.md §5.2,
§5.7; docs/participant_quickstart.md §4).
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WRAPPER = ROOT / "scripts" / "runner" / "my_framework_wrapper.sh"

# stub credentials (short: the release gate flags 12+ char values) — the
# runner only checks that the env vars are set, never their values
MODEL_ENV = {
    "OPENAI_BASE_URL": "https://example.injected/v1",
    "OPENAI_API_KEY": "demo",
    "OPENAI_MODEL": "demo",
}


def run_wrapper(run_root: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env.update(
        {
            **MODEL_ENV,
            "RUN_ROOT": str(run_root),
            "FRAMEWORK_ID": "01",
            "FRAMEWORK_NAME": "smoke",
            "TOPIC": "tdc_admet_tox",
            "CONTRACT_FILE": str(ROOT / "contracts" / "tdc_admet_tox_contract.md"),
            "DATASET_ENV_NAME": "SMOKE_DATASET_ROOT",
            "SMOKE_DATASET_ROOT": str(run_root / "dataset"),
            "PROMPT_TASK_SUMMARY": "Predict three molecular toxicity endpoints from SMILES.",
            "FRAMEWORK_ENTRY_PATHS": 'sh -c \'echo "[smoke] framework started"; printf %s "$WORKSPACE" > "$WORKSPACE/ws_probe.txt"\'',
        }
    )
    return subprocess.run(["bash", str(WRAPPER)], capture_output=True, text=True, env=env)


def test_runner_injects_workspace_and_layout() -> None:
    with tempfile.TemporaryDirectory() as td:
        run_root = Path(td)
        r = run_wrapper(run_root)
        assert r.returncode == 0, f"runner must exit 0: {r.stderr}"
        runs = [p for p in run_root.iterdir() if p.is_dir()]
        assert len(runs) == 1, f"exactly one run dir expected, got {runs}"
        run = runs[0]
        ws = run / "workspace"
        assert ws.is_dir(), f"workspace dir missing: {ws}"
        probe = ws / "ws_probe.txt"
        assert probe.is_file(), "framework did not see a WORKSPACE env var"
        assert probe.read_text(encoding="utf-8") == str(ws)
        assert (run / "logs" / "e2e.log").is_file(), "logs/e2e.log missing at the run root"
        log = (run / "logs" / "e2e.log").read_text(encoding="utf-8")
        # e2e.log carries only the framework's own stdout/stderr stream (the
        # runner's progress lines go to its terminal, not into the log)
        assert "[smoke] framework started" in log, "e2e.log must carry the framework stdout stream"


def test_runner_composes_prompt_txt() -> None:
    with tempfile.TemporaryDirectory() as td:
        run_root = Path(td)
        r = run_wrapper(run_root)
        assert r.returncode == 0, f"runner must exit 0: {r.stderr}"
        runs = [p for p in run_root.iterdir() if p.is_dir()]
        prompt = runs[0] / "workspace" / "input" / "prompt.txt"
        assert prompt.is_file(), "prompt.txt was not composed into input/"
        text = prompt.read_text(encoding="utf-8")
        assert "Predict three molecular toxicity endpoints from SMILES." in text
        assert "TDC-ADMET-Tox Runtime Contract" in text, "prompt.txt must embed the contract"
        assert "## Execution Budget" in text, "prompt.txt must embed the execution budget"


def main() -> None:
    tests = [test_runner_injects_workspace_and_layout, test_runner_composes_prompt_txt]
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
    print("test_runner_smoke: ALL PASS")


if __name__ == "__main__":
    main()