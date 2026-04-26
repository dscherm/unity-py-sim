"""Contract tests for collider auto-build behavior.

These tests verify Unity behavioral contracts:
- In Unity, colliders are active after AddComponent + property configuration
  without any explicit initialization call.
- Collider shape matches the configured size/radius.
- PhysicsMaterial2D is applied to auto-built colliders.
- is_trigger flag is respected on auto-built colliders.
- Rebuilding a collider (calling build() again) replaces the old shape cleanly.
"""

import pytest
import pymunk

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.math.vector import Vector2
from src.engine.physics.collider import (
    BoxCollider2D,
    CircleCollider2D,
    PhysicsMaterial2D,
)
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


class TestUnityContractColliderActiveAfterAddComponent:
    """Unity contract: Collider is active after AddComponent + property set, no explicit build."""

    def test_box_collider_active_after_awake(self):
        go = GameObject("Box")
        go.transform.position = Vector2(0, 0)
        go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(3, 4)

        _run_awake_start()

        assert col._shape is not None, "BoxCollider2D must be active after awake"

    def test_circle_collider_active_after_awake(self):
        go = GameObject("Circle")
        go.transform.position = Vector2(0, 0)
        go.add_component(Rigidbody2D)
        col = go.add_component(CircleCollider2D)
        col.radius = 2.5

        _run_awake_start()

        assert col._shape is not None, "CircleCollider2D must be active after awake"

    def test_collider_without_rigidbody_uses_static_body(self):
        """Unity: collider without Rigidbody2D acts as static collider."""
        go = GameObject("Static")
        go.transform.position = Vector2(5, 5)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(1, 1)

        _run_awake_start()

        assert col._shape is not None, "Collider without Rigidbody2D must still build"
        assert col._shape.body.body_type == pymunk.Body.STATIC


class TestUnityContractColliderShapeMatchesConfiguration:
    """Unity contract: physics shape dimensions match configured size/radius."""

    def test_box_collider_shape_matches_size(self):
        go = GameObject("Box")
        go.transform.position = Vector2(0, 0)
        go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(4, 6)

        _run_awake_start()

        # The pymunk Poly shape should have vertices spanning the configured size
        shape = col._shape
        assert isinstance(shape, pymunk.Poly)
        verts = shape.get_vertices()
        xs = [v[0] for v in verts]
        ys = [v[1] for v in verts]
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        assert abs(width - 4.0) < 0.01, f"Box width should be 4, got {width}"
        assert abs(height - 6.0) < 0.01, f"Box height should be 6, got {height}"

    def test_circle_collider_shape_matches_radius(self):
        go = GameObject("Circle")
        go.transform.position = Vector2(0, 0)
        go.add_component(Rigidbody2D)
        col = go.add_component(CircleCollider2D)
        col.radius = 3.0

        _run_awake_start()

        shape = col._shape
        assert isinstance(shape, pymunk.Circle)
        assert abs(shape.radius - 3.0) < 0.01, f"Circle radius should be 3.0, got {shape.radius}"


class TestUnityContractPhysicsMaterialApplied:
    """Unity contract: PhysicsMaterial2D bounciness/friction are applied to the shape."""

    def test_material_applied_to_auto_built_collider(self):
        go = GameObject("Bouncy")
        go.transform.position = Vector2(0, 0)
        go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(1, 1)
        mat = PhysicsMaterial2D(bounciness=0.8, friction=0.2)
        col.shared_material = mat

        _run_awake_start()

        assert col._shape is not None
        assert abs(col._shape.elasticity - 0.8) < 0.01, "Bounciness should be 0.8"
        assert abs(col._shape.friction - 0.2) < 0.01, "Friction should be 0.2"

    def test_default_material_applied_when_none_set(self):
        """Unity defaults: bounciness=0, friction=0.4."""
        go = GameObject("Default")
        go.transform.position = Vector2(0, 0)
        go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(1, 1)

        _run_awake_start()

        assert col._shape is not None
        assert abs(col._shape.elasticity - 0.0) < 0.01, "Default bounciness should be 0"
        assert abs(col._shape.friction - 0.4) < 0.01, "Default friction should be 0.4"

    def test_instance_material_overrides_shared_material(self):
        go = GameObject("Override")
        go.transform.position = Vector2(0, 0)
        go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(1, 1)
        col.shared_material = PhysicsMaterial2D(bounciness=0.5, friction=0.5)
        col.material = PhysicsMaterial2D(bounciness=1.0, friction=0.1)

        _run_awake_start()

        # Instance material should win
        assert abs(col._shape.elasticity - 1.0) < 0.01
        assert abs(col._shape.friction - 0.1) < 0.01


class TestUnityContractIsTriggerRespected:
    """Unity contract: is_trigger flag makes the collider a trigger (sensor)."""

    def test_trigger_flag_on_auto_built_collider(self):
        go = GameObject("Trigger")
        go.transform.position = Vector2(0, 0)
        go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(1, 1)
        col.is_trigger = True

        _run_awake_start()

        assert col._shape is not None
        # After build, is_trigger should mark the shape as sensor
        # The is_trigger setter checks _shape, but it was None at set time.
        # awake() builds the shape. Check if the trigger flag is applied.
        pm = PhysicsManager.instance()
        assert pm.is_trigger(col._shape) or col._shape.sensor, \
            "Trigger collider shape should be marked as sensor"

    def test_non_trigger_collider_is_not_sensor(self):
        go = GameObject("Solid")
        go.transform.position = Vector2(0, 0)
        go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(1, 1)
        col.is_trigger = False

        _run_awake_start()

        assert col._shape is not None
        assert not col._shape.sensor, "Non-trigger collider should not be a sensor"


class TestUnityContractRebuildSafety:
    """Unity contract: calling build() multiple times is safe and replaces the old shape."""

    def test_double_build_replaces_shape(self):
        go = GameObject("Rebuild")
        go.transform.position = Vector2(0, 0)
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(2, 2)

        _run_awake_start()

        old_shape = col._shape
        assert old_shape is not None

        # Manually rebuild
        col.size = Vector2(4, 4)
        col.build()

        new_shape = col._shape
        assert new_shape is not None
        assert new_shape is not old_shape, "Rebuild should create a new shape"

    def test_old_shape_removed_from_space_on_rebuild(self):
        go = GameObject("Rebuild")
        go.transform.position = Vector2(0, 0)
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(2, 2)

        _run_awake_start()

        old_shape = col._shape
        pm = PhysicsManager.instance()
        assert old_shape in pm._space.shapes

        col.build()

        assert old_shape not in pm._space.shapes, "Old shape should be removed from space"
        assert col._shape in pm._space.shapes, "New shape should be in space"

    def test_old_shape_removed_from_rigidbody_shapes_on_rebuild(self):
        go = GameObject("Rebuild")
        go.transform.position = Vector2(0, 0)
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(2, 2)

        _run_awake_start()

        old_shape = col._shape
        assert old_shape in rb._shapes

        col.build()

        assert old_shape not in rb._shapes, "Old shape should be removed from rb._shapes"
        assert col._shape in rb._shapes, "New shape should be in rb._shapes"
