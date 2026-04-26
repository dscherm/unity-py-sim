"""Parity tests: UnityEngine.Vector2 / Vector3 static constants.

Documented Unity behavior:
- https://docs.unity3d.com/ScriptReference/Vector2.html
- https://docs.unity3d.com/ScriptReference/Vector3.html

Vector2 statics: zero(0,0), one(1,1), up(0,1), down(0,-1), left(-1,0), right(1,0)
Vector3 statics: zero(0,0,0), one(1,1,1), up(0,1,0), down(0,-1,0),
                  left(-1,0,0), right(1,0,0), forward(0,0,1), back(0,0,-1)

These are accessed as class-level attributes (Vector2.zero), and each access
returns a fresh instance so callers cannot mutate the canonical reference.
"""

from __future__ import annotations

import pytest

from src.engine.math.vector import Vector2, Vector3


# ---------------- Vector2 ----------------

@pytest.mark.parametrize("attr,expected", [
    ("zero", (0.0, 0.0)),
    ("one", (1.0, 1.0)),
    ("up", (0.0, 1.0)),
    ("down", (0.0, -1.0)),
    ("left", (-1.0, 0.0)),
    ("right", (1.0, 0.0)),
])
def test_vector2_static_constants_match_unity(attr: str, expected: tuple[float, float]):
    """Vector2.<attr> must return the documented (x, y) pair."""
    v = getattr(Vector2, attr)
    assert isinstance(v, Vector2), f"Vector2.{attr} must be a Vector2"
    assert (v.x, v.y) == expected, f"Vector2.{attr} expected {expected}, got ({v.x}, {v.y})"


def test_vector2_zero_is_independent_per_access():
    """Mutating one Vector2.zero must not affect a subsequent read.
    Unity returns a fresh struct each time; our sim must too."""
    a = Vector2.zero
    a.x = 99.0
    b = Vector2.zero
    assert (b.x, b.y) == (0.0, 0.0), (
        f"Vector2.zero leaked mutation across reads: got ({b.x}, {b.y})"
    )


# ---------------- Vector3 ----------------

@pytest.mark.parametrize("attr,expected", [
    ("zero", (0.0, 0.0, 0.0)),
    ("one", (1.0, 1.0, 1.0)),
    ("up", (0.0, 1.0, 0.0)),
    ("down", (0.0, -1.0, 0.0)),
    ("left", (-1.0, 0.0, 0.0)),
    ("right", (1.0, 0.0, 0.0)),
    ("forward", (0.0, 0.0, 1.0)),
    ("back", (0.0, 0.0, -1.0)),
])
def test_vector3_static_constants_match_unity(attr: str, expected: tuple[float, float, float]):
    """Vector3.<attr> must return the documented (x, y, z) triple."""
    v = getattr(Vector3, attr)
    assert isinstance(v, Vector3), f"Vector3.{attr} must be a Vector3"
    assert (v.x, v.y, v.z) == expected, (
        f"Vector3.{attr} expected {expected}, got ({v.x}, {v.y}, {v.z})"
    )


def test_vector3_forward_is_positive_z():
    """Unity uses a left-handed coordinate system; forward is +Z.
    Catches accidental flip to -Z (a common porting bug)."""
    f = Vector3.forward
    assert f.z == 1.0
    assert f.x == 0.0 and f.y == 0.0


def test_vector3_back_opposes_forward():
    """back = -forward by Unity's documented values."""
    f = Vector3.forward
    b = Vector3.back
    assert (b.x, b.y, b.z) == (-f.x, -f.y, -f.z)


def test_vector3_zero_is_independent_per_access():
    """Mutating Vector3.zero must not leak to subsequent reads."""
    a = Vector3.zero
    a.x = 42.0
    b = Vector3.zero
    assert (b.x, b.y, b.z) == (0.0, 0.0, 0.0)
