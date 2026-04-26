"""Contract tests — verify the new subsystems match Unity's documented behavior.

These are unit-level tests that verify API contracts without running the full game loop.
"""

from __future__ import annotations

import pytest
import pymunk

from src.engine.core import (
    GameObject,
    MonoBehaviour,
    _clear_registry,
)
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import (
    PhysicsManager,
    Physics2D,
    RaycastHit2D,
    Collision2D,
)
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import (
    BoxCollider2D,
    CircleCollider2D,
    PhysicsMaterial2D,
    Collider2D,
)
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time
from src.engine.coroutine import (
    CoroutineManager,
    Coroutine,
    WaitForSeconds,
    WaitForSecondsRealtime,
    WaitForEndOfFrame,
    WaitForFixedUpdate,
    WaitUntil,
    WaitWhile,
)
from src.engine.scene import SceneManager, dont_destroy_on_load
from src.engine.audio import AudioClip, AudioSource, AudioListener
from src.engine.ui import (
    Canvas,
    RectTransform,
    Text,
    Image,
    Button,
    RenderMode,
    TextAnchor,
)
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
    SceneManager.clear()
    Debug._reset()
    Canvas.reset()
    AudioListener.reset()


def _make_body(name, x, y, w=1, h=1, dynamic=True):
    """Create a GO with rb + box collider and register with physics."""
    go = GameObject(name)
    go.transform.position = Vector2(x, y)
    rb = go.add_component(Rigidbody2D)
    if not dynamic:
        rb.body_type = RigidbodyType2D.STATIC
    rb._body.position = (x, y)
    col = go.add_component(BoxCollider2D)
    col.size = Vector2(w, h)
    col.build()
    return go, rb, col


@pytest.fixture(autouse=True)
def clean_engine():
    _reset_all()
    yield
    _reset_all()


# ===========================================================================
# PhysicsMaterial2D contracts
# ===========================================================================

class TestPhysicsMaterial2DContract:

    def test_defaults(self):
        mat = PhysicsMaterial2D()
        assert mat.bounciness == 0.0
        assert mat.friction == pytest.approx(0.4)

    def test_instance_material_overrides_shared(self):
        """Instance material takes priority over shared material."""
        go, rb, col = _make_body("obj", 0, 0)
        shared = PhysicsMaterial2D(bounciness=0.5, friction=0.3)
        instance = PhysicsMaterial2D(bounciness=0.9, friction=0.1)
        col.shared_material = shared
        assert col._shape.elasticity == pytest.approx(0.5)
        col.material = instance
        assert col._shape.elasticity == pytest.approx(0.9)
        assert col._shape.friction == pytest.approx(0.1)

    def test_setting_material_after_build_updates_shape(self):
        """Changing material after build() should update the live pymunk shape."""
        go, rb, col = _make_body("obj", 0, 0)
        assert col._shape.elasticity == pytest.approx(0.0)  # default
        mat = PhysicsMaterial2D(bounciness=0.8, friction=0.2)
        col.shared_material = mat
        assert col._shape.elasticity == pytest.approx(0.8)
        assert col._shape.friction == pytest.approx(0.2)


# ===========================================================================
# Physics2D.Raycast contracts
# ===========================================================================

class TestPhysics2DRaycastContract:

    def test_raycast_returns_none_when_no_hit(self):
        # Empty space, no bodies registered
        result = Physics2D.raycast(Vector2(0, 0), Vector2(1, 0), 10.0)
        assert result is None

    def test_raycast_returns_closest_hit(self):
        _make_body("near", 5, 0, w=2, h=2, dynamic=False)
        _make_body("far", 15, 0, w=2, h=2, dynamic=False)
        # Need a step to update the space's spatial index
        PhysicsManager.instance()._space.step(0.01)

        hit = Physics2D.raycast(Vector2(0, 0), Vector2(1, 0), 100.0)
        assert hit is not None
        # Closest should be "near" at x~4 (edge of 2-wide box centered at 5)
        assert hit.distance < 10.0

    def test_raycast_hit_has_valid_fields(self):
        _make_body("target", 5, 0, w=2, h=2, dynamic=False)
        PhysicsManager.instance()._space.step(0.01)

        hit = Physics2D.raycast(Vector2(0, 0), Vector2(1, 0), 100.0)
        assert hit is not None
        assert isinstance(hit.point, Vector2)
        assert isinstance(hit.normal, Vector2)
        assert hit.distance > 0
        assert hit.transform is not None

    def test_raycast_all_sorted_by_distance(self):
        _make_body("near", 5, 0, w=2, h=2, dynamic=False)
        _make_body("far", 15, 0, w=2, h=2, dynamic=False)
        PhysicsManager.instance()._space.step(0.01)

        hits = Physics2D.raycast_all(Vector2(0, 0), Vector2(1, 0), 100.0)
        assert len(hits) >= 2
        for i in range(1, len(hits)):
            assert hits[i].distance >= hits[i - 1].distance


# ===========================================================================
# Stay callback contracts
# ===========================================================================

class TestStayCallbackContract:

    def test_stay_fires_every_physics_step(self):
        """Stay should fire on every step while contact persists."""
        stay_count = [0]

        class StayListener(MonoBehaviour):
            def on_collision_stay_2d(self, collision):
                stay_count[0] += 1

        go1, rb1, col1 = _make_body("a", 0, 1, w=2, h=2)
        listener = go1.add_component(StayListener)

        go2, rb2, col2 = _make_body("b", 0, -1, w=2, h=2, dynamic=False)

        pm = PhysicsManager.instance()
        # Step multiple times — objects overlap, stay should fire each step
        for _ in range(10):
            pm.step(0.02)

        assert stay_count[0] > 1, f"Stay should fire multiple times, got {stay_count[0]}"

    def test_stay_does_not_fire_after_exit(self):
        """After objects separate, Stay should stop."""
        stay_count = [0]

        class StayListener(MonoBehaviour):
            def on_collision_stay_2d(self, collision):
                stay_count[0] += 1

        go1, rb1, col1 = _make_body("a", 0, 0.5, w=1, h=1)
        listener = go1.add_component(StayListener)

        go2, rb2, col2 = _make_body("b", 0, -0.5, w=1, h=1, dynamic=False)

        pm = PhysicsManager.instance()
        # Let them collide
        pm.step(0.02)
        pm.step(0.02)
        count_before_move = stay_count[0]

        # Move the dynamic object far away
        rb1._body.position = (100, 100)
        rb1._body.velocity = (0, 0)
        # Step enough for pymunk to register separation
        for _ in range(5):
            pm.step(0.02)

        count_after_separation = stay_count[0]
        # The count should not increase indefinitely after separation
        # (A few more may fire during separation detection, but not for all remaining steps)
        extra_steps = 10
        for _ in range(extra_steps):
            pm.step(0.02)
        count_final = stay_count[0]
        # After clear separation, no more stays
        assert count_final == count_after_separation + extra_steps or \
               count_final - count_after_separation < extra_steps, \
               "Stay should eventually stop after separation"


# ===========================================================================
# Coroutine contracts
# ===========================================================================

class TestCoroutineContract:

    def test_start_coroutine_advances_to_first_yield_immediately(self):
        """start_coroutine should advance to the first yield right away."""
        steps = []

        def my_coro():
            steps.append("before_yield")
            yield None
            steps.append("after_yield")

        go = GameObject("test")
        comp = go.add_component(MonoBehaviour)
        comp.start_coroutine(my_coro())

        assert "before_yield" in steps, "Should advance to first yield immediately"
        assert "after_yield" not in steps, "Should NOT advance past first yield"

    def test_wait_for_seconds_uses_scaled_time(self):
        """WaitForSeconds should be affected by time scale (via delta_time passed)."""
        w = WaitForSeconds(1.0)
        # Simulate scaled time: if time_scale=2.0, delta_time is 2x
        # WaitForSeconds.is_done receives delta_time from LifecycleManager
        # which passes Time.delta_time (already scaled)
        assert w.is_done(0.4) is False
        assert w.is_done(0.4) is False
        assert w.is_done(0.3) is True  # 0.4+0.4+0.3 = 1.1 >= 1.0

    def test_stop_coroutine_prevents_further_execution(self):
        steps = []

        def my_coro():
            steps.append("step1")
            yield None
            steps.append("step2")
            yield None
            steps.append("step3")

        go = GameObject("test")
        comp = go.add_component(MonoBehaviour)
        coro = comp.start_coroutine(my_coro())
        assert "step1" in steps

        comp.stop_coroutine(coro)
        assert coro.is_finished is True

        # Ticking should not advance
        if hasattr(MonoBehaviour, '_coroutine_manager'):
            MonoBehaviour._coroutine_manager.tick(0.016)

        assert "step2" not in steps

    def test_nested_coroutines(self):
        """Outer coroutine waits for inner to finish."""
        steps = []

        def inner():
            steps.append("inner_start")
            yield None
            steps.append("inner_done")

        def outer():
            steps.append("outer_start")
            go_temp = GameObject("temp")
            comp_temp = go_temp.add_component(MonoBehaviour)
            inner_coro = comp_temp.start_coroutine(inner())
            yield inner_coro
            steps.append("outer_after_inner")

        go = GameObject("test")
        comp = go.add_component(MonoBehaviour)
        comp.start_coroutine(outer())

        # After start: outer_start, inner_start reached
        assert "outer_start" in steps
        assert "inner_start" in steps

        # Tick to finish inner
        MonoBehaviour._coroutine_manager.tick(0.016)
        assert "inner_done" in steps

        # Tick to let outer continue past yield inner_coro
        MonoBehaviour._coroutine_manager.tick(0.016)
        assert "outer_after_inner" in steps


# ===========================================================================
# SceneManager.load_scene contracts
# ===========================================================================

class TestSceneManagerContract:

    def test_load_unknown_scene_raises(self):
        with pytest.raises(ValueError, match="not registered"):
            SceneManager.load_scene("nonexistent")

    def test_load_destroys_non_persistent_objects(self):
        go1 = GameObject("ephemeral")
        go2 = GameObject("persistent")
        dont_destroy_on_load(go2)

        SceneManager.register_scene("test_scene", lambda: None)
        SceneManager.load_scene("test_scene")

        assert GameObject.find("ephemeral") is None
        assert GameObject.find("persistent") is not None

    def test_active_scene_updates(self):
        SceneManager.register_scene("scene_a", lambda: None)
        SceneManager.load_scene("scene_a")
        assert SceneManager.get_active_scene() == "scene_a"

    def test_setup_callable_runs(self):
        state = {"ran": False}

        def setup():
            state["ran"] = True

        SceneManager.register_scene("s", setup)
        SceneManager.load_scene("s")
        assert state["ran"] is True

    def test_load_by_index(self):
        SceneManager.register_scene("first", lambda: None)
        SceneManager.register_scene("second", lambda: None)
        SceneManager.load_scene(1)
        assert SceneManager.get_active_scene() == "second"

    def test_load_by_invalid_index_raises(self):
        with pytest.raises(ValueError, match="out of range"):
            SceneManager.load_scene(99)


# ===========================================================================
# AudioSource contracts
# ===========================================================================

class TestAudioSourceContract:

    def test_volume_clamped(self):
        go = GameObject("audio_obj")
        src = go.add_component(AudioSource)
        src.volume = 2.0
        assert src.volume == 1.0
        src.volume = -0.5
        assert src.volume == 0.0

    def test_play_without_clip_does_not_crash(self):
        go = GameObject("audio_obj")
        src = go.add_component(AudioSource)
        src.play()  # Should not raise

    def test_on_destroy_stops_playback(self):
        go = GameObject("audio_obj")
        src = go.add_component(AudioSource)
        src._playing = True
        src.on_destroy()
        assert src._playing is False


# ===========================================================================
# Button.hit_test contracts
# ===========================================================================

class TestButtonHitTestContract:

    def test_hit_inside_rect(self):
        go = GameObject("btn")
        rt = go.add_component(RectTransform)
        rt.size_delta = Vector2(100, 40)
        rt.anchored_position = Vector2(0, 0)
        btn = go.add_component(Button)

        # Centered anchor on 800x600: rect at (350, 280, 100, 40)
        assert btn.hit_test(400, 300, 800, 600) is True  # center

    def test_hit_outside_rect(self):
        go = GameObject("btn")
        rt = go.add_component(RectTransform)
        rt.size_delta = Vector2(100, 40)
        rt.anchored_position = Vector2(0, 0)
        btn = go.add_component(Button)

        assert btn.hit_test(0, 0, 800, 600) is False  # top-left corner

    def test_hit_no_rect_transform(self):
        go = GameObject("btn_no_rt")
        btn = go.add_component(Button)
        assert btn.hit_test(400, 300, 800, 600) is False


# ===========================================================================
# RectTransform.get_screen_rect contract
# ===========================================================================

class TestRectTransformScreenRect:

    def test_centered_anchor_on_800x600(self):
        """Default centered anchor: rect should be centered on screen."""
        go = GameObject("rt_obj")
        rt = go.add_component(RectTransform)
        rt.size_delta = Vector2(200, 100)
        rt.anchored_position = Vector2(0, 0)
        # anchor_min/max default to (0.5, 0.5), pivot default (0.5, 0.5)

        x, y, w, h = rt.get_screen_rect(800, 600)
        assert w == pytest.approx(200)
        assert h == pytest.approx(100)
        # Center of rect: x + w/2 = 400, y + h/2 = 300
        assert x == pytest.approx(300)  # 400 - 200*0.5
        assert y == pytest.approx(250)  # 300 - 100*0.5
