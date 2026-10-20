#!/usr/bin/env python3
"""Release-safety gate tests — self-executing assertions (no pytest needed).

Run directly:  python3 tests/test_release_safety.py
The suite shells out to scripts/check-release.sh --path <dir> and asserts
its red/green behavior over fixture directories. Fixtures are created in a
temp dir and never touch the repository.

NOTE: this file necessarily contains pattern text; it is exempted from the
gate's own scan (see EXEMPT in scripts/check-release.sh).
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = ROOT / "scripts" / "check-release.sh"


def run_check(target: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(CHECK), "--path", str(target)],
        capture_output=True,
        text=True,
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_clean_dir_passes() -> None:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write(d / "ok.txt", "hello world\n")
        r = run_check(d)
        assert r.returncode == 0, f"clean dir should pass, got rc={r.returncode}:\n{r.stdout}{r.stderr}"


def test_leaked_topic_word_fails() -> None:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write(d / "brief.md", "The BabyLM corpus stats\n")
        r = run_check(d)
        assert r.returncode != 0, "forbidden topic word must fail"
        assert "FINDING" in r.stderr


def test_leaked_secret_fails() -> None:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        # assembled from parts so gitleaks does not flag the test source itself;
        # the fixture FILE still contains the full credential-shaped value.
        secret = "sk-" + "123456789012345678901234"
        write(d / "cfg.txt", f'api_key = "{secret}"\n')
        r = run_check(d)
        assert r.returncode != 0, "credential-shaped value must fail"


def test_private_path_fails() -> None:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write(d / "run.sh", "export ROOT=/home/jianbiao/research\n")
        r = run_check(d)
        assert r.returncode != 0, "absolute machine path must fail"


def test_results_file_name_fails() -> None:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write(d / "score.json", "{}\n")
        r = run_check(d)
        assert r.returncode != 0, "tracked score artifact must fail"


def test_forbidden_host_fails() -> None:
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write(d / "cfg.txt", "base = \"https://api.paratera.example/v1\"\n")
        r = run_check(d)
        assert r.returncode != 0, "forbidden host substring must fail"


def test_rack_file_name_allowed() -> None:
    # 'results' appearing inside a file NAME that is not the artifact should
    # still fail only for the exact artifact names; a README mention is fine.
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        write(d / "notes.md", "results are published after the window closes\n")
        r = run_check(d)
        assert r.returncode == 0, "prose mention of results must pass"


def main() -> None:
    tests = [
        test_clean_dir_passes,
        test_leaked_topic_word_fails,
        test_leaked_secret_fails,
        test_private_path_fails,
        test_results_file_name_fails,
        test_forbidden_host_fails,
        test_rack_file_name_allowed,
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
    print("test_release_safety: ALL PASS")


if __name__ == "__main__":
    main()