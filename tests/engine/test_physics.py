"""Tests for physics layer — Rigidbody2D, colliders, PhysicsManager."""

import pytest

from src.engine.core import GameObject, MonoBehaviour, _clear_registry
from src.engine.math.vector import Vector2
from src.engine.physics.physics_manager import PhysicsManager, Collision2D
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D, ForceMode2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D


@pytest.fixture(autouse=True)
def reset_physics():
    yield
    PhysicsManager.reset()
    _clear_registry()


class TestRigidbody2D:
    def test_default_mass(self):
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        assert rb.mass == 1.0

    def test_set_velocity(self):
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        rb.velocity = Vector2(5, 10)
        assert abs(rb.velocity.x - 5.0) < 0.01
        assert abs(rb.velocity.y - 10.0) < 0.01

    def test_body_type_default(self):
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        assert rb.body_type == RigidbodyType2D.DYNAMIC

    def test_set_body_type_kinematic(self):
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.KINEMATIC
        assert rb.body_type == RigidbodyType2D.KINEMATIC

    def test_set_body_type_static(self):
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.STATIC
        assert rb.body_type == RigidbodyType2D.STATIC

    def test_gravity_scale_default(self):
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        assert rb.gravity_scale == 1.0

    def test_add_force_impulse(self):
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        rb.add_force(Vector2(100, 0), ForceMode2D.IMPULSE)
        assert rb.velocity.x > 0

    def test_move_position(self):
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.KINEMATIC
        rb.move_position(Vector2(5, 10))
        # Body position should update
        assert abs(rb._body.position[0] - 5.0) < 0.01

    def test_angular_velocity(self):
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        rb.angular_velocity = 3.14
        assert abs(rb.angular_velocity - 3.14) < 0.01


class TestPhysicsManager:
    def test_singleton(self):
        pm1 = PhysicsManager.instance()
        pm2 = PhysicsManager.instance()
        assert pm1 is pm2

    def test_default_gravity(self):
        pm = PhysicsManager.instance()
        assert abs(pm.gravity.y - (-9.81)) < 0.01

    def test_set_gravity(self):
        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, -20)
        assert abs(pm.gravity.y - (-20)) < 0.01

    def test_register_and_step(self):
        pm = PhysicsManager.instance()
        go = GameObject("Ball")
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(CircleCollider2D)
        col.radius = 0.5
        col.build()
        initial_y = rb._body.position[1]
        # Step physics — body should fall due to gravity
        for _ in range(10):
            pm.step(0.02)
        assert rb._body.position[1] < initial_y

    def test_sync_to_transform(self):
        pm = PhysicsManager.instance()
        go = GameObject("Ball")
        go.transform.position = Vector2(0, 10)  # type: ignore
        rb = go.add_component(Rigidbody2D)
        rb._sync_from_transform()
        col = go.add_component(CircleCollider2D)
        col.radius = 0.5
        col.build()
        for _ in range(10):
            pm.step(0.02)
        # Transform should have been updated
        assert go.transform.position.y < 10.0  # type: ignore


class TestColliders:
    def test_box_collider_default_size(self):
        go = GameObject("Test")
        col = go.add_component(BoxCollider2D)
        assert col.size == Vector2(1, 1)

    def test_box_collider_set_size(self):
        go = GameObject("Test")
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(2, 3)
        assert col.size == Vector2(2, 3)

    def test_circle_collider_default_radius(self):
        go = GameObject("Test")
        col = go.add_component(CircleCollider2D)
        assert col.radius == 0.5

    def test_circle_collider_set_radius(self):
        go = GameObject("Test")
        col = go.add_component(CircleCollider2D)
        col.radius = 2.0
        assert col.radius == 2.0

    def test_is_trigger_default(self):
        go = GameObject("Test")
        col = go.add_component(BoxCollider2D)
        assert col.is_trigger is False

    def test_box_collider_build(self):
        pm = PhysicsManager.instance()
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(2, 2)
        col.build()
        assert len(rb._shapes) == 1

    def test_circle_collider_build(self):
        pm = PhysicsManager.instance()
        go = GameObject("Test")
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(CircleCollider2D)
        col.radius = 1.0
        col.build()
        assert len(rb._shapes) == 1


class TestCollisionCallbacks:
    def test_collision_enter_dispatched(self):
        collisions = []

        class Detector(MonoBehaviour):
            def on_collision_enter_2d(self, collision):
                collisions.append(collision)

        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        # Create two objects moving toward each other
        go_a = GameObject("A")
        rb_a = go_a.add_component(Rigidbody2D)
        col_a = go_a.add_component(CircleCollider2D)
        col_a.radius = 1.0
        go_a.add_component(Detector)
        rb_a._body.position = (-5, 0)
        rb_a.velocity = Vector2(10, 0)
        col_a.build()

        go_b = GameObject("B")
        rb_b = go_b.add_component(Rigidbody2D)
        col_b = go_b.add_component(CircleCollider2D)
        col_b.radius = 1.0
        go_b.add_component(Detector)
        rb_b._body.position = (5, 0)
        rb_b.velocity = Vector2(-10, 0)
        col_b.build()

        # Step until collision occurs
        for _ in range(100):
            pm.step(0.02)
            if collisions:
                break

        assert len(collisions) >= 2  # Both A and B should get callbacks

    def test_trigger_enter_dispatched(self):
        triggers = []

        class TriggerDetector(MonoBehaviour):
            def on_trigger_enter_2d(self, other):
                triggers.append(other)

        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        go_a = GameObject("A")
        rb_a = go_a.add_component(Rigidbody2D)
        col_a = go_a.add_component(CircleCollider2D)
        col_a.radius = 1.0
        col_a.is_trigger = True
        go_a.add_component(TriggerDetector)
        rb_a._body.position = (-3, 0)
        rb_a.velocity = Vector2(10, 0)
        col_a.build()

        go_b = GameObject("B")
        rb_b = go_b.add_component(Rigidbody2D)
        col_b = go_b.add_component(CircleCollider2D)
        col_b.radius = 1.0
        go_b.add_component(TriggerDetector)
        rb_b._body.position = (3, 0)
        rb_b.velocity = Vector2(-10, 0)
        col_b.build()

        for _ in range(100):
            pm.step(0.02)
            if triggers:
                break

        assert len(triggers) >= 2
