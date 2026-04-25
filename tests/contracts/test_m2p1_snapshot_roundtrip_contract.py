"""Contract tests for src.gates.snapshot's roundtrip metric derivation (M-2 phase 1).

Verifies the documented behavior of how take_snapshot consumes
data/metrics/roundtrip_baseline.json:

  - Absent file → roundtrip_compile_pct AND roundtrip_ast_pct == None.
  - With synthetic baseline (4 pairs: overall=1.0/0.5/0.0/0.0+error="x"):
      * roundtrip_compile_pct == 2/4 == 0.5  (overall>0 AND error is None)
      * roundtrip_ast_pct     == 1/4 == 0.25 (overall>=0.999 AND error is None)
      * roundtrip_avg_overall echoes the baseline's avg_overall verbatim.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.gates import snapshot as snapshot_mod  # noqa: E402


def _write_baseline(metrics_dir: Path, baseline: dict) -> None:
    metrics_dir.mkdir(parents=True, exist_ok=True)
    (metrics_dir / "roundtrip_baseline.json").write_text(json.dumps(baseline))


def _read_snapshot(history_dir: Path) -> dict:
    files = list(history_dir.glob("*.json"))
    assert len(files) == 1, f"expected 1 snapshot, got {len(files)}: {files}"
    return json.loads(files[0].read_text())


def test_absent_baseline_yields_null_roundtrip_metrics(tmp_path):
    metrics_dir = tmp_path / "metrics"
    metrics_dir.mkdir()
    history_dir = metrics_dir / "history"

    snapshot_mod.take_snapshot(history_dir=history_dir, metrics_dir=metrics_dir)
    snap = _read_snapshot(history_dir)

    metrics = snap["metrics"]
    assert metrics["roundtrip_compile_pct"] is None
    assert metrics["roundtrip_ast_pct"] is None


def test_synthetic_baseline_compile_and_ast_percentages(tmp_path):
    metrics_dir = tmp_path / "metrics"
    history_dir = metrics_dir / "history"

    baseline = {
        "total_pairs": 4,
        "succeeded": 3,
        "failed": 1,
        "avg_overall": 0.5,
        "by_game": {"x": {"count": 3, "avg_overall": 0.5}},
        "pairs": [
            {"id": "perfect", "game": "x", "overall": 1.0, "error": None},
            {"id": "partial", "game": "x", "overall": 0.5, "error": None},
            {"id": "zero",    "game": "x", "overall": 0.0, "error": None},
            {"id": "thrown",  "game": "x", "overall": 0.0, "error": "boom"},
        ],
    }
    _write_baseline(metrics_dir, baseline)
    snapshot_mod.take_snapshot(history_dir=history_dir, metrics_dir=metrics_dir)
    metrics = _read_snapshot(history_dir)["metrics"]

    # 2 of 4 pairs are error-free AND overall > 0 (1.0 and 0.5)
    assert metrics["roundtrip_compile_pct"] == pytest.approx(0.5)
    # 1 of 4 pairs is error-free AND overall >= 0.999 (only the 1.0 pair)
    assert metrics["roundtrip_ast_pct"] == pytest.approx(0.25)


def test_roundtrip_avg_overall_echoed_from_baseline(tmp_path):
    metrics_dir = tmp_path / "metrics"
    history_dir = metrics_dir / "history"

    baseline = {
        "total_pairs": 2,
        "succeeded": 2,
        "failed": 0,
        "avg_overall": 0.7777,  # arbitrary value snapshot must NOT recompute.
        "by_game": {},
        "pairs": [
            {"id": "a", "game": "x", "overall": 1.0, "error": None},
            {"id": "b", "game": "x", "overall": 0.5, "error": None},
        ],
    }
    _write_baseline(metrics_dir, baseline)
    snapshot_mod.take_snapshot(history_dir=history_dir, metrics_dir=metrics_dir)
    metrics = _read_snapshot(history_dir)["metrics"]

    assert metrics["roundtrip_avg_overall"] == 0.7777


def test_thrown_error_pair_does_not_count_as_compile(tmp_path):
    """A pair with overall=1.0 but error!=None must NOT count toward compile.

    Defensive: prevents a regression where a swallowed parser error that
    nevertheless populates a perfect-looking overall would be counted.
    """
    metrics_dir = tmp_path / "metrics"
    history_dir = metrics_dir / "history"
    baseline = {
        "total_pairs": 1,
        "succeeded": 0,
        "failed": 1,
        "avg_overall": 0.0,
        "by_game": {},
        "pairs": [
            # Pathological: nonzero overall but error set.
            {"id": "weird", "game": "x", "overall": 1.0, "error": "boom"},
        ],
    }
    _write_baseline(metrics_dir, baseline)
    snapshot_mod.take_snapshot(history_dir=history_dir, metrics_dir=metrics_dir)
    metrics = _read_snapshot(history_dir)["metrics"]

    assert metrics["roundtrip_compile_pct"] == pytest.approx(0.0)
    assert metrics["roundtrip_ast_pct"] == pytest.approx(0.0)


def test_zero_overall_no_error_does_not_count_as_compile(tmp_path):
    """Per the spec: roundtrip_compile_pct requires overall > 0 (NOT >= 0).

    A swallowed Python parse error returns overall=0.0 with error=None and
    must NOT register as 'compile-clean'.
    """
    metrics_dir = tmp_path / "metrics"
    history_dir = metrics_dir / "history"
    baseline = {
        "total_pairs": 2,
        "succeeded": 2,
        "failed": 0,
        "avg_overall": 0.5,
        "by_game": {},
        "pairs": [
            {"id": "good",    "game": "x", "overall": 1.0, "error": None},
            {"id": "swallow", "game": "x", "overall": 0.0, "error": None},
        ],
    }
    _write_baseline(metrics_dir, baseline)
    snapshot_mod.take_snapshot(history_dir=history_dir, metrics_dir=metrics_dir)
    metrics = _read_snapshot(history_dir)["metrics"]

    # Only 'good' counts.
    assert metrics["roundtrip_compile_pct"] == pytest.approx(0.5)
    assert metrics["roundtrip_ast_pct"] == pytest.approx(0.5)
