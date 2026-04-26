"""Integration tests for auto-build colliders (Task 2).

Validates that colliders auto-build their physics shapes during the lifecycle
awake phase, matching Unity's behavior where colliders become active after
AddComponent + property configuration without explicit build() calls.
"""

import pytest

from src.engine.core import GameObject, MonoBehaviour, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.math.vector import Vector2
from src.engine.physics.collider import (
    BoxCollider2D,
    CircleCollider2D,
)
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D


@pytest.fixture(autouse=True)
def clean_state():
    """Reset all singletons before each test."""
    LifecycleManager.reset()
    PhysicsManager.reset()
    _clear_registry()
    yield
    LifecycleManager.reset()
    PhysicsManager.reset()
    _clear_registry()


def _run_awake_start():
    """Process awake and start queues, simulating first frame setup."""
    lm = LifecycleManager.instance()
    lm.process_awake_queue()
    lm.process_start_queue()


class TestBoxColliderAutoBuildsOnAwake:
    """BoxCollider2D should have a physics shape after awake without explicit build()."""

    def test_box_collider_has_shape_after_awake(self):
        go = GameObject("Box")
        go.transform.position = Vector2(0, 0)
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(2, 3)

        # Before lifecycle runs, shape should be None
        assert col._shape is None

        _run_awake_start()

        # After awake, shape should be built
        assert col._shape is not None

    def test_box_collider_registered_in_physics_space(self):
        go = GameObject("Box")
        go.transform.position = Vector2(0, 0)
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(2, 2)

        _run_awake_start()

        pm = PhysicsManager.instance()
        assert col._shape in pm._space.shapes


class TestCircleColliderAutoBuildsOnAwake:
    """CircleCollider2D should have a physics shape after awake without explicit build()."""

    def test_circle_collider_has_shape_after_awake(self):
        go = GameObject("Circle")
        go.transform.position = Vector2(0, 0)
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(CircleCollider2D)
        col.radius = 1.5

        assert col._shape is None

        _run_awake_start()

        assert col._shape is not None

    def test_circle_collider_registered_in_physics_space(self):
        go = GameObject("Circle")
        go.transform.position = Vector2(5, 5)
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(CircleCollider2D)
        col.radius = 2.0

        _run_awake_start()

        pm = PhysicsManager.instance()
        assert col._shape in pm._space.shapes


class TestCollisionWithoutExplicitBuild:
    """Two objects with auto-built colliders should detect collisions."""

    def test_collision_detected_without_manual_build(self):
        """Place two dynamic objects at same position; physics step should produce collision."""
        collision_detected = []

        class Detector(MonoBehaviour):
            def on_collision_enter_2d(self, collision):
                collision_detected.append(collision.game_object.name)

        # Object A
        go_a = GameObject("A")
        go_a.transform.position = Vector2(0, 0)
        rb_a = go_a.add_component(Rigidbody2D)
        rb_a.velocity = Vector2(0, 0)
        col_a = go_a.add_component(BoxCollider2D)
        col_a.size = Vector2(2, 2)
        go_a.add_component(Detector)

        # Object B overlapping A
        go_b = GameObject("B")
        go_b.transform.position = Vector2(0.5, 0)
        rb_b = go_b.add_component(Rigidbody2D)
        rb_b.velocity = Vector2(0, 0)
        col_b = go_b.add_component(BoxCollider2D)
        col_b.size = Vector2(2, 2)

        _run_awake_start()

        # Step physics to detect overlap
        pm = PhysicsManager.instance()
        pm.step(1 / 60.0)

        assert len(collision_detected) > 0, "Collision should be detected without explicit build()"


class TestRuntimeColliderAutoBuilds:
    """Colliders added at runtime (after initial awake) should auto-build on next awake cycle."""

    def test_runtime_added_collider_builds_on_next_awake_cycle(self):
        # Initial awake/start with no colliders
        _run_awake_start()

        # Now add a game object with collider at "runtime"
        go = GameObject("Runtime")
        go.transform.position = Vector2(10, 10)
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(1, 1)

        # add_component registers with LifecycleManager, process the queue
        _run_awake_start()

        assert col._shape is not None
        pm = PhysicsManager.instance()
        assert col._shape in pm._space.shapes


class TestMultipleCollidersOnSameObject:
    """Multiple colliders on one GameObject should all auto-build."""

    def test_both_colliders_build(self):
        go = GameObject("Multi")
        go.transform.position = Vector2(0, 0)
        rb = go.add_component(Rigidbody2D)
        box = go.add_component(BoxCollider2D)
        box.size = Vector2(2, 2)
        circle = go.add_component(CircleCollider2D)
        circle.radius = 1.0

        _run_awake_start()

        assert box._shape is not None
        assert circle._shape is not None
        # Both shapes in rb._shapes
        assert box._shape in rb._shapes
        assert circle._shape in rb._shapes
