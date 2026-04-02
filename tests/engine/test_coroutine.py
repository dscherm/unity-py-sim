"""Tests for coroutine system — WaitForSeconds, WaitUntil, nested coroutines."""

import pytest

from src.engine.core import GameObject, MonoBehaviour, _clear_registry
from src.engine.coroutine import (
    Coroutine, CoroutineManager,
    WaitForSeconds, WaitForSecondsRealtime, WaitForEndOfFrame,
    WaitForFixedUpdate, WaitUntil, WaitWhile,
)


@pytest.fixture(autouse=True)
def reset():
    yield
    _clear_registry()


class TestWaitInstructions:
    def test_wait_for_seconds(self):
        w = WaitForSeconds(1.0)
        assert not w.is_done(0.5)
        assert w.is_done(0.5)

    def test_wait_for_seconds_realtime(self):
        w = WaitForSecondsRealtime(0.5)
        assert not w.is_done(0.3)
        assert w.is_done(0.3)

    def test_wait_for_end_of_frame(self):
        w = WaitForEndOfFrame()
        assert w.is_done(0.016)

    def test_wait_for_fixed_update(self):
        w = WaitForFixedUpdate()
        assert not w.is_done(0.02)  # First tick: not done
        assert w.is_done(0.02)      # Second tick: done

    def test_wait_until(self):
        flag = [False]
        w = WaitUntil(lambda: flag[0])
        assert not w.is_done(0.016)
        flag[0] = True
        assert w.is_done(0.016)

    def test_wait_while(self):
        flag = [True]
        w = WaitWhile(lambda: flag[0])
        assert not w.is_done(0.016)
        flag[0] = False
        assert w.is_done(0.016)


class TestCoroutineManager:
    def test_simple_coroutine_runs_to_completion(self):
        results = []

        def my_coroutine():
            results.append("step1")
            yield None
            results.append("step2")
            yield None
            results.append("step3")

        mgr = CoroutineManager()
        co = mgr.start_coroutine(None, my_coroutine())

        # start_coroutine ticks once immediately (to first yield)
        assert results == ["step1"]

        mgr.tick(0.016)
        assert results == ["step1", "step2"]

        mgr.tick(0.016)
        assert results == ["step1", "step2", "step3"]
        assert co.is_finished

    def test_wait_for_seconds_in_coroutine(self):
        results = []

        def timed_coroutine():
            results.append("before")
            yield WaitForSeconds(1.0)
            results.append("after")

        mgr = CoroutineManager()
        co = mgr.start_coroutine(None, timed_coroutine())
        assert results == ["before"]

        # Not enough time
        mgr.tick(0.5)
        assert results == ["before"]

        # Now enough
        mgr.tick(0.5)
        assert "after" in results

    def test_stop_coroutine(self):
        results = []

        def long_coroutine():
            results.append("step1")
            yield None
            results.append("step2")
            yield None
            results.append("step3")

        mgr = CoroutineManager()
        co = mgr.start_coroutine(None, long_coroutine())
        assert results == ["step1"]

        mgr.stop_coroutine(co)
        mgr.tick(0.016)
        assert results == ["step1"]  # step2 never runs

    def test_stop_all_coroutines(self):
        results = []
        owner = object()

        def co1():
            results.append("a1")
            yield None
            results.append("a2")

        def co2():
            results.append("b1")
            yield None
            results.append("b2")

        mgr = CoroutineManager()
        mgr.start_coroutine(owner, co1())
        mgr.start_coroutine(owner, co2())
        assert results == ["a1", "b1"]

        mgr.stop_all_coroutines(owner)
        mgr.tick(0.016)
        assert results == ["a1", "b1"]

    def test_wait_until_in_coroutine(self):
        flag = [False]
        results = []

        def conditional():
            results.append("waiting")
            yield WaitUntil(lambda: flag[0])
            results.append("done")

        mgr = CoroutineManager()
        mgr.start_coroutine(None, conditional())
        assert results == ["waiting"]

        mgr.tick(0.016)
        assert results == ["waiting"]

        flag[0] = True
        mgr.tick(0.016)
        assert "done" in results

    def test_nested_coroutine(self):
        results = []

        def inner():
            results.append("inner_start")
            yield WaitForSeconds(0.5)
            results.append("inner_end")

        def outer():
            results.append("outer_start")
            mgr = CoroutineManager()
            inner_co = Coroutine(inner())
            inner_co.tick(0.0)  # advance to first yield
            yield inner_co
            results.append("outer_end")

        mgr = CoroutineManager()
        mgr.start_coroutine(None, outer())
        assert "outer_start" in results
        assert "inner_start" in results

        # Inner not done yet
        mgr.tick(0.3)
        assert "inner_end" not in results

        # Tick inner manually (in real usage the manager handles this)
        # For the nested case, inner_co needs to be ticked
        # Let's test via MonoBehaviour instead


class TestMonoBehaviourCoroutines:
    def test_start_coroutine_on_behaviour(self):
        results = []

        class MyBehaviour(MonoBehaviour):
            def start(self):
                self.start_coroutine(self.my_routine())

            def my_routine(self):
                results.append("step1")
                yield None
                results.append("step2")

        go = GameObject("Test")
        comp = go.add_component(MyBehaviour)
        comp.start()

        assert results == ["step1"]

        # Tick the coroutine manager
        MonoBehaviour._coroutine_manager.tick(0.016)
        assert results == ["step1", "step2"]

    def test_stop_all_on_behaviour(self):
        results = []

        class MyBehaviour(MonoBehaviour):
            def my_routine(self):
                results.append("started")
                yield None
                results.append("should_not_run")

        go = GameObject("Test")
        comp = go.add_component(MyBehaviour)
        comp.start_coroutine(comp.my_routine())
        assert results == ["started"]

        comp.stop_all_coroutines()
        MonoBehaviour._coroutine_manager.tick(0.016)
        assert results == ["started"]

    def test_wait_for_seconds_via_behaviour(self):
        results = []

        class TimedBehaviour(MonoBehaviour):
            def my_routine(self):
                results.append("before")
                yield WaitForSeconds(1.0)
                results.append("after")

        go = GameObject("Test")
        comp = go.add_component(TimedBehaviour)
        comp.start_coroutine(comp.my_routine())

        mgr = MonoBehaviour._coroutine_manager
        mgr.tick(0.5)
        assert results == ["before"]

        mgr.tick(0.5)
        assert "after" in results

    def test_nested_coroutine_via_behaviour(self):
        results = []

        class NestedBehaviour(MonoBehaviour):
            def outer(self):
                results.append("outer_start")
                yield self.start_coroutine(self.inner())
                results.append("outer_end")

            def inner(self):
                results.append("inner_start")
                yield None
                results.append("inner_end")

        go = GameObject("Test")
        comp = go.add_component(NestedBehaviour)
        comp.start_coroutine(comp.outer())
        assert "outer_start" in results
        assert "inner_start" in results

        mgr = MonoBehaviour._coroutine_manager
        mgr.tick(0.016)  # inner finishes
        assert "inner_end" in results

        mgr.tick(0.016)  # outer resumes
        assert "outer_end" in results
