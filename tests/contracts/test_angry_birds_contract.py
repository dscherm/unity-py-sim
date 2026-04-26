"""Contract tests verifying Unity behavioral contracts in the Angry Birds feature set.

These tests derive expectations from Unity's documented behavior, not from
what the code happens to do.
"""

import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import (
    CircleCollider2D,
    PhysicsMaterial2D,
)
from src.engine.rendering.camera import Camera
from src.engine.rendering.display import DisplayManager
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.time_manager import Time
from src.engine.debug import Debug
from src.engine.trajectory import predict_trajectory

from examples.angry_birds.angry_birds_python.bird import Bird
from examples.angry_birds.angry_birds_python.slingshot import Slingshot
from examples.angry_birds.angry_birds_python.constants import Constants
from examples.angry_birds.angry_birds_python.enums import BirdState


@pytest.fixture(autouse=True)
def _reset_all():
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    DisplayManager.reset()
    Camera.main = None
    Input._reset()
    Time._reset()
    Debug._reset()
    yield
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    DisplayManager.reset()
    Camera.main = None
    Input._reset()
    Time._reset()
    Debug._reset()


# ---------------------------------------------------------------------------
# Input.GetMouseButtonUp — Unity contract: true ONLY on the release frame
# ---------------------------------------------------------------------------
class TestMouseButtonUpContract:
    """Unity's Input.GetMouseButtonUp returns true only on the single frame
    where the button transitions from pressed to released."""

    def test_false_when_never_pressed(self):
        """Should be False if the button was never pressed."""
        Input._begin_frame()
        assert Input.get_mouse_button_up(0) is False

    def test_false_while_held(self):
        """Should be False while the button is held down."""
        Input._set_mouse_button(0, True)
        Input._begin_frame()
        Input._set_mouse_button(0, True)
        assert Input.get_mouse_button_up(0) is False

    def test_true_on_release_frame(self):
        """Should be True on the exact frame the button is released."""
        # Frame 1: press
        Input._set_mouse_button(0, True)
        Input._begin_frame()
        # Frame 2: release
        Input._set_mouse_button(0, False)
        assert Input.get_mouse_button_up(0) is True

    def test_false_on_frame_after_release(self):
        """Should return False on the frame after release."""
        Input._set_mouse_button(0, True)
        Input._begin_frame()
        Input._set_mouse_button(0, False)
        # Now begin next frame
        Input._begin_frame()
        assert Input.get_mouse_button_up(0) is False

    def test_works_for_right_button(self):
        """Same contract must hold for button 1 (right click)."""
        Input._set_mouse_button(1, True)
        Input._begin_frame()
        Input._set_mouse_button(1, False)
        assert Input.get_mouse_button_up(1) is True

    def test_works_for_middle_button(self):
        """Same contract must hold for button 2 (middle click)."""
        Input._set_mouse_button(2, True)
        Input._begin_frame()
        Input._set_mouse_button(2, False)
        assert Input.get_mouse_button_up(2) is True


# ---------------------------------------------------------------------------
# Bird starts kinematic — Unity contract: isKinematic means no gravity
# ---------------------------------------------------------------------------
class TestBirdStartsKinematicContract:
    """In Unity, setting Rigidbody2D.bodyType = Kinematic means the physics
    engine does not apply gravity or other forces to the body."""

    def test_bird_body_type_is_kinematic_after_start(self):
        bird_go = GameObject("Bird")
        rb = bird_go.add_component(Rigidbody2D)
        bird_go.add_component(CircleCollider2D)
        bird_comp = bird_go.add_component(Bird)

        lm = LifecycleManager.instance()
        lm.register_component(bird_comp)
        lm.process_awake_queue()
        lm.process_start_queue()

        assert rb.body_type == RigidbodyType2D.KINEMATIC

    def test_kinematic_bird_velocity_stays_zero(self):
        """A kinematic body should not gain velocity from gravity."""
        bird_go = GameObject("Bird")
        rb = bird_go.add_component(Rigidbody2D)
        col = bird_go.add_component(CircleCollider2D)
        col.radius = 0.3
        col.build()
        bird_comp = bird_go.add_component(Bird)

        lm = LifecycleManager.instance()
        lm.register_component(bird_comp)
        lm.process_awake_queue()
        lm.process_start_queue()

        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, -9.81)
        for _ in range(60):
            pm.step(1.0 / 60.0)

        # Kinematic bodies should not accelerate under gravity
        assert abs(rb.velocity.y) < 0.01, (
            f"Kinematic body gained velocity {rb.velocity.y}; should remain ~0"
        )


# ---------------------------------------------------------------------------
# Bird.on_throw switches to Dynamic
# ---------------------------------------------------------------------------
class TestBirdOnThrowContract:
    """Bird.on_throw must switch the rigidbody to Dynamic so physics
    (gravity, collisions) begin applying."""

    def test_on_throw_sets_dynamic(self):
        bird_go = GameObject("Bird")
        rb = bird_go.add_component(Rigidbody2D)
        bird_go.add_component(CircleCollider2D)
        bird_comp = bird_go.add_component(Bird)

        lm = LifecycleManager.instance()
        lm.register_component(bird_comp)
        lm.process_awake_queue()
        lm.process_start_queue()

        assert rb.body_type == RigidbodyType2D.KINEMATIC
        bird_comp.on_throw()
        assert rb.body_type == RigidbodyType2D.DYNAMIC

    def test_on_throw_sets_bird_state_thrown(self):
        bird_go = GameObject("Bird")
        bird_go.add_component(Rigidbody2D)
        bird_go.add_component(CircleCollider2D)
        bird_comp = bird_go.add_component(Bird)

        lm = LifecycleManager.instance()
        lm.register_component(bird_comp)
        lm.process_awake_queue()
        lm.process_start_queue()

        assert bird_comp.state == BirdState.BEFORE_THROWN
        bird_comp.on_throw()
        assert bird_comp.state == BirdState.THROWN


# ---------------------------------------------------------------------------
# Slingshot pull clamped to SLINGSHOT_MAX_PULL (1.5 units)
# ---------------------------------------------------------------------------
class TestSlingshotPullClampContract:
    """The slingshot must clamp the bird's pull distance to 1.5 world units
    from the slingshot center, per the Constants."""

    def test_max_pull_constant_is_1_5(self):
        assert Constants.SLINGSHOT_MAX_PULL == 1.5

    def test_calc_velocity_uses_distance(self):
        """_calc_throw_velocity direction should point from bird back toward center."""
        sling_go = GameObject("Slingshot")
        sling_go.transform.position = Vector2(0, 0)
        sling = sling_go.add_component(Slingshot)

        lm = LifecycleManager.instance()
        lm.register_component(sling)
        lm.process_awake_queue()
        lm.process_start_queue()

        # Bird pulled to (1, 0) — velocity should point back toward center (negative x)
        bird_pos = Vector2(1, 0)
        vel = sling._calc_throw_velocity(bird_pos)
        assert vel.x < 0, "Throw velocity x should be negative (back toward center)"


# ---------------------------------------------------------------------------
# Trajectory prediction: pos = start + v*t + 0.5*g*t^2
# ---------------------------------------------------------------------------
class TestTrajectoryContract:
    """predict_trajectory must implement the standard kinematic equation."""

    def test_first_point_is_start(self):
        start = Vector2(1, 2)
        points = predict_trajectory(start, Vector2(5, 10), Vector2(0, -9.81))
        assert abs(points[0].x - 1) < 1e-9
        assert abs(points[0].y - 2) < 1e-9

    def test_kinematic_equation_matches(self):
        """Verify each point matches pos = start + v*t + 0.5*g*t^2."""
        start = Vector2(0, 0)
        velocity = Vector2(10, 20)
        gravity = Vector2(0, -9.81)
        segments = 10
        dt = 0.1

        points = predict_trajectory(start, velocity, gravity, segments=segments, time_step=dt)

        for i in range(segments):
            t = i * dt
            expected_x = start.x + velocity.x * t + 0.5 * gravity.x * t * t
            expected_y = start.y + velocity.y * t + 0.5 * gravity.y * t * t
            assert abs(points[i].x - expected_x) < 1e-9, f"X mismatch at segment {i}"
            assert abs(points[i].y - expected_y) < 1e-9, f"Y mismatch at segment {i}"

    def test_no_gravity_yields_straight_line(self):
        """With zero gravity, trajectory should be a straight line."""
        start = Vector2(0, 0)
        velocity = Vector2(5, 0)
        gravity = Vector2(0, 0)
        points = predict_trajectory(start, velocity, gravity, segments=5, time_step=0.1)

        for p in points:
            assert abs(p.y) < 1e-9, "Y should stay zero with no gravity"

    def test_returns_correct_number_of_segments(self):
        points = predict_trajectory(Vector2(0, 0), Vector2(1, 1), Vector2(0, -9.81), segments=20)
        assert len(points) == 20

    def test_gravity_causes_downward_curve(self):
        """With downward gravity, later points should have decreasing Y."""
        start = Vector2(0, 0)
        velocity = Vector2(10, 0)  # horizontal launch
        gravity = Vector2(0, -9.81)
        points = predict_trajectory(start, velocity, gravity, segments=10, time_step=0.1)

        # All points after first should have y < 0
        for i in range(1, len(points)):
            assert points[i].y < 0, f"Point {i} should be below start with downward gravity"


# ---------------------------------------------------------------------------
# PhysicsMaterial2D defaults: bounciness=0, friction=0.4
# ---------------------------------------------------------------------------
class TestPhysicsMaterial2DDefaults:
    """Unity's PhysicsMaterial2D defaults to bounciness=0 and friction=0.4."""

    def test_default_bounciness(self):
        mat = PhysicsMaterial2D()
        assert mat.bounciness == 0.0

    def test_default_friction(self):
        mat = PhysicsMaterial2D()
        assert mat.friction == pytest.approx(0.4)

    def test_custom_values(self):
        mat = PhysicsMaterial2D(bounciness=0.8, friction=0.2)
        assert mat.bounciness == pytest.approx(0.8)
        assert mat.friction == pytest.approx(0.2)
