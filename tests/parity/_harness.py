"""Dual-path parity test harness (M-8).

A *parity case* describes one scenario that must produce equivalent observables
on both backends:

  - Python sim leg: a callable that returns a dict of named observables.
  - C# leg: a code fragment that, when wrapped in a Main() with the existing
    UnityEngine compile-gate stubs, prints a JSON dict to stdout.

The harness runs both, normalizes floats to a fixed tolerance, and asserts the
dicts are deep-equal. When the C# toolchain (`dotnet`) is unavailable, the C#
leg is skipped with a clear pytest message — the Python leg still runs.

Per M-8 description: this is the FOUNDATION for M-9 (parity backfill) and M-12
(gap gate). Without a runner that proves both sides agree, the parity matrix
only proves an API name exists, not that it behaves the same.
"""

from __future__ import annotations

import json
import math
import shutil
import subprocess
import tempfile
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import pytest

ROOT = Path(__file__).parent.parent.parent
_STUBS_DIR = ROOT / "stubs"

ParityScenario = Callable[[], dict[str, Any]]


@dataclass
class ParityCase:
    """One dual-path parity scenario.

    `scenario_python` runs in-process against `src.engine` and returns a dict
    of observables. `scenario_csharp_body` is C# source that runs inside a
    generated `Main()` and is expected to populate `observables` (a
    `Dictionary<string, object>`) before falling out — the harness handles
    JSON emission. Floats are compared with `float_tolerance`; lists are
    compared element-wise; dicts are compared by key.
    """

    name: str
    scenario_python: ParityScenario
    scenario_csharp_body: str
    float_tolerance: float = 1e-4
    extra_csharp_usings: list[str] = field(default_factory=list)


_CSPROJ = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <OutputType>Exe</OutputType>
    <Nullable>disable</Nullable>
    <RootNamespace>ParityHarness</RootNamespace>
    <NoWarn>CS0414;CS0169;CS0649;CS8618;CS0108;CS0114;CS1624;CS0266;CS0162;CS0219</NoWarn>
  </PropertyGroup>
</Project>
"""


_PROGRAM_TEMPLATE = """\
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using UnityEngine;
{extra_usings}

internal static class Program
{{
    private const string OBSERVABLES_TAG = "PARITY_OBSERVABLES:";

    public static void Main()
    {{
        var observables = new Dictionary<string, object>();
        {body}
        Console.WriteLine(OBSERVABLES_TAG + Serialize(observables));
    }}

    private static string Serialize(IDictionary<string, object> obs)
    {{
        var sb = new StringBuilder();
        sb.Append('{{');
        var first = true;
        foreach (var kv in obs)
        {{
            if (!first) sb.Append(',');
            first = false;
            sb.Append('"').Append(Escape(kv.Key)).Append('"').Append(':');
            sb.Append(SerializeValue(kv.Value));
        }}
        sb.Append('}}');
        return sb.ToString();
    }}

    private static string SerializeValue(object v)
    {{
        if (v == null) return "null";
        if (v is string s) return "\\"" + Escape(s) + "\\"";
        if (v is bool b) return b ? "true" : "false";
        if (v is float f) return FormatFloat(f);
        if (v is double d) return FormatFloat((float)d);
        if (v is int i) return i.ToString(CultureInfo.InvariantCulture);
        if (v is long l) return l.ToString(CultureInfo.InvariantCulture);
        if (v is Vector2 v2) return "[" + FormatFloat(v2.x) + "," + FormatFloat(v2.y) + "]";
        if (v is Vector3 v3) return "[" + FormatFloat(v3.x) + "," + FormatFloat(v3.y) + "," + FormatFloat(v3.z) + "]";
        if (v is System.Collections.IEnumerable e)
        {{
            var sb = new StringBuilder("[");
            var first = true;
            foreach (var item in e)
            {{
                if (!first) sb.Append(',');
                first = false;
                sb.Append(SerializeValue(item));
            }}
            sb.Append(']');
            return sb.ToString();
        }}
        return "\\"" + Escape(v.ToString()) + "\\"";
    }}

    private static string FormatFloat(float f) => f.ToString("R", CultureInfo.InvariantCulture);

    private static string Escape(string s)
    {{
        var sb = new StringBuilder();
        foreach (var c in s)
        {{
            switch (c)
            {{
                case '"': sb.Append("\\\\\\""); break;
                case '\\\\': sb.Append("\\\\\\\\"); break;
                case '\\n': sb.Append("\\\\n"); break;
                case '\\r': sb.Append("\\\\r"); break;
                case '\\t': sb.Append("\\\\t"); break;
                default: sb.Append(c); break;
            }}
        }}
        return sb.ToString();
    }}
}}
"""


def dotnet_available() -> bool:
    return shutil.which("dotnet") is not None


def _build_csharp_program(case: ParityCase) -> str:
    extra = "\n".join(f"using {ns};" for ns in case.extra_csharp_usings)
    body = textwrap.indent(textwrap.dedent(case.scenario_csharp_body).strip(), "        ")
    return _PROGRAM_TEMPLATE.format(extra_usings=extra, body=body)


def _run_csharp(case: ParityCase, *, timeout: float = 60.0) -> dict[str, Any]:
    """Compile + execute the C# leg; return parsed observables dict."""
    if not dotnet_available():
        pytest.skip("dotnet SDK not available — C# leg of parity harness skipped")

    program_src = _build_csharp_program(case)

    with tempfile.TemporaryDirectory(prefix="parity_") as tmpdir:
        tmp = Path(tmpdir)
        (tmp / "ParityHarness.csproj").write_text(_CSPROJ, encoding="utf-8")
        for stub in (
            "UnityEngine.cs",
            "UnityEngine.InputSystem.cs",
            "SystemCollections.cs",
            "SystemLinq.cs",
            "GlobalUsings.cs",
        ):
            src = _STUBS_DIR / stub
            if src.exists():
                shutil.copy(src, tmp / stub)
        (tmp / "Program.cs").write_text(program_src, encoding="utf-8")

        proc = subprocess.run(
            ["dotnet", "run", "-c", "Release", "--nologo", "-v", "quiet"],
            cwd=str(tmp),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        combined = (proc.stdout or "") + "\n" + (proc.stderr or "")
        tag = "PARITY_OBSERVABLES:"
        marker_line = next(
            (line for line in combined.splitlines() if tag in line),
            None,
        )
        if proc.returncode != 0 or marker_line is None:
            raise RuntimeError(
                f"C# parity leg failed for {case.name!r} (exit={proc.returncode})\n"
                f"--- stdout ---\n{proc.stdout}\n"
                f"--- stderr ---\n{proc.stderr}\n"
                f"--- program ---\n{program_src}"
            )
        json_text = marker_line[marker_line.index(tag) + len(tag):].strip()
        return json.loads(json_text)


def _run_python(case: ParityCase) -> dict[str, Any]:
    return case.scenario_python()


def _normalize(value: Any) -> Any:
    """Coerce Vector2/Vector3 etc. into plain lists so dict comparison works."""
    if value is None:
        return None
    if isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, (list, tuple)):
        return [_normalize(v) for v in value]
    if isinstance(value, dict):
        return {k: _normalize(v) for k, v in value.items()}
    for attrs in (("x", "y", "z"), ("x", "y")):
        if all(hasattr(value, a) for a in attrs):
            return [float(getattr(value, a)) for a in attrs]
    return value


def _floats_equal(a: Any, b: Any, tol: float) -> bool:
    if isinstance(a, float) or isinstance(b, float):
        try:
            return math.isclose(float(a), float(b), abs_tol=tol, rel_tol=tol)
        except (TypeError, ValueError):
            return False
    return a == b


def _deep_equal(a: Any, b: Any, tol: float) -> bool:
    a, b = _normalize(a), _normalize(b)
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return False
        return all(_deep_equal(a[k], b[k], tol) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return False
        return all(_deep_equal(x, y, tol) for x, y in zip(a, b))
    return _floats_equal(a, b, tol)


def assert_parity(case: ParityCase) -> None:
    """Run both legs, assert deep-equal observables.

    On mismatch the AssertionError shows the case name, both observable dicts
    side-by-side, and the first diverging key path. Skips cleanly if dotnet
    isn't installed (the Python leg still runs as a sanity check).
    """
    py_obs = _normalize(_run_python(case))
    cs_obs = _normalize(_run_csharp(case))  # may pytest.skip
    if not _deep_equal(py_obs, cs_obs, case.float_tolerance):
        raise AssertionError(
            f"Parity mismatch for case {case.name!r}\n"
            f"  python = {py_obs}\n"
            f"  csharp = {cs_obs}\n"
            f"  tolerance = {case.float_tolerance}"
        )
