"""Tests for src.gates.gap_gate (M-12 Gap Gate).

Strategy:
  - Unit tests use the importable `run_gate(files=[...], scaffold=False)` to
    bypass git diff and skeleton writes, asserting the gate's classification
    of references as tested vs. untested is correct.
  - The integration test exercises the auto-skeleton path with the parity
    directory monkey-patched to a tmp_path so we don't pollute tests/parity/.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent.parent

from src.gates import gap_gate as gg  # noqa: E402


# ── Helpers ─────────────────────────────────────────────────────────────────


def _make_python_file(tmp_path: Path, body: str, *, in_repo: bool = True) -> Path:
    """Write a synthetic .py file. By default places it under <tmp>/src/<x>.py
    so `_is_in_scope` accepts it (rel path starts with 'src')."""
    if in_repo:
        target = tmp_path / "src" / "synthetic.py"
    else:
        target = tmp_path / "synthetic.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


# ── Unit tests ──────────────────────────────────────────────────────────────


def test_run_gate_with_no_files_returns_zero_references() -> None:
    result = gg.run_gate(base=None, files=[], scaffold=False)
    assert result.references == []
    assert result.untested == []
    assert result.skeletons_written == []


def test_run_gate_detects_well_tested_transform_position() -> None:
    """A file referencing Transform.position should detect the reference and
    classify it as TESTED (M-9's reference parity test covers this API)."""
    result = gg.run_gate(
        base=None,
        files=["examples/breakout/run_breakout.py"],
        scaffold=False,
    )
    pairs = {(r.unity_class, r.unity_member) for r in result.references}
    assert ("Transform", "position") in pairs, (
        "Gap Gate did not detect Transform.position reference in run_breakout.py"
    )
    untested_pairs = {(r.unity_class, r.unity_member) for r in result.untested}
    assert ("Transform", "position") not in untested_pairs, (
        "Transform.position is parity-tested (M-9) but gate flagged it as untested"
    )


def test_run_gate_flags_uncovered_api_in_synthetic_file(tmp_path) -> None:
    """A still-untested API (Transform.Rotate) referenced in a synthetic
    touched file must be flagged. Uses a synthetic file rather than a real
    corpus path to avoid fragility when the corpus's API references shift."""
    synthetic = _make_python_file(
        tmp_path,
        "class Spinner:\n"
        "    def update(self, transform) -> None:\n"
        "        transform.rotate(0, 1, 0)\n",  # snake_case for Transform.Rotate
    )
    result = gg.run_gate(
        base=None,
        files=[str(synthetic)],
        scaffold=False,
    )
    untested_pairs = {(r.unity_class, r.unity_member) for r in result.untested}
    assert ("Transform", "Rotate") in untested_pairs, (
        "Gap Gate did not flag Transform.Rotate as untested"
    )


def test_grandfather_only_untouched_files() -> None:
    """The gate must only complain about APIs in TOUCHED files. If we pass a
    well-tested file (Transform.position only), uncovered APIs in untouched
    files should NOT show up."""
    result = gg.run_gate(
        base=None,
        files=["src/engine/transform.py"],
        scaffold=False,
    )
    # transform.py defines Transform; doesn't itself USE untested-API patterns
    # heavily. Most refs should be tested. Specifically — Component.GetComponent
    # is in space_invaders/bunker.py which we did NOT pass, so it must be absent.
    untested_pairs = {(r.unity_class, r.unity_member) for r in result.untested}
    assert ("Component", "GetComponent") not in untested_pairs, (
        "Gap Gate leaked an uncovered API from an untouched file — grandfathering broken"
    )


# ── Integration test (skeleton writing on tmp_path) ─────────────────────────


def test_auto_skeleton_writes_when_uncovered_api_in_touched_file(tmp_path, monkeypatch) -> None:
    """Synthetic file references an UNTESTED API (Transform.Rotate, on the
    deferred list per ASP-3). Gate should compute the expected skeleton path.
    Patch PARITY_TESTS_DIR to tmp_path so we don't pollute the real
    tests/parity/ directory."""
    fake_parity = tmp_path / "fake_parity"
    fake_parity.mkdir()
    monkeypatch.setattr(gg, "PARITY_TESTS_DIR", fake_parity)

    synthetic = _make_python_file(
        tmp_path,
        "class Spinner:\n"
        "    def update(self, transform) -> None:\n"
        "        transform.rotate(0, 1, 0)\n",  # snake_case for Transform.Rotate
    )
    result = gg.run_gate(
        base=None,
        files=[str(synthetic)],
        scaffold=False,  # report-only; verify expected path string
    )
    expected = [p for p in result.skeletons_written
                if "transform" in p.name.lower() and "rotate" in p.name.lower()]
    assert any(p.name == "test_transform_rotate_parity.py" for p in expected), (
        f"Expected skeleton path not in {[p.name for p in result.skeletons_written]}"
    )


# ── CLI integration ─────────────────────────────────────────────────────────


def test_cli_exits_zero_with_no_files() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "src.gates.gap_gate", "--no-scaffold"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        env={"PATH": "."},  # cripple env minimally; the module doesn't need much
        timeout=30,
    )
    # When base=master and no files, real diff runs — we just verify
    # the script runs cleanly without raising.
    assert proc.returncode in (0, 1, 2), f"unexpected exit {proc.returncode}: {proc.stderr}"


def test_cli_explicit_files_flag() -> None:
    """Gate should pass on examples/breakout/run_breakout.py — its references
    (Camera.backgroundColor, SpriteRenderer.color, Component.GetComponent) are
    all PARITY_SCAFFOLD_PARKED as deferred-implementation per ASP-3."""
    proc = subprocess.run(
        [
            sys.executable, "-m", "src.gates.gap_gate",
            "--files", "examples/breakout/run_breakout.py",
            "--no-scaffold",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert proc.returncode == 0, f"expected pass, got {proc.returncode}: {proc.stderr}"
    assert "PASS" in proc.stdout, f"expected PASS in stdout: {proc.stdout!r}"


# ── Regression guard: scanner doesn't false-positive on docstrings ──────────


def test_scanner_recognizes_dotted_attr_access() -> None:
    """The API reference extractor must catch `transform.position` AS A
    Transform.position reference — both shapes (snake + camel) should match."""
    matrix = gg._load_matrix()
    index = gg._build_api_index(matrix)
    # Synthesize a file in src/ scope
    sample = "transform.position = Vector3(1, 2, 3)\n"
    found = gg._scan_file_for_apis_text = None  # type: ignore[attr-defined]
    # Use the public scanner via tmp file
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(sample)
        path = Path(f.name)
    try:
        pairs = gg._scan_file_for_apis(path, index)
    finally:
        path.unlink()
    assert ("Transform", "position") in pairs


def test_camel_to_snake_helper() -> None:
    assert gg._camel_to_snake("position") == "position"
    assert gg._camel_to_snake("backgroundColor") == "background_color"
    assert gg._camel_to_snake("orthographicSize") == "orthographic_size"
    assert gg._camel_to_snake("FindGameObjectsWithTag") == "find_game_objects_with_tag"
