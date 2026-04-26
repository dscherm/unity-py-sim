from __future__ import annotations
"""Integration tests for auto-registration lifecycle.

Validates that add_component() automatically registers components with
LifecycleManager so lifecycle methods fire without manual registration.
"""

import pytest
from src.engine.core import GameObject, MonoBehaviour, Component, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.rendering.camera import Camera
from src.engine import app


@pytest.fixture(autouse=True)
def clean_state():
    """Reset all global state before each test."""
    _clear_registry()
    LifecycleManager.reset()
    Camera._reset_main()
    yield
    _clear_registry()
    LifecycleManager.reset()
    Camera._reset_main()


class TrackerBehaviour(MonoBehaviour):
    """MonoBehaviour that records which lifecycle methods were called."""

    def __init__(self):
        super().__init__()
        self.awake_called = False
        self.start_called = False
        self.update_count = 0

    def awake(self):
        self.awake_called = True

    def start(self):
        self.start_called = True

    def update(self):
        self.update_count += 1


class LateTrackerBehaviour(MonoBehaviour):
    """Tracks late_update calls."""

    def __init__(self):
        super().__init__()
        self.late_update_count = 0

    def late_update(self):
        self.late_update_count += 1


class RuntimeSpawner(MonoBehaviour):
    """Spawns a new GameObject with TrackerBehaviour during update on frame 2."""

    def __init__(self):
        super().__init__()
        self.spawned_tracker: TrackerBehaviour | None = None
        self.frame = 0

    def update(self):
        self.frame += 1
        if self.frame == 2 and self.spawned_tracker is None:
            go = GameObject("RuntimeSpawned")
            self.spawned_tracker = go.add_component(TrackerBehaviour)


def test_multiple_gameobjects_lifecycle_fires():
    """Create multiple GameObjects with MonoBehaviours via add_component, run loop, verify all fire."""

    trackers = []

    def setup():
        for i in range(5):
            go = GameObject(f"Obj{i}")
            t = go.add_component(TrackerBehaviour)
            trackers.append(t)

    app.run(setup, headless=True, max_frames=3)

    for i, t in enumerate(trackers):
        assert t.awake_called, f"Tracker {i} awake not called"
        assert t.start_called, f"Tracker {i} start not called"
        assert t.update_count >= 2, f"Tracker {i} update_count={t.update_count}, expected >= 2"


def test_runtime_spawned_objects_get_lifecycle():
    """Objects created during update() also get auto-registered and lifecycle fires."""

    spawner_ref = []

    def setup():
        go = GameObject("Spawner")
        s = go.add_component(RuntimeSpawner)
        spawner_ref.append(s)

    app.run(setup, headless=True, max_frames=6)

    spawner = spawner_ref[0]
    assert spawner.spawned_tracker is not None, "Spawner never created runtime object"
    t = spawner.spawned_tracker
    assert t.awake_called, "Runtime-spawned tracker awake not called"
    assert t.start_called, "Runtime-spawned tracker start not called"
    # Spawned on frame 2, so by frame 6 it should have multiple updates
    assert t.update_count >= 2, f"Runtime-spawned tracker update_count={t.update_count}"


def test_camera_main_set_via_awake():
    """Camera extends Component (not MonoBehaviour). Its awake() should be called to set Camera.main."""

    cam_ref = []

    def setup():
        cam_go = GameObject("Main Camera")
        cam = cam_go.add_component(Camera)
        cam_ref.append(cam)

    app.run(setup, headless=True, max_frames=2)

    assert Camera.main is not None, "Camera.main was not set"
    assert Camera.main is cam_ref[0], "Camera.main is not the camera we added"


def test_late_update_fires_for_auto_registered():
    """LateUpdate should also fire for auto-registered MonoBehaviours."""

    tracker_ref = []

    def setup():
        go = GameObject("LateObj")
        t = go.add_component(LateTrackerBehaviour)
        tracker_ref.append(t)

    app.run(setup, headless=True, max_frames=3)

    assert tracker_ref[0].late_update_count >= 2, (
        f"late_update_count={tracker_ref[0].late_update_count}, expected >= 2"
    )


def test_multiple_components_on_same_gameobject():
    """Multiple add_component calls on the same GameObject all register independently."""

    trackers = []

    def setup():
        go = GameObject("MultiComp")
        t1 = go.add_component(TrackerBehaviour)
        t2 = go.add_component(TrackerBehaviour)
        t3 = go.add_component(LateTrackerBehaviour)
        trackers.extend([t1, t2, t3])

    app.run(setup, headless=True, max_frames=3)

    assert trackers[0].awake_called and trackers[0].update_count >= 2
    assert trackers[1].awake_called and trackers[1].update_count >= 2
    assert trackers[2].late_update_count >= 2
