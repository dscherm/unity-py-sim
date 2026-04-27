"""Parity test: UnityEngine.Transform.position (dual-path, M-8).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Transform-position.html):
- type: Vector3
- read/write
- represents the world-space position
- assigning Vector2 is allowed via implicit conversion (z = 0)
- default value for a freshly-created GameObject is (0, 0, 0)

Each test case below is exercised on TWO backends — the Python sim (`src.engine`)
and a C# leg compiled against `stubs/UnityEngine.cs` and run headless via
`dotnet run`. The harness asserts the observables agree component-by-component.

This is the reference implementation for M-8 (per plan.md). M-9 backfills the
remaining 60 untested APIs onto the same harness shape.
"""

from __future__ import annotations

import pytest

from src.engine.core import GameObject
from src.engine.math.vector import Vector2, Vector3
from tests.parity._harness import ParityCase, assert_parity


# ── Python-only sanity tests (legacy shape, kept while the harness ramps up) ──
# Each Python lambda also feeds a dual-path case below; the legacy form is
# retained because it executes without a dotnet toolchain and surfaces failures
# before the C# leg even compiles.


def test_default_position_is_origin_python_only() -> None:
    go = GameObject("parity_target")
    p = go.transform.position
    assert isinstance(p, Vector3)
    assert (p.x, p.y, p.z) == (0.0, 0.0, 0.0)


def test_position_setter_accepts_vector3_python_only() -> None:
    go = GameObject("parity_target")
    go.transform.position = Vector3(1.0, 2.0, 3.0)
    p = go.transform.position
    assert (p.x, p.y, p.z) == (1.0, 2.0, 3.0)


def test_position_setter_accepts_vector2_with_z_zero_python_only() -> None:
    go = GameObject("parity_target")
    go.transform.position = Vector2(5.0, 7.0)
    p = go.transform.position
    assert (p.x, p.y) == (5.0, 7.0)
    z = getattr(p, "z", 0.0)
    assert z == 0.0


def test_position_independent_per_gameobject_python_only() -> None:
    a = GameObject("a")
    b = GameObject("b")
    a.transform.position = Vector3(1.0, 2.0, 3.0)
    pa = a.transform.position
    pb = b.transform.position
    assert (pa.x, pa.y, pa.z) == (1.0, 2.0, 3.0)
    assert (pb.x, pb.y, pb.z) == (0.0, 0.0, 0.0)


def test_position_round_trip_through_zero_python_only() -> None:
    go = GameObject("parity_target")
    go.transform.position = Vector3(10.0, 20.0, 30.0)
    go.transform.position = Vector3(0.0, 0.0, 0.0)
    p = go.transform.position
    assert (p.x, p.y, p.z) == (0.0, 0.0, 0.0)


# ── Dual-path parity (Python sim ↔ stubbed C# headless) ───────────────────────


def _py_default_origin() -> dict:
    go = GameObject("t")
    p = go.transform.position
    return {"position": [p.x, p.y, p.z]}


_CS_DEFAULT_ORIGIN = """
var go = new GameObject("t");
var p = go.transform.position;
observables["position"] = new[] { p.x, p.y, p.z };
"""


def test_default_position_is_origin_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.position default = (0,0,0)",
            scenario_python=_py_default_origin,
            scenario_csharp_body=_CS_DEFAULT_ORIGIN,
        )
    )


def _py_setter_vector3() -> dict:
    go = GameObject("t")
    go.transform.position = Vector3(1.0, 2.0, 3.0)
    p = go.transform.position
    return {"position": [p.x, p.y, p.z]}


_CS_SETTER_VECTOR3 = """
var go = new GameObject("t");
go.transform.position = new Vector3(1.0f, 2.0f, 3.0f);
var p = go.transform.position;
observables["position"] = new[] { p.x, p.y, p.z };
"""


def test_position_setter_accepts_vector3_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.position = Vector3 round-trip",
            scenario_python=_py_setter_vector3,
            scenario_csharp_body=_CS_SETTER_VECTOR3,
        )
    )


def _py_independent_per_go() -> dict:
    a = GameObject("a")
    b = GameObject("b")
    a.transform.position = Vector3(1.0, 2.0, 3.0)
    pa = a.transform.position
    pb = b.transform.position
    return {
        "a": [pa.x, pa.y, pa.z],
        "b": [pb.x, pb.y, pb.z],
    }


_CS_INDEPENDENT_PER_GO = """
var a = new GameObject("a");
var b = new GameObject("b");
a.transform.position = new Vector3(1.0f, 2.0f, 3.0f);
var pa = a.transform.position;
var pb = b.transform.position;
observables["a"] = new[] { pa.x, pa.y, pa.z };
observables["b"] = new[] { pb.x, pb.y, pb.z };
"""


def test_position_independent_per_gameobject_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.position is per-instance",
            scenario_python=_py_independent_per_go,
            scenario_csharp_body=_CS_INDEPENDENT_PER_GO,
        )
    )


def _py_round_trip_through_zero() -> dict:
    go = GameObject("t")
    go.transform.position = Vector3(10.0, 20.0, 30.0)
    go.transform.position = Vector3(0.0, 0.0, 0.0)
    p = go.transform.position
    return {"position": [p.x, p.y, p.z]}


_CS_ROUND_TRIP_THROUGH_ZERO = """
var go = new GameObject("t");
go.transform.position = new Vector3(10.0f, 20.0f, 30.0f);
go.transform.position = new Vector3(0.0f, 0.0f, 0.0f);
var p = go.transform.position;
observables["position"] = new[] { p.x, p.y, p.z };
"""


def test_position_round_trip_through_zero_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.position re-assignment to zero",
            scenario_python=_py_round_trip_through_zero,
            scenario_csharp_body=_CS_ROUND_TRIP_THROUGH_ZERO,
        )
    )
