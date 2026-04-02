"""Tests for physics layer — Rigidbody2D, colliders, PhysicsManager."""

import pytest

from src.engine.core import GameObject, MonoBehaviour, _clear_registry
from src.engine.math.vector import Vector2
from src.engine.physics.physics_manager import PhysicsManager, Collision2D, Physics2D, RaycastHit2D
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D, ForceMode2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D, PhysicsMaterial2D, Bounds


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


class TestPhysicsMaterial2D:
    def test_default_values(self):
        mat = PhysicsMaterial2D()
        assert mat.bounciness == 0.0
        assert mat.friction == 0.4

    def test_custom_values(self):
        mat = PhysicsMaterial2D(bounciness=1.0, friction=0.0)
        assert mat.bounciness == 1.0
        assert mat.friction == 0.0

    def test_setters(self):
        mat = PhysicsMaterial2D()
        mat.bounciness = 0.8
        mat.friction = 0.2
        assert mat.bounciness == 0.8
        assert mat.friction == 0.2

    def test_material_applied_on_build(self):
        pm = PhysicsManager.instance()
        go = GameObject("Ball")
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(CircleCollider2D)
        col.radius = 0.5
        mat = PhysicsMaterial2D(bounciness=1.0, friction=0.0)
        col.shared_material = mat
        col.build()
        # pymunk shape should reflect material
        assert col._shape.elasticity == 1.0
        assert col._shape.friction == 0.0

    def test_default_material_on_build(self):
        """Without material, Unity defaults apply: bounciness=0, friction=0.4."""
        pm = PhysicsManager.instance()
        go = GameObject("Box")
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(1, 1)
        col.build()
        assert col._shape.elasticity == 0.0
        assert col._shape.friction == 0.4

    def test_instance_material_overrides_shared(self):
        pm = PhysicsManager.instance()
        go = GameObject("Ball")
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(CircleCollider2D)
        col.radius = 0.5
        col.shared_material = PhysicsMaterial2D(bounciness=0.5, friction=0.5)
        col.material = PhysicsMaterial2D(bounciness=1.0, friction=0.0)
        col.build()
        assert col._shape.elasticity == 1.0
        assert col._shape.friction == 0.0

    def test_material_applied_after_build(self):
        """Setting material after build() should update the shape."""
        pm = PhysicsManager.instance()
        go = GameObject("Ball")
        rb = go.add_component(Rigidbody2D)
        col = go.add_component(CircleCollider2D)
        col.radius = 0.5
        col.build()
        assert col._shape.elasticity == 0.0  # default
        col.shared_material = PhysicsMaterial2D(bounciness=1.0, friction=0.0)
        assert col._shape.elasticity == 1.0
        assert col._shape.friction == 0.0

    def test_bouncy_ball_preserves_energy(self):
        """Ball with bounciness=1 should maintain speed after bouncing off a wall."""
        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)
        bouncy = PhysicsMaterial2D(bounciness=1.0, friction=0.0)

        # Wall (static)
        wall = GameObject("Wall")
        wall_rb = wall.add_component(Rigidbody2D)
        wall_rb.body_type = RigidbodyType2D.STATIC
        wall_col = wall.add_component(BoxCollider2D)
        wall_col.size = Vector2(1, 10)
        wall_col.shared_material = bouncy
        wall_rb._body.position = (10, 0)
        wall_col.build()

        # Ball
        ball = GameObject("Ball")
        ball_rb = ball.add_component(Rigidbody2D)
        ball_col = ball.add_component(CircleCollider2D)
        ball_col.radius = 0.5
        ball_col.shared_material = bouncy
        ball_rb._body.position = (0, 0)
        ball_rb.velocity = Vector2(10, 0)
        ball_col.build()

        initial_speed = abs(ball_rb.velocity.x)

        for _ in range(200):
            pm.step(0.02)

        # After bouncing, speed should be roughly preserved
        final_speed = ball_rb.velocity.magnitude
        assert final_speed > initial_speed * 0.8  # Allow small numerical loss


class TestColliderBounds:
    def test_circle_bounds(self):
        pm = PhysicsManager.instance()
        go = GameObject("Ball")
        rb = go.add_component(Rigidbody2D)
        rb._body.position = (5, 5)
        col = go.add_component(CircleCollider2D)
        col.radius = 1.0
        col.build()
        # Force a space step to compute BBs
        pm.step(0.0)
        b = col.bounds
        assert abs(b.center.x - 5.0) < 1.5
        assert abs(b.center.y - 5.0) < 1.5
        assert b.size.x > 0
        assert b.size.y > 0

    def test_box_bounds(self):
        pm = PhysicsManager.instance()
        go = GameObject("Box")
        rb = go.add_component(Rigidbody2D)
        rb._body.position = (0, 0)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(4, 2)
        col.build()
        pm.step(0.0)
        b = col.bounds
        assert b.size.x > 0
        assert b.size.y > 0

    def test_bounds_contains(self):
        b = Bounds(center=Vector2(0, 0), size=Vector2(4, 4))
        assert b.contains(Vector2(0, 0))
        assert b.contains(Vector2(1, 1))
        assert not b.contains(Vector2(3, 0))

    def test_bounds_no_shape(self):
        """Bounds without a built shape returns zero-size at transform position."""
        go = GameObject("NoShape")
        go.transform.position = Vector2(3, 4)
        col = go.add_component(BoxCollider2D)
        b = col.bounds
        assert abs(b.center.x - 3.0) < 0.01
        assert abs(b.center.y - 4.0) < 0.01
        assert b.size.x == 0
        assert b.size.y == 0


class TestPhysics2DRaycast:
    def test_raycast_hits_object(self):
        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        wall = GameObject("Wall")
        wall_rb = wall.add_component(Rigidbody2D)
        wall_rb.body_type = RigidbodyType2D.STATIC
        wall_rb._body.position = (10, 0)
        wall_col = wall.add_component(BoxCollider2D)
        wall_col.size = Vector2(2, 10)
        wall_col.build()
        pm.step(0.0)  # update BBs

        hit = Physics2D.raycast(Vector2(0, 0), Vector2(1, 0), 20.0)
        assert hit is not None
        assert hit.distance < 15
        assert hit.rigidbody is wall_rb

    def test_raycast_misses(self):
        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        wall = GameObject("Wall")
        wall_rb = wall.add_component(Rigidbody2D)
        wall_rb.body_type = RigidbodyType2D.STATIC
        wall_rb._body.position = (10, 0)
        wall_col = wall.add_component(BoxCollider2D)
        wall_col.size = Vector2(2, 2)
        wall_col.build()
        pm.step(0.0)

        # Cast in wrong direction
        hit = Physics2D.raycast(Vector2(0, 0), Vector2(-1, 0), 20.0)
        assert hit is None

    def test_raycast_all(self):
        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        for x in [5, 10, 15]:
            w = GameObject(f"Wall_{x}")
            w_rb = w.add_component(Rigidbody2D)
            w_rb.body_type = RigidbodyType2D.STATIC
            w_rb._body.position = (x, 0)
            w_col = w.add_component(BoxCollider2D)
            w_col.size = Vector2(1, 4)
            w_col.build()
        pm.step(0.0)

        hits = Physics2D.raycast_all(Vector2(0, 0), Vector2(1, 0), 20.0)
        assert len(hits) >= 2  # Should hit multiple walls


class TestPhysics2DOverlap:
    def test_overlap_circle_finds_object(self):
        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        ball = GameObject("Ball")
        ball_rb = ball.add_component(Rigidbody2D)
        ball_rb._body.position = (5, 0)
        ball_col = ball.add_component(CircleCollider2D)
        ball_col.radius = 1.0
        ball_col.build()
        pm.step(0.0)

        result = Physics2D.overlap_circle(Vector2(5, 0), 2.0)
        assert result is not None

    def test_overlap_circle_misses(self):
        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        ball = GameObject("Ball")
        ball_rb = ball.add_component(Rigidbody2D)
        ball_rb._body.position = (100, 100)
        ball_col = ball.add_component(CircleCollider2D)
        ball_col.radius = 1.0
        ball_col.build()
        pm.step(0.0)

        result = Physics2D.overlap_circle(Vector2(0, 0), 1.0)
        assert result is None

    def test_overlap_box_finds_object(self):
        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        box = GameObject("Box")
        box_rb = box.add_component(Rigidbody2D)
        box_rb._body.position = (5, 0)
        box_col = box.add_component(BoxCollider2D)
        box_col.size = Vector2(2, 2)
        box_col.build()
        pm.step(0.0)

        result = Physics2D.overlap_box(Vector2(5, 0), Vector2(4, 4))
        assert result is not None

    def test_overlap_circle_all(self):
        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        for i in range(3):
            b = GameObject(f"Ball_{i}")
            b_rb = b.add_component(Rigidbody2D)
            b_rb._body.position = (i, 0)
            b_col = b.add_component(CircleCollider2D)
            b_col.radius = 0.5
            b_col.build()
        pm.step(0.0)

        results = Physics2D.overlap_circle_all(Vector2(1, 0), 5.0)
        assert len(results) >= 2


class TestStayCallbacks:
    def test_collision_stay_fires_each_step(self):
        stay_count = [0]

        class StayDetector(MonoBehaviour):
            def on_collision_stay_2d(self, collision):
                stay_count[0] += 1

        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        # Two objects pressed together
        go_a = GameObject("A")
        rb_a = go_a.add_component(Rigidbody2D)
        col_a = go_a.add_component(CircleCollider2D)
        col_a.radius = 1.0
        go_a.add_component(StayDetector)
        rb_a._body.position = (-3, 0)
        rb_a.velocity = Vector2(10, 0)
        col_a.build()

        go_b = GameObject("B")
        rb_b = go_b.add_component(Rigidbody2D)
        rb_b.body_type = RigidbodyType2D.STATIC
        rb_b._body.position = (0, 0)
        col_b = go_b.add_component(CircleCollider2D)
        col_b.radius = 1.0
        col_b.build()

        # Step many times — Stay should fire on multiple steps
        for _ in range(50):
            pm.step(0.02)

        assert stay_count[0] >= 2, f"Expected multiple Stay calls, got {stay_count[0]}"

    def test_trigger_stay_fires_each_step(self):
        stay_count = [0]

        class TriggerStayDetector(MonoBehaviour):
            def on_trigger_stay_2d(self, other):
                stay_count[0] += 1

        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        go_a = GameObject("A")
        rb_a = go_a.add_component(Rigidbody2D)
        col_a = go_a.add_component(CircleCollider2D)
        col_a.radius = 2.0
        col_a.is_trigger = True
        go_a.add_component(TriggerStayDetector)
        rb_a._body.position = (0, 0)
        col_a.build()

        go_b = GameObject("B")
        rb_b = go_b.add_component(Rigidbody2D)
        rb_b._body.position = (1, 0)  # overlapping
        col_b = go_b.add_component(CircleCollider2D)
        col_b.radius = 2.0
        col_b.build()

        for _ in range(30):
            pm.step(0.02)

        assert stay_count[0] >= 2, f"Expected multiple trigger Stay calls, got {stay_count[0]}"
