"""Integration test that pins the M-2 close numbers on the real 37-pair corpus.

Drives `tools.run_roundtrip_baseline.run_baseline` in-process (no subprocess) so
a regression in any of the three csharp_to_python.py fixes will drop the
aggregate compile% below 0.80 (ASP-1 floor) or AST% below 0.50 (ASP-2 floor),
and the test will fail loudly.

We also pin angry_birds at 1.000 — that game was already perfect before M-2,
so we use it as a "no-regression" sentinel: if anything we did to expand the
var-decl/cast/operator paths broke the previously-perfect angry_birds files,
this assertion will catch it.

Output is written to a `tempfile.TemporaryDirectory` so the committed
`data/metrics/roundtrip_baseline.json` is not clobbered by the test run.

Test agent does not touch src/.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _run_baseline_in_tmp() -> dict:
    from tools.run_roundtrip_baseline import run_baseline  # local import

    corpus_index = ROOT / "data" / "corpus" / "corpus_index.json"
    assert corpus_index.exists(), f"corpus_index.json missing at {corpus_index}"

    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "rt.json"
        summary = run_baseline(corpus_index, out)
        # Sanity: the runner wrote the file too.
        assert out.exists()
        # Round-trip the JSON to make sure it serializes.
        json.loads(out.read_text())
    return summary


@pytest.fixture(scope="module")
def baseline_summary() -> dict:
    return _run_baseline_in_tmp()


def test_corpus_size_is_thirty_seven(baseline_summary: dict) -> None:
    """The 37-pair number is what the M-2 close commit message and the spec
    quote. If a corpus pair is added/removed, this test must be updated
    intentionally — same time as the floors below."""
    assert baseline_summary["total_pairs"] == 37, (
        f"Expected 37 pairs, found {baseline_summary['total_pairs']}; "
        "if the corpus changed deliberately, update this test alongside "
        "the M-2 close metrics."
    )


def test_angry_birds_remains_at_one_point_zero(baseline_summary: dict) -> None:
    """angry_birds was 1.000 before M-2; if the new fixes regressed any of
    those 8 files, we catch it here."""
    by_game = baseline_summary["by_game"]
    assert "angry_birds" in by_game, f"angry_birds missing from by_game: {by_game}"
    avg = by_game["angry_birds"]["avg_overall"]
    assert avg == 1.0, (
        f"angry_birds avg_overall regressed from 1.0 to {avg}; "
        "M-2 fixes should not touch angry_birds outputs."
    )


def test_compile_rate_meets_asp1_floor(baseline_summary: dict) -> None:
    """ASP-1 floor: at least 80% of pairs must produce compileable Python
    (overall > 0 means the round-trip didn't error out).
    M-2 close measured 89.2%; we lock the floor a hair below that."""
    pairs = baseline_summary["pairs"]
    total = len(pairs)
    compile_ok = sum(
        1 for p in pairs if p.get("error") is None and p.get("overall", 0.0) > 0.0
    )
    pct = compile_ok / total
    assert pct >= 0.80, (
        f"Compile% dropped below ASP-1 floor: {pct:.3f} ({compile_ok}/{total}); "
        f"M-2 close measured 0.892. A regression in cs_to_py is likely."
    )


def test_ast_equivalence_meets_asp2_floor(baseline_summary: dict) -> None:
    """ASP-2 floor: at least 50% of pairs must reach AST equivalence
    (overall >= 0.999, i.e. effectively 1.0 within rounding).
    M-2 close measured 59.5%."""
    pairs = baseline_summary["pairs"]
    total = len(pairs)
    ast_ok = sum(
        1 for p in pairs if p.get("error") is None and p.get("overall", 0.0) >= 0.999
    )
    pct = ast_ok / total
    assert pct >= 0.50, (
        f"AST% dropped below ASP-2 floor: {pct:.3f} ({ast_ok}/{total}); "
        f"M-2 close measured 0.595. A regression in cs_to_py is likely."
    )


def test_no_pair_raised_unexpected_exception(baseline_summary: dict) -> None:
    """Pairs whose round-trip raised an unhandled exception will have
    `error` set with a traceback. None should at HEAD."""
    err_pairs = [p for p in baseline_summary["pairs"] if p.get("error")]
    # Allow well-known structural errors (e.g. a corpus pair file is missing
    # the unity_file path) but flag anything that looks like a translator crash.
    for p in err_pairs:
        err = p["error"]
        assert "Traceback" not in err, f"Pair {p['id']} translator crashed: {err}"
