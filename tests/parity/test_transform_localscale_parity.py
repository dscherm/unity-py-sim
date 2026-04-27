"""Parity test: UnityEngine.Transform.localScale (M-9 phase 1).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Transform-localScale.html):
    Transform.localScale is the scale of the transform relative to its parent.
    Default value for a freshly-created transform is Vector3.one (1, 1, 1).
    Setter accepts Vector3 and stores verbatim.

Python impl: src.engine.transform.Transform.local_scale (property)
"""

from __future__ import annotations

from src.engine.core import GameObject
from src.engine.math.vector import Vector3
from tests.parity._harness import ParityCase, assert_parity


def _py_default_local_scale() -> dict:
    go = GameObject("t")
    s = go.transform.local_scale
    return {"local_scale": [s.x, s.y, s.z]}


_CS_DEFAULT_LOCAL_SCALE = """
var go = new GameObject("t");
var s = go.transform.localScale;
observables["local_scale"] = new[] { s.x, s.y, s.z };
"""


def test_default_local_scale_is_one_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.localScale default = (1,1,1)",
            scenario_python=_py_default_local_scale,
            scenario_csharp_body=_CS_DEFAULT_LOCAL_SCALE,
        )
    )


def _py_set_local_scale() -> dict:
    go = GameObject("t")
    go.transform.local_scale = Vector3(2.0, 3.0, 0.5)
    s = go.transform.local_scale
    return {"local_scale": [s.x, s.y, s.z]}


_CS_SET_LOCAL_SCALE = """
var go = new GameObject("t");
go.transform.localScale = new Vector3(2.0f, 3.0f, 0.5f);
var s = go.transform.localScale;
observables["local_scale"] = new[] { s.x, s.y, s.z };
"""


def test_local_scale_setter_round_trip_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.localScale setter round-trip",
            scenario_python=_py_set_local_scale,
            scenario_csharp_body=_CS_SET_LOCAL_SCALE,
        )
    )


def _py_local_scale_independent_per_go() -> dict:
    a = GameObject("a")
    b = GameObject("b")
    a.transform.local_scale = Vector3(5.0, 5.0, 5.0)
    sa = a.transform.local_scale
    sb = b.transform.local_scale
    return {
        "a": [sa.x, sa.y, sa.z],
        "b": [sb.x, sb.y, sb.z],
    }


_CS_LOCAL_SCALE_INDEPENDENT = """
var a = new GameObject("a");
var b = new GameObject("b");
a.transform.localScale = new Vector3(5.0f, 5.0f, 5.0f);
var sa = a.transform.localScale;
var sb = b.transform.localScale;
observables["a"] = new[] { sa.x, sa.y, sa.z };
observables["b"] = new[] { sb.x, sb.y, sb.z };
"""


def test_local_scale_independent_per_gameobject_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.localScale is per-instance",
            scenario_python=_py_local_scale_independent_per_go,
            scenario_csharp_body=_CS_LOCAL_SCALE_INDEPENDENT,
        )
    )
