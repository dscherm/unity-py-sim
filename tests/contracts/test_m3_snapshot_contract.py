"""M-3 contract tests for src.gates.snapshot.

These tests validate the documented behavior of `take_snapshot`:
- Output filename matches `YYYYMMDDTHHMMSSZ.json` (UTC ISO compact).
- Top-level keys: timestamp, git_commit, git_branch, metrics, by_game,
  test_counts, notes.
- `metrics` dict has corpus_compile_pct, avg_overall, roundtrip_compile_pct,
  roundtrip_ast_pct (last two MUST be null).
- The source baseline.json / compilation_baseline.json files are not
  modified by taking a snapshot (read-only behavior).

Tests derive expectations from the M-3 spec, not from the implementation.
"""

from __future__ import annotations

import json
import re
import shutil
import tempfile
from pathlib import Path

import pytest

# Module under test (real code).
from src.gates import snapshot as snapshot_module


# ---- helpers -----------------------------------------------------------------


FILENAME_RE = re.compile(r"^\d{8}T\d{6}Z\.json$")

REQUIRED_TOP_LEVEL = {
    "timestamp",
    "git_commit",
    "git_branch",
    "metrics",
    "by_game",
    "test_counts",
    "notes",
}

REQUIRED_METRIC_KEYS = {
    "corpus_compile_pct",
    "avg_overall",
    "roundtrip_compile_pct",
    "roundtrip_ast_pct",
}


def assert_snapshot_shape(snap: dict) -> None:
    """Reusable structural checks on a snapshot dict.

    Imported by mutation tests to assert that mutated outputs no longer
    satisfy the contract.
    """
    missing = REQUIRED_TOP_LEVEL - set(snap.keys())
    assert not missing, f"missing top-level keys: {missing}"

    metrics = snap["metrics"]
    assert isinstance(metrics, dict)
    missing_m = REQUIRED_METRIC_KEYS - set(metrics.keys())
    assert not missing_m, f"missing metric keys: {missing_m}"

    # Roundtrip must be null until M-2 ships.
    assert metrics["roundtrip_compile_pct"] is None
    assert metrics["roundtrip_ast_pct"] is None


# ---- fixtures ----------------------------------------------------------------


@pytest.fixture()
def isolated_metrics_dir():
    """Copy of the real baseline files into a tmp dir for read-only checks."""
    src = Path(__file__).resolve().parents[2] / "data" / "metrics"
    with tempfile.TemporaryDirectory() as tmp:
        dst = Path(tmp) / "metrics"
        dst.mkdir()
        for name in ("baseline.json", "compilation_baseline.json"):
            real = src / name
            if real.exists():
                shutil.copy2(real, dst / name)
        history = dst / "history"
        history.mkdir()
        yield dst, history


# ---- tests -------------------------------------------------------------------


def test_snapshot_filename_format(isolated_metrics_dir):
    """Filename must match YYYYMMDDTHHMMSSZ.json (UTC ISO compact)."""
    metrics_dir, history_dir = isolated_metrics_dir
    out = snapshot_module.take_snapshot(history_dir=history_dir, metrics_dir=metrics_dir)
    assert out.exists()
    assert FILENAME_RE.match(out.name), f"bad filename: {out.name}"


def test_snapshot_has_required_top_level_keys(isolated_metrics_dir):
    """Snapshot JSON must contain documented top-level keys."""
    metrics_dir, history_dir = isolated_metrics_dir
    out = snapshot_module.take_snapshot(history_dir=history_dir, metrics_dir=metrics_dir)
    data = json.loads(out.read_text())
    assert_snapshot_shape(data)


def test_snapshot_metrics_contain_corpus_compile_pct(isolated_metrics_dir):
    metrics_dir, history_dir = isolated_metrics_dir
    out = snapshot_module.take_snapshot(history_dir=history_dir, metrics_dir=metrics_dir)
    data = json.loads(out.read_text())
    assert "corpus_compile_pct" in data["metrics"]


def test_snapshot_metrics_contain_avg_overall(isolated_metrics_dir):
    metrics_dir, history_dir = isolated_metrics_dir
    out = snapshot_module.take_snapshot(history_dir=history_dir, metrics_dir=metrics_dir)
    data = json.loads(out.read_text())
    assert "avg_overall" in data["metrics"]


def test_snapshot_roundtrip_metrics_are_null(isolated_metrics_dir):
    """Roundtrip metrics must be null until M-2 delivers the bidirectional gate."""
    metrics_dir, history_dir = isolated_metrics_dir
    out = snapshot_module.take_snapshot(history_dir=history_dir, metrics_dir=metrics_dir)
    data = json.loads(out.read_text())
    assert data["metrics"]["roundtrip_compile_pct"] is None
    assert data["metrics"]["roundtrip_ast_pct"] is None


def test_snapshot_does_not_mutate_baseline(isolated_metrics_dir):
    """take_snapshot must be read-only against baseline.json."""
    metrics_dir, history_dir = isolated_metrics_dir
    baseline_path = metrics_dir / "baseline.json"
    if not baseline_path.exists():
        pytest.skip("baseline.json not present in fixture")
    before_bytes = baseline_path.read_bytes()
    snapshot_module.take_snapshot(history_dir=history_dir, metrics_dir=metrics_dir)
    after_bytes = baseline_path.read_bytes()
    assert before_bytes == after_bytes


def test_snapshot_does_not_mutate_compilation_baseline(isolated_metrics_dir):
    """take_snapshot must be read-only against compilation_baseline.json."""
    metrics_dir, history_dir = isolated_metrics_dir
    comp_path = metrics_dir / "compilation_baseline.json"
    if not comp_path.exists():
        pytest.skip("compilation_baseline.json not present in fixture")
    before_bytes = comp_path.read_bytes()
    snapshot_module.take_snapshot(history_dir=history_dir, metrics_dir=metrics_dir)
    after_bytes = comp_path.read_bytes()
    assert before_bytes == after_bytes


def test_snapshot_notes_passed_through(isolated_metrics_dir):
    metrics_dir, history_dir = isolated_metrics_dir
    out = snapshot_module.take_snapshot(
        history_dir=history_dir,
        notes="hello-world",
        metrics_dir=metrics_dir,
    )
    data = json.loads(out.read_text())
    assert data["notes"] == "hello-world"


def test_snapshot_test_counts_dict(isolated_metrics_dir):
    """test_counts must be a dict of int counts."""
    metrics_dir, history_dir = isolated_metrics_dir
    out = snapshot_module.take_snapshot(history_dir=history_dir, metrics_dir=metrics_dir)
    data = json.loads(out.read_text())
    assert isinstance(data["test_counts"], dict)
    for _, v in data["test_counts"].items():
        assert isinstance(v, int)


def test_snapshot_handles_missing_baseline_files():
    """Absent baseline files yield a snapshot with null metrics, not crash."""
    with tempfile.TemporaryDirectory() as tmp:
        empty_metrics = Path(tmp) / "metrics"
        empty_metrics.mkdir()
        history_dir = empty_metrics / "history"
        out = snapshot_module.take_snapshot(history_dir=history_dir, metrics_dir=empty_metrics)
        data = json.loads(out.read_text())
        # Top-level shape still valid.
        assert_snapshot_shape(data)
        # Corpus metrics are None when files absent.
        assert data["metrics"]["corpus_compile_pct"] is None
        assert data["metrics"]["avg_overall"] is None
