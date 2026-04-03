"""Tweening engine — DOTween-equivalent for Python Unity simulator.

Supports typed property animation with easing curves, callbacks, looping,
and sequence chaining. Integrates into the game loop via TweenManager.tick().

Usage:
    from src.engine.tweening import Tween

    # Animate a transform position
    Tween.to(obj.transform, "position", Vector2(5, 3), duration=1.0).set_ease(Ease.OUT_BOUNCE)

    # Chain tweens in a sequence
    seq = Sequence()
    seq.append(Tween.to(obj.transform, "position", Vector2(5, 0), 0.5))
    seq.append(Tween.to(sr, "color", (255, 0, 0), 0.3))
    seq.play()
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from src.engine.math.vector import Vector2, Vector3


# ── Easing functions ─────────────────────────────────────────

class Ease(Enum):
    LINEAR = "linear"
    IN_QUAD = "in_quad"
    OUT_QUAD = "out_quad"
    IN_OUT_QUAD = "in_out_quad"
    IN_CUBIC = "in_cubic"
    OUT_CUBIC = "out_cubic"
    IN_OUT_CUBIC = "in_out_cubic"
    IN_SINE = "in_sine"
    OUT_SINE = "out_sine"
    IN_OUT_SINE = "in_out_sine"
    IN_ELASTIC = "in_elastic"
    OUT_ELASTIC = "out_elastic"
    IN_OUT_ELASTIC = "in_out_elastic"
    IN_BOUNCE = "in_bounce"
    OUT_BOUNCE = "out_bounce"
    IN_OUT_BOUNCE = "in_out_bounce"
    IN_BACK = "in_back"
    OUT_BACK = "out_back"
    IN_OUT_BACK = "in_out_back"


def _ease_out_bounce(t: float) -> float:
    if t < 1 / 2.75:
        return 7.5625 * t * t
    elif t < 2 / 2.75:
        t -= 1.5 / 2.75
        return 7.5625 * t * t + 0.75
    elif t < 2.5 / 2.75:
        t -= 2.25 / 2.75
        return 7.5625 * t * t + 0.9375
    else:
        t -= 2.625 / 2.75
        return 7.5625 * t * t + 0.984375


_EASE_FUNCS: dict[Ease, Callable[[float], float]] = {
    Ease.LINEAR: lambda t: t,
    Ease.IN_QUAD: lambda t: t * t,
    Ease.OUT_QUAD: lambda t: t * (2 - t),
    Ease.IN_OUT_QUAD: lambda t: 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t,
    Ease.IN_CUBIC: lambda t: t * t * t,
    Ease.OUT_CUBIC: lambda t: (t - 1) ** 3 + 1,
    Ease.IN_OUT_CUBIC: lambda t: 4 * t * t * t if t < 0.5 else (t - 1) * (2 * t - 2) ** 2 + 1,
    Ease.IN_SINE: lambda t: 1 - math.cos(t * math.pi / 2),
    Ease.OUT_SINE: lambda t: math.sin(t * math.pi / 2),
    Ease.IN_OUT_SINE: lambda t: 0.5 * (1 - math.cos(math.pi * t)),
    Ease.IN_ELASTIC: lambda t: 0 if t == 0 else (1 if t == 1 else -(2 ** (10 * (t - 1))) * math.sin((t - 1.1) * 5 * math.pi)),
    Ease.OUT_ELASTIC: lambda t: 0 if t == 0 else (1 if t == 1 else 2 ** (-10 * t) * math.sin((t - 0.1) * 5 * math.pi) + 1),
    Ease.IN_OUT_ELASTIC: lambda t: (
        0 if t == 0 else (1 if t == 1 else
        0.5 * -(2 ** (10 * (2 * t - 1))) * math.sin((2 * t - 1.1) * 5 * math.pi) if t < 0.5 else
        0.5 * 2 ** (-10 * (2 * t - 1)) * math.sin((2 * t - 1.1) * 5 * math.pi) + 1)
    ),
    Ease.IN_BOUNCE: lambda t: 1 - _ease_out_bounce(1 - t),
    Ease.OUT_BOUNCE: _ease_out_bounce,
    Ease.IN_OUT_BOUNCE: lambda t: (1 - _ease_out_bounce(1 - 2 * t)) * 0.5 if t < 0.5 else (_ease_out_bounce(2 * t - 1) + 1) * 0.5,
    Ease.IN_BACK: lambda t: t * t * (2.70158 * t - 1.70158),
    Ease.OUT_BACK: lambda t: (t - 1) ** 2 * (2.70158 * (t - 1) + 1.70158) + 1,
    Ease.IN_OUT_BACK: lambda t: (
        (2 * t) ** 2 * ((3.5949095 + 1) * 2 * t - 3.5949095) / 2 if t < 0.5 else
        ((2 * t - 2) ** 2 * ((3.5949095 + 1) * (t * 2 - 2) + 3.5949095) + 2) / 2
    ),
}


def evaluate_ease(ease: Ease, t: float) -> float:
    """Evaluate an easing function at time t (0..1)."""
    return _EASE_FUNCS[ease](max(0.0, min(1.0, t)))


# ── Value interpolation helpers ──────────────────────────────

def _lerp_value(start: Any, end: Any, t: float) -> Any:
    """Interpolate between start and end based on t (0..1)."""
    if isinstance(start, Vector2) and isinstance(end, Vector2):
        return Vector2(
            start.x + (end.x - start.x) * t,
            start.y + (end.y - start.y) * t,
        )
    if isinstance(start, Vector3) and isinstance(end, Vector3):
        return Vector3(
            start.x + (end.x - start.x) * t,
            start.y + (end.y - start.y) * t,
            start.z + (end.z - start.z) * t,
        )
    if isinstance(start, tuple) and isinstance(end, tuple):
        # Color tuples
        return tuple(
            int(s + (e - s) * t) for s, e in zip(start, end)
        )
    if isinstance(start, (int, float)) and isinstance(end, (int, float)):
        return start + (end - start) * t
    return end if t >= 1.0 else start


# ── Loop types ───────────────────────────────────────────────

class LoopType(Enum):
    RESTART = "restart"
    YOYO = "yoyo"


# ── Tween ────────────────────────────────────────────────────

class Tween:
    """Animates a single property on a target object."""

    def __init__(
        self,
        target: Any,
        property_name: str,
        end_value: Any,
        duration: float,
        *,
        from_value: Any = None,
    ):
        self.target = target
        self.property_name = property_name
        self.end_value = end_value
        self.duration = max(0.001, duration)
        self._from_value = from_value
        self._start_value: Any = None
        self._ease: Ease = Ease.LINEAR
        self._elapsed: float = 0.0
        self._is_playing: bool = True
        self._is_complete: bool = False
        self._is_killed: bool = False
        self._loops: int = 1
        self._loop_type: LoopType = LoopType.RESTART
        self._current_loop: int = 0
        self._delay: float = 0.0
        self._delay_elapsed: float = 0.0

        # Callbacks
        self._on_start: Callable[[], None] | None = None
        self._on_update: Callable[[float], None] | None = None
        self._on_complete: Callable[[], None] | None = None
        self._started: bool = False

    # ── Factory methods ──

    @staticmethod
    def to(target: Any, property_name: str, end_value: Any, duration: float) -> Tween:
        """Create a tween that animates TO end_value from the current value."""
        tw = Tween(target, property_name, end_value, duration)
        TweenManager.add(tw)
        return tw

    @staticmethod
    def from_to(target: Any, property_name: str, start_value: Any, end_value: Any, duration: float) -> Tween:
        """Create a tween that animates FROM start_value TO end_value."""
        tw = Tween(target, property_name, end_value, duration, from_value=start_value)
        TweenManager.add(tw)
        return tw

    # ── Configuration (fluent API) ──

    def set_ease(self, ease: Ease) -> Tween:
        self._ease = ease
        return self

    def set_loops(self, count: int, loop_type: LoopType = LoopType.RESTART) -> Tween:
        """Set loop count (-1 for infinite)."""
        self._loops = count
        self._loop_type = loop_type
        return self

    def set_delay(self, delay: float) -> Tween:
        self._delay = delay
        return self

    def on_start(self, callback: Callable[[], None]) -> Tween:
        self._on_start = callback
        return self

    def on_update(self, callback: Callable[[float], None]) -> Tween:
        self._on_update = callback
        return self

    def on_complete(self, callback: Callable[[], None]) -> Tween:
        self._on_complete = callback
        return self

    # ── Control ──

    def kill(self) -> None:
        self._is_killed = True
        self._is_complete = True

    def pause(self) -> None:
        self._is_playing = False

    def resume(self) -> None:
        self._is_playing = True

    @property
    def is_active(self) -> bool:
        return not self._is_complete and not self._is_killed

    @property
    def is_complete(self) -> bool:
        return self._is_complete

    # ── Internal tick ──

    def _tick(self, dt: float) -> bool:
        """Advance the tween. Returns True if complete."""
        if self._is_complete or self._is_killed:
            return True

        # Handle delay
        if self._delay_elapsed < self._delay:
            self._delay_elapsed += dt
            return False

        if not self._is_playing:
            return False

        # Capture start value on first tick
        if not self._started:
            self._started = True
            if self._from_value is not None:
                self._start_value = self._from_value
                # Set the property to from_value immediately
                _set_property(self.target, self.property_name, self._start_value)
            else:
                self._start_value = _get_property(self.target, self.property_name)
            if self._on_start:
                self._on_start()

        self._elapsed += dt
        raw_t = min(1.0, self._elapsed / self.duration)

        # Yoyo: reverse direction on odd loops
        if self._loop_type == LoopType.YOYO and self._current_loop % 2 == 1:
            eased_t = evaluate_ease(self._ease, 1.0 - raw_t)
        else:
            eased_t = evaluate_ease(self._ease, raw_t)

        # Interpolate and set
        value = _lerp_value(self._start_value, self.end_value, eased_t)
        _set_property(self.target, self.property_name, value)

        if self._on_update:
            self._on_update(eased_t)

        # Check completion
        if raw_t >= 1.0:
            self._current_loop += 1
            if self._loops == -1 or self._current_loop < self._loops:
                # Loop
                self._elapsed = 0.0
                if self._loop_type == LoopType.RESTART:
                    _set_property(self.target, self.property_name, self._start_value)
                return False
            else:
                self._is_complete = True
                if self._on_complete:
                    self._on_complete()
                return True

        return False


# ── Sequence ─────────────────────────────────────────────────

class Sequence:
    """Chains multiple tweens in order (append) or in parallel (join)."""

    def __init__(self):
        self._steps: list[_SequenceStep] = []
        self._current_index: int = 0
        self._is_complete: bool = False
        self._is_killed: bool = False
        self._on_complete: Callable[[], None] | None = None
        self._active_joins: list[Tween] = []
        self._joins_collected: bool = False

    def append(self, tween: Tween) -> Sequence:
        """Add a tween that plays after the previous one completes."""
        # Remove from TweenManager — we'll tick it manually
        TweenManager.remove(tween)
        self._steps.append(_SequenceStep(tween=tween, is_join=False))
        return self

    def join(self, tween: Tween) -> Sequence:
        """Add a tween that plays in parallel with the previous append."""
        TweenManager.remove(tween)
        self._steps.append(_SequenceStep(tween=tween, is_join=True))
        return self

    def on_complete(self, callback: Callable[[], None]) -> Sequence:
        self._on_complete = callback
        return self

    def play(self) -> Sequence:
        TweenManager.add_sequence(self)
        return self

    def kill(self) -> None:
        self._is_killed = True
        self._is_complete = True

    @property
    def is_active(self) -> bool:
        return not self._is_complete and not self._is_killed

    def _tick(self, dt: float) -> bool:
        if self._is_complete or self._is_killed:
            return True

        # On first tick or after advancing, collect joins following current append
        if not self._joins_collected:
            self._joins_collected = True
            # Skip the current append step (index), collect all subsequent joins
            idx = self._current_index + 1
            while idx < len(self._steps) and self._steps[idx].is_join:
                self._active_joins.append(self._steps[idx].tween)
                idx += 1

        # Tick active joins
        self._active_joins = [j for j in self._active_joins if not j._tick(dt)]

        # If we have no current step, we're done
        if self._current_index >= len(self._steps):
            if not self._active_joins:
                self._is_complete = True
                if self._on_complete:
                    self._on_complete()
                return True
            return False

        step = self._steps[self._current_index]

        # Non-join: tick this tween
        done = step.tween._tick(dt)
        if done:
            # Skip past collected joins
            self._current_index += 1
            while self._current_index < len(self._steps) and self._steps[self._current_index].is_join:
                self._current_index += 1
            self._joins_collected = False  # Reset for next group
            # Check if sequence is now complete
            if self._current_index >= len(self._steps) and not self._active_joins:
                self._is_complete = True
                if self._on_complete:
                    self._on_complete()
                return True

        return False


@dataclass
class _SequenceStep:
    tween: Tween
    is_join: bool


# ── Property access helpers ──────────────────────────────────

def _get_property(target: Any, name: str) -> Any:
    """Get a property value, supporting dot notation (e.g. 'transform.position')."""
    parts = name.split(".")
    obj = target
    for part in parts:
        obj = getattr(obj, part)
    return obj


def _set_property(target: Any, name: str, value: Any) -> None:
    """Set a property value, supporting dot notation."""
    parts = name.split(".")
    obj = target
    for part in parts[:-1]:
        obj = getattr(obj, part)
    setattr(obj, parts[-1], value)


# ── TweenManager (global singleton) ─────────────────────────

class TweenManager:
    """Manages all active tweens. Call tick(dt) each frame."""

    _tweens: list[Tween] = []
    _sequences: list[Sequence] = []

    @classmethod
    def add(cls, tween: Tween) -> None:
        cls._tweens.append(tween)

    @classmethod
    def remove(cls, tween: Tween) -> None:
        try:
            cls._tweens.remove(tween)
        except ValueError:
            pass

    @classmethod
    def add_sequence(cls, seq: Sequence) -> None:
        cls._sequences.append(seq)

    @classmethod
    def tick(cls, dt: float) -> None:
        """Advance all active tweens and sequences."""
        cls._tweens = [tw for tw in cls._tweens if not tw._tick(dt)]
        cls._sequences = [seq for seq in cls._sequences if not seq._tick(dt)]

    @classmethod
    def kill_all(cls) -> None:
        """Kill all active tweens and sequences."""
        for tw in cls._tweens:
            tw.kill()
        for seq in cls._sequences:
            seq.kill()
        cls._tweens.clear()
        cls._sequences.clear()

    @classmethod
    def active_count(cls) -> int:
        return len(cls._tweens) + len(cls._sequences)

    @classmethod
    def reset(cls) -> None:
        cls._tweens.clear()
        cls._sequences.clear()
