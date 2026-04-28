"""Parse Unity Test Framework NUnit XML output and write the CoPlay leg of
`data/metrics/parity_pass_rates.json`.

Unity batchmode (`Unity.exe -batchmode -runTests -testPlatform PlayMode
-testResults <xml>`) emits NUnit-3 XML. We classify each `<test-case>`:

  - `result="Passed"`           → counts as passed
  - `result="Failed"`           → counts as failed
  - `result="Skipped"`          → counts as skipped (CoPlay-only skip; the
                                  PARKED/SCAFFOLD-skipped Python cases never
                                  reach the CoPlay leg, so a skip here means
                                  Unity could not run the test for some
                                  reason — treated as `skipped_other`).

Output: merges `coplay: { passed, failed, skipped_other, total_runnable, pct }`
into the existing `parity_pass_rates.json` (preserving the `dotnet` block).

Usage:
    python tools/aggregate_coplay_parity_results.py \\
        --results data/metrics/coplay_parity_results.xml

Exit codes:
    0 — success
    1 — XML parse error or missing file
    2 — argparse / I/O error
"""

from __future__ import annotations

import argparse
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_RESULTS = ROOT / "data" / "metrics" / "coplay_parity_results.xml"
DEFAULT_RATES = ROOT / "data" / "metrics" / "parity_pass_rates.json"


def _parse_nunit(xml_path: Path) -> dict[str, int]:
    """Walk every `<test-case>` element and bucket by `result` attribute."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    counts = {"passed": 0, "failed": 0, "skipped_other": 0}
    for tc in root.iter("test-case"):
        result = (tc.get("result") or "").lower()
        if result == "passed":
            counts["passed"] += 1
        elif result in ("failed", "error", "inconclusive"):
            counts["failed"] += 1
        else:
            counts["skipped_other"] += 1
    return counts


def aggregate(results_xml: Path = DEFAULT_RESULTS,
              rates_json: Path = DEFAULT_RATES) -> dict:
    if not results_xml.exists():
        raise SystemExit(f"[coplay-aggregate] missing results XML: {results_xml}")

    counts = _parse_nunit(results_xml)
    runnable = counts["passed"] + counts["failed"]
    pct = (counts["passed"] / runnable) if runnable else 0.0

    coplay = {
        "passed": counts["passed"],
        "failed": counts["failed"],
        "skipped_other": counts["skipped_other"],
        "total_runnable": runnable,
        "pct": pct,
        "measured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": str(results_xml.relative_to(ROOT)) if results_xml.is_relative_to(ROOT) else str(results_xml),
    }

    # Merge into existing JSON (preserves dotnet block).
    existing: dict = {}
    if rates_json.exists():
        try:
            existing = json.loads(rates_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
    existing["coplay"] = coplay
    rates_json.parent.mkdir(parents=True, exist_ok=True)
    rates_json.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    return coplay


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--results", default=str(DEFAULT_RESULTS),
                   help="Unity Test Framework NUnit XML output path.")
    p.add_argument("--rates", default=str(DEFAULT_RATES),
                   help="parity_pass_rates.json to merge into.")
    args = p.parse_args(argv)

    coplay = aggregate(Path(args.results), Path(args.rates))
    print(
        f"[coplay-aggregate] coplay: {coplay['passed']}/{coplay['total_runnable']} "
        f"({coplay['pct']*100:.1f}%); skipped_other={coplay['skipped_other']}"
    )
    print(f"[coplay-aggregate] merged into {args.rates}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
