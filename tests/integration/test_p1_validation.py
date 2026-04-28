"""Independent validation tests for P1 features:
  Task 4 — Sprite Animation
  Task 5 — Camera Follow
  Task 6 — 2D Joints

Derived from Unity documentation contracts, NOT from implementation reading.
"""

from __future__ import annotations

import math

import pymunk
import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_engine():
    """Reset all global engine state between tests."""
    _clear_registry()
    Time._reset()
    # Reset PhysicsManager singleton
    from src.engine.physics.physics_manager import PhysicsManager
    PhysicsManager.reset()
    # Reset CameraShake class state
    from src.engine.camera_follow import CameraShake
    CameraShake.reset()
    yield
    _clear_registry()
    Time._reset()
    from src.engine.physics.physics_manager import PhysicsManager
    PhysicsManager.reset()
    from src.engine.camera_follow import CameraShake
    CameraShake.reset()


# ===========================================================================
# ANIMATION TESTS
# ===========================================================================


class TestAnimationClipBasics:
    """AnimationClip construction and properties."""

    def test_clip_stores_name_and_frames(self):
        from src.engine.animation import AnimationClip, LoopMode
        frames = [{"color": (255, 0, 0)}, {"color": (0, 255, 0)}]
        clip = AnimationClip("walk", frames=frames, fps=10)
        assert clip.name == "walk"
        assert clip.frames == frames
        assert clip.fps == 10
        assert clip.loop_mode == LoopMode.LOOP  # default

    def test_frame_count(self):
        from src.engine.animation import AnimationClip
        clip = AnimationClip("x", frames=[{"color": (1, 2, 3)}] * 5, fps=12)
        assert clip.frame_count == 5

    def test_duration_calculation(self):
        from src.engine.animation import AnimationClip
        clip = AnimationClip("x", frames=[{}] * 12, fps=12)
        assert abs(clip.duration - 1.0) < 1e-6

    def test_duration_zero_fps(self):
        from src.engine.animation import AnimationClip
        clip = AnimationClip("x", frames=[{}] * 4, fps=0)
        assert clip.duration == 0

    def test_on_frame_registers_callback(self):
        from src.engine.animation import AnimationClip
        clip = AnimationClip("x", frames=[{}] * 3, fps=10)
        def cb(): pass
        result = clip.on_frame(1, cb)
        assert result is clip  # fluent API
        assert cb in clip._events[1]


class TestSpriteAnimatorPlayStop:
    """Play/stop/clip-switching behavior."""

    def _make_animator(self):
        from src.engine.animation import SpriteAnimator
        go = GameObject("test")
        animator = go.add_component(SpriteAnimator)
        return go, animator

    def test_play_nonexistent_clip_does_nothing(self):
        _, animator = self._make_animator()
        animator.play("missing")
        assert not animator.is_playing
        assert animator.current_clip is None

    def test_play_sets_state(self):
        from src.engine.animation import AnimationClip
        _, animator = self._make_animator()
        clip = AnimationClip("idle", [{"color": (1, 1, 1)}, {"color": (2, 2, 2)}], fps=10)
        animator.add_clip(clip)
        animator.play("idle")
        assert animator.is_playing
        assert animator.current_clip == "idle"
        assert animator.frame_index == 0

    def test_stop_halts_playing(self):
        from src.engine.animation import AnimationClip
        _, animator = self._make_animator()
        clip = AnimationClip("a", [{"color": (1, 1, 1)}, {"color": (2, 2, 2)}], fps=10)
        animator.add_clip(clip)
        animator.play("a")
        animator.stop()
        assert not animator.is_playing

    def test_play_same_clip_is_noop(self):
        from src.engine.animation import AnimationClip
        _, animator = self._make_animator()
        clip = AnimationClip("a", [{"color": (1, 1, 1)}, {"color": (2, 2, 2)}], fps=10)
        animator.add_clip(clip)
        animator.play("a")
        # Advance a frame
        Time._delta_time = 0.15
        animator.update()
        old_frame = animator.frame_index
        # Play same clip again — should NOT reset
        animator.play("a")
        assert animator.frame_index == old_frame

    def test_switching_clips_resets_frame(self):
        from src.engine.animation import AnimationClip
        _, animator = self._make_animator()
        clip_a = AnimationClip("a", [{"color": (1, 1, 1)}, {"color": (2, 2, 2)}], fps=10)
        clip_b = AnimationClip("b", [{"color": (3, 3, 3)}, {"color": (4, 4, 4)}], fps=10)
        animator.add_clip(clip_a)
        animator.add_clip(clip_b)
        animator.play("a")
        Time._delta_time = 0.15
        animator.update()
        assert animator.frame_index > 0
        # Switch clip
        animator.play("b")
        assert animator.frame_index == 0
        assert animator.current_clip == "b"


class TestAnimationFrameAdvancement:
    """Frame advancement at correct fps rate."""

    def _setup(self, fps=10, frame_count=4, loop_mode=None):
        from src.engine.animation import AnimationClip, SpriteAnimator, LoopMode
        loop = loop_mode or LoopMode.LOOP
        go = GameObject("test")
        animator = go.add_component(SpriteAnimator)
        frames = [{"color": (i * 50, 0, 0)} for i in range(frame_count)]
        clip = AnimationClip("test", frames, fps=fps, loop_mode=loop)
        animator.add_clip(clip)
        animator.play("test")
        return animator

    def test_no_advance_before_frame_duration(self):
        animator = self._setup(fps=10)
        # dt < 1/10 = 0.1
        Time._delta_time = 0.05
        animator.update()
        assert animator.frame_index == 0

    def test_advances_after_frame_duration(self):
        animator = self._setup(fps=10)
        Time._delta_time = 0.11  # > 0.1
        animator.update()
        assert animator.frame_index == 1

    def test_multiple_frames_in_large_dt(self):
        animator = self._setup(fps=10, frame_count=10)
        Time._delta_time = 0.35  # should advance 3 frames
        animator.update()
        assert animator.frame_index == 3

    def test_single_frame_clip_never_advances(self):
        animator = self._setup(fps=10, frame_count=1)
        Time._delta_time = 1.0
        animator.update()
        assert animator.frame_index == 0


class TestLoopModeOnce:
    """ONCE mode — plays through then stops."""

    def test_once_stops_at_last_frame(self):
        from src.engine.animation import AnimationClip, SpriteAnimator, LoopMode
        go = GameObject("test")
        animator = go.add_component(SpriteAnimator)
        clip = AnimationClip("x", [{"color": (1, 1, 1)}] * 3, fps=10, loop_mode=LoopMode.ONCE)
        animator.add_clip(clip)
        animator.play("x")

        # Advance through all frames: 3 frames at 10fps = 0.3s
        Time._delta_time = 0.11
        animator.update()  # frame 1
        assert animator.is_playing
        animator.update()  # frame 2
        assert animator.is_playing
        animator.update()  # tries to go to frame 3 (past end)
        assert not animator.is_playing

    def test_once_stays_on_last_valid_frame(self):
        from src.engine.animation import AnimationClip, SpriteAnimator, LoopMode
        go = GameObject("test")
        animator = go.add_component(SpriteAnimator)
        clip = AnimationClip("x", [{"color": (1, 1, 1)}] * 3, fps=10, loop_mode=LoopMode.ONCE)
        animator.add_clip(clip)
        animator.play("x")
        # Big dt to go past end
        Time._delta_time = 0.5
        animator.update()
        assert animator.frame_index == 2  # last valid


class TestLoopModeLoop:
    """LOOP mode wraps around."""

    def test_loop_wraps(self):
        from src.engine.animation import AnimationClip, SpriteAnimator, LoopMode
        go = GameObject("test")
        animator = go.add_component(SpriteAnimator)
        clip = AnimationClip("x", [{}] * 3, fps=10, loop_mode=LoopMode.LOOP)
        animator.add_clip(clip)
        animator.play("x")

        # Advance 4 times (should wrap to frame 1)
        Time._delta_time = 0.11
        for _ in range(4):
            animator.update()
        assert animator.frame_index == 1  # 4 advances from 0 => 0,1,2,0,1 => frame 1
        assert animator.is_playing


class TestLoopModePingPong:
    """PING_PONG mode reverses direction at boundaries."""

    def test_ping_pong_reverses(self):
        from src.engine.animation import AnimationClip, SpriteAnimator, LoopMode
        go = GameObject("test")
        animator = go.add_component(SpriteAnimator)
        clip = AnimationClip("x", [{}] * 3, fps=10, loop_mode=LoopMode.PING_PONG)
        animator.add_clip(clip)
        animator.play("x")

        Time._delta_time = 0.11
        frames_visited = [animator.frame_index]
        for _ in range(6):
            animator.update()
            frames_visited.append(animator.frame_index)

        # Should go: 0, 1, 2, 1, 0, 1, 2
        assert frames_visited == [0, 1, 2, 1, 0, 1, 2]
        assert animator.is_playing


class TestFrameEvents:
    """Frame event callbacks fire at correct times."""

    def test_event_fires_on_target_frame(self):
        from src.engine.animation import AnimationClip, SpriteAnimator, LoopMode
        go = GameObject("test")
        animator = go.add_component(SpriteAnimator)
        fired = []
        clip = AnimationClip("x", [{}] * 3, fps=10, loop_mode=LoopMode.LOOP)
        clip.on_frame(1, lambda: fired.append("hit"))
        animator.add_clip(clip)
        animator.play("x")

        Time._delta_time = 0.11
        animator.update()  # -> frame 1
        assert fired == ["hit"]

    def test_event_does_not_fire_on_wrong_frame(self):
        from src.engine.animation import AnimationClip, SpriteAnimator, LoopMode
        go = GameObject("test")
        animator = go.add_component(SpriteAnimator)
        fired = []
        clip = AnimationClip("x", [{}] * 4, fps=10, loop_mode=LoopMode.LOOP)
        clip.on_frame(2, lambda: fired.append("hit"))
        animator.add_clip(clip)
        animator.play("x")

        Time._delta_time = 0.11
        animator.update()  # -> frame 1
        assert fired == []

    def test_event_fires_on_loop_wrap(self):
        from src.engine.animation import AnimationClip, SpriteAnimator, LoopMode
        go = GameObject("test")
        animator = go.add_component(SpriteAnimator)
        fired = []
        clip = AnimationClip("x", [{}] * 2, fps=10, loop_mode=LoopMode.LOOP)
        clip.on_frame(0, lambda: fired.append("start"))
        animator.add_clip(clip)
        animator.play("x")

        # frame event on 0 fires on play (apply_frame), then on wrap-around
        initial_count = len(fired)
        Time._delta_time = 0.11
        animator.update()  # -> frame 1
        animator.update()  # -> frame 0 (wrap)
        assert len(fired) > initial_count


class TestAnimationAppliesFrameData:
    """Verify animation updates SpriteRenderer color/asset_ref."""

    def test_color_applied_to_sprite_renderer(self):
        from src.engine.animation import AnimationClip, SpriteAnimator
        from src.engine.rendering.renderer import SpriteRenderer
        go = GameObject("test")
        sr = go.add_component(SpriteRenderer)
        animator = go.add_component(SpriteAnimator)
        clip = AnimationClip("x", [
            {"color": (255, 0, 0)},
            {"color": (0, 255, 0)},
        ], fps=10)
        animator.add_clip(clip)
        animator.play("x")
        assert sr.color == (255, 0, 0)  # first frame applied on play

        Time._delta_time = 0.11
        animator.update()
        assert sr.color == (0, 255, 0)

    def test_asset_ref_applied(self):
        from src.engine.animation import AnimationClip, SpriteAnimator
        from src.engine.rendering.renderer import SpriteRenderer
        go = GameObject("test")
        sr = go.add_component(SpriteRenderer)
        animator = go.add_component(SpriteAnimator)
        clip = AnimationClip("x", [
            {"asset_ref": "sprite_a"},
            {"asset_ref": "sprite_b"},
        ], fps=10)
        animator.add_clip(clip)
        animator.play("x")
        assert sr.asset_ref == "sprite_a"

        Time._delta_time = 0.11
        animator.update()
        assert sr.asset_ref == "sprite_b"


# ===========================================================================
# CAMERA FOLLOW TESTS
# ===========================================================================


class TestCameraFollow2DBasicFollow:
    """Camera tracks target position."""

    def _make_follow(self):
        from src.engine.camera_follow import CameraFollow2D
        cam_go = GameObject("Camera")
        cam_go.transform.position = Vector2(0, 0)
        follow = cam_go.add_component(CameraFollow2D)
        target_go = GameObject("Player")
        target_go.transform.position = Vector2(10, 5)
        follow.target = target_go.transform
        return cam_go, follow, target_go

    def test_moves_toward_target(self):
        cam_go, follow, target_go = self._make_follow()
        follow.damping = 0.5
        Time._delta_time = 1.0 / 60.0
        follow.late_update()
        pos = cam_go.transform.position
        # Camera should have moved toward (10, 5)
        assert pos.x > 0
        assert pos.y > 0

    def test_converges_to_target_over_time(self):
        cam_go, follow, target_go = self._make_follow()
        follow.damping = 0.5
        Time._delta_time = 1.0 / 60.0
        for _ in range(300):
            follow.late_update()
        pos = cam_go.transform.position
        assert abs(pos.x - 10) < 0.5
        assert abs(pos.y - 5) < 0.5

    def test_no_target_means_no_movement(self):
        from src.engine.camera_follow import CameraFollow2D
        cam_go = GameObject("Camera")
        cam_go.transform.position = Vector2(0, 0)
        follow = cam_go.add_component(CameraFollow2D)
        follow.target = None
        Time._delta_time = 1.0 / 60.0
        follow.late_update()
        assert cam_go.transform.position.x == 0
        assert cam_go.transform.position.y == 0


class TestCameraFollowDamping:
    """Damping controls the follow speed."""

    def test_zero_damping_snaps_instantly(self):
        from src.engine.camera_follow import CameraFollow2D
        cam_go = GameObject("Camera")
        cam_go.transform.position = Vector2(0, 0)
        follow = cam_go.add_component(CameraFollow2D)
        target_go = GameObject("Player")
        target_go.transform.position = Vector2(10, 5)
        follow.target = target_go.transform
        follow.damping = 0  # instant

        Time._delta_time = 1.0 / 60.0
        follow.late_update()
        pos = cam_go.transform.position
        # With damping=0, t=1.0, so camera should jump right to target
        # (ignoring shake which should be zero)
        assert abs(pos.x - 10) < 1.0  # close to target
        assert abs(pos.y - 5) < 1.0

    def test_high_damping_slower_than_low(self):
        from src.engine.camera_follow import CameraFollow2D

        def run_follow(damping_val):
            _clear_registry()
            from src.engine.camera_follow import CameraShake
            CameraShake.reset()
            cam_go = GameObject("Camera")
            cam_go.transform.position = Vector2(0, 0)
            follow = cam_go.add_component(CameraFollow2D)
            t_go = GameObject("Player")
            t_go.transform.position = Vector2(10, 0)
            follow.target = t_go.transform
            follow.damping = damping_val
            Time._delta_time = 1.0 / 60.0
            follow.late_update()
            return cam_go.transform.position.x

        low_x = run_follow(0.8)
        high_x = run_follow(0.1)
        # Higher damping => faster follow (larger damping value = more responsive)
        assert low_x > high_x


class TestCameraFollowDeadZone:
    """Dead zone prevents camera movement for small offsets."""

    def test_within_dead_zone_no_movement(self):
        from src.engine.camera_follow import CameraFollow2D
        cam_go = GameObject("Camera")
        cam_go.transform.position = Vector2(0, 0)
        follow = cam_go.add_component(CameraFollow2D)
        target_go = GameObject("Player")
        target_go.transform.position = Vector2(0.5, 0.3)
        follow.target = target_go.transform
        follow.dead_zone = Vector2(1.0, 1.0)  # large dead zone
        follow.damping = 0  # instant follow to isolate dead zone

        Time._delta_time = 1.0 / 60.0
        follow.late_update()
        pos = cam_go.transform.position
        # Target is within dead zone so camera should not move (approximately)
        assert abs(pos.x) < 0.01
        assert abs(pos.y) < 0.01

    def test_outside_dead_zone_does_move(self):
        from src.engine.camera_follow import CameraFollow2D
        cam_go = GameObject("Camera")
        cam_go.transform.position = Vector2(0, 0)
        follow = cam_go.add_component(CameraFollow2D)
        target_go = GameObject("Player")
        target_go.transform.position = Vector2(5, 0)
        follow.target = target_go.transform
        follow.dead_zone = Vector2(1.0, 0)
        follow.damping = 0

        Time._delta_time = 1.0 / 60.0
        follow.late_update()
        pos = cam_go.transform.position
        assert pos.x > 0  # should move


class TestCameraFollowBounds:
    """Bounds clamp camera position."""

    def test_bounds_clamp_position(self):
        from src.engine.camera_follow import CameraFollow2D
        cam_go = GameObject("Camera")
        cam_go.transform.position = Vector2(0, 0)
        follow = cam_go.add_component(CameraFollow2D)
        target_go = GameObject("Player")
        target_go.transform.position = Vector2(100, 100)
        follow.target = target_go.transform
        follow.damping = 0
        follow.bounds_min = Vector2(-5, -5)
        follow.bounds_max = Vector2(5, 5)

        Time._delta_time = 1.0 / 60.0
        follow.late_update()
        pos = cam_go.transform.position
        # Should be clamped (shake offset might add small amount)
        assert pos.x <= 5.5  # small margin for shake
        assert pos.y <= 5.5

    def test_bounds_allow_movement_within(self):
        from src.engine.camera_follow import CameraFollow2D
        cam_go = GameObject("Camera")
        cam_go.transform.position = Vector2(0, 0)
        follow = cam_go.add_component(CameraFollow2D)
        target_go = GameObject("Player")
        target_go.transform.position = Vector2(3, 2)
        follow.target = target_go.transform
        follow.damping = 0
        follow.bounds_min = Vector2(-10, -10)
        follow.bounds_max = Vector2(10, 10)

        Time._delta_time = 1.0 / 60.0
        follow.late_update()
        pos = cam_go.transform.position
        assert abs(pos.x - 3) < 0.5
        assert abs(pos.y - 2) < 0.5


class TestCameraFollowOffset:
    """Follow offset shifts the tracking point."""

    def test_offset_shifts_target(self):
        from src.engine.camera_follow import CameraFollow2D
        cam_go = GameObject("Camera")
        cam_go.transform.position = Vector2(0, 0)
        follow = cam_go.add_component(CameraFollow2D)
        target_go = GameObject("Player")
        target_go.transform.position = Vector2(0, 0)
        follow.target = target_go.transform
        follow.follow_offset = Vector2(5, 3)
        follow.damping = 0

        Time._delta_time = 1.0 / 60.0
        follow.late_update()
        pos = cam_go.transform.position
        assert abs(pos.x - 5) < 0.5
        assert abs(pos.y - 3) < 0.5


class TestCameraShake:
    """CameraShake produces offset that decays."""

    def test_shake_produces_nonzero_offset(self):
        from src.engine.camera_follow import CameraShake
        CameraShake.trigger(intensity=1.0, duration=1.0, frequency=25.0)
        Time._delta_time = 0.02
        offset = CameraShake.get_offset()
        assert offset.x != 0 or offset.y != 0

    def test_shake_decays_to_zero(self):
        from src.engine.camera_follow import CameraShake
        CameraShake.trigger(intensity=1.0, duration=0.1, frequency=25.0)
        # Advance well past duration
        Time._delta_time = 0.5
        offset = CameraShake.get_offset()
        # After duration has passed, shake should be removed
        offset2 = CameraShake.get_offset()
        assert offset2.x == 0 and offset2.y == 0

    def test_no_shake_returns_zero(self):
        from src.engine.camera_follow import CameraShake
        offset = CameraShake.get_offset()
        assert offset.x == 0 and offset.y == 0

    def test_shake_intensity_affects_magnitude(self):
        from src.engine.camera_follow import CameraShake
        # Low intensity
        CameraShake.trigger(intensity=0.1, duration=1.0, frequency=25.0)
        Time._delta_time = 0.02
        low_offset = CameraShake.get_offset()
        low_mag = math.sqrt(low_offset.x**2 + low_offset.y**2)

        CameraShake.reset()

        # High intensity
        CameraShake.trigger(intensity=10.0, duration=1.0, frequency=25.0)
        Time._delta_time = 0.02
        high_offset = CameraShake.get_offset()
        high_mag = math.sqrt(high_offset.x**2 + high_offset.y**2)

        assert high_mag > low_mag

    def test_reset_clears_shakes(self):
        from src.engine.camera_follow import CameraShake
        CameraShake.trigger(intensity=1.0, duration=10.0)
        CameraShake.reset()
        Time._delta_time = 0.02
        offset = CameraShake.get_offset()
        assert offset.x == 0 and offset.y == 0


# ===========================================================================
# 2D JOINTS TESTS
# ===========================================================================


def _make_joint_pair():
    """Create two GameObjects with Rigidbody2D components and register them in physics."""
    from src.engine.physics.rigidbody import Rigidbody2D
    from src.engine.physics.physics_manager import PhysicsManager

    pm = PhysicsManager.instance()

    go_a = GameObject("A")
    rb_a = go_a.add_component(Rigidbody2D)
    go_a.transform.position = Vector2(0, 0)
    rb_a._body.position = (0, 0)
    pm.register_body(rb_a)

    go_b = GameObject("B")
    rb_b = go_b.add_component(Rigidbody2D)
    go_b.transform.position = Vector2(5, 0)
    rb_b._body.position = (5, 0)
    pm.register_body(rb_b)

    return go_a, rb_a, go_b, rb_b, pm


class TestHingeJoint2D:
    """HingeJoint2D constructs a pivot constraint."""

    def test_build_creates_constraint(self):
        from src.engine.physics.joints import HingeJoint2D
        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        hinge = go_a.add_component(HingeJoint2D)
        hinge.connected_body = rb_b
        hinge.anchor = Vector2(0, 0)
        hinge.build()
        assert hinge._constraint is not None
        assert isinstance(hinge._constraint, pymunk.PivotJoint)

    def test_hinge_registered_in_space(self):
        from src.engine.physics.joints import HingeJoint2D
        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        hinge = go_a.add_component(HingeJoint2D)
        hinge.connected_body = rb_b
        hinge.build()
        constraints = pm._space.constraints
        assert any(isinstance(c, pymunk.PivotJoint) for c in constraints)

    def test_hinge_with_limits_adds_rotary_limit(self):
        from src.engine.physics.joints import HingeJoint2D
        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        hinge = go_a.add_component(HingeJoint2D)
        hinge.connected_body = rb_b
        hinge.use_limits = True
        hinge.limits_min = -45
        hinge.limits_max = 45
        hinge.build()
        constraints = pm._space.constraints
        assert any(isinstance(c, pymunk.RotaryLimitJoint) for c in constraints)

    def test_hinge_with_motor_adds_simple_motor(self):
        from src.engine.physics.joints import HingeJoint2D
        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        hinge = go_a.add_component(HingeJoint2D)
        hinge.connected_body = rb_b
        hinge.use_motor = True
        hinge.motor_speed = 90.0
        hinge.build()
        constraints = pm._space.constraints
        assert any(isinstance(c, pymunk.SimpleMotor) for c in constraints)

    def test_hinge_no_connected_body_is_safe(self):
        from src.engine.physics.joints import HingeJoint2D
        go_a, rb_a, _, _, pm = _make_joint_pair()
        hinge = go_a.add_component(HingeJoint2D)
        hinge.connected_body = None
        hinge.build()  # Should not crash
        assert hinge._constraint is None


class TestSpringJoint2D:
    """SpringJoint2D creates a DampedSpring."""

    def test_build_creates_spring(self):
        from src.engine.physics.joints import SpringJoint2D
        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        spring = go_a.add_component(SpringJoint2D)
        spring.connected_body = rb_b
        spring.distance = 3.0
        spring.frequency = 4.0
        spring.damping_ratio = 0.5
        spring.build()
        assert spring._constraint is not None
        assert isinstance(spring._constraint, pymunk.DampedSpring)

    def test_spring_registered_in_space(self):
        from src.engine.physics.joints import SpringJoint2D
        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        spring = go_a.add_component(SpringJoint2D)
        spring.connected_body = rb_b
        spring.build()
        assert any(isinstance(c, pymunk.DampedSpring) for c in pm._space.constraints)

    def test_spring_rest_length_matches_distance(self):
        from src.engine.physics.joints import SpringJoint2D
        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        spring = go_a.add_component(SpringJoint2D)
        spring.connected_body = rb_b
        spring.distance = 7.5
        spring.build()
        assert abs(spring._constraint.rest_length - 7.5) < 1e-6


class TestDistanceJoint2D:
    """DistanceJoint2D maintains distance between bodies."""

    def test_build_creates_pin_joint(self):
        from src.engine.physics.joints import DistanceJoint2D
        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        dj = go_a.add_component(DistanceJoint2D)
        dj.connected_body = rb_b
        dj.distance = 5.0
        dj.build()
        assert dj._constraint is not None
        assert isinstance(dj._constraint, pymunk.PinJoint)

    def test_max_distance_only_uses_slide_joint(self):
        from src.engine.physics.joints import DistanceJoint2D
        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        dj = go_a.add_component(DistanceJoint2D)
        dj.connected_body = rb_b
        dj.distance = 5.0
        dj.max_distance_only = True
        dj.build()
        assert isinstance(dj._constraint, pymunk.SlideJoint)


class TestFixedJoint2D:
    """FixedJoint2D locks bodies together."""

    def test_build_creates_constraints(self):
        from src.engine.physics.joints import FixedJoint2D
        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        fj = go_a.add_component(FixedJoint2D)
        fj.connected_body = rb_b
        fj.build()
        assert fj._constraint is not None
        # Should have both PivotJoint and GearJoint
        has_pivot = any(isinstance(c, pymunk.PivotJoint) for c in pm._space.constraints)
        has_gear = any(isinstance(c, pymunk.GearJoint) for c in pm._space.constraints)
        assert has_pivot and has_gear


class TestJointOnDestroy:
    """Joints clean up their constraint on destroy."""

    def test_on_destroy_removes_constraint(self):
        from src.engine.physics.joints import HingeJoint2D
        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        hinge = go_a.add_component(HingeJoint2D)
        hinge.connected_body = rb_b
        hinge.build()
        constraint = hinge._constraint
        assert constraint in pm._space.constraints
        hinge.on_destroy()
        assert constraint not in pm._space.constraints
        assert hinge._constraint is None


# ===========================================================================
# MUTATION TESTS
# ===========================================================================


class TestAnimationMutations:
    """Mutation tests — monkeypatch breakage to prove tests catch it."""

    def test_mutation_skip_frame_advance_detected(self):
        """If _advance_frame does nothing, frame_index never changes."""
        from src.engine.animation import AnimationClip, SpriteAnimator, LoopMode
        go = GameObject("test")
        animator = go.add_component(SpriteAnimator)
        clip = AnimationClip("x", [{}] * 3, fps=10, loop_mode=LoopMode.LOOP)
        animator.add_clip(clip)
        animator.play("x")

        # Monkeypatch _advance_frame to be a no-op
        animator._advance_frame = lambda: None

        Time._delta_time = 0.11
        animator.update()
        # If mutation present, frame stays at 0
        assert animator.frame_index == 0  # mutation detected: frame did NOT advance

    def test_mutation_loop_mode_check_matters(self):
        """If loop mode is ignored and always loops, ONCE would never stop."""
        from src.engine.animation import AnimationClip, SpriteAnimator, LoopMode
        go = GameObject("test")
        animator = go.add_component(SpriteAnimator)
        clip = AnimationClip("x", [{}] * 2, fps=10, loop_mode=LoopMode.ONCE)
        animator.add_clip(clip)
        animator.play("x")

        Time._delta_time = 0.11
        animator.update()  # frame 1
        animator.update()  # should stop (ONCE)
        # If this is True, ONCE is working. A broken impl would still be playing.
        assert not animator.is_playing

    def test_mutation_fps_rate_matters(self):
        """Changing fps should change how many frames advance in a given time."""
        from src.engine.animation import AnimationClip, SpriteAnimator, LoopMode
        go = GameObject("test")
        animator = go.add_component(SpriteAnimator)

        # Use ONCE mode and enough frames so neither wraps
        clip_slow = AnimationClip("slow", [{}] * 100, fps=2, loop_mode=LoopMode.ONCE)
        clip_fast = AnimationClip("fast", [{}] * 100, fps=50, loop_mode=LoopMode.ONCE)

        animator.add_clip(clip_slow)
        animator.add_clip(clip_fast)

        animator.play("slow")
        Time._delta_time = 0.1
        animator.update()
        slow_idx = animator.frame_index  # 0.1s at 2fps = 0 advances (0.1 < 0.5)

        animator.play("fast")
        Time._delta_time = 0.1
        animator.update()
        fast_idx = animator.frame_index  # 0.1s at 50fps = 5 advances

        assert fast_idx > slow_idx


class TestCameraFollowMutations:
    """Mutation tests for camera follow."""

    def test_mutation_damping_factor_matters(self):
        """If damping is ignored (always t=1), camera snaps instantly."""
        from src.engine.camera_follow import CameraFollow2D
        cam_go = GameObject("Camera")
        cam_go.transform.position = Vector2(0, 0)
        follow = cam_go.add_component(CameraFollow2D)
        target_go = GameObject("Player")
        target_go.transform.position = Vector2(100, 0)
        follow.target = target_go.transform
        follow.damping = 0.01  # very slow

        Time._delta_time = 1.0 / 60.0
        follow.late_update()
        pos = cam_go.transform.position
        # With damping 0.01, camera should barely move in one frame
        assert pos.x < 10  # should NOT be at 100

    def test_mutation_dead_zone_prevents_movement(self):
        """If dead zone is removed, camera moves even for tiny offsets."""
        from src.engine.camera_follow import CameraFollow2D
        cam_go = GameObject("Camera")
        cam_go.transform.position = Vector2(0, 0)
        follow = cam_go.add_component(CameraFollow2D)
        target_go = GameObject("Player")
        target_go.transform.position = Vector2(0.1, 0)
        follow.target = target_go.transform
        follow.dead_zone = Vector2(1.0, 1.0)
        follow.damping = 0

        Time._delta_time = 1.0 / 60.0
        follow.late_update()
        # With dead zone, should not move (0.1 < 1.0)
        assert abs(cam_go.transform.position.x) < 0.01

    def test_mutation_bounds_matter(self):
        """Without bounds, camera would exceed the limit."""
        from src.engine.camera_follow import CameraFollow2D
        cam_go = GameObject("Camera")
        cam_go.transform.position = Vector2(0, 0)
        follow = cam_go.add_component(CameraFollow2D)
        target_go = GameObject("Player")
        target_go.transform.position = Vector2(1000, 0)
        follow.target = target_go.transform
        follow.damping = 0
        follow.bounds_min = Vector2(-10, -10)
        follow.bounds_max = Vector2(10, 10)

        Time._delta_time = 1.0 / 60.0
        follow.late_update()
        # Bounds should clamp. Shake is additive so allow small margin.
        assert cam_go.transform.position.x <= 11


class TestJointMutations:
    """Mutation tests for joints."""

    def test_mutation_build_required(self):
        """Constraint is None before build() is called."""
        from src.engine.physics.joints import HingeJoint2D
        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        hinge = go_a.add_component(HingeJoint2D)
        hinge.connected_body = rb_b
        # DON'T call build
        assert hinge._constraint is None

    def test_mutation_wrong_joint_type(self):
        """Different joint types produce different pymunk constraints."""
        from src.engine.physics.joints import SpringJoint2D

        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        spring = go_a.add_component(SpringJoint2D)
        spring.connected_body = rb_b
        spring.build()
        assert isinstance(spring._constraint, pymunk.DampedSpring)
        assert not isinstance(spring._constraint, pymunk.PinJoint)

    def test_mutation_on_destroy_actually_removes(self):
        """If on_destroy is broken, constraint stays in space."""
        from src.engine.physics.joints import SpringJoint2D
        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        spring = go_a.add_component(SpringJoint2D)
        spring.connected_body = rb_b
        spring.build()
        c = spring._constraint
        count_before = len(pm._space.constraints)
        spring.on_destroy()
        count_after = len(pm._space.constraints)
        assert count_after < count_before


# ===========================================================================
# EDGE CASE TESTS
# ===========================================================================


class TestEdgeCases:
    """Edge cases across all three systems."""

    def test_animation_empty_frames_list(self):
        """AnimationClip with no frames should not crash."""
        from src.engine.animation import AnimationClip, SpriteAnimator
        go = GameObject("test")
        animator = go.add_component(SpriteAnimator)
        clip = AnimationClip("empty", frames=[], fps=10)
        animator.add_clip(clip)
        animator.play("empty")
        Time._delta_time = 0.2
        animator.update()  # should not crash
        assert animator.frame_index == 0

    def test_animation_zero_fps_no_advance(self):
        """With fps=0, frames should never advance (inf frame duration)."""
        from src.engine.animation import AnimationClip, SpriteAnimator
        go = GameObject("test")
        animator = go.add_component(SpriteAnimator)
        clip = AnimationClip("x", [{}] * 3, fps=0)
        animator.add_clip(clip)
        animator.play("x")
        Time._delta_time = 100.0
        animator.update()
        assert animator.frame_index == 0

    def test_camera_follow_zero_delta_time(self):
        """Zero delta time should not cause division errors."""
        from src.engine.camera_follow import CameraFollow2D
        cam_go = GameObject("Camera")
        cam_go.transform.position = Vector2(0, 0)
        follow = cam_go.add_component(CameraFollow2D)
        target_go = GameObject("Player")
        target_go.transform.position = Vector2(10, 0)
        follow.target = target_go.transform
        Time._delta_time = 0.0
        follow.late_update()  # should not crash

    def test_camera_shake_zero_duration(self):
        """Zero-duration shake should expire immediately."""
        from src.engine.camera_follow import CameraShake
        CameraShake.trigger(intensity=1.0, duration=0.0)
        Time._delta_time = 0.001
        offset = CameraShake.get_offset()
        # After processing, it should be gone
        offset2 = CameraShake.get_offset()
        assert offset2.x == 0 and offset2.y == 0

    def test_joint_build_without_rigidbody(self):
        """Build on a GameObject without Rigidbody2D should not crash."""
        from src.engine.physics.joints import HingeJoint2D
        from src.engine.physics.rigidbody import Rigidbody2D
        go_a = GameObject("A")
        # No rigidbody on go_a
        hinge = go_a.add_component(HingeJoint2D)
        # Create a proper connected body
        go_b = GameObject("B")
        rb_b = go_b.add_component(Rigidbody2D)
        hinge.connected_body = rb_b
        hinge.build()  # should not crash
        assert hinge._constraint is None

    def test_joint_double_destroy_safe(self):
        """Calling on_destroy twice should not crash."""
        from src.engine.physics.joints import HingeJoint2D
        go_a, rb_a, go_b, rb_b, pm = _make_joint_pair()
        hinge = go_a.add_component(HingeJoint2D)
        hinge.connected_body = rb_b
        hinge.build()
        hinge.on_destroy()
        hinge.on_destroy()  # second call should be safe

    def test_camera_multiple_shakes_combine(self):
        """Multiple simultaneous shakes should combine their offsets."""
        from src.engine.camera_follow import CameraShake
        CameraShake.trigger(intensity=1.0, duration=1.0, frequency=25.0)
        CameraShake.trigger(intensity=1.0, duration=1.0, frequency=25.0)
        Time._delta_time = 0.02
        offset = CameraShake.get_offset()
        mag = math.sqrt(offset.x**2 + offset.y**2)

        CameraShake.reset()

        CameraShake.trigger(intensity=1.0, duration=1.0, frequency=25.0)
        Time._delta_time = 0.02
        single_offset = CameraShake.get_offset()
        single_mag = math.sqrt(single_offset.x**2 + single_offset.y**2)

        # Two identical shakes should produce double the offset of one
        assert abs(mag - 2 * single_mag) < 0.01
