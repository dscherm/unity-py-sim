"""Tests for Tween, Sequence, and TweenManager."""

import pytest

from src.engine.tweening import (
    Tween, Sequence, TweenManager, Ease, LoopType, evaluate_ease,
)


@pytest.fixture(autouse=True)
def _reset_tween_manager():
    TweenManager.reset()
    yield
    TweenManager.reset()


class _Obj:
    """Simple target for property animation."""
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


class TestEasing:
    def test_linear_zero_and_one(self):
        assert evaluate_ease(Ease.LINEAR, 0.0) == pytest.approx(0.0)
        assert evaluate_ease(Ease.LINEAR, 1.0) == pytest.approx(1.0)

    def test_in_out_quad_midpoint(self):
        val = evaluate_ease(Ease.IN_OUT_QUAD, 0.5)
        assert val == pytest.approx(0.5)

    def test_in_out_quad_start_end(self):
        assert evaluate_ease(Ease.IN_OUT_QUAD, 0.0) == pytest.approx(0.0)
        assert evaluate_ease(Ease.IN_OUT_QUAD, 1.0) == pytest.approx(1.0)

    def test_clamps_input(self):
        assert evaluate_ease(Ease.LINEAR, -1.0) == pytest.approx(0.0)
        assert evaluate_ease(Ease.LINEAR, 2.0) == pytest.approx(1.0)


class TestTween:
    def test_to_creates_and_interpolates(self):
        obj = _Obj(x=0.0)
        tw = Tween.to(obj, "x", 10.0, duration=1.0)
        TweenManager.tick(0.5)
        assert obj.x == pytest.approx(5.0)

    def test_tween_completes(self):
        obj = _Obj(x=0.0)
        tw = Tween.to(obj, "x", 10.0, duration=1.0)
        TweenManager.tick(1.0)
        assert tw.is_complete
        assert obj.x == pytest.approx(10.0)

    def test_on_start_callback(self):
        called = []
        obj = _Obj(x=0.0)
        Tween.to(obj, "x", 5.0, 1.0).on_start(lambda: called.append(True))
        TweenManager.tick(0.1)
        assert called

    def test_on_complete_callback(self):
        called = []
        obj = _Obj(x=0.0)
        Tween.to(obj, "x", 5.0, 1.0).on_complete(lambda: called.append(True))
        TweenManager.tick(1.0)
        assert called

    def test_kill(self):
        obj = _Obj(x=0.0)
        tw = Tween.to(obj, "x", 10.0, 1.0)
        tw.kill()
        TweenManager.tick(0.5)
        assert obj.x == pytest.approx(0.0)  # never started / no progress
        assert not tw.is_active

    def test_pause_resume(self):
        obj = _Obj(x=0.0)
        tw = Tween.to(obj, "x", 10.0, 1.0)
        TweenManager.tick(0.25)
        tw.pause()
        val_at_pause = obj.x
        TweenManager.tick(0.5)
        assert obj.x == pytest.approx(val_at_pause)  # no change while paused
        tw.resume()
        TweenManager.tick(0.25)
        assert obj.x > val_at_pause

    def test_ease_in_out_quad(self):
        obj = _Obj(x=0.0)
        Tween.to(obj, "x", 10.0, 1.0).set_ease(Ease.IN_OUT_QUAD)
        TweenManager.tick(0.5)
        assert obj.x == pytest.approx(5.0)

    def test_loop_restart(self):
        obj = _Obj(x=0.0)
        tw = Tween.to(obj, "x", 10.0, 1.0).set_loops(2, LoopType.RESTART)
        TweenManager.tick(1.0)  # end of first loop
        assert not tw.is_complete
        # After restart, property should reset to start
        assert obj.x == pytest.approx(0.0)
        TweenManager.tick(1.0)  # second loop done
        assert tw.is_complete

    def test_loop_yoyo(self):
        obj = _Obj(x=0.0)
        tw = Tween.to(obj, "x", 10.0, 1.0).set_loops(2, LoopType.YOYO)
        TweenManager.tick(1.0)  # first loop complete, yoyo starts
        assert not tw.is_complete
        TweenManager.tick(0.5)  # halfway back
        assert obj.x == pytest.approx(5.0)

    def test_tween_manager_tick_removes_completed(self):
        obj = _Obj(x=0.0)
        Tween.to(obj, "x", 10.0, 0.5)
        assert TweenManager.active_count() == 1
        TweenManager.tick(0.5)
        assert TweenManager.active_count() == 0

    def test_tween_manager_kill_all(self):
        obj = _Obj(x=0.0)
        Tween.to(obj, "x", 5.0, 1.0)
        Tween.to(obj, "x", 10.0, 2.0)
        assert TweenManager.active_count() == 2
        TweenManager.kill_all()
        assert TweenManager.active_count() == 0


class TestSequence:
    def test_append_plays_sequentially(self):
        a = _Obj(x=0.0)
        b = _Obj(x=0.0)
        seq = Sequence()
        seq.append(Tween.to(a, "x", 10.0, 1.0))
        seq.append(Tween.to(b, "x", 20.0, 1.0))
        seq.play()

        TweenManager.tick(1.0)
        assert a.x == pytest.approx(10.0)
        assert b.x == pytest.approx(0.0)  # second hasn't started yet

        TweenManager.tick(1.0)
        assert b.x == pytest.approx(20.0)

    def test_join_plays_in_parallel(self):
        a = _Obj(x=0.0)
        b = _Obj(x=0.0)
        seq = Sequence()
        seq.append(Tween.to(a, "x", 10.0, 1.0))
        seq.join(Tween.to(b, "x", 20.0, 1.0))
        seq.play()

        TweenManager.tick(1.0)
        assert a.x == pytest.approx(10.0)
        assert b.x == pytest.approx(20.0)

    def test_sequence_on_complete(self):
        called = []
        a = _Obj(x=0.0)
        seq = Sequence()
        seq.append(Tween.to(a, "x", 5.0, 0.5))
        seq.on_complete(lambda: called.append(True))
        seq.play()

        TweenManager.tick(0.5)
        assert called
