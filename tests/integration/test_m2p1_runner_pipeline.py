"""Integration tests for M-2 phase 1: runner E2E + workflow YAML order.

Two distinct integrations are exercised here:

  1. Synthetic-corpus E2E: build a tiny corpus_index.json + manifests +
     trivial Unity .cs files in tmp_path, invoke run_roundtrip_baseline as
     a subprocess (simulating CI), and assert the resulting JSON has the
     required structure and that the runner exited 0.

  2. Workflow YAML structure: parse `.github/workflows/test.yml` and
     verify the snapshot job exists and its steps appear in the
     documented order (deps → roundtrip baseline → snapshot → render
     dashboard → upload artifact).
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
RUNNER_PATH = ROOT / "tools" / "run_roundtrip_baseline.py"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "test.yml"


def _venv_python() -> str:
    candidate = ROOT / ".venv" / "Scripts" / "python.exe"
    if candidate.exists():
        return str(candidate)
    return sys.executable


def _write_csharp(p: Path, name: str, body: str = "    public int x;") -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        f"using UnityEngine;\n\npublic class {name} : MonoBehaviour\n{{\n{body}\n}}\n",
        encoding="utf-8",
    )


def _build_synth_corpus(tmp_path: Path, n: int = 2) -> Path:
    corpus_dir = tmp_path / "corpus"
    pairs_dir = corpus_dir / "pairs"
    pairs_dir.mkdir(parents=True, exist_ok=True)

    index = []
    for i in range(n):
        pid = f"synth_{i:03d}"
        cs_path = tmp_path / f"Synth{i}.cs"
        _write_csharp(cs_path, f"Synth{i}")
        manifest = {
            "id": pid,
            "game": "synthetic",
            "unity_file": str(cs_path),
        }
        (pairs_dir / f"{pid}.json").write_text(json.dumps(manifest))
        index.append({"id": pid, "game": "synthetic", "file": f"pairs/{pid}.json"})

    index_path = corpus_dir / "corpus_index.json"
    index_path.write_text(json.dumps(index))
    return index_path


def test_runner_subprocess_e2e_writes_valid_output(tmp_path):
    """Run tools/run_roundtrip_baseline.py as a subprocess on a synthetic corpus.

    Asserts: exit code 0, output JSON exists, and has the documented schema.
    """
    index = _build_synth_corpus(tmp_path, n=2)
    out = tmp_path / "out.json"

    env = os.environ.copy()
    # Ensure the runner can import src.* by setting cwd to ROOT.
    proc = subprocess.run(
        [
            _venv_python(),
            str(RUNNER_PATH),
            "--corpus-index", str(index),
            "--output", str(out),
        ],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, (
        f"runner exited {proc.returncode}\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    assert out.exists(), "runner did not write output file"
    data = json.loads(out.read_text())

    for key in ("total_pairs", "succeeded", "failed", "avg_overall", "by_game", "pairs"):
        assert key in data
    assert data["total_pairs"] == 2
    assert data["succeeded"] + data["failed"] == 2
    # The synthetic.count entry should match succeeded if any pair was error-free.
    if data["succeeded"] > 0:
        assert data["by_game"]["synthetic"]["count"] == data["succeeded"]


def test_runner_module_run_baseline_returns_summary(tmp_path):
    """Exercise the in-process API (run_baseline) — same contract as subprocess.

    This test exists to catch the case where the function returns dict but
    the script doesn't. They should agree.
    """
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("_m2p1_inproc", str(RUNNER_PATH))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    index = _build_synth_corpus(tmp_path, n=2)
    out = tmp_path / "out.json"
    summary = mod.run_baseline(index, out)
    assert isinstance(summary, dict)
    assert summary["total_pairs"] == 2
    assert out.exists()
    on_disk = json.loads(out.read_text())
    assert on_disk["total_pairs"] == summary["total_pairs"]


# ---------------------------------------------------------------------------
# Workflow YAML order tests
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def workflow_doc():
    assert WORKFLOW_PATH.exists(), f"missing {WORKFLOW_PATH}"
    return yaml.safe_load(WORKFLOW_PATH.read_text())


def test_workflow_yaml_parses(workflow_doc):
    assert isinstance(workflow_doc, dict)
    assert "jobs" in workflow_doc


def test_workflow_has_snapshot_job(workflow_doc):
    jobs = workflow_doc["jobs"]
    assert "snapshot" in jobs, f"snapshot job missing; jobs={list(jobs.keys())}"
    snap = jobs["snapshot"]
    assert "steps" in snap


def _step_indices(steps: list[dict], substrings: list[str]) -> dict[str, int]:
    """Return {substring: first index whose `run` contains it}."""
    found: dict[str, int] = {}
    for i, step in enumerate(steps):
        run = step.get("run", "") or ""
        if not isinstance(run, str):
            continue
        for needle in substrings:
            if needle in run and needle not in found:
                found[needle] = i
    return found


def test_workflow_snapshot_steps_in_documented_order(workflow_doc):
    """Documented order:
       dependency install → roundtrip baseline → snapshot → render dashboard → upload artifact
    """
    steps = workflow_doc["jobs"]["snapshot"]["steps"]
    assert len(steps) >= 5, f"expected >=5 steps, got {len(steps)}"

    needles = [
        "pip install -r requirements.txt",  # dependency install
        "tools/run_roundtrip_baseline.py",  # roundtrip baseline
        "src.gates.snapshot",                # snapshot
        "tools/render_dashboard.py",         # render dashboard
    ]
    idx = _step_indices(steps, needles)
    for n in needles:
        assert n in idx, f"step containing {n!r} not found"

    install_i = idx["pip install -r requirements.txt"]
    baseline_i = idx["tools/run_roundtrip_baseline.py"]
    snapshot_i = idx["src.gates.snapshot"]
    dashboard_i = idx["tools/render_dashboard.py"]

    assert install_i < baseline_i < snapshot_i < dashboard_i, (
        f"steps out of order: install={install_i} baseline={baseline_i} "
        f"snapshot={snapshot_i} dashboard={dashboard_i}"
    )

    # Upload artifact step is the LAST step (uses `uses: actions/upload-artifact`).
    upload_idx = None
    for i, s in enumerate(steps):
        uses = s.get("uses", "")
        if isinstance(uses, str) and uses.startswith("actions/upload-artifact"):
            upload_idx = i
            break
    assert upload_idx is not None, "upload-artifact step missing"
    assert upload_idx > dashboard_i, (
        f"upload-artifact step (i={upload_idx}) must come after render-dashboard (i={dashboard_i})"
    )


def test_workflow_baseline_step_continues_on_error(workflow_doc):
    """The baseline step must use continue-on-error so a flaky runner
    doesn't block the snapshot job (per commit message intent)."""
    steps = workflow_doc["jobs"]["snapshot"]["steps"]
    for s in steps:
        run = s.get("run", "") or ""
        if isinstance(run, str) and "tools/run_roundtrip_baseline.py" in run:
            assert s.get("continue-on-error") is True, (
                "baseline step should set continue-on-error: true"
            )
            return
    pytest.fail("baseline step not found in snapshot job")
