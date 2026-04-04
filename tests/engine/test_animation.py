"""Tests for AnimationClip and SpriteAnimator."""

import pytest

from src.engine.animation import AnimationClip, SpriteAnimator, LoopMode
from src.engine.core import GameObject
from src.engine.time_manager import Time


@pytest.fixture(autouse=True)
def _reset_time():
    Time._delta_time = 0.0
    Time._time_scale = 1.0
    yield
    Time._delta_time = 0.0
    Time._time_scale = 1.0


def _make_animator(frames=None, fps=4.0, loop_mode=LoopMode.LOOP, clip_name="test"):
    """Helper: create a GameObject with a SpriteAnimator and one clip."""
    if frames is None:
        frames = [{"color": (255, 0, 0)}, {"color": (0, 255, 0)}, {"color": (0, 0, 255)}]
    clip = AnimationClip(clip_name, frames=frames, fps=fps, loop_mode=loop_mode)
    go = GameObject("AnimObj")
    animator = go.add_component(SpriteAnimator)
    animator.add_clip(clip)
    return animator, clip


class TestAnimationClip:
    def test_creation_stores_properties(self):
        clip = AnimationClip("walk", frames=[{"color": (1, 2, 3)}], fps=10, loop_mode=LoopMode.ONCE)
        assert clip.name == "walk"
        assert clip.fps == 10
        assert clip.loop_mode == LoopMode.ONCE
        assert clip.frame_count == 1

    def test_frame_count(self):
        clip = AnimationClip("idle", frames=[{}, {}, {}, {}])
        assert clip.frame_count == 4

    def test_duration_calculation(self):
        clip = AnimationClip("run", frames=[{}, {}, {}, {}], fps=2.0)
        assert clip.duration == pytest.approx(2.0)

    def test_duration_zero_fps(self):
        clip = AnimationClip("x", frames=[{}], fps=0)
        assert clip.duration == 0

    def test_on_frame_registers_callback(self):
        clip = AnimationClip("a", frames=[{}, {}])
        called = []
        clip.on_frame(0, lambda: called.append(True))
        assert 0 in clip._events
        assert len(clip._events[0]) == 1


class TestSpriteAnimator:
    def test_play_sets_state(self):
        animator, _ = _make_animator()
        assert not animator.is_playing
        animator.play("test")
        assert animator.is_playing
        assert animator.current_clip == "test"
        assert animator.frame_index == 0

    def test_stop(self):
        animator, _ = _make_animator()
        animator.play("test")
        animator.stop()
        assert not animator.is_playing

    def test_play_unknown_clip_no_op(self):
        animator, _ = _make_animator()
        animator.play("nonexistent")
        assert not animator.is_playing

    def test_frame_advancement_loop(self):
        animator, _ = _make_animator(fps=4.0, loop_mode=LoopMode.LOOP)
        animator.play("test")
        assert animator.frame_index == 0
        # Advance 0.25s = exactly 1 frame at 4fps
        Time._delta_time = 0.25
        animator.update()
        assert animator.frame_index == 1

    def test_loop_mode_wraps(self):
        frames = [{"color": (1,)}, {"color": (2,)}, {"color": (3,)}]
        animator, _ = _make_animator(frames=frames, fps=4.0, loop_mode=LoopMode.LOOP)
        animator.play("test")
        # Advance 3 frames (0.75s at 4fps) -> should wrap to 0
        Time._delta_time = 0.75
        animator.update()
        assert animator.frame_index == 0
        assert animator.is_playing

    def test_once_mode_stops_at_end(self):
        frames = [{"color": (1,)}, {"color": (2,)}]
        animator, _ = _make_animator(frames=frames, fps=4.0, loop_mode=LoopMode.ONCE)
        animator.play("test")
        # Advance 2 frames -> should stop
        Time._delta_time = 0.5
        animator.update()
        assert not animator.is_playing

    def test_ping_pong_reverses(self):
        frames = [{"color": (1,)}, {"color": (2,)}, {"color": (3,)}]
        animator, _ = _make_animator(frames=frames, fps=4.0, loop_mode=LoopMode.PING_PONG)
        animator.play("test")
        # Advance to frame 2 (last), then should reverse
        Time._delta_time = 0.25
        animator.update()  # frame 1
        animator.update()  # frame 2
        animator.update()  # should reverse -> frame 1
        assert animator.frame_index == 1
        assert animator.is_playing

    def test_clip_switching(self):
        go = GameObject("AnimObj")
        animator = go.add_component(SpriteAnimator)
        clip_a = AnimationClip("a", frames=[{"color": (1,)}, {"color": (2,)}], fps=4)
        clip_b = AnimationClip("b", frames=[{"color": (3,)}, {"color": (4,)}], fps=4)
        animator.add_clip(clip_a)
        animator.add_clip(clip_b)

        animator.play("a")
        assert animator.current_clip == "a"
        animator.play("b")
        assert animator.current_clip == "b"
        assert animator.frame_index == 0

    def test_frame_callback_fires(self):
        called = []
        frames = [{"color": (1,)}, {"color": (2,)}]
        clip = AnimationClip("cb", frames=frames, fps=4.0, loop_mode=LoopMode.LOOP)
        clip.on_frame(1, lambda: called.append("hit"))

        go = GameObject("AnimObj")
        animator = go.add_component(SpriteAnimator)
        animator.add_clip(clip)
        animator.play("cb")

        Time._delta_time = 0.25
        animator.update()  # advance to frame 1
        assert "hit" in called

    def test_no_update_when_stopped(self):
        animator, _ = _make_animator(fps=4.0)
        animator.play("test")
        animator.stop()
        Time._delta_time = 1.0
        animator.update()
        assert animator.frame_index == 0
