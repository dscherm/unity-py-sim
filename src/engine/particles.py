"""2D Particle system — emission, lifetime, velocity, color/size over lifetime.

Usage:
    ps = go.add_component(ParticleSystem)
    ps.emission_rate = 20
    ps.start_lifetime = 1.5
    ps.start_speed = 3.0
    ps.start_color = (255, 200, 50)
    ps.end_color = (255, 50, 0)
    ps.gravity_modifier = 1.0
    ps.play()
"""

from __future__ import annotations

import math
import random

from src.engine.core import Component
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time


class EmissionShape:
    POINT = "point"
    CIRCLE = "circle"
    BOX = "box"


class Particle:
    """Single particle state."""
    __slots__ = ("position", "velocity", "lifetime", "age", "start_color",
                 "end_color", "start_size", "end_size")

    def __init__(self):
        self.position: Vector2 = Vector2(0, 0)
        self.velocity: Vector2 = Vector2(0, 0)
        self.lifetime: float = 1.0
        self.age: float = 0.0
        self.start_color: tuple = (255, 255, 255)
        self.end_color: tuple = (255, 255, 255)
        self.start_size: float = 0.1
        self.end_size: float = 0.0

    @property
    def normalized_age(self) -> float:
        return min(1.0, self.age / self.lifetime) if self.lifetime > 0 else 1.0

    @property
    def is_alive(self) -> bool:
        return self.age < self.lifetime

    @property
    def current_color(self) -> tuple:
        t = self.normalized_age
        return tuple(
            int(self.start_color[i] + (self.end_color[i] - self.start_color[i]) * t)
            for i in range(min(len(self.start_color), len(self.end_color)))
        )

    @property
    def current_size(self) -> float:
        t = self.normalized_age
        return self.start_size + (self.end_size - self.start_size) * t


class ParticleSystem(Component):
    """2D particle emitter and simulator."""

    def __init__(self):
        super().__init__()
        self.emission_rate: float = 10.0
        self.start_lifetime: float = 1.0
        self.start_speed: float = 2.0
        self.start_size: float = 0.1
        self.end_size: float = 0.0
        self.start_color: tuple = (255, 255, 255)
        self.end_color: tuple = (255, 255, 255)
        self.gravity_modifier: float = 0.0
        self.max_particles: int = 100
        self.emission_shape: str = EmissionShape.POINT
        self.emission_radius: float = 0.5
        self.emission_box: Vector2 = Vector2(1, 1)
        self.start_speed_variance: float = 0.0
        self.start_lifetime_variance: float = 0.0
        self.sorting_order: int = 0

        self._particles: list[Particle] = []
        self._is_playing: bool = False
        self._emit_timer: float = 0.0

    def play(self) -> None:
        self._is_playing = True

    def stop(self) -> None:
        self._is_playing = False

    def pause(self) -> None:
        self._is_playing = False

    @property
    def is_playing(self) -> bool:
        return self._is_playing

    @property
    def particle_count(self) -> int:
        return len(self._particles)

    def get_particles(self) -> list[Particle]:
        return list(self._particles)

    def clear(self) -> None:
        self._particles.clear()

    def emit(self, count: int = 1) -> None:
        """Manually emit particles."""
        for _ in range(count):
            if len(self._particles) >= self.max_particles:
                break
            self._particles.append(self._create_particle())

    def update(self) -> None:
        dt = Time.delta_time
        if dt <= 0:
            return

        # Emit
        if self._is_playing and self.emission_rate > 0:
            self._emit_timer += dt
            emit_interval = 1.0 / self.emission_rate
            while self._emit_timer >= emit_interval and len(self._particles) < self.max_particles:
                self._emit_timer -= emit_interval
                self._particles.append(self._create_particle())

        # Update particles
        gravity = Vector2(0, -9.81 * self.gravity_modifier)
        alive = []
        for p in self._particles:
            p.age += dt
            if not p.is_alive:
                continue
            p.velocity = Vector2(
                p.velocity.x + gravity.x * dt,
                p.velocity.y + gravity.y * dt,
            )
            p.position = Vector2(
                p.position.x + p.velocity.x * dt,
                p.position.y + p.velocity.y * dt,
            )
            alive.append(p)
        self._particles = alive

    def _create_particle(self) -> Particle:
        p = Particle()

        # Position from emission shape
        origin = self.transform.position if self.game_object else Vector2(0, 0)
        if self.emission_shape == EmissionShape.CIRCLE:
            angle = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, self.emission_radius)
            p.position = Vector2(origin.x + math.cos(angle) * r, origin.y + math.sin(angle) * r)
        elif self.emission_shape == EmissionShape.BOX:
            p.position = Vector2(
                origin.x + random.uniform(-self.emission_box.x / 2, self.emission_box.x / 2),
                origin.y + random.uniform(-self.emission_box.y / 2, self.emission_box.y / 2),
            )
        else:
            p.position = Vector2(origin.x, origin.y)

        # Velocity (random direction at start_speed)
        angle = random.uniform(0, 2 * math.pi)
        speed = self.start_speed + random.uniform(-self.start_speed_variance, self.start_speed_variance)
        p.velocity = Vector2(math.cos(angle) * speed, math.sin(angle) * speed)

        # Lifetime
        p.lifetime = self.start_lifetime + random.uniform(-self.start_lifetime_variance, self.start_lifetime_variance)
        p.lifetime = max(0.01, p.lifetime)

        # Color and size
        p.start_color = self.start_color
        p.end_color = self.end_color
        p.start_size = self.start_size
        p.end_size = self.end_size

        return p
