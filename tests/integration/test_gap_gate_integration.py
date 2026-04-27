"""Integration tests for the Gap Gate (M-12).

These run the gate via subprocess against real files in the repo, asserting
the actual exit codes and stdout content the CI step would see.

Validation lane: do NOT modify src/ or tools/. Tests only.

Why subprocess: the CI step is `python -m src.gates.gap_gate ...`, so an
in-process call (`main(...)`) would cover the run_gate happy path but not the
argparse + module-as-script wiring. Both shapes matter to a CI gate.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BREAKOUT_RUN = "examples/breakout/run_breakout.py"


def _run_gate(*args: str) -> subprocess.CompletedProcess:
    """Invoke the gate as a subprocess in --no-scaffold (read-only) mode by
    default; callers can override by passing `--scaffold` themselves."""
    cmd = [sys.executable, "-m", "src.gates.gap_gate", *args]
    return subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Known-bad path: examples/breakout/run_breakout.py references
# Camera.backgroundColor, which is documented as parity_skipped in SUCCESS.md.


def test_gate_fails_on_breakout_camera_background_color():
    """`examples/breakout/run_breakout.py` sets `cam.background_color = (...)`
    — a deferred-coverage API per ASP-3. Running the gate against this file
    must exit non-zero and call the API out by name."""
    proc = _run_gate("--files", BREAKOUT_RUN, "--no-scaffold")
    assert proc.returncode == 1, (
        f"expected exit 1, got {proc.returncode}\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    )
    combined = proc.stdout + proc.stderr
    # The gate must surface either Camera.backgroundColor or
    # SpriteRenderer.color — the two genuinely-untested APIs touched.
    assert (
        "Camera.backgroundColor" in combined
        or "SpriteRenderer.color" in combined
    ), f"expected Camera.backgroundColor or SpriteRenderer.color in output:\n{combined}"


def test_gate_failure_message_points_at_skeleton():
    """Failure message should include the skeleton path under tests/parity/
    so the agent has a clear next step."""
    proc = _run_gate("--files", BREAKOUT_RUN, "--no-scaffold")
    assert proc.returncode == 1
    assert (
        "tests/parity/" in proc.stdout
        or "tests\\parity\\" in proc.stdout
    ), f"expected a tests/parity/ pointer in output:\n{proc.stdout}"


def test_gate_passes_on_clean_baseline():
    """A PR that touches only out-of-scope files (docs, configs) should exit 0
    even though the gate runs. We pass a single non-source file so argparse
    happily consumes it, and the in-scope filter produces an empty list."""
    proc = _run_gate("--files", "README.md", "--no-scaffold")
    assert proc.returncode == 0, (
        f"expected exit 0, got {proc.returncode}\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    )
    # Output should reflect the no-references branch.
    assert "no Unity API references" in proc.stdout or "PASS" in proc.stdout


def test_gate_passes_on_test_only_changes(tmp_path):
    """Files under tests/ are explicitly out of scope per `_is_in_scope`. A
    diff that only changes test files should exit 0 even though those test
    files probably reference Unity APIs."""
    # Pick any test file that exists; the gate must filter it out before
    # scanning. We don't need a real diff — `--files` is enough.
    proc = _run_gate(
        "--files",
        "tests/parity/_harness.py",
        "tests/parity/test_class_existence_parity.py",
        "--no-scaffold",
    )
    assert proc.returncode == 0, (
        f"expected exit 0 on test-only diff, got {proc.returncode}\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    )


def test_gate_filters_non_python_files():
    """Markdown / JSON / YAML / .meta diffs aren't Python and shouldn't
    trigger the gate."""
    proc = _run_gate(
        "--files",
        "README.md",
        "data/metrics/parity_matrix.json",
        ".github/workflows/test.yml",
        "--no-scaffold",
    )
    assert proc.returncode == 0


def test_gate_no_scaffold_does_not_write_files():
    """Running with --no-scaffold should NOT mutate tests/parity/ on disk.
    We compare directory contents before and after."""
    parity_dir = REPO_ROOT / "tests" / "parity"
    before = sorted(p.name for p in parity_dir.iterdir())
    proc = _run_gate("--files", BREAKOUT_RUN, "--no-scaffold")
    assert proc.returncode == 1
    after = sorted(p.name for p in parity_dir.iterdir())
    assert before == after, (
        f"--no-scaffold mutated tests/parity/:\n"
        f"added: {set(after) - set(before)}\nremoved: {set(before) - set(after)}"
    )
