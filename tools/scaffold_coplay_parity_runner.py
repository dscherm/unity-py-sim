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


_PARITY_HARNESS_SHIM = """\
// AUTO-GENERATED by tools/scaffold_coplay_parity_runner.py — do not edit.
// Mirrors src/parity/_harness.py's _PROGRAM_TEMPLATE Serialize() so the
// CoPlay/UnityTest leg emits observables in the same JSON shape as the
// dotnet leg. Used by every generated [UnityTest] under this asmdef.

using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using UnityEngine;

namespace UnityPySim.Parity
{
    public static class ParityHarnessShim
    {
        public static string Serialize(IDictionary<string, object> obs)
        {
            var sb = new StringBuilder();
            sb.Append('{');
            var first = true;
            foreach (var kv in obs)
            {
                if (!first) sb.Append(',');
                first = false;
                sb.Append('"').Append(Escape(kv.Key)).Append('"').Append(':');
                sb.Append(SerializeValue(kv.Value));
            }
            sb.Append('}');
            return sb.ToString();
        }

        private static string SerializeValue(object v)
        {
            if (v == null) return "null";
            if (v is string s) return "\\"" + Escape(s) + "\\"";
            if (v is bool b) return b ? "true" : "false";
            if (v is float f) return FormatFloat(f);
            if (v is double d) return FormatFloat((float)d);
            if (v is int i) return i.ToString(CultureInfo.InvariantCulture);
            if (v is long l) return l.ToString(CultureInfo.InvariantCulture);
            if (v is Vector2 v2) return "[" + FormatFloat(v2.x) + "," + FormatFloat(v2.y) + "]";
            if (v is Vector3 v3) return "[" + FormatFloat(v3.x) + "," + FormatFloat(v3.y) + "," + FormatFloat(v3.z) + "]";
            if (v is IEnumerable e)
            {
                var sb = new StringBuilder("[");
                var firstItem = true;
                foreach (var item in e)
                {
                    if (!firstItem) sb.Append(',');
                    firstItem = false;
                    sb.Append(SerializeValue(item));
                }
                sb.Append(']');
                return sb.ToString();
            }
            return "\\"" + Escape(v.ToString()) + "\\"";
        }

        private static string FormatFloat(float f) => f.ToString("R", CultureInfo.InvariantCulture);

        private static string Escape(string s)
        {
            var sb = new StringBuilder();
            foreach (var c in s)
            {
                switch (c)
                {
                    case '"': sb.Append("\\\\\\""); break;
                    case '\\\\': sb.Append("\\\\\\\\"); break;
                    case '\\n': sb.Append("\\\\n"); break;
                    case '\\r': sb.Append("\\\\r"); break;
                    case '\\t': sb.Append("\\\\t"); break;
                    default: sb.Append(c); break;
                }
            }
            return sb.ToString();
        }
    }
}
"""


_PARITY_ASMDEF = json.dumps({
    "name": "UnityPySim.Parity.PlayModeTests",
    "rootNamespace": "UnityPySim.Parity",
    "references": [
        "UnityEngine.TestRunner",
        "UnityEditor.TestRunner",
    ],
    "includePlatforms": [],
    "excludePlatforms": [],
    "allowUnsafeCode": False,
    "overrideReferences": True,
    "precompiledReferences": ["nunit.framework.dll"],
    "autoReferenced": False,
    "defineConstraints": ["UNITY_INCLUDE_TESTS"],
    "versionDefines": [],
    "noEngineReferences": False,
}, indent=2) + "\n"


_PACKAGES_MANIFEST = json.dumps({
    "dependencies": {
        "com.unity.test-framework": "1.6.0",
        "com.unity.modules.physics2d": "1.0.0",
        "com.unity.modules.imgui": "1.0.0",
        "com.unity.modules.ui": "1.0.0",
        "com.unity.2d.sprite": "1.0.0",
        "com.unity.inputsystem": "1.11.2",
    }
}, indent=2) + "\n"


def _slug(s: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", s).strip("_")


def _emit_project_skeleton(out_dir: Path, project_settings_src: Path) -> None:
    """Drop the minimum Unity-recognizes-this-as-a-project files: ProjectSettings/
    (copied from a known-good source) + Packages/manifest.json + the parity test
    asmdef + ParityHarnessShim.cs. Idempotent."""
    out_dir.mkdir(parents=True, exist_ok=True)
    target_settings = out_dir / "ProjectSettings"
    if not target_settings.exists() and project_settings_src.exists():
        import shutil
        shutil.copytree(project_settings_src, target_settings)
    (out_dir / "Packages").mkdir(exist_ok=True)
    (out_dir / "Packages" / "manifest.json").write_text(_PACKAGES_MANIFEST, encoding="utf-8")
    test_dir = out_dir / "Assets" / "Tests" / "PlayMode"
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / "UnityPySim.Parity.PlayModeTests.asmdef").write_text(_PARITY_ASMDEF, encoding="utf-8")
    (test_dir / "ParityHarnessShim.cs").write_text(_PARITY_HARNESS_SHIM, encoding="utf-8")


_COMPONENT_TYPES = (
    "Rigidbody2D",
    "BoxCollider2D",
    "CircleCollider2D",
    "Camera",
    "SpriteRenderer",
    "AudioSource",
    "Animator",
    "MeshRenderer",
)


def _rewrite_for_unity(body: str) -> str:
    """Rewrite dotnet-leg C# bodies into Unity-runtime-compatible form.

    The dotnet stubs let component constructors run via `new Rigidbody2D()`
    because they're plain CLR objects. In Unity proper, components must live
    on a GameObject and be added via `AddComponent<T>()`. We:

      - inject a `__parityHost` GameObject preamble when the body uses any
        bare `new <Component>()` pattern
      - rewrite each `new <Component>()` → `__parityHost.AddComponent<...>()`
    """
    needs_host = False
    new_body = body
    for cls in _COMPONENT_TYPES:
        pattern = rf"\bnew\s+{re.escape(cls)}\s*\(\s*\)"
        if re.search(pattern, new_body):
            needs_host = True
            new_body = re.sub(pattern, f"__parityHost.AddComponent<{cls}>()", new_body)
    if needs_host:
        preamble = 'var __parityHost = new GameObject("__parity_host");\n'
        new_body = preamble + new_body
    return new_body


def _emit_unity_test(case: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    class_name = _slug(case["test_function"]).title().replace("_", "")
    method_name = _slug(case["case_name"]) or "RunCase"
    extra_usings = "\n".join(f"using {ns};" for ns in case["extra_csharp_usings"])
    body = _rewrite_for_unity(case["scenario_csharp_body"].strip())
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
    p.add_argument("--project-settings-src",
                   default=str(ROOT / "data" / "generated" / "breakout_project" / "ProjectSettings"),
                   help="Source ProjectSettings/ to copy when emitting the runner project. "
                        "Defaults to breakout_project's, which is known-good for Unity 6.")
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

    out_dir = Path(args.output_dir)
    _emit_project_skeleton(out_dir, Path(args.project_settings_src))
    print(f"[coplay-scaffold] wrote project skeleton (ProjectSettings/, Packages/, asmdef, shim) under {out_dir}")

    test_dir = out_dir / "Assets" / "Tests" / "PlayMode"
    written = 0
    for case in cases:
        _emit_unity_test(case, test_dir)
        written += 1
    print(f"[coplay-scaffold] wrote {written} UnityTest C# file(s) under {test_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
