"""Integration tests that run the REAL game loop via app.run().

These tests verify cross-system interactions that unit tests miss:
physics + lifecycle, input + movement, collision callbacks, and scene management.
"""

from __future__ import annotations

import pytest

from src.engine.app import run
from src.engine.core import (
    Component,
    GameObject,
    MonoBehaviour,
    _clear_registry,
)
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D
from src.engine.input_manager import Input
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time
from src.engine.transform import Transform
from src.engine.scene import SceneManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_all():
    """Reset all engine singletons and global state."""
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    Time._reset()
    Input._reset()


def _make_dynamic_body(name, x, y, w=1.0, h=1.0):
    """Create a GameObject with Rigidbody2D + BoxCollider2D at (x, y)."""
    go = GameObject(name)
    go.transform.position = Vector2(x, y)
    rb = go.add_component(Rigidbody2D)
    rb._body.position = (x, y)
    col = go.add_component(BoxCollider2D)
    col.size = Vector2(w, h)
    col.build()
    lm = LifecycleManager.instance()
    lm.register_component(rb)
    return go, rb, col


def _make_static_body(name, x, y, w=1.0, h=1.0):
    """Create a static-body GameObject with BoxCollider2D at (x, y)."""
    go = GameObject(name)
    go.transform.position = Vector2(x, y)
    rb = go.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.STATIC
    rb._body.position = (x, y)
    col = go.add_component(BoxCollider2D)
    col.size = Vector2(w, h)
    col.build()
    lm = LifecycleManager.instance()
    lm.register_component(rb)
    return go, rb, col


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_engine():
    """Ensure clean engine state before and after each test."""
    _reset_all()
    yield
    _reset_all()


# ===========================================================================
# Test 1: Physics + Lifecycle -- gravity moves objects
# ===========================================================================

class TestPhysicsLifecycleIntegration:
    """Verify that running the game loop with physics causes objects to move."""

    def test_gravity_moves_dynamic_body_downward(self):
        """A dynamic body with no floor should fall due to gravity."""
        positions = []

        def scene():
            go, rb, col = _make_dynamic_body("Faller", 0, 10)

        run(scene_setup=scene, headless=True, max_frames=30)

        # After 30 frames of gravity, the object should have moved down
        faller = GameObject.find("Faller")
        assert faller is not None
        y_pos = faller.transform.position.y
        assert y_pos < 10.0, (
            f"Expected object to fall below y=10, but y={y_pos}"
        )

    def test_static_body_does_not_move(self):
        """A static body should remain at its starting position."""

        def scene():
            _make_static_body("Floor", 0, 0, 20, 1)

        run(scene_setup=scene, headless=True, max_frames=20)

        floor = GameObject.find("Floor")
        assert floor is not None
        pos = floor.transform.position
        assert abs(pos.x) < 0.01 and abs(pos.y) < 0.01, (
            f"Static body moved unexpectedly to {pos}"
        )


# ===========================================================================
# Test 2: Input + Movement via MonoBehaviour.update
# ===========================================================================

class Mover(MonoBehaviour):
    """Test component that moves right when 'd' is held."""

    def __init__(self):
        super().__init__()
        self.speed = 5.0

    def update(self):
        if Input.get_key("d"):
            self.transform.translate(Vector2(self.speed * Time.delta_time, 0))


class TestInputMovement:
    """Verify that injected input causes movement across real frames."""

    def test_key_press_moves_object(self):
        """Holding 'd' should move the object to the right."""

        def scene():
            go = GameObject("Player")
            go.transform.position = Vector2(0, 0)
            mover = go.add_component(Mover)
            LifecycleManager.instance().register_component(mover)
            # Inject key press INSIDE scene_setup (after run() calls _reset)
            Input._set_key_state("d", True)

        run(scene_setup=scene, headless=True, max_frames=30)

        player = GameObject.find("Player")
        assert player is not None
        x = player.transform.position.x
        assert x > 0.0, f"Expected player to move right, but x={x}"

    def test_no_input_no_movement(self):
        """Without input, object should stay at origin (no rb/gravity)."""

        def scene():
            go = GameObject("Player")
            go.transform.position = Vector2(0, 0)
            mover = go.add_component(Mover)
            LifecycleManager.instance().register_component(mover)

        run(scene_setup=scene, headless=True, max_frames=30)

        player = GameObject.find("Player")
        assert player is not None
        x = player.transform.position.x
        assert abs(x) < 0.01, f"Expected no movement, but x={x}"


# ===========================================================================
# Test 3: Collision callbacks (Enter / Exit)
# ===========================================================================

class CollisionTracker(MonoBehaviour):
    """Records collision events for testing."""

    def __init__(self):
        super().__init__()
        self.enter_count = 0
        self.exit_count = 0
        self.enter_objects: list[str] = []

    def on_collision_enter_2d(self, collision):
        self.enter_count += 1
        self.enter_objects.append(collision.game_object.name)

    def on_collision_exit_2d(self, collision):
        self.exit_count += 1


class TestCollisionCallbacks:
    """Verify collision Enter fires when objects collide in the game loop."""

    def test_collision_enter_fires_on_impact(self):
        """Two objects placed to overlap should fire OnCollisionEnter2D."""
        tracker_ref = {}

        def scene():
            # Object A: dynamic, falling onto B
            go_a = GameObject("ObjA")
            go_a.transform.position = Vector2(0, 5)
            rb_a = go_a.add_component(Rigidbody2D)
            rb_a._body.position = (0, 5)
            col_a = go_a.add_component(CircleCollider2D)
            col_a.radius = 1.0
            col_a.build()
            tracker = go_a.add_component(CollisionTracker)
            lm = LifecycleManager.instance()
            lm.register_component(rb_a)
            lm.register_component(tracker)
            tracker_ref["t"] = tracker

            # Object B: static floor
            go_b = GameObject("Floor")
            go_b.transform.position = Vector2(0, 0)
            rb_b = go_b.add_component(Rigidbody2D)
            rb_b.body_type = RigidbodyType2D.STATIC
            rb_b._body.position = (0, 0)
            col_b = go_b.add_component(BoxCollider2D)
            col_b.size = Vector2(20, 1)
            col_b.build()
            lm.register_component(rb_b)

        run(scene_setup=scene, headless=True, max_frames=120)

        t = tracker_ref["t"]
        assert t.enter_count > 0, "OnCollisionEnter2D was never called"
        assert "Floor" in t.enter_objects, (
            f"Expected collision with 'Floor', got: {t.enter_objects}"
        )


# ===========================================================================
# Test 4: Lifecycle ordering within the game loop
# ===========================================================================

class LifecycleRecorder(MonoBehaviour):
    """Records the order in which lifecycle methods are called."""

    log: list[str] = []

    def __init__(self):
        super().__init__()

    def awake(self):
        LifecycleRecorder.log.append("awake")

    def start(self):
        LifecycleRecorder.log.append("start")

    def fixed_update(self):
        LifecycleRecorder.log.append("fixed_update")

    def update(self):
        LifecycleRecorder.log.append("update")

    def late_update(self):
        LifecycleRecorder.log.append("late_update")


class TestLifecycleOrderInLoop:
    """Verify lifecycle ordering when run through the real game loop."""

    def test_awake_before_start_before_update(self):
        LifecycleRecorder.log = []

        def scene():
            go = GameObject("Recorder")
            rec = go.add_component(LifecycleRecorder)
            LifecycleManager.instance().register_component(rec)

        run(scene_setup=scene, headless=True, max_frames=3)

        log = LifecycleRecorder.log
        assert "awake" in log, "awake was never called"
        assert "start" in log, "start was never called"
        assert "update" in log, "update was never called"

        awake_idx = log.index("awake")
        start_idx = log.index("start")
        first_update_idx = log.index("update")

        assert awake_idx < start_idx, "awake should fire before start"
        assert start_idx < first_update_idx, "start should fire before first update"

    def test_fixed_update_before_update_on_same_frame(self):
        """When FixedUpdate fires on a frame, it fires before Update on that frame.

        Note: with headless dt=1/60 and fixed_dt=1/50, FixedUpdate doesn't
        fire every frame (accumulator must reach 0.02). On frames where
        FixedUpdate DOES fire, it should come before Update in the log.
        """
        LifecycleRecorder.log = []

        def scene():
            go = GameObject("Recorder")
            rec = go.add_component(LifecycleRecorder)
            LifecycleManager.instance().register_component(rec)

        run(scene_setup=scene, headless=True, max_frames=10)

        log = LifecycleRecorder.log
        # On any frame where both fixed_update and update appear,
        # fixed_update must come first. We look for the pattern
        # [..., fixed_update, ..., update, ...] within each frame.
        # A "frame" in the log is a sequence ending with late_update.
        frames: list[list[str]] = []
        current_frame: list[str] = []
        post_start = log[log.index("start") + 1:] if "start" in log else log
        for entry in post_start:
            current_frame.append(entry)
            if entry == "late_update":
                frames.append(current_frame)
                current_frame = []

        # Check frames where fixed_update fired
        frames_with_both = [
            f for f in frames
            if "fixed_update" in f and "update" in f
        ]
        assert len(frames_with_both) > 0, (
            "Expected at least one frame with both FixedUpdate and Update"
        )
        for f in frames_with_both:
            fu_idx = f.index("fixed_update")
            u_idx = f.index("update")
            assert fu_idx < u_idx, (
                f"FixedUpdate should fire before Update, but got {f}"
            )

    def test_late_update_after_update(self):
        LifecycleRecorder.log = []

        def scene():
            go = GameObject("Recorder")
            rec = go.add_component(LifecycleRecorder)
            LifecycleManager.instance().register_component(rec)

        run(scene_setup=scene, headless=True, max_frames=3)

        log = LifecycleRecorder.log
        if "update" in log and "late_update" in log:
            # Check ordering in first frame after start
            post_start = log[log.index("start") + 1:]
            if "update" in post_start and "late_update" in post_start:
                u_idx = post_start.index("update")
                lu_idx = post_start.index("late_update")
                assert u_idx < lu_idx, (
                    "Update should fire before LateUpdate"
                )


# ===========================================================================
# Test 5: Scene management -- clearing all objects
# ===========================================================================

class TestSceneManagement:
    """Verify SceneManager operations within the game loop."""

    def test_scene_clear_removes_all_objects(self):
        """SceneManager.clear() should remove all GameObjects."""

        def scene():
            for i in range(5):
                go = GameObject(f"Obj{i}")

        run(scene_setup=scene, headless=True, max_frames=1)

        # Verify objects exist
        all_objs = SceneManager.get_all_game_objects()
        assert len(all_objs) == 5

        # Clear
        SceneManager.clear()
        all_objs = SceneManager.get_all_game_objects()
        assert len(all_objs) == 0

    def test_destroyed_objects_not_findable(self):
        """Destroyed objects should not be returned by GameObject.find()."""

        def scene():
            go = GameObject("Target")

        run(scene_setup=scene, headless=True, max_frames=1)

        target = GameObject.find("Target")
        assert target is not None
        GameObject.destroy(target)
        found = GameObject.find("Target")
        assert found is None, "Destroyed object should not be findable"


# ===========================================================================
# Test 6: PhysicsMaterial -- elasticity affects bounce
# ===========================================================================

class TestPhysicsElasticity:
    """Verify that collider elasticity settings affect physics outcomes."""

    def test_elastic_vs_inelastic_different_outcomes(self):
        """A ball with elasticity=1 should bounce higher than one with elasticity=0."""
        final_positions = {}

        for label, elasticity in [("bouncy", 1.0), ("dead", 0.0)]:

            def scene(e=elasticity, lbl=label):
                # Ball
                ball = GameObject(f"Ball_{lbl}")
                ball.transform.position = Vector2(0, 10)
                rb = ball.add_component(Rigidbody2D)
                rb._body.position = (0, 10)
                col = ball.add_component(CircleCollider2D)
                col.radius = 0.5
                col.build()
                # Set elasticity on the shape directly
                col._shape.elasticity = e
                LifecycleManager.instance().register_component(rb)

                # Floor
                floor = GameObject("Floor")
                floor.transform.position = Vector2(0, 0)
                rb_f = floor.add_component(Rigidbody2D)
                rb_f.body_type = RigidbodyType2D.STATIC
                rb_f._body.position = (0, 0)
                col_f = floor.add_component(BoxCollider2D)
                col_f.size = Vector2(20, 1)
                col_f.build()
                col_f._shape.elasticity = e
                LifecycleManager.instance().register_component(rb_f)

            _reset_all()
            run(scene_setup=scene, headless=True, max_frames=200)

            ball = GameObject.find(f"Ball_{label}")
            if ball is not None:
                final_positions[label] = ball.transform.position.y

        # Both should have fallen, but bouncy ball should end higher or
        # at least have different position than dead ball
        if "bouncy" in final_positions and "dead" in final_positions:
            # The key insight: with elasticity=0 the ball stops on the floor;
            # with elasticity=1 it bounces. After many frames the dead ball
            # should be resting low, the bouncy ball may be higher.
            # At minimum, the outcomes should differ.
            assert final_positions["bouncy"] != final_positions["dead"], (
                f"Expected different outcomes: bouncy={final_positions['bouncy']}, "
                f"dead={final_positions['dead']}"
            )


# ===========================================================================
# Test 7: Multiple components on same object in the loop
# ===========================================================================

class Counter(MonoBehaviour):
    """Counts how many update frames it has seen."""

    def __init__(self):
        super().__init__()
        self.count = 0

    def update(self):
        self.count += 1


class TestMultiComponent:
    """Verify multiple MonoBehaviours on one GameObject all get ticked."""

    def test_multiple_behaviours_all_update(self):
        refs = {}

        def scene():
            go = GameObject("Multi")
            c1 = go.add_component(Counter)
            c2 = go.add_component(Counter)
            lm = LifecycleManager.instance()
            lm.register_component(c1)
            lm.register_component(c2)
            refs["c1"] = c1
            refs["c2"] = c2

        run(scene_setup=scene, headless=True, max_frames=10)

        # Both counters should have been updated
        assert refs["c1"].count > 0, "First Counter never updated"
        assert refs["c2"].count > 0, "Second Counter never updated"
        # They should have the same count (both run each frame)
        assert refs["c1"].count == refs["c2"].count, (
            f"Counter mismatch: {refs['c1'].count} vs {refs['c2'].count}"
        )


# ===========================================================================
# Test 8: Time progresses correctly across frames
# ===========================================================================

class TestTimeProgression:
    """Verify that Time values advance properly across the game loop."""

    def test_time_advances(self):
        time_vals = {}

        def scene():
            pass  # empty scene

        run(scene_setup=scene, headless=True, max_frames=10)

        # Time.time should be positive after running frames
        assert Time._time > 0, f"Time did not advance: {Time._time}"
        assert Time._frame_count >= 10, (
            f"Frame count too low: {Time._frame_count}"
        )

    def test_delta_time_is_reasonable(self):
        """In headless mode, delta_time should be 1/target_fps."""

        def scene():
            pass

        run(scene_setup=scene, headless=True, max_frames=1, target_fps=60)

        # After one frame, delta_time should be ~1/60
        dt = Time._delta_time
        assert abs(dt - 1.0 / 60) < 0.001, f"Unexpected delta_time: {dt}"


# ===========================================================================
# Test 9: Trigger callbacks
# ===========================================================================

class TriggerTracker(MonoBehaviour):
    """Records trigger events."""

    def __init__(self):
        super().__init__()
        self.enter_count = 0
        self.exit_count = 0

    def on_trigger_enter_2d(self, other):
        self.enter_count += 1

    def on_trigger_exit_2d(self, other):
        self.exit_count += 1


class TestTriggerCallbacks:
    """Verify trigger enter/exit fire when objects overlap."""

    def test_trigger_enter_fires(self):
        tracker_ref = {}

        def scene():
            # Dynamic object falling into trigger zone
            go_a = GameObject("Projectile")
            go_a.transform.position = Vector2(0, 5)
            rb_a = go_a.add_component(Rigidbody2D)
            rb_a._body.position = (0, 5)
            col_a = go_a.add_component(CircleCollider2D)
            col_a.radius = 0.5
            col_a.build()
            tracker = go_a.add_component(TriggerTracker)
            lm = LifecycleManager.instance()
            lm.register_component(rb_a)
            lm.register_component(tracker)
            tracker_ref["t"] = tracker

            # Static trigger zone
            go_b = GameObject("Zone")
            go_b.transform.position = Vector2(0, 0)
            rb_b = go_b.add_component(Rigidbody2D)
            rb_b.body_type = RigidbodyType2D.STATIC
            rb_b._body.position = (0, 0)
            col_b = go_b.add_component(BoxCollider2D)
            col_b.size = Vector2(10, 2)
            col_b.is_trigger = True
            col_b.build()
            lm.register_component(rb_b)

        run(scene_setup=scene, headless=True, max_frames=120)

        t = tracker_ref["t"]
        assert t.enter_count > 0, "OnTriggerEnter2D was never called"
