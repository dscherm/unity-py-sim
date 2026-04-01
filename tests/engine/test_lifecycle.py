"""Tests for LifecycleManager."""

import pytest

from src.engine.core import Component, MonoBehaviour, GameObject
from src.engine.lifecycle import LifecycleManager


class OrderTracker(MonoBehaviour):
    """Test helper that records lifecycle call order."""

    log: list[str] = []

    def __init__(self):
        super().__init__()
        OrderTracker.log = []

    def awake(self):
        OrderTracker.log.append("awake")

    def start(self):
        OrderTracker.log.append("start")

    def update(self):
        OrderTracker.log.append("update")

    def fixed_update(self):
        OrderTracker.log.append("fixed_update")

    def late_update(self):
        OrderTracker.log.append("late_update")

    def on_destroy(self):
        OrderTracker.log.append("on_destroy")


class TestLifecycleManager:
    def setup_method(self):
        LifecycleManager.reset()

    def test_singleton(self):
        lm1 = LifecycleManager.instance()
        lm2 = LifecycleManager.instance()
        assert lm1 is lm2

    def test_awake_called(self):
        lm = LifecycleManager.instance()
        go = GameObject("Test")
        tracker = go.add_component(OrderTracker)
        lm.register_component(tracker)
        lm.process_awake_queue()
        assert "awake" in OrderTracker.log

    def test_start_called_after_awake(self):
        lm = LifecycleManager.instance()
        go = GameObject("Test")
        tracker = go.add_component(OrderTracker)
        lm.register_component(tracker)
        lm.process_awake_queue()
        lm.process_start_queue()
        assert OrderTracker.log == ["awake", "start"]

    def test_update_called(self):
        lm = LifecycleManager.instance()
        go = GameObject("Test")
        tracker = go.add_component(OrderTracker)
        lm.register_component(tracker)
        lm.process_awake_queue()
        lm.process_start_queue()
        lm.run_update()
        assert "update" in OrderTracker.log

    def test_fixed_update_called(self):
        lm = LifecycleManager.instance()
        go = GameObject("Test")
        tracker = go.add_component(OrderTracker)
        lm.register_component(tracker)
        lm.process_awake_queue()
        lm.process_start_queue()
        lm.run_fixed_update()
        assert "fixed_update" in OrderTracker.log

    def test_late_update_called(self):
        lm = LifecycleManager.instance()
        go = GameObject("Test")
        tracker = go.add_component(OrderTracker)
        lm.register_component(tracker)
        lm.process_awake_queue()
        lm.process_start_queue()
        lm.run_late_update()
        assert "late_update" in OrderTracker.log

    def test_full_lifecycle_order(self):
        lm = LifecycleManager.instance()
        go = GameObject("Test")
        tracker = go.add_component(OrderTracker)
        lm.register_component(tracker)

        lm.process_awake_queue()
        lm.process_start_queue()
        lm.run_fixed_update()
        lm.run_update()
        lm.run_late_update()

        assert OrderTracker.log == ["awake", "start", "fixed_update", "update", "late_update"]

    def test_disabled_component_skipped(self):
        lm = LifecycleManager.instance()
        go = GameObject("Test")
        tracker = go.add_component(OrderTracker)
        tracker.enabled = False
        lm.register_component(tracker)
        lm.process_awake_queue()
        assert OrderTracker.log == []

    def test_disabled_during_update(self):
        lm = LifecycleManager.instance()
        go = GameObject("Test")
        tracker = go.add_component(OrderTracker)
        lm.register_component(tracker)
        lm.process_awake_queue()
        lm.process_start_queue()
        tracker.enabled = False
        lm.run_update()
        # update should NOT appear since disabled
        assert "update" not in OrderTracker.log

    def test_destroy_queue(self):
        lm = LifecycleManager.instance()
        go = GameObject("Test")
        tracker = go.add_component(OrderTracker)
        lm.register_component(tracker)
        lm.process_awake_queue()
        lm.process_start_queue()
        lm.schedule_destroy(tracker)
        lm.process_destroy_queue()
        assert "on_destroy" in OrderTracker.log
        # Should be unregistered — update should do nothing
        OrderTracker.log.clear()
        lm.run_update()
        assert "update" not in OrderTracker.log

    def test_multiple_components(self):
        lm = LifecycleManager.instance()
        counts = {"a": 0, "b": 0}

        class CounterA(MonoBehaviour):
            def update(self):
                counts["a"] += 1

        class CounterB(MonoBehaviour):
            def update(self):
                counts["b"] += 1

        g1 = GameObject("A")
        g2 = GameObject("B")
        ca = g1.add_component(CounterA)
        cb = g2.add_component(CounterB)
        lm.register_component(ca)
        lm.register_component(cb)
        lm.process_awake_queue()
        lm.process_start_queue()
        lm.run_update()
        assert counts["a"] == 1
        assert counts["b"] == 1

    def test_unregister_component(self):
        lm = LifecycleManager.instance()
        go = GameObject("Test")
        tracker = go.add_component(OrderTracker)
        lm.register_component(tracker)
        lm.process_awake_queue()
        lm.process_start_queue()
        lm.unregister_component(tracker)
        OrderTracker.log.clear()
        lm.run_update()
        assert "update" not in OrderTracker.log
