"""Sprite animation system — frame-based animation with named clips.

Provides AnimationClip (frame sequence) and SpriteAnimator (component that
plays clips by swapping SpriteRenderer color/asset_ref per frame).

Usage:
    from src.engine.animation import AnimationClip, SpriteAnimator, LoopMode

    idle_clip = AnimationClip("idle", frames=[
        {"color": (255, 0, 0)},
        {"color": (200, 0, 0)},
        {"color": (255, 0, 0)},
    ], fps=4, loop_mode=LoopMode.LOOP)

    animator = go.add_component(SpriteAnimator)
    animator.add_clip(idle_clip)
    animator.play("idle")
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable

from src.engine.core import Component
from src.engine.time_manager import Time


class LoopMode(Enum):
    ONCE = "once"
    LOOP = "loop"
    PING_PONG = "ping_pong"


class AnimationClip:
    """Sequence of frames for sprite animation."""

    def __init__(
        self,
        name: str,
        frames: list[dict[str, Any]],
        fps: float = 12.0,
        loop_mode: LoopMode = LoopMode.LOOP,
    ):
        self.name = name
        self.frames = frames
        self.fps = fps
        self.loop_mode = loop_mode
        self._events: dict[int, list[Callable]] = {}

    def on_frame(self, frame_index: int, callback: Callable) -> AnimationClip:
        """Register a callback to fire when a specific frame is reached."""
        if frame_index not in self._events:
            self._events[frame_index] = []
        self._events[frame_index].append(callback)
        return self

    @property
    def frame_count(self) -> int:
        return len(self.frames)

    @property
    def duration(self) -> float:
        return len(self.frames) / self.fps if self.fps > 0 else 0


class SpriteAnimator(Component):
    """Component that plays AnimationClips by updating SpriteRenderer each frame."""

    def __init__(self):
        super().__init__()
        self._clips: dict[str, AnimationClip] = {}
        self._current_clip: AnimationClip | None = None
        self._frame_index: int = 0
        self._timer: float = 0.0
        self._is_playing: bool = False
        self._direction: int = 1  # 1=forward, -1=backward (for ping-pong)
        self._last_frame_applied: int = -1

    def add_clip(self, clip: AnimationClip) -> None:
        """Register a named animation clip."""
        self._clips[clip.name] = clip

    def play(self, clip_name: str) -> None:
        """Start playing a clip by name."""
        if clip_name not in self._clips:
            return
        clip = self._clips[clip_name]
        if self._current_clip is clip and self._is_playing:
            return  # Already playing this clip
        self._current_clip = clip
        self._frame_index = 0
        self._timer = 0.0
        self._is_playing = True
        self._direction = 1
        self._last_frame_applied = -1
        self._apply_frame()

    def stop(self) -> None:
        """Stop the current animation."""
        self._is_playing = False

    @property
    def current_clip(self) -> str | None:
        return self._current_clip.name if self._current_clip else None

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    @property
    def frame_index(self) -> int:
        return self._frame_index

    def update(self) -> None:
        """Advance animation. Called by LifecycleManager."""
        if not self._is_playing or self._current_clip is None:
            return

        clip = self._current_clip
        if clip.frame_count <= 1:
            return

        self._timer += Time.delta_time
        frame_duration = 1.0 / clip.fps if clip.fps > 0 else float('inf')

        while self._timer >= frame_duration:
            self._timer -= frame_duration
            self._advance_frame()

    def _advance_frame(self) -> None:
        clip = self._current_clip
        if clip is None:
            return

        next_index = self._frame_index + self._direction

        if clip.loop_mode == LoopMode.LOOP:
            self._frame_index = next_index % clip.frame_count
        elif clip.loop_mode == LoopMode.ONCE:
            if 0 <= next_index < clip.frame_count:
                self._frame_index = next_index
            else:
                self._is_playing = False
                return
        elif clip.loop_mode == LoopMode.PING_PONG:
            if 0 <= next_index < clip.frame_count:
                self._frame_index = next_index
            else:
                self._direction *= -1
                self._frame_index += self._direction

        self._apply_frame()

    def _apply_frame(self) -> None:
        """Apply current frame data to the SpriteRenderer."""
        clip = self._current_clip
        if clip is None or not (0 <= self._frame_index < clip.frame_count):
            return

        frame = clip.frames[self._frame_index]

        # Get SpriteRenderer from same GameObject
        from src.engine.rendering.renderer import SpriteRenderer
        sr = self.get_component(SpriteRenderer) if self.game_object else None

        if sr:
            if "color" in frame:
                sr.color = frame["color"]
            if "asset_ref" in frame:
                sr.asset_ref = frame["asset_ref"]

        # Fire frame events
        if self._frame_index != self._last_frame_applied:
            self._last_frame_applied = self._frame_index
            if self._frame_index in clip._events:
                for callback in clip._events[self._frame_index]:
                    callback()
