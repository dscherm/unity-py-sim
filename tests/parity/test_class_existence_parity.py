"""Parity tests: class-existence + canonical default for utility classes (M-9 phase 4).

Covers single-row entries in the parity matrix where the class itself counts
toward coverage and there's one obvious "does the API exist with the right
default" check. Exercised classes:

  - Quaternion       — identity.w == 1
  - Mathf            — PI ≈ 3.14159 (float-tolerance ok)
  - Debug            — Log() callable without throw
  - BoxCollider2D    — default size (1, 1)
  - CircleCollider2D — default radius 0.5
  - PhysicsMaterial2D — default bounciness 0, friction 0.4
  - Physics2D        — Raycast returns a default RaycastHit2D
  - RaycastHit2D     — default-constructed has zero-distance

These don't replace future per-property parity tests; they just lock in the
"this class exists and has Unity-canonical defaults" fact so a future stub
regression on any of them shows up red.
"""

from __future__ import annotations

import math

import pytest

from src.engine.math.mathf import Mathf
from src.engine.math.quaternion import Quaternion
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D, PhysicsMaterial2D
from tests.parity._harness import ParityCase, assert_parity


# ── Quaternion.identity ─────────────────────────────────────────────────────


def _py_quaternion_identity() -> dict:
    q = Quaternion.identity
    return {"q": [q.x, q.y, q.z, q.w]}


_CS_QUATERNION_IDENTITY = """
var q = Quaternion.identity;
observables["q"] = new[] { q.x, q.y, q.z, q.w };
"""


def test_quaternion_identity_is_0001_parity() -> None:
    assert_parity(
        ParityCase(
            name="Quaternion.identity = (0, 0, 0, 1)",
            scenario_python=_py_quaternion_identity,
            scenario_csharp_body=_CS_QUATERNION_IDENTITY,
        )
    )


# ── Mathf.PI ─────────────────────────────────────────────────────────────────


def _py_mathf_pi() -> dict:
    return {"pi": float(Mathf.PI)}


_CS_MATHF_PI = """
observables["pi"] = Mathf.PI;
"""


def test_mathf_pi_matches_pi_parity() -> None:
    assert_parity(
        ParityCase(
            name="Mathf.PI ≈ 3.14159",
            scenario_python=_py_mathf_pi,
            scenario_csharp_body=_CS_MATHF_PI,
            float_tolerance=1e-5,  # double vs float precision difference
        )
    )


# ── Debug.Log (callable without throw) ───────────────────────────────────────


def _py_debug_log_no_throw() -> dict:
    """Python's Debug.Log mirrors Unity — fire-and-forget logging. No return."""
    from src.engine.debug import Debug
    Debug.log("parity-debug-message")
    return {"ok": True}


_CS_DEBUG_LOG_NO_THROW = """
Debug.Log("parity-debug-message");
observables["ok"] = true;
"""


def test_debug_log_does_not_throw_parity() -> None:
    assert_parity(
        ParityCase(
            name="Debug.Log() runs without throwing",
            scenario_python=_py_debug_log_no_throw,
            scenario_csharp_body=_CS_DEBUG_LOG_NO_THROW,
        )
    )


# ── BoxCollider2D default size = (1, 1) ──────────────────────────────────────


def _py_boxcollider2d_default_size() -> dict:
    bc = BoxCollider2D()
    return {"size": [bc.size.x, bc.size.y]}


_CS_BOXCOLLIDER2D_DEFAULT_SIZE = """
var bc = new BoxCollider2D();
observables["size"] = new[] { bc.size.x, bc.size.y };
"""


def test_boxcollider2d_default_size_parity() -> None:
    assert_parity(
        ParityCase(
            name="BoxCollider2D default size = (1, 1)",
            scenario_python=_py_boxcollider2d_default_size,
            scenario_csharp_body=_CS_BOXCOLLIDER2D_DEFAULT_SIZE,
        )
    )


# ── CircleCollider2D default radius = 0.5 ────────────────────────────────────


def _py_circlecollider2d_default_radius() -> dict:
    cc = CircleCollider2D()
    return {"radius": cc.radius}


_CS_CIRCLECOLLIDER2D_DEFAULT_RADIUS = """
var cc = new CircleCollider2D();
observables["radius"] = cc.radius;
"""


def test_circlecollider2d_default_radius_parity() -> None:
    assert_parity(
        ParityCase(
            name="CircleCollider2D default radius = 0.5",
            scenario_python=_py_circlecollider2d_default_radius,
            scenario_csharp_body=_CS_CIRCLECOLLIDER2D_DEFAULT_RADIUS,
        )
    )


# ── PhysicsMaterial2D defaults: bounciness=0, friction=0.4 ──────────────────


def _py_physicsmaterial2d_defaults() -> dict:
    pm = PhysicsMaterial2D()
    return {"bounciness": pm.bounciness, "friction": pm.friction}


_CS_PHYSICSMATERIAL2D_DEFAULTS = """
var pm = new PhysicsMaterial2D();
observables["bounciness"] = pm.bounciness;
observables["friction"] = pm.friction;
"""


def test_physicsmaterial2d_defaults_parity() -> None:
    assert_parity(
        ParityCase(
            name="PhysicsMaterial2D defaults: bounciness=0, friction=0.4",
            scenario_python=_py_physicsmaterial2d_defaults,
            scenario_csharp_body=_CS_PHYSICSMATERIAL2D_DEFAULTS,
        )
    )


# ── Physics2D + RaycastHit2D (no-hit raycast yields default RaycastHit2D) ───


def _py_physics2d_no_hit_raycast() -> dict:
    """Python Physics2D.raycast on an empty world yields a hit-less RaycastHit2D
    with collider==None and a zero distance. C# stub returns default(RaycastHit2D)
    which has the same zero-distance shape. Both legs emit the distance for parity."""
    from src.engine.math.vector import Vector2
    from src.engine.physics.physics_manager import Physics2D
    hit = Physics2D.raycast(Vector2(0, 0), Vector2(1, 0), 10.0)
    distance = hit.distance if hit is not None else 0.0
    return {"distance": float(distance)}


_CS_PHYSICS2D_NO_HIT_RAYCAST = """
var hit = Physics2D.Raycast(new Vector2(0f, 0f), new Vector2(1f, 0f), 10f);
observables["distance"] = hit.distance;
"""


def test_physics2d_raycast_no_hit_distance_parity() -> None:
    assert_parity(
        ParityCase(
            name="Physics2D.Raycast no-hit yields zero-distance RaycastHit2D",
            scenario_python=_py_physics2d_no_hit_raycast,
            scenario_csharp_body=_CS_PHYSICS2D_NO_HIT_RAYCAST,
        )
    )
