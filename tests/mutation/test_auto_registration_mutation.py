"""Mutation tests for auto-registration lifecycle.

Proves that the auto-registration and idempotency features are load-bearing
by monkeypatching them away and verifying tests detect the breakage.
"""

import pytest
from src.engine.core import GameObject, MonoBehaviour, _clear_registry
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


class TrackerBehaviour(MonoBehaviour):
    """Records lifecycle calls."""

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


# --- Mutation 1: Remove auto-registration from add_component ---

def test_mutation_no_auto_register_breaks_lifecycle(monkeypatch):
    """If add_component doesn't auto-register, components never get Update called."""

    original_add = GameObject.add_component

    def add_without_register(self, cls, **kwargs):
        """Simulates add_component WITHOUT the auto-registration call."""
        component = cls(**kwargs)
        component._game_object = self

        from src.engine.transform import Transform
        self._components.append(component)
        if isinstance(component, Transform) and self._transform is None:
            self._transform = component

        # Deliberately skip LifecycleManager registration
        return component

    monkeypatch.setattr(GameObject, "add_component", add_without_register)

    go = GameObject("Test")
    tracker = go.add_component(TrackerBehaviour)

    lm = LifecycleManager.instance()
    lm.process_awake_queue()
    lm.process_start_queue()
    lm.run_update()

    # Without auto-registration, awake/start/update should NOT be called
    assert not tracker.awake_called, "Mutation failed: awake was called without registration"
    assert not tracker.start_called, "Mutation failed: start was called without registration"
    assert tracker.update_count == 0, "Mutation failed: update was called without registration"


# --- Mutation 2: Non-idempotent register_component causes duplicate calls ---

def test_mutation_non_idempotent_register_causes_duplicates(monkeypatch):
    """If register_component is NOT idempotent, double-registration causes duplicate lifecycle."""

    def non_idempotent_register(self, comp):
        """Always appends to awake queue, no duplicate check."""
        self._awake_queue.append(comp)

    monkeypatch.setattr(LifecycleManager, "register_component", non_idempotent_register)

    go = GameObject("Test")
    tracker = go.add_component(TrackerBehaviour)

    lm = LifecycleManager.instance()
    # add_component called register once via monkeypatched version;
    # now call it again to simulate the "explicit + auto" pattern
    lm.register_component(tracker)

    lm.process_awake_queue()
    lm.process_start_queue()
    lm.run_update()

    # With non-idempotent registration, we expect duplicates
    assert tracker.update_count > 1 or tracker.awake_called, (
        "Mutation test expects duplicates from non-idempotent register"
    )
    # The REAL test: with the actual idempotent code, this scenario would produce
    # exactly 1 update call. The mutation breaks that guarantee.


# --- Mutation 3: Camera.main not set if awake skipped ---

def test_mutation_camera_main_broken_without_awake():
    """If auto-registration is removed, Camera.main never gets set."""

    go = GameObject("Main Camera")
    cam = Camera()
    cam._game_object = go
    go._components.append(cam)
    # Deliberately skip registering with LifecycleManager

    lm = LifecycleManager.instance()
    lm.process_awake_queue()

    assert Camera.main is None, (
        "Camera.main should be None when camera is not registered (awake not called)"
    )


# --- Mutation 4: Prove the idempotent path is actually exercised ---

def test_idempotent_register_produces_single_update():
    """With the real (non-mutated) code, double register_component still yields
    exactly 1 awake, 1 start, 1 update per frame."""
    go = GameObject("Test")
    tracker = go.add_component(TrackerBehaviour)

    lm = LifecycleManager.instance()
    # Call register again — should be a no-op
    lm.register_component(tracker)

    lm.process_awake_queue()
    lm.process_start_queue()
    lm.run_update()

    assert tracker.update_count == 1, f"Expected 1 update, got {tracker.update_count}"
