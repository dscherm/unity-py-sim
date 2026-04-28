"""Scaffolds the ASP-4 CoPlay leg from Python ParityCases (M-13 follow-up).

Discovers every `ParityCase` defined under `tests/parity/test_*_parity.py` by
monkey-patching `assert_parity` to intercept registrations, then emits two
artifacts:

  1. A JSON manifest at `data/metrics/coplay_parity_cases.json` — single
     source of truth for the home-machine UTF runner. Schema:
       {
         "generated_at": "...",
         "total_cases": <int>,
         "cases": [
           {
             "test_module": "tests.parity.test_transform_translate_parity",
             "test_function": "test_translate_shifts_position_parity",
             "case_name": "Transform.Translate single shift",
             "scenario_csharp_body": "...",
             "extra_csharp_usings": [],
             "float_tolerance": 1e-4
           },
           ...
         ]
       }

  2. (Stub) one `[UnityTest]` C# template per case, written under
     `data/generated/coplay_parity_runner/Assets/Tests/PlayMode/`. Each
     template wraps the Python-side `scenario_csharp_body` in a
     `UnityEngine.TestTools.UnityTest` IEnumerator and emits the observables
     dict via `Debug.Log("PARITY_OBSERVABLES:" + json)` so the same JSON tag
     the dotnet harness uses (`OBSERVABLES_TAG`) carries through to the
     Unity Editor log.

Note: this tool is **scaffold-only** today. Home-machine work to land:
  - Drop the generated `Assets/Tests/PlayMode/` tree into a Unity project.
  - Run `Unity -batchmode -runTests -testPlatform PlayMode` per game.
  - Parse the JUnit/NUnit XML output, classify pass/fail, write back to
    `data/metrics/parity_pass_rates.json :: coplay { passed, failed, ... }`.
  - Wire that into `.github/workflows/home_machine.yml`.

See SUCCESS.md ASP-4 for the closure criteria.

Usage:
    python tools/scaffold_coplay_parity_runner.py
    python tools/scaffold_coplay_parity_runner.py --dry-run     # discovery only
    python tools/scaffold_coplay_parity_runner.py --output-dir <path>
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARITY_DIR = ROOT / "tests" / "parity"
DEFAULT_MANIFEST = ROOT / "data" / "metrics" / "coplay_parity_cases.json"
DEFAULT_GENERATED_DIR = ROOT / "data" / "generated" / "coplay_parity_runner"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _discover_cases() -> list[dict]:
    """Monkey-patch `assert_parity`, import each parity test module, and
    invoke its test functions so the patched callback records each case.

    Each case lands in `_DISCOVERED` with the test_module/test_function
    context attached so the home-machine runner can map results back."""
    from tests.parity import _harness  # noqa: PLC0415

    discovered: list[dict] = []
    current_ctx = {"module": "?", "function": "?"}

    original = _harness.assert_parity

    def _intercept(case) -> None:  # type: ignore[no-untyped-def]
        discovered.append({
            "test_module": current_ctx["module"],
            "test_function": current_ctx["function"],
            "case_name": case.name,
            "scenario_csharp_body": case.scenario_csharp_body,
            "extra_csharp_usings": list(case.extra_csharp_usings),
            "float_tolerance": case.float_tolerance,
        })

    _harness.assert_parity = _intercept  # type: ignore[assignment]
    try:
        for path in sorted(PARITY_DIR.glob("test_*_parity.py")):
            mod_name = f"tests.parity.{path.stem}"
            text = path.read_text(encoding="utf-8")
            if "PARITY_SCAFFOLD_PARKED" in text or "PARITY_SCAFFOLD_SKELETON" in text:
                continue  # parked / skeleton files have no runnable cases
            try:
                module = importlib.import_module(mod_name)
            except Exception as e:  # noqa: BLE001
                print(f"[coplay-scaffold] skip {mod_name}: import failed ({e})", file=sys.stderr)
                continue
            for name in dir(module):
                if not name.startswith("test_"):
                    continue
                fn = getattr(module, name)
                if not callable(fn):
                    continue
                current_ctx["module"] = mod_name
                current_ctx["function"] = name
                try:
                    fn()
                except Exception as e:  # noqa: BLE001
                    # Test bodies can raise outside `assert_parity` (e.g.
                    # parametrized fixtures, harness-skips). We only care
                    # about whether `assert_parity` was reached.
                    print(
                        f"[coplay-scaffold] note: {mod_name}::{name} raised "
                        f"{type(e).__name__} during discovery — skipped if no case recorded",
                        file=sys.stderr,
                    )
    finally:
        _harness.assert_parity = original  # type: ignore[assignment]

    return discovered


_UNITY_TEST_TEMPLATE = """\
// AUTO-GENERATED by tools/scaffold_coplay_parity_runner.py — do not edit.
// Source: {test_module}::{test_function} ({case_name!r})
// See SUCCESS.md ASP-4 for the home-machine wiring contract.

using System.Collections;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
{extra_usings}

namespace UnityPySim.Parity
{{
    public class {class_name}
    {{
        private const string OBSERVABLES_TAG = "PARITY_OBSERVABLES:";

        [UnityTest]
        public IEnumerator {method_name}()
        {{
            var observables = new Dictionary<string, object>();
            {body}
            // Tag the line so the home-machine log parser can pick it up.
            // Match the dotnet harness's emit shape (src/parity/_harness.py).
            Debug.Log(OBSERVABLES_TAG + ParityHarnessShim.Serialize(observables));
            yield return null;
        }}
    }}
}}
"""


def _slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_")


def _emit_unity_test(case: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    class_name = _slug(case["test_function"]).title().replace("_", "")
    method_name = _slug(case["case_name"]) or "RunCase"
    extra_usings = "\n".join(f"using {ns};" for ns in case["extra_csharp_usings"])
    body = case["scenario_csharp_body"].strip()
    indented_body = "\n            ".join(body.splitlines())
    src = _UNITY_TEST_TEMPLATE.format(
        test_module=case["test_module"],
        test_function=case["test_function"],
        case_name=case["case_name"],
        extra_usings=extra_usings,
        class_name=class_name,
        method_name=method_name,
        body=indented_body,
    )
    target = out_dir / f"{class_name}.cs"
    target.write_text(src, encoding="utf-8")
    return target


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true",
                   help="Discover cases + write the manifest only; skip C# emission.")
    p.add_argument("--manifest", default=str(DEFAULT_MANIFEST),
                   help=f"Path to the JSON case manifest (default: {DEFAULT_MANIFEST}).")
    p.add_argument("--output-dir", default=str(DEFAULT_GENERATED_DIR),
                   help=f"Where to write generated UnityTest C# (default: {DEFAULT_GENERATED_DIR}).")
    args = p.parse_args(argv)

    cases = _discover_cases()
    manifest_path = Path(args.manifest)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_cases": len(cases),
        "cases": cases,
    }, indent=2) + "\n", encoding="utf-8")
    print(f"[coplay-scaffold] discovered {len(cases)} parity case(s); manifest: {manifest_path}")

    if args.dry_run:
        return 0

    test_dir = Path(args.output_dir) / "Assets" / "Tests" / "PlayMode"
    written = 0
    for case in cases:
        _emit_unity_test(case, test_dir)
        written += 1
    print(f"[coplay-scaffold] wrote {written} UnityTest C# file(s) under {test_dir}")
    print("[coplay-scaffold] NOTE: a `ParityHarnessShim.Serialize` static is required at "
          "<output-dir>/Assets/Tests/PlayMode/ParityHarnessShim.cs — implement on the home machine.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
