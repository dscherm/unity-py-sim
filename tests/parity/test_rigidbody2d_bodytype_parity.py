"""Parity test: UnityEngine.Rigidbody2D.bodyType (M-9 phase 2).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Rigidbody2D-bodyType.html):
    Rigidbody2D.bodyType is a RigidbodyType2D enum: Dynamic | Kinematic | Static.
    Default Dynamic. Writeable. Both legs emit the enum NAME (lowercased) so
    Python's string-valued enum and C#'s int-valued enum compare equally.

Python impl: src.engine.physics.rigidbody.Rigidbody2D.body_type (property)
"""

from __future__ import annotations

from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from tests.parity._harness import ParityCase, assert_parity


def _py_default_body_type() -> dict:
    rb = Rigidbody2D()
    return {"body_type": rb.body_type.name.lower()}


_CS_DEFAULT_BODY_TYPE = """
var rb = new Rigidbody2D();
observables["body_type"] = rb.bodyType.ToString().ToLower();
"""


def test_default_body_type_is_dynamic_parity() -> None:
    assert_parity(
        ParityCase(
            name="Rigidbody2D.bodyType default = Dynamic",
            scenario_python=_py_default_body_type,
            scenario_csharp_body=_CS_DEFAULT_BODY_TYPE,
        )
    )


def _py_body_type_kinematic() -> dict:
    rb = Rigidbody2D()
    rb.body_type = RigidbodyType2D.KINEMATIC
    return {"body_type": rb.body_type.name.lower()}


_CS_BODY_TYPE_KINEMATIC = """
var rb = new Rigidbody2D();
rb.bodyType = RigidbodyType2D.Kinematic;
observables["body_type"] = rb.bodyType.ToString().ToLower();
"""


def test_body_type_kinematic_round_trip_parity() -> None:
    assert_parity(
        ParityCase(
            name="Rigidbody2D.bodyType = Kinematic round-trip",
            scenario_python=_py_body_type_kinematic,
            scenario_csharp_body=_CS_BODY_TYPE_KINEMATIC,
        )
    )


def _py_body_type_static() -> dict:
    rb = Rigidbody2D()
    rb.body_type = RigidbodyType2D.STATIC
    return {"body_type": rb.body_type.name.lower()}


_CS_BODY_TYPE_STATIC = """
var rb = new Rigidbody2D();
rb.bodyType = RigidbodyType2D.Static;
observables["body_type"] = rb.bodyType.ToString().ToLower();
"""


def test_body_type_static_round_trip_parity() -> None:
    assert_parity(
        ParityCase(
            name="Rigidbody2D.bodyType = Static round-trip",
            scenario_python=_py_body_type_static,
            scenario_csharp_body=_CS_BODY_TYPE_STATIC,
        )
    )
