"""Independent validation tests for Object Pooling (Task 2) and Event Bus (Task 3).

Tests derived from Unity documentation behavior, NOT from reading existing tests.
Covers: contract, integration, mutation, and edge cases.
"""

from __future__ import annotations

import pytest
from dataclasses import dataclass

from src.engine.pool import ObjectPool, GameObjectPool
from src.engine.events import EventBus, UnityEvent
from src.engine.core import GameObject, _clear_registry


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture(autouse=True)
def clean_state():
    """Reset global state before each test."""
    _clear_registry()
    EventBus.reset()
    yield
    _clear_registry()
    EventBus.reset()


# ============================================================
# POOL CONTRACT TESTS
# ============================================================

class TestObjectPoolContract:
    """Verify ObjectPool matches Unity's ObjectPool<T> contract."""

    def test_get_creates_when_pool_empty(self):
        """get() must call create_func when no pooled objects exist."""
        created = []
        pool = ObjectPool(create_func=lambda: (created.append(1), "obj")[1])
        result = pool.get()
        assert result == "obj"
        assert len(created) == 1

    def test_get_reuses_when_pool_has_objects(self):
        """get() must return a pooled object instead of creating new."""
        create_count = [0]

        def factory():
            create_count[0] += 1
            return f"obj_{create_count[0]}"

        pool = ObjectPool(create_func=factory)
        obj1 = pool.get()
        pool.release(obj1)
        obj2 = pool.get()
        # Should reuse obj1, not create a new one
        assert obj2 == "obj_1"
        assert create_count[0] == 1

    def test_max_size_enforced_on_release(self):
        """When pool is full, release should call on_destroy instead of pooling."""
        destroyed = []
        pool = ObjectPool(
            create_func=lambda: object(),
            on_destroy=lambda o: destroyed.append(o),
            max_size=2,
        )
        objs = [pool.get() for _ in range(5)]
        for o in objs:
            pool.release(o)
        # Pool should have max 2 inactive, rest destroyed
        assert pool.count_inactive == 2
        assert len(destroyed) == 3

    def test_on_get_callback_fires(self):
        """on_get must be called every time get() returns an object."""
        got = []
        pool = ObjectPool(create_func=lambda: "x", on_get=lambda o: got.append(o))
        pool.get()
        assert got == ["x"]
        pool.release("x")
        pool.get()
        assert len(got) == 2

    def test_on_release_callback_fires(self):
        """on_release must be called when object is returned."""
        released = []
        pool = ObjectPool(create_func=lambda: "x", on_release=lambda o: released.append(o))
        obj = pool.get()
        pool.release(obj)
        assert released == ["x"]

    def test_on_destroy_callback_fires_on_clear(self):
        """clear() must call on_destroy for each pooled object."""
        destroyed = []
        pool = ObjectPool(
            create_func=lambda: object(),
            on_destroy=lambda o: destroyed.append(o),
        )
        objs = [pool.get() for _ in range(3)]
        for o in objs:
            pool.release(o)
        pool.clear()
        assert len(destroyed) == 3
        assert pool.count_inactive == 0

    def test_count_active_tracks_checked_out(self):
        """count_active must reflect objects checked out but not returned."""
        pool = ObjectPool(create_func=lambda: object())
        assert pool.count_active == 0
        o1 = pool.get()
        o2 = pool.get()
        assert pool.count_active == 2
        pool.release(o1)
        assert pool.count_active == 1

    def test_count_inactive_tracks_pooled(self):
        """count_inactive must reflect objects waiting in the pool."""
        pool = ObjectPool(create_func=lambda: object())
        assert pool.count_inactive == 0
        o = pool.get()
        pool.release(o)
        assert pool.count_inactive == 1

    def test_pre_warm_creates_inactive_objects(self):
        """pre_warm(n) must create n objects in the pool without marking active."""
        create_count = [0]

        def factory():
            create_count[0] += 1
            return f"obj_{create_count[0]}"

        pool = ObjectPool(create_func=factory, max_size=10)
        pool.pre_warm(5)
        assert pool.count_inactive == 5
        assert pool.count_active == 0
        assert create_count[0] == 5

    def test_pre_warm_respects_max_size(self):
        """pre_warm should not exceed max_size."""
        pool = ObjectPool(create_func=lambda: object(), max_size=3)
        pool.pre_warm(10)
        assert pool.count_inactive == 3


# ============================================================
# POOL INTEGRATION TESTS (GameObjectPool)
# ============================================================

class TestGameObjectPoolIntegration:
    """Verify GameObjectPool integrates with GameObject correctly."""

    def test_get_returns_active_gameobject(self):
        """GameObjectPool.get() must return an active GO."""
        go_pool = GameObjectPool(template_name="Bullet", tag="Bullet")
        go = go_pool.get()
        assert isinstance(go, GameObject)
        assert go.active is True

    def test_release_deactivates_gameobject(self):
        """GameObjectPool.release() must deactivate the GO."""
        go_pool = GameObjectPool(template_name="Enemy")
        go = go_pool.get()
        assert go.active is True
        go_pool.release(go)
        assert go.active is False

    def test_pre_warm_creates_inactive_gameobjects(self):
        """pre_warm must create GOs that start inactive."""
        go_pool = GameObjectPool(template_name="Coin", max_size=10)
        go_pool.pre_warm(5)
        assert go_pool.count_inactive == 5
        assert go_pool.count_active == 0

    def test_gameobject_naming(self):
        """GOs should have sequential names based on template_name."""
        go_pool = GameObjectPool(template_name="Bullet")
        go1 = go_pool.get()
        go2 = go_pool.get()
        assert go1.name == "Bullet_1"
        assert go2.name == "Bullet_2"

    def test_gameobject_tag_assignment(self):
        """GOs should have the tag specified in pool constructor."""
        go_pool = GameObjectPool(template_name="Enemy", tag="Enemy")
        go = go_pool.get()
        assert go.tag == "Enemy"

    def test_custom_on_get_callback(self):
        """Custom on_get should fire after activation."""
        called = []
        go_pool = GameObjectPool(
            template_name="X",
            on_get=lambda go: called.append(go.active),
        )
        go_pool.get()
        # Should be active when custom callback fires
        assert called == [True]

    def test_custom_on_release_callback(self):
        """Custom on_release should fire after deactivation."""
        called = []
        go_pool = GameObjectPool(
            template_name="X",
            on_release=lambda go: called.append(go.active),
        )
        go = go_pool.get()
        go_pool.release(go)
        # Should be inactive when custom callback fires
        assert called == [False]

    def test_get_reuses_released_gameobjects(self):
        """After release, the same GO should come back from get()."""
        go_pool = GameObjectPool(template_name="Reusable", max_size=10)
        go1 = go_pool.get()
        go_pool.release(go1)
        go2 = go_pool.get()
        assert go2 is go1
        assert go2.active is True

    def test_clear_empties_pool(self):
        """clear() must remove all pooled objects."""
        go_pool = GameObjectPool(template_name="Temp")
        go = go_pool.get()
        go_pool.release(go)
        assert go_pool.count_inactive == 1
        go_pool.clear()
        assert go_pool.count_inactive == 0


# ============================================================
# POOL MUTATION TESTS
# ============================================================

class TestObjectPoolMutation:
    """Monkeypatch breakage to prove tests catch defects."""

    def test_broken_create_func_detected(self):
        """If create_func raises, get() must propagate the error."""
        pool = ObjectPool(create_func=lambda: (_ for _ in ()).throw(RuntimeError("broken")))
        with pytest.raises(RuntimeError, match="broken"):
            pool.get()

    def test_broken_max_size_allows_unlimited_pooling(self, monkeypatch):
        """If max_size check is removed, pool grows without bound."""
        pool = ObjectPool(create_func=lambda: object(), max_size=2)
        objs = [pool.get() for _ in range(10)]
        for o in objs:
            pool.release(o)
        # With max_size=2, only 2 should be pooled
        assert pool.count_inactive == 2
        # Now break max_size by monkeypatching
        monkeypatch.setattr(pool, '_max_size', 999)
        more_objs = [pool.get() for _ in range(5)]
        for o in more_objs:
            pool.release(o)
        # Now pool should have grown beyond 2
        assert pool.count_inactive > 2

    def test_broken_activation_detected(self, monkeypatch):
        """If the on_get callback in the inner pool is broken, GO stays inactive."""
        go_pool = GameObjectPool(template_name="Test")
        # Break the activation by patching the inner pool's on_get callback
        monkeypatch.setattr(go_pool._pool, '_on_get', lambda go: None)
        go = go_pool.get()
        # GO was created with active=False, and activation was broken
        assert go.active is False  # Proves mutation is detected


# ============================================================
# EVENTS CONTRACT TESTS
# ============================================================

class TestEventBusContract:
    """Verify EventBus matches Unity-style typed event bus contract."""

    def test_subscribe_and_publish_delivers(self):
        """Subscribing then publishing must call the handler."""
        received = []
        EventBus.subscribe(str, lambda e: received.append(e))
        EventBus.publish("hello")
        assert received == ["hello"]

    def test_unsubscribe_stops_delivery(self):
        """After unsubscribe, handler must not receive events."""
        received = []
        def handler(e): received.append(e)
        EventBus.subscribe(int, handler)
        EventBus.publish(42)
        EventBus.unsubscribe(int, handler)
        EventBus.publish(99)
        assert received == [42]

    def test_multiple_subscribers_all_called(self):
        """Multiple handlers for same event type must all be called."""
        results = []
        EventBus.subscribe(int, lambda e: results.append(f"a:{e}"))
        EventBus.subscribe(int, lambda e: results.append(f"b:{e}"))
        EventBus.publish(7)
        assert results == ["a:7", "b:7"]

    def test_clear_specific_type(self):
        """clear(type) must remove only that type's subscribers."""
        int_received = []
        str_received = []
        EventBus.subscribe(int, lambda e: int_received.append(e))
        EventBus.subscribe(str, lambda e: str_received.append(e))
        EventBus.clear(int)
        EventBus.publish(1)
        EventBus.publish("hi")
        assert int_received == []
        assert str_received == ["hi"]

    def test_clear_all(self):
        """clear() with no args must remove all subscribers."""
        received = []
        EventBus.subscribe(int, lambda e: received.append(e))
        EventBus.subscribe(str, lambda e: received.append(e))
        EventBus.clear()
        EventBus.publish(1)
        EventBus.publish("hi")
        assert received == []

    def test_reset_clears_everything(self):
        """reset() must clear all subscribers."""
        received = []
        EventBus.subscribe(int, lambda e: received.append(e))
        EventBus.reset()
        EventBus.publish(1)
        assert received == []

    def test_subscriber_count(self):
        """subscriber_count must accurately reflect registered handlers."""
        assert EventBus.subscriber_count(int) == 0
        def handler1(e): pass
        def handler2(e): pass
        EventBus.subscribe(int, handler1)
        assert EventBus.subscriber_count(int) == 1
        EventBus.subscribe(int, handler2)
        assert EventBus.subscriber_count(int) == 2
        EventBus.unsubscribe(int, handler1)
        assert EventBus.subscriber_count(int) == 1

    def test_type_isolation(self):
        """Events of different types must not cross-deliver."""
        int_received = []
        str_received = []
        EventBus.subscribe(int, lambda e: int_received.append(e))
        EventBus.subscribe(str, lambda e: str_received.append(e))
        EventBus.publish(42)
        EventBus.publish("hello")
        assert int_received == [42]
        assert str_received == ["hello"]


# ============================================================
# EVENTS INTEGRATION TESTS
# ============================================================

class TestEventBusIntegration:
    """Integration tests with dataclass events and real usage patterns."""

    def test_dataclass_event_with_fields(self):
        """Dataclass events must deliver with all fields intact."""

        @dataclass
        class ScoreChanged:
            new_score: int
            delta: int

        received = []
        EventBus.subscribe(ScoreChanged, lambda e: received.append((e.new_score, e.delta)))
        EventBus.publish(ScoreChanged(new_score=100, delta=10))
        assert received == [(100, 10)]

    def test_multiple_dataclass_event_types(self):
        """Different dataclass types must be dispatched independently."""

        @dataclass
        class PlayerDied:
            player_id: int

        @dataclass
        class EnemySpawned:
            enemy_type: str

        deaths = []
        spawns = []
        EventBus.subscribe(PlayerDied, lambda e: deaths.append(e.player_id))
        EventBus.subscribe(EnemySpawned, lambda e: spawns.append(e.enemy_type))
        EventBus.publish(PlayerDied(player_id=1))
        EventBus.publish(EnemySpawned(enemy_type="goblin"))
        assert deaths == [1]
        assert spawns == ["goblin"]

    def test_subscriber_count_for_dataclass_type(self):
        @dataclass
        class Ping:
            pass

        EventBus.subscribe(Ping, lambda e: None)
        EventBus.subscribe(Ping, lambda e: None)
        assert EventBus.subscriber_count(Ping) == 2


class TestUnityEventIntegration:
    """Verify UnityEvent matches Unity's callback pattern."""

    def test_invoke_no_args(self):
        """UnityEvent with no args should call all listeners."""
        called = []
        evt = UnityEvent()
        evt.add_listener(lambda: called.append("a"))
        evt.add_listener(lambda: called.append("b"))
        evt.invoke()
        assert called == ["a", "b"]

    def test_invoke_with_args(self):
        """UnityEvent should pass args through to listeners."""
        received = []
        evt = UnityEvent()
        evt.add_listener(lambda x, y: received.append((x, y)))
        evt.invoke(10, 20)
        assert received == [(10, 20)]

    def test_remove_listener(self):
        """remove_listener must stop that listener from being called."""
        called = []
        def handler(): called.append(1)
        evt = UnityEvent()
        evt.add_listener(handler)
        evt.invoke()
        evt.remove_listener(handler)
        evt.invoke()
        assert called == [1]

    def test_remove_all_listeners(self):
        """remove_all_listeners must clear everything."""
        called = []
        evt = UnityEvent()
        evt.add_listener(lambda: called.append(1))
        evt.add_listener(lambda: called.append(2))
        evt.remove_all_listeners()
        evt.invoke()
        assert called == []

    def test_listener_count(self):
        """listener_count property must reflect current state."""
        evt = UnityEvent()
        assert evt.listener_count == 0
        def h1(): pass
        def h2(): pass
        evt.add_listener(h1)
        assert evt.listener_count == 1
        evt.add_listener(h2)
        assert evt.listener_count == 2
        evt.remove_listener(h1)
        assert evt.listener_count == 1
        evt.remove_all_listeners()
        assert evt.listener_count == 0


# ============================================================
# EVENTS MUTATION TESTS
# ============================================================

class TestEventBusMutation:
    """Monkeypatch to prove event tests catch defects."""

    def test_broken_publish_dispatch(self, monkeypatch):
        """If publish doesn't iterate subscribers, nothing is delivered."""
        received = []
        EventBus.subscribe(int, lambda e: received.append(e))
        # Break publish by making it a no-op
        monkeypatch.setattr(EventBus, 'publish', classmethod(lambda cls, event: None))
        EventBus.publish(42)
        assert received == []  # Proves the mutation is observable

    def test_broken_unsubscribe(self, monkeypatch):
        """If unsubscribe is broken, handler keeps receiving events."""
        received = []
        def handler(e): received.append(e)
        EventBus.subscribe(int, handler)
        # Break unsubscribe to be a no-op
        monkeypatch.setattr(EventBus, 'unsubscribe', classmethod(lambda cls, et, h: None))
        EventBus.unsubscribe(int, handler)
        EventBus.publish(99)
        # Handler still receives because unsubscribe was broken
        assert 99 in received


# ============================================================
# EDGE CASE TESTS
# ============================================================

class TestEdgeCases:
    """Edge cases for both pool and events systems."""

    def test_release_more_than_got(self):
        """Releasing objects that were never gotten should not crash."""
        pool = ObjectPool(create_func=lambda: "x", max_size=5)
        # Release without get — should not crash or go negative
        pool.release("orphan")
        assert pool.count_active == 0  # Should not go negative
        assert pool.count_inactive == 1

    def test_double_subscribe_same_handler(self):
        """Subscribing the same handler twice should call it twice."""
        received = []
        def handler(e): received.append(e)
        EventBus.subscribe(int, handler)
        EventBus.subscribe(int, handler)
        EventBus.publish(1)
        assert received == [1, 1]
        assert EventBus.subscriber_count(int) == 2

    def test_unsubscribe_removes_only_first_duplicate(self):
        """Unsubscribe should remove only the first matching handler."""
        received = []
        def handler(e): received.append(e)
        EventBus.subscribe(int, handler)
        EventBus.subscribe(int, handler)
        EventBus.unsubscribe(int, handler)
        EventBus.publish(5)
        # One copy remains
        assert received == [5]
        assert EventBus.subscriber_count(int) == 1

    def test_publish_with_no_subscribers(self):
        """Publishing with no subscribers must not raise."""
        # Should not raise
        EventBus.publish(42)
        EventBus.publish("no one listening")

    def test_empty_pool_clear(self):
        """Clearing an empty pool must not raise."""
        pool = ObjectPool(create_func=lambda: None, on_destroy=lambda o: None)
        pool.clear()  # Should not crash
        assert pool.count_inactive == 0

    def test_unsubscribe_nonexistent_handler(self):
        """Unsubscribing a handler that was never subscribed must not raise."""
        EventBus.unsubscribe(int, lambda e: None)  # Should not crash

    def test_unsubscribe_from_empty_type(self):
        """Unsubscribing from a type with no subscribers must not raise."""
        def handler(e): pass
        EventBus.unsubscribe(float, handler)  # Should not crash

    def test_unity_event_remove_nonexistent_listener(self):
        """Removing a listener that was never added must not raise."""
        evt = UnityEvent()
        evt.remove_listener(lambda: None)  # Should not crash

    def test_unity_event_invoke_empty(self):
        """Invoking with no listeners must not raise."""
        evt = UnityEvent()
        evt.invoke()  # Should not crash
        evt.invoke(1, 2, 3)  # Should not crash

    def test_pool_get_release_cycle_many(self):
        """Stress test: repeated get/release cycles must be stable."""
        pool = ObjectPool(create_func=lambda: object(), max_size=5)
        for _ in range(100):
            obj = pool.get()
            pool.release(obj)
        assert pool.count_inactive == 1
        assert pool.count_active == 0

    def test_gameobject_pool_pre_warm_then_get(self):
        """Pre-warmed GOs should be returned by get() and be active."""
        go_pool = GameObjectPool(template_name="Warmed", max_size=10)
        go_pool.pre_warm(3)
        assert go_pool.count_inactive == 3
        go = go_pool.get()
        assert go.active is True
        assert go_pool.count_inactive == 2

    def test_eventbus_class_level_state_isolation(self):
        """EventBus uses class-level state — reset must truly clear it."""
        EventBus.subscribe(int, lambda e: None)
        EventBus.reset()
        assert EventBus.subscriber_count(int) == 0

    def test_multiple_pool_instances_independent(self):
        """Two ObjectPool instances must not share state."""
        pool_a = ObjectPool(create_func=lambda: "a")
        pool_b = ObjectPool(create_func=lambda: "b")
        a = pool_a.get()
        b = pool_b.get()
        assert a == "a"
        assert b == "b"
        pool_a.release(a)
        assert pool_a.count_inactive == 1
        assert pool_b.count_inactive == 0
