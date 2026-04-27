"""Parity test: UnityEngine.Rigidbody2D.gravityScale (M-9 phase 2).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Rigidbody2D-gravityScale.html):
    Rigidbody2D.gravityScale is a float multiplier on the global gravity vector.
    Default 1.0. Setting to 0 disables gravity for this body. Writeable.

Python impl: src.engine.physics.rigidbody.Rigidbody2D.gravity_scale (property)
"""

from __future__ import annotations

from src.engine.physics.rigidbody import Rigidbody2D
from tests.parity._harness import ParityCase, assert_parity


def _py_default_gravity_scale() -> dict:
    rb = Rigidbody2D()
    return {"gravity_scale": rb.gravity_scale}


_CS_DEFAULT_GRAVITY_SCALE = """
var rb = new Rigidbody2D();
observables["gravity_scale"] = rb.gravityScale;
"""


def test_default_gravity_scale_is_one_parity() -> None:
    assert_parity(
        ParityCase(
            name="Rigidbody2D.gravityScale default = 1.0",
            scenario_python=_py_default_gravity_scale,
            scenario_csharp_body=_CS_DEFAULT_GRAVITY_SCALE,
        )
    )


def _py_gravity_scale_zero() -> dict:
    rb = Rigidbody2D()
    rb.gravity_scale = 0.0
    return {"gravity_scale": rb.gravity_scale}


_CS_GRAVITY_SCALE_ZERO = """
var rb = new Rigidbody2D();
rb.gravityScale = 0.0f;
observables["gravity_scale"] = rb.gravityScale;
"""


def test_gravity_scale_zero_disables_gravity_parity() -> None:
    assert_parity(
        ParityCase(
            name="Rigidbody2D.gravityScale = 0 round-trip",
            scenario_python=_py_gravity_scale_zero,
            scenario_csharp_body=_CS_GRAVITY_SCALE_ZERO,
        )
    )


def _py_gravity_scale_negative() -> dict:
    """Negative gravity-scale flips the gravity direction. Both legs must agree."""
    rb = Rigidbody2D()
    rb.gravity_scale = -2.0
    return {"gravity_scale": rb.gravity_scale}


_CS_GRAVITY_SCALE_NEGATIVE = """
var rb = new Rigidbody2D();
rb.gravityScale = -2.0f;
observables["gravity_scale"] = rb.gravityScale;
"""


def test_gravity_scale_negative_round_trip_parity() -> None:
    assert_parity(
        ParityCase(
            name="Rigidbody2D.gravityScale = -2.0 round-trip",
            scenario_python=_py_gravity_scale_negative,
            scenario_csharp_body=_CS_GRAVITY_SCALE_NEGATIVE,
        )
    )
