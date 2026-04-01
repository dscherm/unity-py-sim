"""Tests for Vector2, Vector3, Quaternion, and Mathf."""

import math
import pytest

from src.engine.math.vector import Vector2, Vector3
from src.engine.math.quaternion import Quaternion
from src.engine.math.mathf import Mathf


# ── Vector2 ──────────────────────────────────────────────────


class TestVector2:
    def test_construction(self):
        v = Vector2(3, 4)
        assert v.x == 3.0
        assert v.y == 4.0

    def test_zero(self):
        assert Vector2.zero == Vector2(0, 0)

    def test_magnitude(self):
        v = Vector2(3, 4)
        assert abs(v.magnitude - 5.0) < 1e-5

    def test_sqr_magnitude(self):
        v = Vector2(3, 4)
        assert abs(v.sqr_magnitude - 25.0) < 1e-5

    def test_normalized(self):
        v = Vector2(3, 4)
        n = v.normalized
        assert abs(n.magnitude - 1.0) < 1e-5

    def test_normalized_zero(self):
        assert Vector2(0, 0).normalized == Vector2(0, 0)

    def test_add(self):
        assert Vector2(1, 2) + Vector2(3, 4) == Vector2(4, 6)

    def test_sub(self):
        assert Vector2(5, 7) - Vector2(2, 3) == Vector2(3, 4)

    def test_mul(self):
        assert Vector2(2, 3) * 2 == Vector2(4, 6)

    def test_rmul(self):
        assert 2 * Vector2(2, 3) == Vector2(4, 6)

    def test_div(self):
        assert Vector2(4, 6) / 2 == Vector2(2, 3)

    def test_neg(self):
        assert -Vector2(1, -2) == Vector2(-1, 2)

    def test_dot(self):
        assert abs(Vector2.dot(Vector2(1, 0), Vector2(0, 1))) < 1e-5

    def test_distance(self):
        assert abs(Vector2.distance(Vector2(0, 0), Vector2(3, 4)) - 5.0) < 1e-5

    def test_lerp(self):
        result = Vector2.lerp(Vector2(0, 0), Vector2(10, 10), 0.5)
        assert result == Vector2(5, 5)

    def test_lerp_clamped(self):
        result = Vector2.lerp(Vector2(0, 0), Vector2(10, 10), 2.0)
        assert result == Vector2(10, 10)

    def test_angle(self):
        a = Vector2(1, 0)
        b = Vector2(0, 1)
        assert abs(Vector2.angle(a, b) - 90.0) < 0.01

    def test_equality(self):
        assert Vector2(1.0, 2.0) == Vector2(1.0, 2.0)
        assert Vector2(1.0, 2.0) != Vector2(1.0, 3.0)

    def test_static_constructors(self):
        assert Vector2.up == Vector2(0, 1)
        assert Vector2.right == Vector2(1, 0)
        assert Vector2.down == Vector2(0, -1)
        assert Vector2.left == Vector2(-1, 0)
        assert Vector2.one == Vector2(1, 1)


# ── Vector3 ──────────────────────────────────────────────────


class TestVector3:
    def test_construction(self):
        v = Vector3(1, 2, 3)
        assert v.x == 1.0
        assert v.y == 2.0
        assert v.z == 3.0

    def test_magnitude(self):
        v = Vector3(1, 2, 2)
        assert abs(v.magnitude - 3.0) < 1e-5

    def test_normalized(self):
        v = Vector3(0, 0, 5)
        assert v.normalized == Vector3(0, 0, 1)

    def test_dot(self):
        assert abs(Vector3.dot(Vector3(1, 0, 0), Vector3(0, 1, 0))) < 1e-5

    def test_cross(self):
        result = Vector3.cross(Vector3(1, 0, 0), Vector3(0, 1, 0))
        assert result == Vector3(0, 0, 1)

    def test_distance(self):
        assert abs(Vector3.distance(Vector3.zero, Vector3(1, 2, 2)) - 3.0) < 1e-5

    def test_lerp(self):
        result = Vector3.lerp(Vector3.zero, Vector3(10, 10, 10), 0.5)
        assert result == Vector3(5, 5, 5)

    def test_angle(self):
        assert abs(Vector3.angle(Vector3(1, 0, 0), Vector3(0, 1, 0)) - 90.0) < 0.01

    def test_project(self):
        result = Vector3.project(Vector3(1, 1, 0), Vector3(1, 0, 0))
        assert result == Vector3(1, 0, 0)

    def test_reflect(self):
        result = Vector3.reflect(Vector3(1, -1, 0), Vector3(0, 1, 0))
        assert result == Vector3(1, 1, 0)

    def test_add(self):
        assert Vector3(1, 2, 3) + Vector3(4, 5, 6) == Vector3(5, 7, 9)

    def test_sub(self):
        assert Vector3(5, 7, 9) - Vector3(1, 2, 3) == Vector3(4, 5, 6)

    def test_mul(self):
        assert Vector3(1, 2, 3) * 3 == Vector3(3, 6, 9)

    def test_neg(self):
        assert -Vector3(1, -2, 3) == Vector3(-1, 2, -3)

    def test_static_constructors(self):
        assert Vector3.zero == Vector3(0, 0, 0)
        assert Vector3.one == Vector3(1, 1, 1)
        assert Vector3.up == Vector3(0, 1, 0)
        assert Vector3.forward == Vector3(0, 0, 1)
        assert Vector3.right == Vector3(1, 0, 0)
        assert Vector3.back == Vector3(0, 0, -1)

    def test_normalize_in_place(self):
        v = Vector3(0, 0, 5)
        v.normalize()
        assert v == Vector3(0, 0, 1)

    def test_setters(self):
        v = Vector3(1, 2, 3)
        v.x = 10
        assert v.x == 10.0
        assert v == Vector3(10, 2, 3)


# ── Quaternion ───────────────────────────────────────────────


class TestQuaternion:
    def test_identity(self):
        q = Quaternion.identity
        assert q.w == 1.0
        assert q.x == 0.0

    def test_euler_roundtrip(self):
        q = Quaternion.euler(30, 45, 60)
        euler = q.euler_angles
        # Roundtrip through euler should preserve angles approximately
        q2 = Quaternion.euler(euler.x, euler.y, euler.z)
        assert abs(Quaternion.angle(q, q2)) < 1.0

    def test_angle_axis(self):
        q = Quaternion.angle_axis(90, Vector3(0, 1, 0))
        rotated = q.rotate_vector(Vector3(1, 0, 0))
        assert abs(rotated.x) < 0.01
        assert abs(rotated.z - 1.0) < 0.01 or abs(rotated.z + 1.0) < 0.01

    def test_multiply_identity(self):
        q = Quaternion.euler(30, 45, 60)
        result = q * Quaternion.identity
        assert abs(Quaternion.angle(q, result)) < 0.01

    def test_slerp_endpoints(self):
        a = Quaternion.identity
        b = Quaternion.euler(0, 90, 0)
        assert Quaternion.slerp(a, b, 0.0) == a
        assert abs(Quaternion.angle(Quaternion.slerp(a, b, 1.0), b)) < 0.01

    def test_rotate_vector(self):
        q = Quaternion.euler(0, 0, 90)
        result = q.rotate_vector(Vector3(1, 0, 0))
        assert abs(result.x) < 0.01
        assert abs(result.y - 1.0) < 0.01


# ── Mathf ────────────────────────────────────────────────────


class TestMathf:
    def test_clamp(self):
        assert Mathf.clamp(5, 0, 10) == 5
        assert Mathf.clamp(-1, 0, 10) == 0
        assert Mathf.clamp(15, 0, 10) == 10

    def test_clamp01(self):
        assert Mathf.clamp01(0.5) == 0.5
        assert Mathf.clamp01(-1) == 0.0
        assert Mathf.clamp01(2) == 1.0

    def test_lerp(self):
        assert Mathf.lerp(0, 10, 0.5) == 5.0

    def test_lerp_clamped(self):
        assert Mathf.lerp(0, 10, 2.0) == 10.0

    def test_inverse_lerp(self):
        assert abs(Mathf.inverse_lerp(0, 10, 5) - 0.5) < 1e-5

    def test_move_towards(self):
        assert Mathf.move_towards(0, 10, 3) == 3.0
        assert Mathf.move_towards(0, 10, 20) == 10.0

    def test_approximately(self):
        assert Mathf.approximately(1.0, 1.0 + 1e-7)
        assert not Mathf.approximately(1.0, 2.0)

    def test_smooth_step(self):
        assert Mathf.smooth_step(0, 1, 0.0) == 0.0
        assert Mathf.smooth_step(0, 1, 1.0) == 1.0

    def test_repeat(self):
        assert abs(Mathf.repeat(5.5, 3.0) - 2.5) < 1e-5

    def test_ping_pong(self):
        assert abs(Mathf.ping_pong(2.5, 3.0) - 2.5) < 1e-5
        assert abs(Mathf.ping_pong(4.0, 3.0) - 2.0) < 1e-5

    def test_sign(self):
        assert Mathf.sign(5) == 1.0
        assert Mathf.sign(-3) == -1.0
        assert Mathf.sign(0) == 0.0

    def test_deg2rad_rad2deg(self):
        assert abs(90 * Mathf.DEG2RAD - math.pi / 2) < 1e-5
        assert abs(math.pi * Mathf.RAD2DEG - 180.0) < 1e-5
