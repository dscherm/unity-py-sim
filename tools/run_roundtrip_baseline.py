"""Run roundtrip_gate over every corpus pair, write JSON baseline.

Reads `data/corpus/corpus_index.json` to enumerate pairs, runs
`score_roundtrip_file` on each pair's `unity_file`, aggregates per-game,
and writes `data/metrics/roundtrip_baseline.json`.

Designed to be cheap (no subprocess; pure in-process). Errors during any
single pair are caught — the pair lands in the output with `error` set.

Usage:
    python tools/run_roundtrip_baseline.py
    python tools/run_roundtrip_baseline.py --output data/metrics/roundtrip_2026.json
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.gates.roundtrip_gate import score_roundtrip_file  # noqa: E402


def run_baseline(corpus_index: Path, output: Path) -> dict[str, Any]:
    index = json.loads(corpus_index.read_text())
    pairs_out: list[dict[str, Any]] = []
    by_game: dict[str, list[float]] = defaultdict(list)
    failures = 0

    corpus_root = corpus_index.parent
    for entry in index:
        pair_id = entry["id"]
        game = entry["game"]
        pair_path = corpus_root / entry["file"]
        try:
            pair = json.loads(pair_path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            pairs_out.append({
                "id": pair_id, "game": game,
                "error": f"pair manifest unreadable: {exc}",
                "overall": 0.0, "structural": 0.0, "type": 0.0, "naming": 0.0,
            })
            failures += 1
            continue
        unity_rel = pair.get("unity_file") or pair.get("csharp_file")
        if not unity_rel:
            pairs_out.append({
                "id": pair_id, "game": game,
                "error": "pair manifest missing unity_file/csharp_file",
                "overall": 0.0, "structural": 0.0, "type": 0.0, "naming": 0.0,
            })
            failures += 1
            continue
        unity_path = ROOT / unity_rel
        if not unity_path.exists():
            pairs_out.append({
                "id": pair_id, "game": game,
                "error": f"unity file missing: {unity_rel}",
                "overall": 0.0, "structural": 0.0, "type": 0.0, "naming": 0.0,
            })
            failures += 1
            continue
        try:
            r = score_roundtrip_file(unity_path)
            pairs_out.append({
                "id": pair_id,
                "game": game,
                "overall": r.overall_score,
                "structural": r.structural_score,
                "type": r.type_score,
                "naming": r.naming_score,
                "original_classes": r.original_class_count,
                "roundtrip_classes": r.roundtrip_class_count,
                "details": r.details[:5],
                "error": None,
            })
            by_game[game].append(r.overall_score)
        except Exception as exc:
            pairs_out.append({
                "id": pair_id, "game": game,
                "error": f"{type(exc).__name__}: {exc}",
                "trace": traceback.format_exc().splitlines()[-3:],
                "overall": 0.0, "structural": 0.0, "type": 0.0, "naming": 0.0,
            })
            failures += 1

    overall_scores = [p["overall"] for p in pairs_out if p.get("error") is None]
    avg_overall = round(sum(overall_scores) / len(overall_scores), 3) if overall_scores else 0.0

    by_game_summary = {
        game: {
            "count": len(scores),
            "avg_overall": round(sum(scores) / len(scores), 3) if scores else 0.0,
        }
        for game, scores in by_game.items()
    }

    summary: dict[str, Any] = {
        "total_pairs": len(pairs_out),
        "succeeded": len(overall_scores),
        "failed": failures,
        "avg_overall": avg_overall,
        "by_game": by_game_summary,
        "pairs": sorted(pairs_out, key=lambda p: p["overall"]),
    }

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2) + "\n")
    return summary


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--corpus-index", default=str(ROOT / "data/corpus/corpus_index.json"))
    p.add_argument("--output", default=str(ROOT / "data/metrics/roundtrip_baseline.json"))
    args = p.parse_args(argv)
    summary = run_baseline(Path(args.corpus_index), Path(args.output))
    print(
        f"[roundtrip] {summary['succeeded']}/{summary['total_pairs']} pairs scored, "
        f"{summary['failed']} errors, avg_overall={summary['avg_overall']}"
    )
    print(f"[roundtrip] wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
