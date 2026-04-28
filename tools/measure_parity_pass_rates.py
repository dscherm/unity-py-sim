"""Measure parity-test pass rates per ASP-4.

Runs `pytest tests/parity/` with `--junitxml`, classifies each testcase, and
writes `data/metrics/parity_pass_rates.json` so the snapshot/dashboard pipeline
can include dotnet (and eventually CoPlay) pass rates as live trend columns.

Schema written to JSON:

    {
      "timestamp": "2026-04-27T...Z",
      "dotnet": {
        "passed":   <int>,
        "failed":   <int>,
        "skipped_parked":   <int>,  # PARITY_SCAFFOLD_PARKED — out of scope
        "skipped_other":    <int>,  # dotnet missing, scaffold skeletons, etc.
        "total_runnable":   <int>,  # passed + failed
        "pct":              <float>  # passed / total_runnable, 0.0–1.0
      },
      "coplay": { "deferred": true, "note": "home-machine UTF runner; not yet wired" }
    }

`total_runnable` deliberately excludes parked + scaffold-skipped tests — they
are explicit out-of-scope decisions per M-9 ("PARITY_SCAFFOLD_PARKED" /
"PARITY_SCAFFOLD_SKELETON"). Including them would punish the rate for
intentional decisions.

Usage:
    python tools/measure_parity_pass_rates.py
    python tools/measure_parity_pass_rates.py --output data/metrics/parity_pass_rates.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARITY_DIR = ROOT / "tests" / "parity"
DEFAULT_OUTPUT = ROOT / "data" / "metrics" / "parity_pass_rates.json"


def _classify_skip(message: str) -> str:
    """Decide whether a skipped testcase counts as `parked` or `other`."""
    msg = (message or "").lower()
    if "parked" in msg or "out of scope" in msg or "out-of-scope" in msg:
        return "parked"
    if "scaffold" in msg or "skeleton" in msg or "todo" in msg:
        return "parked"  # treat skeletons as out-of-scope until filled
    return "other"


def _run_pytest(junit_path: Path) -> int:
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(PARITY_DIR),
        f"--junitxml={junit_path}",
        "--tb=no",
        "-q",
    ]
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    # Pytest exit 1 = failures (expected when something regresses).
    # Pytest exit 5 = no tests collected (treat as error).
    if proc.returncode == 5:
        print(proc.stdout)
        print(proc.stderr, file=sys.stderr)
        raise SystemExit("[parity] no tests collected — refusing to write zeros")
    return proc.returncode


def _parse_junit(junit_path: Path) -> dict[str, int]:
    tree = ET.parse(junit_path)
    root = tree.getroot()
    counts = {"passed": 0, "failed": 0, "skipped_parked": 0, "skipped_other": 0}
    for tc in root.iter("testcase"):
        skipped = tc.find("skipped")
        failure = tc.find("failure")
        error = tc.find("error")
        if skipped is not None:
            cls = _classify_skip(skipped.get("message", ""))
            counts["skipped_parked" if cls == "parked" else "skipped_other"] += 1
        elif failure is not None or error is not None:
            counts["failed"] += 1
        else:
            counts["passed"] += 1
    return counts


def measure(output: Path = DEFAULT_OUTPUT) -> dict:
    junit_path = output.with_suffix(".junit.xml")
    output.parent.mkdir(parents=True, exist_ok=True)
    _run_pytest(junit_path)
    counts = _parse_junit(junit_path)
    runnable = counts["passed"] + counts["failed"]
    pct = (counts["passed"] / runnable) if runnable else 0.0
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "dotnet": {
            "passed": counts["passed"],
            "failed": counts["failed"],
            "skipped_parked": counts["skipped_parked"],
            "skipped_other": counts["skipped_other"],
            "total_runnable": runnable,
            "pct": pct,
        },
        "coplay": {
            "deferred": True,
            "note": "home-machine UTF runner; not yet wired (see SUCCESS.md ASP-4)",
        },
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    junit_path.unlink(missing_ok=True)
    return payload


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--output", default=str(DEFAULT_OUTPUT), help="JSON output path"
    )
    args = p.parse_args(argv)
    payload = measure(Path(args.output))
    d = payload["dotnet"]
    print(
        f"[parity-rates] dotnet: {d['passed']}/{d['total_runnable']} "
        f"({d['pct']*100:.1f}%); parked={d['skipped_parked']}, "
        f"other-skipped={d['skipped_other']}"
    )
    print(f"[parity-rates] wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
