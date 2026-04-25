"""Translation accuracy snapshot — captures point-in-time metrics into history.

Reads existing metric artifacts (`data/metrics/baseline.json`,
`compilation_baseline.json`) plus test-file inventory and git context, and
writes a single timestamped JSON to `data/metrics/history/<UTC>.json`.

Designed to be cheap so CI can run it on every push without re-running the
gate suite. The gates write their own `data/metrics/*.json` artifacts; this
module is a metadata roll-up over those artifacts.

Usage:
    python -m src.gates.snapshot
    python -m src.gates.snapshot --notes "post M-3 wiring"
"""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
METRICS_DIR = ROOT / "data" / "metrics"
HISTORY_DIR = METRICS_DIR / "history"
BASELINE_PATH = METRICS_DIR / "baseline.json"
COMPILATION_BASELINE_PATH = METRICS_DIR / "compilation_baseline.json"


@dataclass
class Snapshot:
    timestamp: str
    git_commit: str | None
    git_branch: str | None
    metrics: dict[str, float | int | None]
    by_game: dict[str, dict[str, float]]
    test_counts: dict[str, int]
    notes: str = ""


def _git(args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args], capture_output=True, text=True, cwd=str(ROOT), timeout=5
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    out = result.stdout.strip()
    return out or None


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _count_tests(test_dir: Path) -> int:
    if not test_dir.exists():
        return 0
    return len(list(test_dir.rglob("test_*.py")))


def take_snapshot(
    history_dir: Path = HISTORY_DIR,
    notes: str = "",
    *,
    metrics_dir: Path = METRICS_DIR,
) -> Path:
    """Capture current metrics, write to ``history_dir/<UTC-ISO>.json``."""
    history_dir.mkdir(parents=True, exist_ok=True)

    baseline = _read_json(metrics_dir / "baseline.json")
    compilation = _read_json(metrics_dir / "compilation_baseline.json")

    metrics: dict[str, float | int | None] = {
        "corpus_compile_pct": compilation.get("pass_rate"),
        "corpus_pairs": baseline.get("total_pairs"),
        "avg_overall": baseline.get("avg_overall"),
        "avg_class": baseline.get("avg_class"),
        "avg_method": baseline.get("avg_method"),
        "avg_field": baseline.get("avg_field"),
        "avg_using": baseline.get("avg_using"),
        # Roundtrip metrics — populated once M-2 ships
        "roundtrip_compile_pct": None,
        "roundtrip_ast_pct": None,
    }

    by_game = baseline.get("by_game", {})
    if not isinstance(by_game, dict):
        by_game = {}

    tests_dir = ROOT / "tests"
    test_counts = {
        "unit": _count_tests(tests_dir / "engine") + _count_tests(tests_dir / "translator"),
        "contracts": _count_tests(tests_dir / "contracts"),
        "integration": _count_tests(tests_dir / "integration"),
        "mutation": _count_tests(tests_dir / "mutation"),
        "parity": _count_tests(tests_dir / "parity"),
    }

    now = datetime.now(timezone.utc)
    snap = Snapshot(
        timestamp=now.isoformat(timespec="seconds"),
        git_commit=_git(["rev-parse", "--short", "HEAD"]),
        git_branch=_git(["rev-parse", "--abbrev-ref", "HEAD"]),
        metrics=metrics,
        by_game=by_game,
        test_counts=test_counts,
        notes=notes,
    )

    fname = now.strftime("%Y%m%dT%H%M%SZ") + ".json"
    out_path = history_dir / fname
    out_path.write_text(json.dumps(asdict(snap), indent=2) + "\n")
    return out_path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--notes", default="", help="Free-form notes attached to the snapshot")
    p.add_argument("--output-dir", default=str(HISTORY_DIR), help="History directory")
    args = p.parse_args(argv)
    out = take_snapshot(history_dir=Path(args.output_dir), notes=args.notes)
    print(f"[snapshot] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
