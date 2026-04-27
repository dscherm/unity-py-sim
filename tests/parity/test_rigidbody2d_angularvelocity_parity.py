"""Parity test: UnityEngine.Rigidbody2D.angularVelocity (M-9 phase 2).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Rigidbody2D-angularVelocity.html):
    Rigidbody2D.angularVelocity is a float of degrees/second. Default 0. Writeable.

Python impl: src.engine.physics.rigidbody.Rigidbody2D.angular_velocity (property)
"""

from __future__ import annotations

from src.engine.physics.rigidbody import Rigidbody2D
from tests.parity._harness import ParityCase, assert_parity


def _py_default_angular_velocity() -> dict:
    rb = Rigidbody2D()
    return {"angular": rb.angular_velocity}


_CS_DEFAULT_ANGULAR = """
var rb = new Rigidbody2D();
observables["angular"] = rb.angularVelocity;
"""


def test_default_angular_velocity_is_zero_parity() -> None:
    assert_parity(
        ParityCase(
            name="Rigidbody2D.angularVelocity default = 0",
            scenario_python=_py_default_angular_velocity,
            scenario_csharp_body=_CS_DEFAULT_ANGULAR,
        )
    )


def _py_angular_round_trip() -> dict:
    rb = Rigidbody2D()
    rb.angular_velocity = 45.0
    return {"angular": rb.angular_velocity}


_CS_ANGULAR_ROUND_TRIP = """
var rb = new Rigidbody2D();
rb.angularVelocity = 45.0f;
observables["angular"] = rb.angularVelocity;
"""


def test_angular_velocity_setter_round_trip_parity() -> None:
    assert_parity(
        ParityCase(
            name="Rigidbody2D.angularVelocity setter round-trip",
            scenario_python=_py_angular_round_trip,
            scenario_csharp_body=_CS_ANGULAR_ROUND_TRIP,
        )
    )
