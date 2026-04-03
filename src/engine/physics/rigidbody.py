"""Unity-compatible Rigidbody2D component wrapping pymunk.Body."""

from __future__ import annotations

from enum import Enum

import pymunk

from src.engine.core import Component
from src.engine.math.vector import Vector2


class RigidbodyType2D(Enum):
    DYNAMIC = "dynamic"
    KINEMATIC = "kinematic"
    STATIC = "static"


class ForceMode2D(Enum):
    FORCE = "force"
    IMPULSE = "impulse"


class Rigidbody2D(Component):
    """2D rigidbody wrapping pymunk.Body."""

    def __init__(self) -> None:
        super().__init__()
        self._body = pymunk.Body(mass=1.0, moment=pymunk.moment_for_circle(1.0, 0, 1))
        self._shapes: list[pymunk.Shape] = []
        self._body_type = RigidbodyType2D.DYNAMIC
        self._gravity_scale: float = 1.0
        self._drag: float = 0.0
        self._registered = False

    @property
    def velocity(self) -> Vector2:
        v = self._body.velocity
        return Vector2(v[0], v[1])

    @velocity.setter
    def velocity(self, value: Vector2) -> None:
        self._body.velocity = (value.x, value.y)

    @property
    def angular_velocity(self) -> float:
        return float(self._body.angular_velocity)

    @angular_velocity.setter
    def angular_velocity(self, value: float) -> None:
        self._body.angular_velocity = value

    @property
    def mass(self) -> float:
        return float(self._body.mass)

    @mass.setter
    def mass(self, value: float) -> None:
        self._body.mass = value

    @property
    def drag(self) -> float:
        return self._drag

    @drag.setter
    def drag(self, value: float) -> None:
        self._drag = value
        self._body.damping = 1.0 - value  # Approximate mapping

    @property
    def gravity_scale(self) -> float:
        return self._gravity_scale

    @gravity_scale.setter
    def gravity_scale(self, value: float) -> None:
        self._gravity_scale = value

    @property
    def body_type(self) -> RigidbodyType2D:
        return self._body_type

    @body_type.setter
    def body_type(self, value: RigidbodyType2D) -> None:
        import math
        # Save finite mass before type change — pymunk uses inf for KINEMATIC/STATIC
        current_mass = self._body.mass
        if 0 < current_mass < math.inf:
            self._saved_mass = current_mass
        self._body_type = value
        if value == RigidbodyType2D.DYNAMIC:
            self._body.body_type = pymunk.Body.DYNAMIC
            # Restore mass/moment — pymunk may have zeroed them
            restore_mass = getattr(self, '_saved_mass', 1.0)
            if not (0 < self._body.mass < math.inf):
                self._body.mass = restore_mass if restore_mass > 0 else 1.0
            if not (0 < self._body.moment < math.inf):
                self._body.moment = pymunk.moment_for_circle(self._body.mass, 0, 1)
        elif value == RigidbodyType2D.KINEMATIC:
            self._body.body_type = pymunk.Body.KINEMATIC
        elif value == RigidbodyType2D.STATIC:
            self._body.body_type = pymunk.Body.STATIC

    def add_force(self, force: Vector2, mode: ForceMode2D = ForceMode2D.FORCE) -> None:
        if mode == ForceMode2D.FORCE:
            self._body.apply_force_at_local_point((force.x, force.y))
        elif mode == ForceMode2D.IMPULSE:
            self._body.apply_impulse_at_local_point((force.x, force.y))

    def add_torque(self, torque: float) -> None:
        self._body.torque += torque

    def move_position(self, position: Vector2) -> None:
        """For kinematic bodies — move to position."""
        self._body.position = (position.x, position.y)

    def _sync_to_transform(self) -> None:
        """Sync pymunk body position back to the GameObject's Transform."""
        if self._game_object is not None:
            pos = self._body.position
            self._game_object.transform.position = Vector2(pos[0], pos[1])  # type: ignore

    def _sync_from_transform(self) -> None:
        """Sync Transform position to pymunk body."""
        if self._game_object is not None:
            pos = self._game_object.transform.position
            self._body.position = (pos.x, pos.y)
