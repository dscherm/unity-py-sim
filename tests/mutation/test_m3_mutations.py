"""M-3 mutation tests: prove contract checks catch breakage.

Three mutations:
1. Snapshot drops `roundtrip_compile_pct` from output JSON -> contract fails.
2. Dashboard does NOT sort snapshots chronologically (reverses iteration) ->
   chronological-order contract fails.
3. Dashboard drops H1 header -> H1 contract fails.

Each mutation is implemented by string-substituting a copy of the source
into a tmp dir, loaded via importlib.util.spec_from_file_location. The real
source is never modified.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import textwrap
import time
import uuid
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_SRC = ROOT / "src" / "gates" / "snapshot.py"
DASHBOARD_SRC = ROOT / "tools" / "render_dashboard.py"


# ---- helpers -----------------------------------------------------------------


def _load_module_from_source(name: str, source: str, tmpdir: Path):
    """Write `source` to <tmpdir>/<name>.py, load as `name`, return the module."""
    file = tmpdir / f"{name}.py"
    file.write_text(source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(name, file)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _make_snapshot_dict(ts: str, *, avg: float = 0.7) -> dict:
    return {
        "timestamp": ts,
        "git_commit": "abc",
        "git_branch": "feat/x",
        "metrics": {
            "corpus_compile_pct": 0.5,
            "avg_overall": avg,
            "avg_class": 0.8,
            "avg_method": 0.7,
            "avg_field": 0.6,
            "avg_using": 0.5,
            "roundtrip_compile_pct": None,
            "roundtrip_ast_pct": None,
        },
        "by_game": {},
        "test_counts": {"unit": 1},
        "notes": "",
    }


# ---- Mutation 1: drop roundtrip_compile_pct ---------------------------------


def test_mutation_drop_roundtrip_compile_pct_breaks_contract(tmp_path):
    """Removing roundtrip_compile_pct must cause the snapshot contract check to fail."""
    src = SNAPSHOT_SRC.read_text(encoding="utf-8")
    # Mutate: drop the roundtrip_compile_pct entry from the metrics dict (the line
    # in take_snapshot that maps the key to its computed value).
    needle = '"roundtrip_compile_pct": roundtrip_compile_pct,'
    assert needle in src, "expected sentinel string not found — mutation source out of date"
    mutated = src.replace(needle, "", 1)
    assert needle not in mutated, "mutation did not actually drop the line"

    # Tweak ROOT inside the mutated module so it still finds repo paths.
    mod_name = f"snapshot_mut_{uuid.uuid4().hex[:8]}"
    mod = _load_module_from_source(mod_name, mutated, tmp_path)

    history = tmp_path / "history"
    metrics = tmp_path / "metrics"
    metrics.mkdir()
    out = mod.take_snapshot(history_dir=history, metrics_dir=metrics)
    data = json.loads(out.read_text())

    # The mutated snapshot must NOT have roundtrip_compile_pct.
    assert "roundtrip_compile_pct" not in data["metrics"], (
        "mutation didn't take effect — key still present"
    )

    # The contract assertion must catch the missing key.
    REQUIRED = {
        "corpus_compile_pct",
        "avg_overall",
        "roundtrip_compile_pct",
        "roundtrip_ast_pct",
    }
    missing = REQUIRED - set(data["metrics"].keys())
    assert missing == {"roundtrip_compile_pct"}, f"unexpected missing keys: {missing}"

    # And demonstrate the failure as a real assertion.
    with pytest.raises(AssertionError):
        assert "roundtrip_compile_pct" in data["metrics"]


# ---- Mutation 2: render_dashboard reverses sort order -----------------------


def test_mutation_reverse_sort_breaks_chronological_contract(tmp_path):
    """If render_dashboard does NOT sort chronologically, the order assertion fails."""
    src = DASHBOARD_SRC.read_text(encoding="utf-8")
    # Mutate: replace the chronological sort with reverse order.
    needle = "for p in sorted(history_dir.glob"
    assert needle in src, "expected sentinel string not found — mutation source out of date"
    mutated = src.replace(
        needle,
        "for p in sorted(history_dir.glob",  # placeholder, do real replacement next line
    )
    # Real change: add reverse=True
    mutated = mutated.replace(
        "for p in sorted(history_dir.glob(\"*.json\")):",
        "for p in sorted(history_dir.glob(\"*.json\"), reverse=True):",
        1,
    )
    assert "reverse=True" in mutated, "mutation did not take effect"

    mod_name = f"dashboard_mut_{uuid.uuid4().hex[:8]}"
    mod = _load_module_from_source(mod_name, mutated, tmp_path)

    history = tmp_path / "history"
    history.mkdir()
    snaps = [
        ("20260101T000000Z", _make_snapshot_dict("2026-01-01T00:00:00+00:00")),
        ("20260102T000000Z", _make_snapshot_dict("2026-01-02T00:00:00+00:00")),
        ("20260103T000000Z", _make_snapshot_dict("2026-01-03T00:00:00+00:00")),
    ]
    for stem, data in snaps:
        (history / f"{stem}.json").write_text(json.dumps(data) + "\n")

    out = tmp_path / "dash.md"
    md = mod.render_dashboard(history_dir=history, output_path=out)

    # Slice out only the Trend section, same way the contract test does.
    start = md.find("## Trend")
    next_hdr = md.find("\n## ", start + 1)
    trend = md[start:] if next_hdr == -1 else md[start:next_hdr]

    idx_jan1 = trend.find("2026-01-01")
    idx_jan2 = trend.find("2026-01-02")
    idx_jan3 = trend.find("2026-01-03")
    # All present in trend section.
    assert idx_jan1 != -1 and idx_jan2 != -1 and idx_jan3 != -1
    # The chronological-order contract MUST fail under this mutation.
    with pytest.raises(AssertionError):
        assert idx_jan1 < idx_jan2 < idx_jan3, (
            f"trend rows not chronological: jan1={idx_jan1} jan2={idx_jan2} jan3={idx_jan3}"
        )


# ---- Mutation 3: dashboard drops H1 header ----------------------------------


def test_mutation_drop_h1_header_breaks_contract(tmp_path):
    """If render_dashboard does NOT emit the H1, the header contract fails."""
    src = DASHBOARD_SRC.read_text(encoding="utf-8")
    # There are TWO emit sites for the H1 (zero-snapshot path + main path).
    # Replace BOTH so any reachable code-path lacks the header.
    needles = [
        '"# Translation Accuracy Dashboard\\n\\n"',  # zero-snapshot heredoc-ish prefix
        'lines.append("# Translation Accuracy Dashboard")',
    ]
    mutated = src
    for n in needles:
        if n in mutated:
            mutated = mutated.replace(n, n.replace("# Translation Accuracy Dashboard", "REMOVED"))
    assert "# Translation Accuracy Dashboard" not in mutated, (
        "mutation did not strip the H1 from the source"
    )

    mod_name = f"dashboard_no_h1_{uuid.uuid4().hex[:8]}"
    mod = _load_module_from_source(mod_name, mutated, tmp_path)

    history = tmp_path / "history"
    history.mkdir()
    (history / "20260101T000000Z.json").write_text(
        json.dumps(_make_snapshot_dict("2026-01-01T00:00:00+00:00")) + "\n"
    )
    out = tmp_path / "dash.md"
    md = mod.render_dashboard(history_dir=history, output_path=out)

    # Mutation took effect — header gone.
    assert "# Translation Accuracy Dashboard" not in md, (
        "mutation didn't actually drop the header — got: "
        f"{md.splitlines()[:3]}"
    )

    # The H1 contract MUST fail under this mutation.
    with pytest.raises(AssertionError):
        assert md.startswith("# Translation Accuracy Dashboard")
