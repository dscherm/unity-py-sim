"""Parity test: UnityEngine.Transform.position.

Documented Unity behavior (https://docs.unity3d.com/ScriptReference/Transform-position.html):
- type: Vector3
- read/write
- represents the world-space position
- assigning Vector2 is allowed via implicit conversion (z = 0)
- default value for a freshly-created GameObject is (0, 0, 0)
"""

from __future__ import annotations

import pytest

from src.engine.core import GameObject
from src.engine.math.vector import Vector2, Vector3


@pytest.fixture
def go() -> GameObject:
    return GameObject("parity_target")


def test_default_position_is_origin(go: GameObject) -> None:
    """A freshly-created GameObject's transform.position is (0, 0, 0)."""
    p = go.transform.position
    assert isinstance(p, Vector3), f"expected Vector3, got {type(p).__name__}"
    assert (p.x, p.y, p.z) == (0.0, 0.0, 0.0)


def test_position_setter_accepts_vector3(go: GameObject) -> None:
    """Setting transform.position to a Vector3 stores the components verbatim."""
    go.transform.position = Vector3(1.0, 2.0, 3.0)
    p = go.transform.position
    assert (p.x, p.y, p.z) == (1.0, 2.0, 3.0)


def test_position_setter_accepts_vector2_with_z_zero(go: GameObject) -> None:
    """Unity allows Vector2 → Vector3 implicit conversion: the z component
    becomes 0. unity-py-sim mirrors this so 2D code reads naturally."""
    go.transform.position = Vector2(5.0, 7.0)
    p = go.transform.position
    assert (p.x, p.y) == (5.0, 7.0)
    z = getattr(p, "z", 0.0)
    assert z == 0.0, f"Vector2 assignment must zero the z component, got z={z}"


def test_position_independent_per_gameobject() -> None:
    """Each GameObject's Transform.position is independent — assigning to
    one does not affect another. Catches accidental shared state."""
    a = GameObject("a")
    b = GameObject("b")
    a.transform.position = Vector3(1.0, 2.0, 3.0)
    pa = a.transform.position
    pb = b.transform.position
    assert (pa.x, pa.y, pa.z) == (1.0, 2.0, 3.0)
    assert (pb.x, pb.y, pb.z) == (0.0, 0.0, 0.0)


def test_position_round_trip_through_zero(go: GameObject) -> None:
    """Set → mutate → reset round-trips cleanly."""
    go.transform.position = Vector3(10.0, 20.0, 30.0)
    go.transform.position = Vector3(0.0, 0.0, 0.0)
    p = go.transform.position
    assert (p.x, p.y, p.z) == (0.0, 0.0, 0.0)
