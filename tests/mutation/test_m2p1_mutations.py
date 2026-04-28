"""Mutation tests for M-2 phase 1.

Two mutations, each must be caught by an assertion derived from the spec:

  A. Snapshot mutation: drop the `> 0` filter from the _scored predicate
     in src/gates/snapshot.py — this would let zero-overall pairs (e.g.
     swallowed Python parser errors) count as "compiled". With a
     synthetic baseline of 50% real failures, the mutated metric goes
     to 1.0 instead of 0.5, which is wrong.

  B. Runner mutation: drop the `sorted(...)` call from
     tools/run_roundtrip_baseline.py — this breaks the worst-first
     ordering contract on the output's `pairs` list.

Mutations are applied by string-substituting the source into a tmp dir
and loading the file via importlib.util — the real source files are
never touched.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import uuid
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
SNAPSHOT_SRC = ROOT / "src" / "gates" / "snapshot.py"
RUNNER_SRC = ROOT / "tools" / "run_roundtrip_baseline.py"


# ---------------------------------------------------------------------------
# Mutation A — snapshot's _scored predicate
# ---------------------------------------------------------------------------

def _load_mutated_module(mod_name: str, src_text: str, tmp_path: Path):
    """Write `src_text` to tmp_path/<unique>.py and load it as `mod_name`."""
    fname = f"{mod_name}_{uuid.uuid4().hex}.py"
    p = tmp_path / fname
    p.write_text(src_text, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(mod_name, str(p))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


def _build_synth_baseline(metrics_dir: Path, pairs: list[dict]) -> None:
    metrics_dir.mkdir(parents=True, exist_ok=True)
    (metrics_dir / "roundtrip_baseline.json").write_text(json.dumps({
        "total_pairs": len(pairs),
        "succeeded": sum(1 for p in pairs if p.get("error") is None),
        "failed": sum(1 for p in pairs if p.get("error") is not None),
        "avg_overall": 0.0,
        "by_game": {},
        "pairs": pairs,
    }))


def test_mutation_A_drops_overall_gt_zero_filter(tmp_path):
    """Mutate snapshot's `_scored` predicate so it ignores `> 0`.

    Synthetic baseline: 4 pairs, 2 with overall=0.0/error=None (50% real
    fails) and 2 with overall=1.0/error=None.

    Original metric: roundtrip_compile_pct = 2/4 = 0.5
    Mutated metric:  roundtrip_compile_pct = 4/4 = 1.0  ← WRONG
    """
    src = SNAPSHOT_SRC.read_text(encoding="utf-8")
    mutant = src.replace(
        'return isinstance(p, dict) and p.get("error") is None and p.get("overall", 0) > 0',
        'return isinstance(p, dict) and p.get("error") is None',
    )
    assert mutant != src, "mutation A: substring not found in source"

    mutated_mod = _load_mutated_module("m2p1_mutA_snapshot", mutant, tmp_path)

    metrics_dir = tmp_path / "metrics"
    history_dir = metrics_dir / "history"
    _build_synth_baseline(metrics_dir, [
        {"id": "perfect1", "game": "x", "overall": 1.0, "error": None},
        {"id": "perfect2", "game": "x", "overall": 1.0, "error": None},
        {"id": "swallow1", "game": "x", "overall": 0.0, "error": None},
        {"id": "swallow2", "game": "x", "overall": 0.0, "error": None},
    ])
    mutated_mod.take_snapshot(history_dir=history_dir, metrics_dir=metrics_dir)
    snap_files = list(history_dir.glob("*.json"))
    assert snap_files, "no snapshot written"
    snap = json.loads(snap_files[0].read_text())
    mutated_pct = snap["metrics"]["roundtrip_compile_pct"]

    # The mutation makes it 1.0 (4/4); the correct answer is 0.5 (2/4).
    assert mutated_pct == pytest.approx(1.0), (
        f"expected mutated value 1.0 (caught by spec), got {mutated_pct}"
    )
    assert mutated_pct != pytest.approx(0.5), (
        "mutation didn't change behavior — predicate may be reachable via another path"
    )


# ---------------------------------------------------------------------------
# Mutation B — runner sort
# ---------------------------------------------------------------------------

def _write_csharp(p: Path, name: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        f"using UnityEngine;\n\npublic class {name} : MonoBehaviour\n{{\n    public int x;\n}}\n",
        encoding="utf-8",
    )


def test_mutation_B_drops_sort_breaks_worst_first(tmp_path):
    """Drop the sorted(...) call in the runner.

    Synthetic corpus deliberately ordered "best, worst, middle" by
    construction:
      - pair_0: trivial valid C# → high overall
      - pair_1: bad unity_file path → error → overall 0.0
      - pair_2: trivial valid C# → high overall

    Sorted output (worst-first) places pair_1 first.  The mutated output
    keeps insertion order, so pair_0 (high overall) is first — failing
    the worst-first invariant.
    """
    src = RUNNER_SRC.read_text(encoding="utf-8")
    # Replace the sorted(...) wrapper inside the summary dict with an
    # unsorted reference to pairs_out.
    mutant = src.replace(
        'sorted(pairs_out, key=lambda p: p["overall"])',
        "pairs_out",
    )
    assert mutant != src, "mutation B: substring not found in source"

    # Patch the path so `ROOT` and `from src.gates...` still resolve.
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    mutated_mod = _load_mutated_module("m2p1_mutB_runner", mutant, tmp_path)

    # Build a synthetic corpus where insertion order has the errored pair
    # in the MIDDLE (not at the front).
    corpus_dir = tmp_path / "corpus"
    pairs_dir = corpus_dir / "pairs"
    pairs_dir.mkdir(parents=True, exist_ok=True)

    cs_a = tmp_path / "A.cs"
    _write_csharp(cs_a, "A")
    cs_c = tmp_path / "C.cs"
    _write_csharp(cs_c, "C")
    bogus = tmp_path / "MISSING.cs"  # never written → error

    spec_pairs = [
        ("aaa_first", "g1", cs_a),    # likely overall>0
        ("zzz_middle_bad", "g1", bogus),  # error, overall=0.0
        ("ccc_last", "g1", cs_c),     # likely overall>0
    ]
    index = []
    for pid, game, unity_path in spec_pairs:
        manifest = {"id": pid, "game": game, "unity_file": str(unity_path)}
        (pairs_dir / f"{pid}.json").write_text(json.dumps(manifest))
        index.append({"id": pid, "game": game, "file": f"pairs/{pid}.json"})
    index_path = corpus_dir / "corpus_index.json"
    index_path.write_text(json.dumps(index))

    out = tmp_path / "out.json"
    summary = mutated_mod.run_baseline(index_path, out)

    overalls = [p["overall"] for p in summary["pairs"]]
    # In the mutated build, the first pair is whatever was inserted first
    # (aaa_first), which scored > 0, while a later pair has overall=0.0.
    # Therefore overalls is NOT in ascending order.
    assert overalls != sorted(overalls), (
        f"mutation didn't break sort invariant: overalls={overalls}"
    )
    # Concrete: the errored pair must NOT be first under the mutation.
    assert summary["pairs"][0]["id"] != "zzz_middle_bad", (
        "errored pair landed first by accident — strengthen test fixture"
    )
