"""Parity test: UnityEngine.Rigidbody2D.drag (M-9 phase 2).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Rigidbody2D-drag.html):
    Rigidbody2D.drag is a float of linear drag coefficient. Default 0. Writeable.
    Affects how velocity decays; this test only verifies the read/write round-trip.

Python impl: src.engine.physics.rigidbody.Rigidbody2D.drag (property)
"""

from __future__ import annotations

from src.engine.physics.rigidbody import Rigidbody2D
from tests.parity._harness import ParityCase, assert_parity


def _py_default_drag() -> dict:
    rb = Rigidbody2D()
    return {"drag": rb.drag}


_CS_DEFAULT_DRAG = """
var rb = new Rigidbody2D();
observables["drag"] = rb.drag;
"""


def test_default_drag_is_zero_parity() -> None:
    assert_parity(
        ParityCase(
            name="Rigidbody2D.drag default = 0",
            scenario_python=_py_default_drag,
            scenario_csharp_body=_CS_DEFAULT_DRAG,
        )
    )


def _py_drag_round_trip() -> dict:
    rb = Rigidbody2D()
    rb.drag = 0.5
    return {"drag": rb.drag}


_CS_DRAG_ROUND_TRIP = """
var rb = new Rigidbody2D();
rb.drag = 0.5f;
observables["drag"] = rb.drag;
"""


def test_drag_setter_round_trip_parity() -> None:
    assert_parity(
        ParityCase(
            name="Rigidbody2D.drag setter round-trip",
            scenario_python=_py_drag_round_trip,
            scenario_csharp_body=_CS_DRAG_ROUND_TRIP,
        )
    )
