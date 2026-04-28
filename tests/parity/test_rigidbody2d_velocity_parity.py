"""Parity test: UnityEngine.Rigidbody2D.velocity (M-9 phase 2 / Rigidbody2D batch).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Rigidbody2D-velocity.html):
    Rigidbody2D.velocity is a Vector2 of linear velocity in world units / second.
    Default value for a freshly-created body is Vector2.zero. Writeable.

Python impl: src.engine.physics.rigidbody.Rigidbody2D.velocity (property)
"""

from __future__ import annotations

from src.engine.math.vector import Vector2
from src.engine.physics.rigidbody import Rigidbody2D
from tests.parity._harness import ParityCase, assert_parity


def _py_default_velocity() -> dict:
    rb = Rigidbody2D()
    v = rb.velocity
    return {"velocity": [v.x, v.y]}


_CS_DEFAULT_VELOCITY = """
var rb = new Rigidbody2D();
var v = rb.velocity;
observables["velocity"] = new[] { v.x, v.y };
"""


def test_default_velocity_is_zero_parity() -> None:
    assert_parity(
        ParityCase(
            name="Rigidbody2D.velocity default = (0,0)",
            scenario_python=_py_default_velocity,
            scenario_csharp_body=_CS_DEFAULT_VELOCITY,
        )
    )


def _py_velocity_round_trip() -> dict:
    rb = Rigidbody2D()
    rb.velocity = Vector2(3.5, -2.0)
    v = rb.velocity
    return {"velocity": [v.x, v.y]}


_CS_VELOCITY_ROUND_TRIP = """
var rb = new Rigidbody2D();
rb.velocity = new Vector2(3.5f, -2.0f);
var v = rb.velocity;
observables["velocity"] = new[] { v.x, v.y };
"""


def test_velocity_setter_round_trip_parity() -> None:
    assert_parity(
        ParityCase(
            name="Rigidbody2D.velocity setter round-trip",
            scenario_python=_py_velocity_round_trip,
            scenario_csharp_body=_CS_VELOCITY_ROUND_TRIP,
        )
    )
