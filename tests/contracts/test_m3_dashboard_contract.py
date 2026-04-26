"""M-3 contract tests for tools.render_dashboard.

These tests validate the documented behavior of `render_dashboard`:
- Always emits H1 `# Translation Accuracy Dashboard`.
- With zero snapshots: contains `_No snapshots yet._`.
- With 1+ snapshots: contains `## Latest Snapshot`, `## Trend (last N snapshots)`.
- Trend table rows are in chronological order (oldest first, newest last).
- Δ arrows: `→` equal, `↑` increase, `↓` decrease, blank when null.

Loaded as a top-level module via importlib because tools/ is not a package.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
DASHBOARD_PATH = ROOT / "tools" / "render_dashboard.py"


def _load_render_dashboard():
    """Load tools/render_dashboard.py as a fresh module."""
    spec = importlib.util.spec_from_file_location(
        "render_dashboard_under_test", DASHBOARD_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["render_dashboard_under_test"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def render_module():
    return _load_render_dashboard()


def _make_snapshot(
    ts: str,
    *,
    corpus: float | None = 0.5,
    avg: float | None = 0.7,
    rt_compile: float | None = None,
) -> dict:
    return {
        "timestamp": ts,
        "git_commit": "abc1234",
        "git_branch": "feat/test",
        "metrics": {
            "corpus_compile_pct": corpus,
            "avg_overall": avg,
            "avg_class": 0.8,
            "avg_method": 0.7,
            "avg_field": 0.6,
            "avg_using": 0.5,
            "roundtrip_compile_pct": rt_compile,
            "roundtrip_ast_pct": None,
        },
        "by_game": {},
        "test_counts": {"unit": 10, "contracts": 5},
        "notes": "",
    }


def _write_history(history_dir: Path, snapshots: list[tuple[str, dict]]) -> None:
    """Write each (filename_stem, snapshot_dict) into history_dir/<stem>.json."""
    history_dir.mkdir(parents=True, exist_ok=True)
    for stem, data in snapshots:
        (history_dir / f"{stem}.json").write_text(json.dumps(data) + "\n")


# ---- tests -------------------------------------------------------------------


def test_dashboard_emits_h1_header(render_module, tmp_path):
    history = tmp_path / "h"
    _write_history(history, [("20260101T000000Z", _make_snapshot("2026-01-01T00:00:00+00:00"))])
    out = tmp_path / "dash.md"
    md = render_module.render_dashboard(history_dir=history, output_path=out)
    assert md.startswith("# Translation Accuracy Dashboard")


def test_dashboard_zero_snapshots_message(render_module, tmp_path):
    history = tmp_path / "empty_history"
    history.mkdir()
    out = tmp_path / "dash.md"
    md = render_module.render_dashboard(history_dir=history, output_path=out)
    assert "# Translation Accuracy Dashboard" in md
    assert "_No snapshots yet._" in md


def test_dashboard_has_latest_section_when_snapshots(render_module, tmp_path):
    history = tmp_path / "h"
    _write_history(history, [("20260101T000000Z", _make_snapshot("2026-01-01T00:00:00+00:00"))])
    out = tmp_path / "dash.md"
    md = render_module.render_dashboard(history_dir=history, output_path=out)
    assert "## Latest Snapshot" in md


def test_dashboard_trend_section_label_uses_actual_count(render_module, tmp_path):
    history = tmp_path / "h"
    _write_history(
        history,
        [
            ("20260101T000000Z", _make_snapshot("2026-01-01T00:00:00+00:00")),
            ("20260102T000000Z", _make_snapshot("2026-01-02T00:00:00+00:00")),
            ("20260103T000000Z", _make_snapshot("2026-01-03T00:00:00+00:00")),
        ],
    )
    out = tmp_path / "dash.md"
    md = render_module.render_dashboard(history_dir=history, output_path=out, last_n=10)
    # We have 3 snapshots and last_n=10 — header should reflect actual count (3).
    assert "## Trend (last 3 snapshots)" in md


def _extract_trend_section(md: str) -> str:
    """Slice out only the Trend table section to avoid Latest-Snapshot timestamps."""
    start = md.find("## Trend")
    assert start != -1, "no Trend section found in dashboard"
    # End at the next '## ' header or EOF.
    next_hdr = md.find("\n## ", start + 1)
    return md[start:] if next_hdr == -1 else md[start:next_hdr]


def test_dashboard_trend_chronological_order(render_module, tmp_path):
    """First trend row must be the oldest snapshot, last row must be newest."""
    history = tmp_path / "h"
    _write_history(
        history,
        [
            ("20260101T000000Z", _make_snapshot("2026-01-01T00:00:00+00:00")),
            ("20260102T000000Z", _make_snapshot("2026-01-02T00:00:00+00:00")),
            ("20260103T000000Z", _make_snapshot("2026-01-03T00:00:00+00:00")),
        ],
    )
    out = tmp_path / "dash.md"
    md = render_module.render_dashboard(history_dir=history, output_path=out)
    trend = _extract_trend_section(md)
    idx_jan1 = trend.find("2026-01-01")
    idx_jan2 = trend.find("2026-01-02")
    idx_jan3 = trend.find("2026-01-03")
    assert idx_jan1 != -1 and idx_jan2 != -1 and idx_jan3 != -1
    assert idx_jan1 < idx_jan2 < idx_jan3, (
        f"trend rows not chronological: jan1={idx_jan1} jan2={idx_jan2} jan3={idx_jan3}"
    )


def test_dashboard_arrow_equal(render_module, tmp_path):
    """Equal current vs prior produces → arrow."""
    history = tmp_path / "h"
    _write_history(
        history,
        [
            ("20260101T000000Z", _make_snapshot("2026-01-01T00:00:00+00:00", avg=0.5)),
            ("20260102T000000Z", _make_snapshot("2026-01-02T00:00:00+00:00", avg=0.5)),
        ],
    )
    out = tmp_path / "dash.md"
    md = render_module.render_dashboard(history_dir=history, output_path=out)
    # Latest summary table has a Δ column. With current==prior, expect →.
    assert "→" in md, "expected → arrow when current==prior"


def test_dashboard_arrow_up(render_module, tmp_path):
    """Increasing current vs prior produces ↑ arrow."""
    history = tmp_path / "h"
    _write_history(
        history,
        [
            ("20260101T000000Z", _make_snapshot("2026-01-01T00:00:00+00:00", avg=0.5)),
            ("20260102T000000Z", _make_snapshot("2026-01-02T00:00:00+00:00", avg=0.7)),
        ],
    )
    out = tmp_path / "dash.md"
    md = render_module.render_dashboard(history_dir=history, output_path=out)
    assert "↑" in md, "expected ↑ arrow when current>prior"


def test_dashboard_arrow_down(render_module, tmp_path):
    """Decreasing current vs prior produces ↓ arrow."""
    history = tmp_path / "h"
    _write_history(
        history,
        [
            ("20260101T000000Z", _make_snapshot("2026-01-01T00:00:00+00:00", avg=0.7)),
            ("20260102T000000Z", _make_snapshot("2026-01-02T00:00:00+00:00", avg=0.3)),
        ],
    )
    out = tmp_path / "dash.md"
    md = render_module.render_dashboard(history_dir=history, output_path=out)
    assert "↓" in md, "expected ↓ arrow when current<prior"


def test_dashboard_arrow_blank_when_null(render_module, tmp_path):
    """When prior or current is null, arrow column is blank (no arrow char)."""
    history = tmp_path / "h"
    # Roundtrip metrics are null in both — expect blank arrow on those rows.
    _write_history(
        history,
        [
            ("20260101T000000Z", _make_snapshot("2026-01-01T00:00:00+00:00", rt_compile=None)),
            ("20260102T000000Z", _make_snapshot("2026-01-02T00:00:00+00:00", rt_compile=None)),
        ],
    )
    out = tmp_path / "dash.md"
    md = render_module.render_dashboard(history_dir=history, output_path=out)
    # Find the roundtrip-compile row in the latest summary table.
    rt_lines = [
        line for line in md.splitlines()
        if "Roundtrip compile" in line and "|" in line
    ]
    assert rt_lines, "expected a Roundtrip compile row in latest summary"
    rt_row = rt_lines[0]
    # The trailing arrow column for two nulls should not contain an arrow.
    for arrow in ("↑", "↓", "→"):
        assert arrow not in rt_row, f"unexpected {arrow} in null-vs-null row: {rt_row}"


def test_dashboard_writes_output_file(render_module, tmp_path):
    """render_dashboard persists output to disk."""
    history = tmp_path / "h"
    _write_history(history, [("20260101T000000Z", _make_snapshot("2026-01-01T00:00:00+00:00"))])
    out = tmp_path / "subdir" / "dash.md"
    md = render_module.render_dashboard(history_dir=history, output_path=out)
    assert out.exists()
    assert out.read_text() == md
