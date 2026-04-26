"""Mutation tests for auto-build colliders.

Prove that the auto-build and cleanup mechanisms are load-bearing by
monkeypatching them to be no-ops and verifying that tests detect the breakage.
"""

import pytest

from src.engine.core import GameObject, MonoBehaviour, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.math.vector import Vector2
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D, Collider2D
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D


@pytest.fixture(autouse=True)
def clean_state():
    LifecycleManager.reset()
    PhysicsManager.reset()
    _clear_registry()
    yield
    LifecycleManager.reset()
    PhysicsManager.reset()
    _clear_registry()


def _run_awake_start():
    lm = LifecycleManager.instance()
    lm.process_awake_queue()
    lm.process_start_queue()


class TestMutationAwakeNoBuild:
    """Monkeypatch Collider2D.awake to NOT call build() -- prove physics breaks."""

    def test_no_shape_without_auto_build(self, monkeypatch):
        """If awake doesn't call build, shape stays None."""
        monkeypatch.setattr(Collider2D, "awake", lambda self: None)

        go = GameObject("Box")
        go.transform.position = Vector2(0, 0)
        go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(2, 2)

        _run_awake_start()

        assert col._shape is None, "With awake mutated to no-op, shape must remain None"

    def test_no_collision_without_auto_build(self, monkeypatch):
        """If awake doesn't build, collisions cannot happen."""
        monkeypatch.setattr(Collider2D, "awake", lambda self: None)

        collision_detected = []

        class Detector(MonoBehaviour):
            def on_collision_enter_2d(self, collision):
                collision_detected.append(True)

        go_a = GameObject("A")
        go_a.transform.position = Vector2(0, 0)
        rb_a = go_a.add_component(Rigidbody2D)
        col_a = go_a.add_component(BoxCollider2D)
        col_a.size = Vector2(2, 2)
        go_a.add_component(Detector)

        go_b = GameObject("B")
        go_b.transform.position = Vector2(0.5, 0)
        rb_b = go_b.add_component(Rigidbody2D)
        col_b = go_b.add_component(BoxCollider2D)
        col_b.size = Vector2(2, 2)

        _run_awake_start()

        pm = PhysicsManager.instance()
        pm.step(1 / 60.0)

        assert len(collision_detected) == 0, \
            "Without auto-build, no shapes exist so no collisions should fire"

    def test_circle_no_shape_without_auto_build(self, monkeypatch):
        """Circle collider also must not build if awake is broken."""
        monkeypatch.setattr(Collider2D, "awake", lambda self: None)

        go = GameObject("Circle")
        go.transform.position = Vector2(0, 0)
        go.add_component(Rigidbody2D)
        col = go.add_component(CircleCollider2D)
        col.radius = 1.0

        _run_awake_start()

        assert col._shape is None


class TestMutationCleanupNoOp:
    """Monkeypatch _cleanup_old_shape to be a no-op -- prove double-build creates duplicates."""

    def test_duplicate_shapes_without_cleanup(self, monkeypatch):
        """If cleanup is a no-op, calling build() twice adds duplicate shapes to rigidbody."""
        monkeypatch.setattr(Collider2D, "_cleanup_old_shape", lambda self: None)

        go = GameObject("Box")
        go.transform.position = Vector2(0, 0)
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(2, 2)

        _run_awake_start()

        first_shape = col._shape
        assert first_shape is not None

        # Build again -- cleanup is a no-op so old shape stays
        col.build()

        second_shape = col._shape
        assert second_shape is not None
        assert first_shape is not second_shape, "Build should create a new shape object"

        # Without cleanup, BOTH shapes should be in rb._shapes
        assert first_shape in rb._shapes, "Old shape should remain (cleanup was disabled)"
        assert second_shape in rb._shapes, "New shape should also be present"
        assert len([s for s in rb._shapes if s is first_shape or s is second_shape]) == 2, \
            "Should have exactly 2 shapes (duplicate) when cleanup is disabled"

    def test_old_shape_stays_in_space_without_cleanup(self, monkeypatch):
        """Without cleanup, old shape remains in the physics space after rebuild."""
        monkeypatch.setattr(Collider2D, "_cleanup_old_shape", lambda self: None)

        go = GameObject("Box")
        go.transform.position = Vector2(0, 0)
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(2, 2)

        _run_awake_start()

        first_shape = col._shape
        pm = PhysicsManager.instance()
        assert first_shape in pm._space.shapes

        col.build()

        # Both old and new should be in space (cleanup disabled)
        assert first_shape in pm._space.shapes, \
            "Old shape must remain in space when cleanup is disabled"
        assert col._shape in pm._space.shapes, \
            "New shape should also be in space"


class TestMutationBuildReturnsEarly:
    """Prove that if build() in BoxCollider2D is replaced with a no-op, awake achieves nothing."""

    def test_awake_with_broken_build(self, monkeypatch):
        """awake calls build(), but if build() does nothing, shape stays None."""
        monkeypatch.setattr(BoxCollider2D, "build", lambda self: None)

        go = GameObject("Box")
        go.transform.position = Vector2(0, 0)
        go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(2, 2)

        _run_awake_start()

        assert col._shape is None, "If build() is a no-op, awake should leave shape as None"
