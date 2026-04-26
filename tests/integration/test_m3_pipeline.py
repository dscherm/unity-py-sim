"""M-3 integration tests: end-to-end snapshot -> render pipeline + CI workflow.

- Take 3 snapshots via take_snapshot, render dashboard, assert 3 trend rows
  in chronological order.
- Run snapshot module + render_dashboard tool via subprocess; both exit 0.
- The GitHub Actions workflow YAML parses, has a `snapshot` job under `jobs`,
  push-only guard, and uploads an artifact whose name includes ${{ github.sha }}.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[2]
PYTHON = sys.executable  # current venv python — works on Windows + Linux
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "test.yml"
DASHBOARD_TOOL = ROOT / "tools" / "render_dashboard.py"


# ---- e2e snapshot -> render --------------------------------------------------


def _load_render_module():
    spec = importlib.util.spec_from_file_location(
        "render_dashboard_pipeline_test", DASHBOARD_TOOL
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_three_snapshots_render_to_three_trend_rows(tmp_path):
    """Three back-to-back snapshots -> 3 trend rows in chronological order."""
    from src.gates import snapshot as snapshot_module

    history = tmp_path / "history"
    metrics = ROOT / "data" / "metrics"  # use real baseline files for realism

    out_paths = []
    for i in range(3):
        out = snapshot_module.take_snapshot(
            history_dir=history,
            notes=f"snap-{i}",
            metrics_dir=metrics,
        )
        out_paths.append(out)
        if i < 2:
            time.sleep(1.05)  # ensure UTC second tick advances

    # Three distinct files written.
    assert len(set(out_paths)) == 3, f"expected 3 unique snapshot files, got {out_paths}"

    # Render the dashboard.
    render_mod = _load_render_module()
    dash = tmp_path / "dash.md"
    md = render_mod.render_dashboard(history_dir=history, output_path=dash)

    # 3 trend rows.
    assert "## Trend (last 3 snapshots)" in md

    # Chronological: slice out the Trend section so the Latest-Snapshot
    # timestamp doesn't pollute the lookup, then assert order.
    start = md.find("## Trend")
    next_hdr = md.find("\n## ", start + 1)
    trend = md[start:] if next_hdr == -1 else md[start:next_hdr]

    snaps = [json.loads(p.read_text()) for p in sorted(out_paths)]
    ts_indices = [trend.find(s["timestamp"][:19]) for s in snaps]
    assert all(i != -1 for i in ts_indices), (
        f"snapshot timestamps not all in trend section: {ts_indices}"
    )
    assert ts_indices == sorted(ts_indices), (
        f"trend rows not chronological: {ts_indices}"
    )


# ---- subprocess module entrypoints ------------------------------------------


def test_snapshot_module_runs_via_subprocess(tmp_path):
    """`python -m src.gates.snapshot --notes "test" --output-dir <tmp>` exits 0."""
    out_dir = tmp_path / "history"
    result = subprocess.run(
        [PYTHON, "-m", "src.gates.snapshot", "--notes", "test", "--output-dir", str(out_dir)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"stderr={result.stderr}\nstdout={result.stdout}"
    files = list(out_dir.glob("*.json"))
    assert len(files) == 1, f"expected 1 snapshot file, got {files}"


def test_render_dashboard_tool_runs_via_subprocess(tmp_path):
    """`python tools/render_dashboard.py --history-dir <tmp> --output <tmp>/dash.md` exits 0."""
    history = tmp_path / "history"
    history.mkdir()
    # Empty history is allowed — emits the "no snapshots yet" placeholder.
    out_md = tmp_path / "dash.md"
    result = subprocess.run(
        [
            PYTHON,
            str(DASHBOARD_TOOL),
            "--history-dir",
            str(history),
            "--output",
            str(out_md),
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, f"stderr={result.stderr}\nstdout={result.stdout}"
    assert out_md.exists()
    assert "# Translation Accuracy Dashboard" in out_md.read_text()


# ---- CI workflow contract ---------------------------------------------------


@pytest.fixture(scope="module")
def workflow_data():
    assert WORKFLOW_PATH.exists(), f"missing workflow file: {WORKFLOW_PATH}"
    return yaml.safe_load(WORKFLOW_PATH.read_text())


def test_workflow_yaml_parses(workflow_data):
    assert isinstance(workflow_data, dict)
    assert "jobs" in workflow_data


def test_workflow_has_snapshot_job(workflow_data):
    assert "snapshot" in workflow_data["jobs"], (
        f"snapshot job missing — jobs: {list(workflow_data['jobs'])}"
    )


def test_snapshot_job_is_push_guarded(workflow_data):
    """Snapshot job must guard with `if: github.event_name == 'push'`."""
    snap = workflow_data["jobs"]["snapshot"]
    if_clause = snap.get("if", "")
    assert "github.event_name" in if_clause and "push" in if_clause, (
        f"snapshot job missing push guard: if={if_clause!r}"
    )


def test_snapshot_job_uploads_artifact_with_sha_name(workflow_data):
    """Snapshot job must upload an artifact whose name includes ${{ github.sha }}."""
    snap = workflow_data["jobs"]["snapshot"]
    steps = snap.get("steps", [])
    upload_steps = [
        s for s in steps if isinstance(s, dict) and "upload-artifact" in str(s.get("uses", ""))
    ]
    assert upload_steps, "snapshot job has no upload-artifact step"
    upload = upload_steps[0]
    name = upload.get("with", {}).get("name", "")
    assert "github.sha" in name, f"artifact name missing github.sha: {name!r}"
