from __future__ import annotations
"""Contract tests: Unity lifecycle behaviour contracts.

These tests verify that the engine honours Unity's documented lifecycle guarantees,
derived from Unity documentation rather than from the implementation.

Unity contracts tested:
1. AddComponent<T>() triggers Awake() before the next frame's Update.
2. After Awake(), Start() is called before the component's first Update().
3. Multiple AddComponent calls on the same GameObject all register independently.
4. Components added at runtime during Update() get Awake/Start before their first Update.
5. Calling register_component twice is safe (idempotent).
"""

import pytest
from src.engine.core import GameObject, MonoBehaviour, Component, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.rendering.camera import Camera


@pytest.fixture(autouse=True)
def clean_state():
    _clear_registry()
    LifecycleManager.reset()
    Camera._reset_main()
    yield
    _clear_registry()
    LifecycleManager.reset()
    Camera._reset_main()


class OrderRecorder(MonoBehaviour):
    """Records the order of lifecycle calls."""

    def __init__(self):
        super().__init__()
        self.call_order: list[str] = []

    def awake(self):
        self.call_order.append("awake")

    def start(self):
        self.call_order.append("start")

    def update(self):
        self.call_order.append("update")


class SpawnDuringUpdate(MonoBehaviour):
    """Spawns a child with OrderRecorder on its first update."""

    def __init__(self):
        super().__init__()
        self.child_recorder: OrderRecorder | None = None
        self._spawned = False

    def update(self):
        if not self._spawned:
            self._spawned = True
            go = GameObject("Child")
            self.child_recorder = go.add_component(OrderRecorder)


# --- Contract 1: AddComponent triggers Awake before next frame Update ---

def test_awake_called_after_add_component():
    """Unity contract: AddComponent<T>() causes Awake() to be called when the
    lifecycle manager next processes its awake queue (before that frame's Update)."""
    go = GameObject("Test")
    recorder = go.add_component(OrderRecorder)

    lm = LifecycleManager.instance()
    lm.process_awake_queue()

    assert "awake" in recorder.call_order, "Awake was not called after add_component + process_awake_queue"


# --- Contract 2: Start is called after Awake and before first Update ---

def test_start_after_awake_before_update():
    """Unity contract: lifecycle order is Awake -> Start -> Update."""
    go = GameObject("Test")
    recorder = go.add_component(OrderRecorder)

    lm = LifecycleManager.instance()
    # Simulate one frame
    lm.process_awake_queue()
    lm.process_start_queue()
    lm.run_update()

    assert recorder.call_order == ["awake", "start", "update"], (
        f"Expected [awake, start, update], got {recorder.call_order}"
    )


# --- Contract 3: Multiple AddComponent calls all register independently ---

def test_multiple_add_component_independent():
    """Unity contract: each AddComponent call creates an independent component,
    each gets its own Awake/Start/Update cycle."""
    go = GameObject("Test")
    r1 = go.add_component(OrderRecorder)
    r2 = go.add_component(OrderRecorder)

    lm = LifecycleManager.instance()
    lm.process_awake_queue()
    lm.process_start_queue()
    lm.run_update()

    for i, r in enumerate([r1, r2]):
        assert r.call_order == ["awake", "start", "update"], (
            f"Recorder {i}: expected [awake, start, update], got {r.call_order}"
        )


# --- Contract 4: Runtime-added components get Awake/Start before their first Update ---

def test_runtime_added_component_lifecycle_order():
    """Unity contract: a component added during Update() gets Awake and Start
    processed before its own first Update (on the next frame)."""
    go = GameObject("Spawner")
    spawner = go.add_component(SpawnDuringUpdate)

    lm = LifecycleManager.instance()

    # Frame 1: spawner gets awake+start, then update (which spawns child)
    lm.process_awake_queue()
    lm.process_start_queue()
    lm.run_update()

    child = spawner.child_recorder
    assert child is not None, "Spawner didn't create child"
    # Child was just added — its awake/start haven't been processed yet
    # (Unity processes them at the start of the next frame)

    # Frame 2: process awake+start for child, then update
    lm.process_awake_queue()
    lm.process_start_queue()
    lm.run_update()

    assert child.call_order[:3] == ["awake", "start", "update"], (
        f"Child lifecycle order wrong: {child.call_order}"
    )


# --- Contract 5: register_component is idempotent ---

def test_register_component_idempotent():
    """Calling register_component multiple times for the same component should
    not cause duplicate Awake/Start/Update calls."""
    go = GameObject("Test")
    recorder = go.add_component(OrderRecorder)

    lm = LifecycleManager.instance()
    # add_component already registered it; register again explicitly
    lm.register_component(recorder)
    lm.register_component(recorder)

    lm.process_awake_queue()
    lm.process_start_queue()
    lm.run_update()

    assert recorder.call_order.count("awake") == 1, "Awake called more than once"
    assert recorder.call_order.count("start") == 1, "Start called more than once"
    assert recorder.call_order.count("update") == 1, "Update called more than once"


# --- Contract 6: Non-MonoBehaviour Components still get Awake ---

def test_plain_component_gets_awake():
    """Unity contract: Components (not just MonoBehaviours) receive Awake when added."""
    class PlainComponent(Component):
        def __init__(self):
            super().__init__()
            self.awake_called = False

        def awake(self):
            self.awake_called = True

    go = GameObject("Test")
    comp = go.add_component(PlainComponent)

    lm = LifecycleManager.instance()
    lm.process_awake_queue()

    assert comp.awake_called, "Plain Component's awake was not called"


# --- Contract 7: Camera.main set through auto-registration ---

def test_camera_main_set_by_auto_registration():
    """Camera (a Component, not MonoBehaviour) should get awake() called via
    auto-registration, setting Camera.main."""
    go = GameObject("Main Camera")
    cam = go.add_component(Camera)

    lm = LifecycleManager.instance()
    lm.process_awake_queue()

    assert Camera.main is cam, f"Camera.main is {Camera.main}, expected the added camera"
