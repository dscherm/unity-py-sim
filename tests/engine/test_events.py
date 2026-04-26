"""Tests for EventBus and UnityEvent."""

import pytest
from dataclasses import dataclass

from src.engine.events import EventBus, UnityEvent


@pytest.fixture(autouse=True)
def _reset_event_bus():
    EventBus.reset()
    yield
    EventBus.reset()


@dataclass
class ScoreChanged:
    new_score: int
    delta: int


@dataclass
class HealthChanged:
    hp: int


class TestEventBus:
    def test_subscribe_and_publish(self):
        received = []
        EventBus.subscribe(ScoreChanged, lambda e: received.append(e))
        EventBus.publish(ScoreChanged(new_score=100, delta=10))
        assert len(received) == 1
        assert received[0].new_score == 100

    def test_unsubscribe_removes_handler(self):
        received = []
        def handler(e): received.append(e)
        EventBus.subscribe(ScoreChanged, handler)
        EventBus.unsubscribe(ScoreChanged, handler)
        EventBus.publish(ScoreChanged(new_score=50, delta=5))
        assert received == []

    def test_multiple_subscribers(self):
        a, b = [], []
        EventBus.subscribe(ScoreChanged, lambda e: a.append(e))
        EventBus.subscribe(ScoreChanged, lambda e: b.append(e))
        EventBus.publish(ScoreChanged(new_score=10, delta=1))
        assert len(a) == 1
        assert len(b) == 1

    def test_different_event_types_isolated(self):
        scores, healths = [], []
        EventBus.subscribe(ScoreChanged, lambda e: scores.append(e))
        EventBus.subscribe(HealthChanged, lambda e: healths.append(e))
        EventBus.publish(ScoreChanged(new_score=1, delta=1))
        assert len(scores) == 1
        assert len(healths) == 0

    def test_publish_with_no_subscribers(self):
        # Should not raise
        EventBus.publish(ScoreChanged(new_score=0, delta=0))

    def test_unsubscribe_nonexistent_handler_no_op(self):
        EventBus.unsubscribe(ScoreChanged, lambda e: None)

    def test_clear_specific_type(self):
        EventBus.subscribe(ScoreChanged, lambda e: None)
        EventBus.subscribe(HealthChanged, lambda e: None)
        EventBus.clear(ScoreChanged)
        assert EventBus.subscriber_count(ScoreChanged) == 0
        assert EventBus.subscriber_count(HealthChanged) == 1

    def test_clear_all(self):
        EventBus.subscribe(ScoreChanged, lambda e: None)
        EventBus.subscribe(HealthChanged, lambda e: None)
        EventBus.clear()
        assert EventBus.subscriber_count(ScoreChanged) == 0
        assert EventBus.subscriber_count(HealthChanged) == 0

    def test_subscriber_count(self):
        assert EventBus.subscriber_count(ScoreChanged) == 0
        EventBus.subscribe(ScoreChanged, lambda e: None)
        EventBus.subscribe(ScoreChanged, lambda e: None)
        assert EventBus.subscriber_count(ScoreChanged) == 2


class TestUnityEvent:
    def test_add_listener_and_invoke(self):
        called = []
        ev = UnityEvent()
        ev.add_listener(lambda: called.append(True))
        ev.invoke()
        assert called == [True]

    def test_remove_listener(self):
        called = []
        def handler(): called.append(True)
        ev = UnityEvent()
        ev.add_listener(handler)
        ev.remove_listener(handler)
        ev.invoke()
        assert called == []

    def test_multiple_listeners(self):
        a, b = [], []
        ev = UnityEvent()
        ev.add_listener(lambda: a.append(1))
        ev.add_listener(lambda: b.append(2))
        ev.invoke()
        assert a == [1]
        assert b == [2]

    def test_invoke_with_args(self):
        received = []
        ev = UnityEvent()
        ev.add_listener(lambda x, y: received.append((x, y)))
        ev.invoke(42, "hello")
        assert received == [(42, "hello")]

    def test_remove_all_listeners(self):
        ev = UnityEvent()
        ev.add_listener(lambda: None)
        ev.add_listener(lambda: None)
        ev.remove_all_listeners()
        assert ev.listener_count == 0

    def test_listener_count(self):
        ev = UnityEvent()
        assert ev.listener_count == 0
        ev.add_listener(lambda: None)
        assert ev.listener_count == 1

    def test_remove_nonexistent_no_op(self):
        ev = UnityEvent()
        ev.remove_listener(lambda: None)  # should not raise

    def test_invoke_empty_no_error(self):
        ev = UnityEvent()
        ev.invoke()  # should not raise
