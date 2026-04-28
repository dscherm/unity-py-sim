"""Parity test: UnityEngine.Rigidbody2D.mass (M-9 phase 2).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Rigidbody2D-mass.html):
    Rigidbody2D.mass is a float in kg. Default 1.0. Writeable. Mass affects how
    AddForce-applied forces translate to acceleration; this test only verifies
    the read/write round-trip — physics integration parity is out of scope.

Python impl: src.engine.physics.rigidbody.Rigidbody2D.mass (property)
"""

from __future__ import annotations

from src.engine.physics.rigidbody import Rigidbody2D
from tests.parity._harness import ParityCase, assert_parity


def _py_default_mass() -> dict:
    rb = Rigidbody2D()
    return {"mass": rb.mass}


_CS_DEFAULT_MASS = """
var rb = new Rigidbody2D();
observables["mass"] = rb.mass;
"""


def test_default_mass_is_one_parity() -> None:
    assert_parity(
        ParityCase(
            name="Rigidbody2D.mass default = 1.0",
            scenario_python=_py_default_mass,
            scenario_csharp_body=_CS_DEFAULT_MASS,
        )
    )


def _py_mass_round_trip() -> dict:
    rb = Rigidbody2D()
    rb.mass = 5.0
    return {"mass": rb.mass}


_CS_MASS_ROUND_TRIP = """
var rb = new Rigidbody2D();
rb.mass = 5.0f;
observables["mass"] = rb.mass;
"""


def test_mass_setter_round_trip_parity() -> None:
    assert_parity(
        ParityCase(
            name="Rigidbody2D.mass setter round-trip",
            scenario_python=_py_mass_round_trip,
            scenario_csharp_body=_CS_MASS_ROUND_TRIP,
        )
    )
