"""Camera follow system — Cinemachine-lite for 2D.

CameraFollow2D: smooth follow with damping, dead zone, look-ahead, and bounds.
CameraShake: additive screen shake using Perlin-style noise.

Usage:
    follow = cam_go.add_component(CameraFollow2D)
    follow.target = player.transform
    follow.damping = 0.1
    follow.dead_zone = Vector2(1, 0.5)

    CameraShake.trigger(intensity=0.5, duration=0.3)
"""

from __future__ import annotations

import math
import random

from src.engine.core import Component
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time
from src.engine.transform import Transform


class CameraFollow2D(Component):
    """Smooth 2D camera follow with damping, dead zone, and bounds."""

    def __init__(self):
        super().__init__()
        self.target: Transform | None = None
        self.follow_offset: Vector2 = Vector2(0, 0)
        self.damping: float = 0.1
        self.dead_zone: Vector2 = Vector2(0, 0)
        self.look_ahead_factor: float = 0.0
        self.bounds_min: Vector2 | None = None
        self.bounds_max: Vector2 | None = None
        self._last_target_pos: Vector2 | None = None

    def late_update(self) -> None:
        """Follow target in LateUpdate (after all movement)."""
        if self.target is None:
            return

        target_pos = Vector2(
            self.target.position.x + self.follow_offset.x,
            self.target.position.y + self.follow_offset.y,
        )

        # Look-ahead based on target velocity
        if self.look_ahead_factor > 0 and self._last_target_pos is not None:
            vel_x = target_pos.x - self._last_target_pos.x
            vel_y = target_pos.y - self._last_target_pos.y
            target_pos = Vector2(
                target_pos.x + vel_x * self.look_ahead_factor,
                target_pos.y + vel_y * self.look_ahead_factor,
            )
        self._last_target_pos = Vector2(target_pos.x, target_pos.y)

        cam_pos = self.transform.position
        dx = target_pos.x - cam_pos.x
        dy = target_pos.y - cam_pos.y

        # Dead zone: don't move if target is within dead zone
        if abs(dx) < self.dead_zone.x:
            dx = 0
        else:
            dx = dx - math.copysign(self.dead_zone.x, dx)

        if abs(dy) < self.dead_zone.y:
            dy = 0
        else:
            dy = dy - math.copysign(self.dead_zone.y, dy)

        # Damping (lerp toward target)
        if self.damping > 0:
            t = min(1.0, self.damping * Time.delta_time * 60)  # Frame-rate independent
        else:
            t = 1.0

        new_x = cam_pos.x + dx * t
        new_y = cam_pos.y + dy * t

        # Bounds clamping
        if self.bounds_min is not None and self.bounds_max is not None:
            new_x = max(self.bounds_min.x, min(self.bounds_max.x, new_x))
            new_y = max(self.bounds_min.y, min(self.bounds_max.y, new_y))

        # Apply shake offset
        shake = CameraShake.get_offset()

        self.transform.position = Vector2(new_x + shake.x, new_y + shake.y)


class CameraShake:
    """Screen shake with intensity decay."""

    _active_shakes: list[_ShakeInstance] = []

    @classmethod
    def trigger(cls, intensity: float = 0.5, duration: float = 0.3, frequency: float = 25.0) -> None:
        """Start a camera shake."""
        cls._active_shakes.append(_ShakeInstance(
            intensity=intensity,
            duration=duration,
            frequency=frequency,
            elapsed=0.0,
        ))

    @classmethod
    def get_offset(cls) -> Vector2:
        """Get combined shake offset for this frame. Call once per frame."""
        if not cls._active_shakes:
            return Vector2(0, 0)

        dt = Time.delta_time
        total_x = 0.0
        total_y = 0.0
        alive = []

        for shake in cls._active_shakes:
            shake.elapsed += dt
            if shake.elapsed >= shake.duration:
                continue
            alive.append(shake)

            # Decay intensity over time
            t = shake.elapsed / shake.duration
            current_intensity = shake.intensity * (1.0 - t)

            # Pseudo-random shake (deterministic from elapsed time)
            phase = shake.elapsed * shake.frequency
            total_x += math.sin(phase * 7.31) * current_intensity
            total_y += math.cos(phase * 5.17) * current_intensity

        cls._active_shakes = alive
        return Vector2(total_x, total_y)

    @classmethod
    def reset(cls) -> None:
        cls._active_shakes.clear()


class _ShakeInstance:
    __slots__ = ("intensity", "duration", "frequency", "elapsed")

    def __init__(self, intensity: float, duration: float, frequency: float, elapsed: float):
        self.intensity = intensity
        self.duration = duration
        self.frequency = frequency
        self.elapsed = elapsed
