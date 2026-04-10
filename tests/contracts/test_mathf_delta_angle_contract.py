"""Contract tests for Mathf.delta_angle — matches UnityEngine.Mathf.DeltaAngle.

These tests are derived from the acceptance criteria spec for
demo-blind-tdd-delta-angle. They are blind tests: written without reading
the implementation. In the red phase, Mathf.delta_angle does not yet exist
and these tests are expected to fail with AttributeError.
"""

import math

import pytest

from src.engine.math.mathf import Mathf


def test_delta_angle_simple_forward():
    """Covers: AC-1 — current=0, target=90 returns 90.0."""
    result = Mathf.delta_angle(0.0, 90.0)
    assert result == pytest.approx(90.0, abs=1e-4)


def test_delta_angle_180_boundary_is_positive():
    """Covers: AC-2 — current=0, target=180 returns exactly 180.0 (not -180.0).

    Unity's DeltaAngle returns the positive boundary value at exactly 180
    degrees of separation. This test asserts the exact sign, not just
    magnitude.
    """
    result = Mathf.delta_angle(0.0, 180.0)
    # Must be exactly 180.0, not -180.0. Use approx for float safety but
    # explicitly reject the negative boundary.
    assert result == pytest.approx(180.0, abs=1e-4)
    assert result > 0, f"Expected +180.0, got {result} (wrong sign at boundary)"


def test_delta_angle_forward_wrap_around_zero():
    """Covers: AC-3 — current=350, target=10 returns 20.0 (not -340.0)."""
    result = Mathf.delta_angle(350.0, 10.0)
    assert result == pytest.approx(20.0, abs=1e-4)
    # Guard against the naive (target - current) implementation.
    assert not math.isclose(result, -340.0, abs_tol=1e-4)


def test_delta_angle_backward_wrap_around_zero():
    """Covers: AC-4 — current=10, target=350 returns -20.0 (not 340.0)."""
    result = Mathf.delta_angle(10.0, 350.0)
    assert result == pytest.approx(-20.0, abs=1e-4)
    assert not math.isclose(result, 340.0, abs_tol=1e-4)


def test_delta_angle_identical_inputs_zero():
    """Covers: AC-5 — current=5, target=5 returns 0.0."""
    result = Mathf.delta_angle(5.0, 5.0)
    assert result == pytest.approx(0.0, abs=1e-4)


def test_delta_angle_normalizes_large_inputs():
    """Covers: AC-6 — current=1080 (three full rotations), target=90 returns 90.0.

    Inputs outside [0, 360) must be normalized before computing the
    shortest signed difference.
    """
    result = Mathf.delta_angle(1080.0, 90.0)
    assert result == pytest.approx(90.0, abs=1e-4)
