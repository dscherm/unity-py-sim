"""Parity test: UnityEngine.Transform.rotation (M-9 phase 4).

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Transform-rotation.html):
    Transform.rotation is a Quaternion of world-space rotation. Default is
    Quaternion.identity = (0, 0, 0, 1). Writeable.

This test exercises only the field default + setter round-trip on Quaternion
identity values (which both legs can store as plain xyzw fields without
requiring full Quaternion arithmetic). Behavioral parity for Quaternion-math-
dependent surfaces is intentionally not yet covered — the C# stub's Quaternion
operators return `default` and would diverge from Python's faithful pyrr-backed
math. Those skeletons remain SCAFFOLD-marked.

Python impl: src.engine.transform.Transform.rotation (property)
"""

from __future__ import annotations

from src.engine.core import GameObject
from src.engine.math.quaternion import Quaternion
from tests.parity._harness import ParityCase, assert_parity


def _py_default_rotation_is_identity() -> dict:
    go = GameObject("t")
    q = go.transform.rotation
    return {"q": [q.x, q.y, q.z, q.w]}


_CS_DEFAULT_ROTATION_IS_IDENTITY = """
var go = new GameObject("t");
var q = go.transform.rotation;
observables["q"] = new[] { q.x, q.y, q.z, q.w };
"""


def test_default_rotation_is_identity_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.rotation default = Quaternion.identity",
            scenario_python=_py_default_rotation_is_identity,
            scenario_csharp_body=_CS_DEFAULT_ROTATION_IS_IDENTITY,
        )
    )


def _py_rotation_setter_round_trip() -> dict:
    go = GameObject("t")
    go.transform.rotation = Quaternion(0.1, 0.2, 0.3, 0.9)
    q = go.transform.rotation
    return {"q": [q.x, q.y, q.z, q.w]}


_CS_ROTATION_SETTER_ROUND_TRIP = """
var go = new GameObject("t");
go.transform.rotation = new Quaternion(0.1f, 0.2f, 0.3f, 0.9f);
var q = go.transform.rotation;
observables["q"] = new[] { q.x, q.y, q.z, q.w };
"""


def test_rotation_setter_round_trip_parity() -> None:
    assert_parity(
        ParityCase(
            name="Transform.rotation setter round-trip preserves Quaternion components",
            scenario_python=_py_rotation_setter_round_trip,
            scenario_csharp_body=_CS_ROTATION_SETTER_ROUND_TRIP,
        )
    )
