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


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
BREAKOUT_RUN = "examples/breakout/run_breakout.py"


def _make_synthetic_uncovered_file(tmp_path: Path) -> Path:
    """Write a synthetic .py file under tmp_path/src/ that references a
    still-untested Unity API (Transform.Rotate per ASP-3 deferred list).
    The gate's `_is_in_scope` accepts files with `src/` or `examples/` in
    their path parts even when not under REPO_ROOT."""
    target = tmp_path / "src" / "synthetic_spinner.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "class Spinner:\n"
        "    def update(self, transform) -> None:\n"
        "        transform.rotate(0, 1, 0)\n",  # snake_case for Transform.Rotate
        encoding="utf-8",
    )
    return target


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


def test_gate_fails_on_synthetic_file_referencing_untested_api(tmp_path):
    """A synthetic file that references a still-untested API
    (Transform.Rotate) must make the gate exit non-zero and call the API out
    by name. Synthetic-fixture pattern is more durable than asserting a real
    corpus file fails — when an API moves between tested/parked, the corpus
    test silently flips."""
    synthetic = _make_synthetic_uncovered_file(tmp_path)
    proc = _run_gate("--files", str(synthetic), "--no-scaffold")
    assert proc.returncode == 1, (
        f"expected exit 1, got {proc.returncode}\n"
        f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
    )
    combined = proc.stdout + proc.stderr
    assert "Transform.Rotate" in combined, (
        f"expected Transform.Rotate in output:\n{combined}"
    )


def test_gate_failure_message_points_at_skeleton(tmp_path):
    """Failure message should include the skeleton path under tests/parity/
    so the agent has a clear next step."""
    synthetic = _make_synthetic_uncovered_file(tmp_path)
    proc = _run_gate("--files", str(synthetic), "--no-scaffold")
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


def test_gate_no_scaffold_does_not_write_files(tmp_path):
    """Running with --no-scaffold against a file with an uncovered API
    should NOT mutate tests/parity/ on disk."""
    parity_dir = REPO_ROOT / "tests" / "parity"
    before = sorted(p.name for p in parity_dir.iterdir())
    synthetic = _make_synthetic_uncovered_file(tmp_path)
    proc = _run_gate("--files", str(synthetic), "--no-scaffold")
    assert proc.returncode == 1
    after = sorted(p.name for p in parity_dir.iterdir())
    assert before == after, (
        f"--no-scaffold mutated tests/parity/:\n"
        f"added: {set(after) - set(before)}\nremoved: {set(before) - set(after)}"
    )
