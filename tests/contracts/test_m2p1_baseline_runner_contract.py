"""Contract tests for tools/run_roundtrip_baseline.py (M-2 phase 1).

These tests verify the documented output schema of the baseline runner
without depending on the real corpus. We build a tiny synthetic corpus
in tmp_path and assert the documented invariants:

  - Top-level keys: total_pairs, succeeded, failed, avg_overall, by_game, pairs.
  - Each pair has at least: id, game, overall, error.
  - Pairs with error is None have numeric `overall` in [0, 1].
  - Pairs with error is not None have `overall == 0.0`.
  - Pairs are sorted worst-first (overall ascending).
  - succeeded + failed == total_pairs.
  - by_game[g].count == count of error-free pairs in that game.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
RUNNER_PATH = ROOT / "tools" / "run_roundtrip_baseline.py"


@pytest.fixture
def runner_module():
    """Load tools/run_roundtrip_baseline.py as a module."""
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location(
        "_m2p1_runner_under_test", str(RUNNER_PATH)
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write_simple_csharp(p: Path, class_name: str, body: str = "    public int x;") -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        f"using UnityEngine;\n\npublic class {class_name} : MonoBehaviour\n{{\n{body}\n}}\n",
        encoding="utf-8",
    )


def _make_corpus(tmp_path: Path, pairs_spec: list[tuple[str, str, Path]]) -> Path:
    """Build a fake corpus_index.json + per-pair manifests + Unity files.

    pairs_spec: list of (id, game, unity_file_path).
    """
    corpus_dir = tmp_path / "corpus"
    pairs_dir = corpus_dir / "pairs"
    pairs_dir.mkdir(parents=True, exist_ok=True)

    index = []
    for pid, game, unity_path in pairs_spec:
        manifest_rel = f"pairs/{pid}.json"
        index.append({"id": pid, "game": game, "file": manifest_rel})
        manifest = {
            "id": pid,
            "game": game,
            # Path relative to ROOT — we'll use absolute paths instead so
            # the runner's `ROOT / unity_rel` resolves correctly even with
            # a non-repo path.
            "unity_file": str(unity_path),
        }
        (pairs_dir / f"{pid}.json").write_text(json.dumps(manifest))

    index_path = corpus_dir / "corpus_index.json"
    index_path.write_text(json.dumps(index))
    return index_path


def test_output_has_required_top_level_keys(tmp_path, runner_module):
    cs_a = tmp_path / "A.cs"
    _write_simple_csharp(cs_a, "Foo")
    index = _make_corpus(tmp_path, [("p1", "test_game", cs_a)])
    out = tmp_path / "out.json"

    summary = runner_module.run_baseline(index, out)

    for key in ("total_pairs", "succeeded", "failed", "avg_overall", "by_game", "pairs"):
        assert key in summary, f"missing top-level key {key!r}"

    # Output file should also exist and round-trip through json.
    assert out.exists()
    on_disk = json.loads(out.read_text())
    for key in ("total_pairs", "succeeded", "failed", "avg_overall", "by_game", "pairs"):
        assert key in on_disk


def test_pair_dict_minimum_fields(tmp_path, runner_module):
    cs_a = tmp_path / "A.cs"
    _write_simple_csharp(cs_a, "Foo")
    index = _make_corpus(tmp_path, [("p1", "g1", cs_a)])
    out = tmp_path / "out.json"

    summary = runner_module.run_baseline(index, out)
    assert summary["pairs"], "pairs list should be non-empty"
    for p in summary["pairs"]:
        for f in ("id", "game", "overall", "error"):
            assert f in p, f"pair missing field {f!r}: {p!r}"


def test_error_free_pairs_have_overall_in_unit_interval(tmp_path, runner_module):
    cs_a = tmp_path / "A.cs"
    _write_simple_csharp(cs_a, "Foo")
    cs_b = tmp_path / "B.cs"
    _write_simple_csharp(cs_b, "Bar", "    public float y;")
    index = _make_corpus(tmp_path, [("p1", "g1", cs_a), ("p2", "g2", cs_b)])
    out = tmp_path / "out.json"

    summary = runner_module.run_baseline(index, out)
    for p in summary["pairs"]:
        if p["error"] is None:
            assert isinstance(p["overall"], (int, float))
            assert 0.0 <= p["overall"] <= 1.0


def test_errored_pairs_have_overall_zero(tmp_path, runner_module):
    # Point one pair at a non-existent unity file to force an error.
    bogus = tmp_path / "DoesNotExist.cs"  # never created
    cs_a = tmp_path / "A.cs"
    _write_simple_csharp(cs_a, "Foo")
    index = _make_corpus(tmp_path, [("bad", "g1", bogus), ("good", "g1", cs_a)])
    out = tmp_path / "out.json"

    summary = runner_module.run_baseline(index, out)
    errored = [p for p in summary["pairs"] if p["error"] is not None]
    assert errored, "expected at least one errored pair"
    for p in errored:
        assert p["overall"] == 0.0


def test_pairs_sorted_worst_first(tmp_path, runner_module):
    # Mix several pairs; assert the output list is sorted by overall ascending.
    cs_a = tmp_path / "A.cs"
    _write_simple_csharp(cs_a, "Foo")
    cs_b = tmp_path / "B.cs"
    _write_simple_csharp(cs_b, "Bar")
    bogus = tmp_path / "Missing.cs"
    index = _make_corpus(
        tmp_path,
        [
            ("err1", "g1", bogus),
            ("ok1", "g1", cs_a),
            ("ok2", "g2", cs_b),
        ],
    )
    out = tmp_path / "out.json"

    summary = runner_module.run_baseline(index, out)
    overalls = [p["overall"] for p in summary["pairs"]]
    assert overalls == sorted(overalls), (
        f"pairs not sorted worst-first; got overalls={overalls}"
    )


def test_succeeded_plus_failed_equals_total(tmp_path, runner_module):
    cs_a = tmp_path / "A.cs"
    _write_simple_csharp(cs_a, "Foo")
    bogus = tmp_path / "Missing.cs"
    index = _make_corpus(
        tmp_path,
        [("p1", "g1", cs_a), ("p2", "g1", bogus), ("p3", "g2", cs_a)],
    )
    out = tmp_path / "out.json"

    summary = runner_module.run_baseline(index, out)
    assert summary["succeeded"] + summary["failed"] == summary["total_pairs"]
    assert summary["total_pairs"] == 3


def test_by_game_count_matches_error_free_pairs(tmp_path, runner_module):
    cs_a = tmp_path / "A.cs"
    _write_simple_csharp(cs_a, "Foo")
    cs_b = tmp_path / "B.cs"
    _write_simple_csharp(cs_b, "Bar")
    bogus = tmp_path / "Missing.cs"
    index = _make_corpus(
        tmp_path,
        [
            ("ok1", "alpha", cs_a),
            ("ok2", "alpha", cs_b),
            ("err1", "alpha", bogus),  # errored — must NOT count toward alpha.count
            ("ok3", "beta", cs_a),
        ],
    )
    out = tmp_path / "out.json"

    summary = runner_module.run_baseline(index, out)
    by_game = summary["by_game"]
    # Compute expected counts from error-free pairs grouped by game.
    expected = {"alpha": 0, "beta": 0}
    for p in summary["pairs"]:
        if p["error"] is None:
            expected[p["game"]] = expected.get(p["game"], 0) + 1

    for game, exp_count in expected.items():
        if exp_count == 0:
            # by_game only tracks games with at least one error-free pair.
            continue
        assert game in by_game, f"missing {game!r} in by_game"
        assert by_game[game]["count"] == exp_count, (
            f"by_game[{game!r}].count={by_game[game]['count']} expected {exp_count}"
        )

    # Concrete: alpha=2 ok pairs (err1 dropped), beta=1.
    assert by_game["alpha"]["count"] == 2
    assert by_game["beta"]["count"] == 1


def test_avg_overall_excludes_errored_pairs(tmp_path, runner_module):
    """avg_overall should be averaged over error-free pairs only.

    A pair that errored has overall=0.0 but should not pull the average down.
    """
    cs_a = tmp_path / "A.cs"
    _write_simple_csharp(cs_a, "Foo")
    bogus = tmp_path / "Missing.cs"
    index = _make_corpus(tmp_path, [("ok", "g1", cs_a), ("err", "g1", bogus)])
    out = tmp_path / "out.json"

    summary = runner_module.run_baseline(index, out)
    error_free = [p["overall"] for p in summary["pairs"] if p["error"] is None]
    assert error_free, "test requires at least one error-free pair"
    expected = round(sum(error_free) / len(error_free), 3)
    assert summary["avg_overall"] == expected
