"""Parity test: UnityEngine.Transform.Translate (M-9 phase 1).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Transform.Translate.html):
    Transform.Translate(Vector3 translation) shifts the transform's world-space
    position by `translation`. Successive calls accumulate. The default overload
    is in world space; relativeTo overloads are out of scope here.

Python impl: src.engine.transform.Transform.translate
"""

from __future__ import annotations

from src.engine.core import GameObject
from src.engine.math.vector import Vector3
from tests.parity._harness import ParityCase, assert_parity


def _py_single_translate() -> dict:
    go = GameObject("t")
    go.transform.translate(Vector3(1.0, 2.0, 3.0))
    p = go.transform.position
    return {"position": [p.x, p.y, p.z]}


_CS_SINGLE_TRANSLATE = """
var go = new GameObject("t");
go.transform.Translate(new Vector3(1.0f, 2.0f, 3.0f));
var p = go.transform.position;
observables["position"] = new[] { p.x, p.y, p.z };
"""


def test_translate_shifts_position_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.Translate single shift",
            scenario_python=_py_single_translate,
            scenario_csharp_body=_CS_SINGLE_TRANSLATE,
        )
    )


def _py_accumulating_translate() -> dict:
    go = GameObject("t")
    go.transform.translate(Vector3(1.0, 0.0, 0.0))
    go.transform.translate(Vector3(2.0, 0.0, 0.0))
    go.transform.translate(Vector3(0.0, 5.0, -1.0))
    p = go.transform.position
    return {"position": [p.x, p.y, p.z]}


_CS_ACCUMULATING_TRANSLATE = """
var go = new GameObject("t");
go.transform.Translate(new Vector3(1.0f, 0.0f, 0.0f));
go.transform.Translate(new Vector3(2.0f, 0.0f, 0.0f));
go.transform.Translate(new Vector3(0.0f, 5.0f, -1.0f));
var p = go.transform.position;
observables["position"] = new[] { p.x, p.y, p.z };
"""


def test_translate_calls_accumulate_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.Translate accumulates across calls",
            scenario_python=_py_accumulating_translate,
            scenario_csharp_body=_CS_ACCUMULATING_TRANSLATE,
        )
    )


def _py_translate_from_nonzero_origin() -> dict:
    go = GameObject("t")
    go.transform.position = Vector3(10.0, 10.0, 10.0)
    go.transform.translate(Vector3(-3.0, -3.0, -3.0))
    p = go.transform.position
    return {"position": [p.x, p.y, p.z]}


_CS_TRANSLATE_FROM_NONZERO = """
var go = new GameObject("t");
go.transform.position = new Vector3(10.0f, 10.0f, 10.0f);
go.transform.Translate(new Vector3(-3.0f, -3.0f, -3.0f));
var p = go.transform.position;
observables["position"] = new[] { p.x, p.y, p.z };
"""


def test_translate_relative_to_existing_position_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.Translate adds to existing position",
            scenario_python=_py_translate_from_nonzero_origin,
            scenario_csharp_body=_CS_TRANSLATE_FROM_NONZERO,
        )
    )
