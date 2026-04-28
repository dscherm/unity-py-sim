"""Integration tests for the 9 new subsystems — run through the REAL game loop.

These tests use app.run(headless=True, max_frames=N) to exercise subsystems
end-to-end in the actual engine tick order.
"""

from __future__ import annotations

import pytest

from src.engine.app import run
from src.engine.core import (
    GameObject,
    MonoBehaviour,
    _clear_registry,
)
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager, Physics2D
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import (
    BoxCollider2D,
    PhysicsMaterial2D,
)
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time
from src.engine.input_manager import Input
from src.engine.scene import SceneManager, dont_destroy_on_load
from src.engine.coroutine import WaitForSeconds
from src.engine.debug import Debug
from src.engine.rendering.display import DisplayManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_all():
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    DisplayManager.reset()
    Time._reset()
    Input._reset()
    SceneManager.clear()
    Debug._reset()


def _make_dynamic(name, x, y, w=1.0, h=1.0, bounciness=None):
    """Create a dynamic body at (x,y). Optionally set bounciness via material."""
    go = GameObject(name)
    go.transform.position = Vector2(x, y)
    rb = go.add_component(Rigidbody2D)
    rb._body.position = (x, y)
    col = go.add_component(BoxCollider2D)
    col.size = Vector2(w, h)
    if bounciness is not None:
        mat = PhysicsMaterial2D(bounciness=bounciness, friction=0.0)
        col.shared_material = mat
    col.build()
    lm = LifecycleManager.instance()
    lm.register_component(rb)
    return go, rb, col


def _make_static(name, x, y, w=1.0, h=1.0, bounciness=None):
    """Create a static body at (x,y)."""
    go = GameObject(name)
    go.transform.position = Vector2(x, y)
    rb = go.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.STATIC
    rb._body.position = (x, y)
    col = go.add_component(BoxCollider2D)
    col.size = Vector2(w, h)
    if bounciness is not None:
        mat = PhysicsMaterial2D(bounciness=bounciness, friction=0.0)
        col.shared_material = mat
    col.build()
    lm = LifecycleManager.instance()
    lm.register_component(rb)
    return go, rb, col


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_engine():
    _reset_all()
    yield
    _reset_all()


# ===========================================================================
# 1. PhysicsMaterial2D in simulation
# ===========================================================================

class TestPhysicsMaterial2DIntegration:
    """Ball with bounciness=1 vs bounciness=0 bouncing off a wall."""

    def test_bouncy_vs_non_bouncy_different_positions(self):
        """Record the max y reached after initial contact. A bouncy ball should
        bounce back up (max y > resting y), while a dead ball stays put."""
        max_y_records = {}

        for tag, bounce in [("bouncy", 1.0), ("dead", 0.0)]:
            _reset_all()
            tracker = {"max_y_after_contact": -999.0, "contacted": False}

            class BounceTracker(MonoBehaviour):
                def __init__(self):
                    super().__init__()
                    self._tracker = tracker

                def on_collision_enter_2d(self, collision):
                    self._tracker["contacted"] = True

                def update(self):
                    if self._tracker["contacted"]:
                        y = self.game_object.transform.position.y
                        if y > self._tracker["max_y_after_contact"]:
                            self._tracker["max_y_after_contact"] = y

            def scene(b=bounce, trk=tracker):
                _make_static("floor", 0, -5, w=20, h=1, bounciness=b)
                go, rb, col = _make_dynamic("ball", 0, 5, w=1, h=1, bounciness=b)
                bt = go.add_component(BounceTracker)
                bt._tracker = trk
                LifecycleManager.instance().register_component(bt)

            run(scene, headless=True, max_frames=120)
            max_y_records[tag] = tracker["max_y_after_contact"]

        # Bouncy ball should reach a higher max-y after contact than the dead ball
        assert max_y_records["bouncy"] > max_y_records["dead"] + 0.1, (
            f"Bouncy max_y={max_y_records['bouncy']:.3f} should be significantly "
            f"higher than dead max_y={max_y_records['dead']:.3f}"
        )


# ===========================================================================
# 2. Physics2D.overlap_circle as ground check
# ===========================================================================

class TestOverlapCircleGroundCheck:
    """Player above ground, falls, use overlap_circle to verify grounded."""

    def test_overlap_circle_detects_ground(self):
        grounded = {}

        class GroundChecker(MonoBehaviour):
            def update(self):
                pos = self.game_object.transform.position
                check_point = Vector2(pos.x, pos.y - 1.0)
                result = Physics2D.overlap_circle(check_point, 0.5)
                grounded["result"] = result is not None

        def scene():
            # Wide static floor
            _make_static("ground", 0, -5, w=20, h=2)
            # Player above
            go, rb, col = _make_dynamic("player", 0, 0, w=1, h=1)
            checker = go.add_component(GroundChecker)
            LifecycleManager.instance().register_component(checker)

        run(scene, headless=True, max_frames=120)

        assert grounded.get("result") is True, "Player should be grounded after falling"


# ===========================================================================
# 3. Coroutine in game loop
# ===========================================================================

class TestCoroutineInGameLoop:
    """MonoBehaviour starts coroutine in start(), waits 0.5s, sets flag."""

    def test_coroutine_completes_after_wait(self):
        state = {"flag": False}

        class CoroutineUser(MonoBehaviour):
            def start(self):
                self.start_coroutine(self._my_routine())

            def _my_routine(self):
                yield WaitForSeconds(0.5)
                state["flag"] = True

        def scene():
            go = GameObject("coroutine_obj")
            comp = go.add_component(CoroutineUser)
            LifecycleManager.instance().register_component(comp)

        # At 60fps headless, dt=1/60~0.0167, so 0.5s ~ 30 frames. Use 60 for margin.
        run(scene, headless=True, max_frames=60)

        assert state["flag"] is True, "Coroutine should have set flag after 0.5s"


# ===========================================================================
# 4. Scene loading mid-loop
# ===========================================================================

class TestSceneLoadingMidLoop:
    """MonoBehaviour calls SceneManager.load_scene() during update()."""

    def test_scene_load_replaces_objects(self):
        state = {"loaded": False, "new_obj_found": False, "old_obj_gone": True}

        class SceneLoader(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self._loaded = False

            def update(self):
                from src.engine.time_manager import Time
                # Load scene on frame 5
                if Time._frame_count >= 5 and not self._loaded:
                    self._loaded = True
                    SceneManager.load_scene("scene_b")

        class PostLoadChecker(MonoBehaviour):
            def start(self):
                state["new_obj_found"] = True

        def scene_a():
            SceneManager.register_scene("scene_b", scene_b)
            go = GameObject("scene_a_obj")
            loader = go.add_component(SceneLoader)
            LifecycleManager.instance().register_component(loader)
            # Mark the loader's object as persistent so it can trigger the load
            dont_destroy_on_load(go)

        def scene_b():
            state["loaded"] = True
            go = GameObject("scene_b_obj")
            checker = go.add_component(PostLoadChecker)
            LifecycleManager.instance().register_component(checker)

        def setup():
            SceneManager.register_scene("scene_a", scene_a)
            scene_a()
            SceneManager._active_scene = "scene_a"

        run(setup, headless=True, max_frames=30)

        assert state["loaded"] is True, "Scene B should have been loaded"
        assert SceneManager.get_active_scene() == "scene_b"
        scene_b_obj = GameObject.find("scene_b_obj")
        assert scene_b_obj is not None, "Scene B object should exist"


# ===========================================================================
# 5. Stay callbacks across frames
# ===========================================================================

class TestStayCallbacksAcrossFrames:
    """Two overlapping objects -- stay callback should fire > 1 time."""

    def test_stay_fires_multiple_times(self):
        state = {"stay_count": 0}

        class StayCounter(MonoBehaviour):
            def on_collision_stay_2d(self, collision):
                state["stay_count"] += 1

        def scene():
            # Two objects on top of each other — will be in constant contact
            pm = PhysicsManager.instance()
            pm.gravity = Vector2(0, -9.81)

            go1, rb1, col1 = _make_dynamic("obj1", 0, 2, w=2, h=2)
            counter = go1.add_component(StayCounter)
            LifecycleManager.instance().register_component(counter)

            _make_static("floor", 0, -2, w=20, h=2)

        run(scene, headless=True, max_frames=120)

        assert state["stay_count"] > 1, (
            f"Stay should fire multiple times, got {state['stay_count']}"
        )


# ===========================================================================
# 6. Debug.draw_line lifecycle in loop
# ===========================================================================

class TestDebugDrawLineLifecycle:
    """Draw lines with different durations and verify tick-based expiry."""

    def test_duration_zero_line_removed_after_one_frame(self):
        state = {"line_count_frame_2": None}

        class LineDrawer(MonoBehaviour):
            def start(self):
                Debug.draw_line(Vector2(0, 0), Vector2(1, 1), duration=0.0)

            def update(self):
                from src.engine.time_manager import Time
                # On frame 1, tick has already run for the line drawn in start
                if Time._frame_count == 2:
                    Debug.tick(Time.delta_time)
                    state["line_count_frame_2"] = len(Debug.get_lines())

        def scene():
            go = GameObject("debug_obj")
            comp = go.add_component(LineDrawer)
            LifecycleManager.instance().register_component(comp)

        run(scene, headless=True, max_frames=5)

        assert state["line_count_frame_2"] == 0, (
            f"Duration=0 line should be gone by frame 2, got {state['line_count_frame_2']}"
        )

    def test_duration_line_persists_then_expires(self):
        """A line with duration=0.5 should survive several frames then expire."""
        state = {"lines_at_frame_5": None, "lines_at_frame_60": None}

        class LinePersister(MonoBehaviour):
            def start(self):
                Debug.draw_line(Vector2(0, 0), Vector2(1, 1), duration=0.5)

            def update(self):
                from src.engine.time_manager import Time
                Debug.tick(Time.delta_time)
                if Time._frame_count == 5:
                    state["lines_at_frame_5"] = len(Debug.get_lines())
                if Time._frame_count == 60:
                    state["lines_at_frame_60"] = len(Debug.get_lines())

        def scene():
            go = GameObject("debug_obj2")
            comp = go.add_component(LinePersister)
            LifecycleManager.instance().register_component(comp)

        run(scene, headless=True, max_frames=65)

        assert state["lines_at_frame_5"] == 1, "Line should still exist at frame 5"
        assert state["lines_at_frame_60"] == 0, "Line should be expired by frame 60"
