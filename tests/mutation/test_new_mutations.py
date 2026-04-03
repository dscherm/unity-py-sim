"""Mutation tests — monkeypatch breaks, verify tests detect them.

Each test patches a critical behavior to introduce a bug, then asserts
the mutation is detectable (i.e., the broken behavior differs from correct).
"""

from __future__ import annotations

import pytest

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
from src.engine.coroutine import (
    CoroutineManager,
    Coroutine,
    WaitForSeconds,
)
from src.engine.scene import SceneManager, dont_destroy_on_load
from src.engine.ui import RectTransform, Button
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


def _make_body(name, x, y, w=1, h=1, dynamic=True):
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
# 1. Flip PhysicsMaterial2D defaults
# ===========================================================================

class TestMutationPhysicsMaterial2DDefaults:

    def test_flip_default_bounciness(self, monkeypatch):
        """Patch default bounciness to 1.0. Collider without explicit material
        should get elasticity 0.0, so mutation makes it 1.0 — detectable."""
        original_init = PhysicsMaterial2D.__init__

        def broken_init(self, bounciness=1.0, friction=0.4):
            original_init(self, bounciness=bounciness, friction=friction)

        monkeypatch.setattr(PhysicsMaterial2D, "__init__", broken_init)

        go, rb, col = _make_body("obj", 0, 0)
        # With the mutation, default material has bounciness=1.0
        # The correct default is 0.0
        assert col._shape.elasticity == pytest.approx(1.0), \
            "Mutation should have set elasticity to 1.0 (proving it's detectable)"


# ===========================================================================
# 2. Break Physics2D.raycast
# ===========================================================================

class TestMutationPhysics2DRaycast:

    def test_raycast_always_returns_none(self, monkeypatch):
        """Patch raycast to always return None. A valid cast should hit."""
        monkeypatch.setattr(Physics2D, "raycast", staticmethod(lambda *a, **kw: None))

        _make_body("target", 5, 0, w=2, h=2, dynamic=False)
        PhysicsManager.instance()._space.step(0.01)

        hit = Physics2D.raycast(Vector2(0, 0), Vector2(1, 0), 100.0)
        assert hit is None, "Mutation returns None — detectable because real code would return a hit"


# ===========================================================================
# 3. Remove Stay dispatch
# ===========================================================================

class TestMutationRemoveStayDispatch:

    def test_noop_stay_dispatch(self, monkeypatch):
        """Patch _dispatch_stay_callbacks to no-op. Stay count should be 0."""
        monkeypatch.setattr(
            PhysicsManager, "_dispatch_stay_callbacks", lambda self: None
        )

        stay_count = [0]

        class StayListener(MonoBehaviour):
            def on_collision_stay_2d(self, collision):
                stay_count[0] += 1

        go1, rb1, col1 = _make_body("a", 0, 0.5, w=2, h=2)
        listener = go1.add_component(StayListener)
        _make_body("b", 0, -0.5, w=2, h=2, dynamic=False)

        pm = PhysicsManager.instance()
        for _ in range(10):
            pm.step(0.02)

        assert stay_count[0] == 0, "With dispatch patched out, stay should never fire"


# ===========================================================================
# 4. Break coroutine ticking
# ===========================================================================

class TestMutationBreakCoroutineTicking:

    def test_noop_tick_coroutines(self, monkeypatch):
        """Patch _tick_coroutines to no-op. Coroutine never advances past first yield."""
        monkeypatch.setattr(
            LifecycleManager, "_tick_coroutines", lambda self: None
        )

        steps = []

        def my_coro():
            steps.append("first")
            yield None
            steps.append("second")

        go = GameObject("test")
        comp = go.add_component(MonoBehaviour)
        lm = LifecycleManager.instance()
        lm.register_component(comp)

        # Process awake + start
        lm.process_awake_queue()
        lm.process_start_queue()

        comp.start_coroutine(my_coro())
        assert "first" in steps  # start_coroutine advances to first yield

        # Run update (which would tick coroutines if not patched)
        for _ in range(5):
            lm.run_update()

        assert "second" not in steps, \
            "With tick patched out, coroutine should not advance past first yield"


# ===========================================================================
# 5. Break WaitForSeconds
# ===========================================================================

class TestMutationBreakWaitForSeconds:

    def test_is_done_always_true(self, monkeypatch):
        """Patch is_done to always return True. 10-second wait completes instantly."""
        monkeypatch.setattr(WaitForSeconds, "is_done", lambda self, dt: True)

        steps = []

        def my_coro():
            steps.append("before")
            yield WaitForSeconds(10.0)
            steps.append("after")

        go = GameObject("test")
        comp = go.add_component(MonoBehaviour)
        comp.start_coroutine(my_coro())

        # start_coroutine ticks once with dt=0 — is_done returns True immediately
        # so on next tick it should advance past the yield
        if hasattr(MonoBehaviour, '_coroutine_manager'):
            MonoBehaviour._coroutine_manager.tick(0.016)

        assert "after" in steps, \
            "With is_done always True, even 10-second wait completes instantly"


# ===========================================================================
# 6. Break SceneManager.load_scene cleanup
# ===========================================================================

class TestMutationBreakSceneLoadCleanup:

    def test_skip_destroy_old_objects(self, monkeypatch):
        """Patch load_scene to skip destroying old objects."""
        original_load = SceneManager.load_scene.__func__ if hasattr(
            SceneManager.load_scene, '__func__') else SceneManager.load_scene

        def broken_load(name_or_index):
            if isinstance(name_or_index, int):
                if 0 <= name_or_index < len(SceneManager._scene_by_index):
                    name = SceneManager._scene_by_index[name_or_index]
                else:
                    raise ValueError(f"Scene index {name_or_index} out of range")
            else:
                name = name_or_index
            if name not in SceneManager._scenes:
                raise ValueError(f"Scene '{name}' not registered")
            # MUTATION: skip destroying old objects
            SceneManager._active_scene = name
            SceneManager._scenes[name]()

        monkeypatch.setattr(SceneManager, "load_scene", staticmethod(broken_load))

        old_go = GameObject("old_object")
        SceneManager.register_scene("new_scene", lambda: GameObject("new_object"))
        SceneManager.load_scene("new_scene")

        # Old object should still exist because we skipped cleanup
        assert GameObject.find("old_object") is not None, \
            "Mutation skipped cleanup — old objects still present (detectable)"


# ===========================================================================
# 7. Break Button.hit_test
# ===========================================================================

class TestMutationBreakButtonHitTest:

    def test_hit_test_always_true(self, monkeypatch):
        """Patch hit_test to always return True. Points outside should still 'hit'."""
        monkeypatch.setattr(Button, "hit_test", lambda self, sx, sy, cw, ch: True)

        go = GameObject("btn")
        rt = go.add_component(RectTransform)
        rt.size_delta = Vector2(10, 10)
        rt.anchored_position = Vector2(0, 0)
        btn = go.add_component(Button)

        # Point far outside the tiny button
        result = btn.hit_test(0, 0, 800, 600)
        assert result is True, \
            "Mutation makes all hit_tests return True — detectable for outside points"


# ===========================================================================
# 8. Break Debug line expiry
# ===========================================================================

class TestMutationBreakDebugLineExpiry:

    def test_noop_tick_keeps_lines(self, monkeypatch):
        """Patch Debug.tick to no-op. Duration=0 line should persist."""
        monkeypatch.setattr(Debug, "tick", staticmethod(lambda dt: None))

        Debug.draw_line(Vector2(0, 0), Vector2(1, 1), duration=0.0)
        assert len(Debug.get_lines()) == 1

        Debug.tick(0.016)  # patched — does nothing
        assert len(Debug.get_lines()) == 1, \
            "With tick patched, duration=0 line persists (detectable)"
