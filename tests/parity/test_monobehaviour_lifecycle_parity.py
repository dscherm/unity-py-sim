"""Parity tests: UnityEngine.MonoBehaviour lifecycle order.

Documented Unity behavior (https://docs.unity3d.com/Manual/ExecutionOrder.html):
- Awake runs once when the script instance is created (even if disabled)
- OnEnable runs whenever the component becomes enabled (after Awake first time)
- Start runs once before the first frame Update (only if enabled)
- FixedUpdate runs at fixed intervals before Update
- Update runs every frame
- LateUpdate runs every frame after all Updates
- OnDestroy runs when the component is being destroyed

Order on a fresh enabled component spun up via AddComponent:
  Awake -> OnEnable -> Start -> (FixedUpdate, Update, LateUpdate)*
"""

from __future__ import annotations

import pytest

from src.engine.core import GameObject, MonoBehaviour, _clear_registry
from src.engine.lifecycle import LifecycleManager


@pytest.fixture(autouse=True)
def _reset_engine():
    LifecycleManager.reset()
    _clear_registry()
    yield
    LifecycleManager.reset()
    _clear_registry()


class _Recorder(MonoBehaviour):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[str] = []

    def awake(self) -> None:
        self.calls.append("awake")

    def on_enable(self) -> None:
        self.calls.append("on_enable")

    def start(self) -> None:
        self.calls.append("start")

    def update(self) -> None:
        self.calls.append("update")

    def fixed_update(self) -> None:
        self.calls.append("fixed_update")

    def late_update(self) -> None:
        self.calls.append("late_update")

    def on_destroy(self) -> None:
        self.calls.append("on_destroy")


def _drive_one_frame(lm: LifecycleManager) -> None:
    """Mirror Unity's per-frame order: awake, start, fixed, update, late."""
    lm.process_awake_queue()
    lm.process_start_queue()
    lm.run_fixed_update()
    lm.run_update()
    lm.run_late_update()
    lm.process_destroy_queue()


def test_awake_before_start():
    """Unity guarantees Awake() runs before Start(), and both run before Update."""
    go = GameObject("LifecycleHost")
    rec = go.add_component(_Recorder)
    lm = LifecycleManager.instance()
    _drive_one_frame(lm)
    assert "awake" in rec.calls and "start" in rec.calls
    assert rec.calls.index("awake") < rec.calls.index("start"), (
        f"Awake must run before Start, got order: {rec.calls}"
    )


def test_on_enable_runs_after_awake_for_initially_enabled():
    """Documented behavior: 'OnEnable is called whenever the object is enabled'.
    For an initially-enabled component, OnEnable fires immediately after Awake."""
    go = GameObject("EnabledHost")
    rec = go.add_component(_Recorder)
    lm = LifecycleManager.instance()
    _drive_one_frame(lm)
    assert "awake" in rec.calls and "on_enable" in rec.calls
    assert rec.calls.index("awake") < rec.calls.index("on_enable")


def test_start_before_first_update():
    """Unity: 'Start is called before the first frame update'."""
    go = GameObject("StartFirstHost")
    rec = go.add_component(_Recorder)
    lm = LifecycleManager.instance()
    _drive_one_frame(lm)
    assert "start" in rec.calls
    assert "update" in rec.calls
    assert rec.calls.index("start") < rec.calls.index("update"), (
        f"Start must precede the first Update, got: {rec.calls}"
    )


def test_fixed_update_runs_before_update_in_same_frame():
    """Unity: FixedUpdate executes before Update during a frame that triggers
    a physics step. Our driver always runs both, so FixedUpdate must come first."""
    go = GameObject("PhysicsHost")
    rec = go.add_component(_Recorder)
    lm = LifecycleManager.instance()
    _drive_one_frame(lm)
    assert "fixed_update" in rec.calls
    assert "update" in rec.calls
    assert rec.calls.index("fixed_update") < rec.calls.index("update")


def test_late_update_runs_after_update():
    """Unity: 'LateUpdate is called every frame, after all Update functions'."""
    go = GameObject("LateHost")
    rec = go.add_component(_Recorder)
    lm = LifecycleManager.instance()
    _drive_one_frame(lm)
    assert rec.calls.index("update") < rec.calls.index("late_update")


def test_disabled_component_does_not_get_start_or_update():
    """Unity: components with enabled=false do not receive Start/Update.
    Awake still runs (Unity calls Awake regardless of enabled state)."""
    go = GameObject("DisabledHost")
    rec = go.add_component(_Recorder)
    rec.enabled = False
    # Reset the calls captured during enable→disable transition
    rec.calls.clear()
    lm = LifecycleManager.instance()
    _drive_one_frame(lm)
    # Awake must run even when disabled
    assert "awake" in rec.calls
    # But Start and Update must not fire
    assert "start" not in rec.calls
    assert "update" not in rec.calls


def test_on_destroy_fires_on_destroy_queue():
    """Unity: OnDestroy is called when the component/GameObject is destroyed."""
    go = GameObject("DestroyHost")
    rec = go.add_component(_Recorder)
    lm = LifecycleManager.instance()
    _drive_one_frame(lm)
    rec.calls.clear()
    lm.schedule_destroy(rec)
    lm.process_destroy_queue()
    assert "on_destroy" in rec.calls
