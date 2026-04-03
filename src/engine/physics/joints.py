"""2D Joint components — wraps pymunk constraints as Unity-style joint components.

HingeJoint2D: rotational joint with optional angle limits and motor.
SpringJoint2D: elastic connection between two bodies.
DistanceJoint2D: maintains distance between two bodies.
FixedJoint2D: rigid connection (no relative movement).

Usage:
    hinge = go.add_component(HingeJoint2D)
    hinge.connected_body = other_rb
    hinge.anchor = Vector2(0, 0)
    hinge.build()
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pymunk

from src.engine.core import Component
from src.engine.math.vector import Vector2

if TYPE_CHECKING:
    from src.engine.physics.rigidbody import Rigidbody2D


class Joint2D(Component):
    """Base class for 2D joint components."""

    def __init__(self):
        super().__init__()
        self.connected_body: Rigidbody2D | None = None
        self.auto_configure_offset: bool = True
        self._constraint: pymunk.Constraint | None = None

    def _get_bodies(self) -> tuple[pymunk.Body, pymunk.Body] | None:
        """Get the pymunk bodies for this joint."""
        from src.engine.physics.rigidbody import Rigidbody2D
        my_rb = self.get_component(Rigidbody2D) if self.game_object else None
        if my_rb is None or my_rb._body is None:
            return None
        if self.connected_body is None or self.connected_body._body is None:
            return None
        return (my_rb._body, self.connected_body._body)

    def build(self) -> None:
        """Create the pymunk constraint. Call after setting properties."""
        raise NotImplementedError

    def _register(self, constraint: pymunk.Constraint) -> None:
        """Register constraint with the physics space."""
        from src.engine.physics.physics_manager import PhysicsManager
        self._constraint = constraint
        PhysicsManager.instance()._space.add(constraint)

    def on_destroy(self) -> None:
        if self._constraint:
            from src.engine.physics.physics_manager import PhysicsManager
            try:
                PhysicsManager.instance()._space.remove(self._constraint)
            except Exception:
                pass
            self._constraint = None


class HingeJoint2D(Joint2D):
    """Rotational joint — allows rotation around an anchor point."""

    def __init__(self):
        super().__init__()
        self.anchor: Vector2 = Vector2(0, 0)
        self.use_limits: bool = False
        self.limits_min: float = 0.0  # degrees
        self.limits_max: float = 0.0  # degrees
        self.use_motor: bool = False
        self.motor_speed: float = 0.0  # degrees/sec
        self.max_motor_torque: float = 10000.0

    def build(self) -> None:
        bodies = self._get_bodies()
        if bodies is None:
            return
        a, b = bodies
        anchor = (self.anchor.x, self.anchor.y)
        pivot = pymunk.PivotJoint(a, b, anchor)
        self._register(pivot)

        if self.use_limits:
            import math
            limit = pymunk.RotaryLimitJoint(
                a, b,
                math.radians(self.limits_min),
                math.radians(self.limits_max),
            )
            from src.engine.physics.physics_manager import PhysicsManager
            PhysicsManager.instance()._space.add(limit)

        if self.use_motor:
            import math
            motor = pymunk.SimpleMotor(a, b, math.radians(self.motor_speed))
            motor.max_force = self.max_motor_torque
            from src.engine.physics.physics_manager import PhysicsManager
            PhysicsManager.instance()._space.add(motor)


class SpringJoint2D(Joint2D):
    """Elastic spring connection between two bodies."""

    def __init__(self):
        super().__init__()
        self.anchor: Vector2 = Vector2(0, 0)
        self.connected_anchor: Vector2 = Vector2(0, 0)
        self.distance: float = 1.0
        self.frequency: float = 4.0
        self.damping_ratio: float = 0.5

    def build(self) -> None:
        bodies = self._get_bodies()
        if bodies is None:
            return
        a, b = bodies
        stiffness = (2 * 3.14159 * self.frequency) ** 2
        damping = 2 * self.damping_ratio * (2 * 3.14159 * self.frequency)
        spring = pymunk.DampedSpring(
            a, b,
            anchor_a=(self.anchor.x, self.anchor.y),
            anchor_b=(self.connected_anchor.x, self.connected_anchor.y),
            rest_length=self.distance,
            stiffness=stiffness,
            damping=damping,
        )
        self._register(spring)


class DistanceJoint2D(Joint2D):
    """Maintains a fixed distance between two bodies."""

    def __init__(self):
        super().__init__()
        self.distance: float = 1.0
        self.max_distance_only: bool = False

    def build(self) -> None:
        bodies = self._get_bodies()
        if bodies is None:
            return
        a, b = bodies
        if self.max_distance_only:
            joint = pymunk.SlideJoint(a, b, (0, 0), (0, 0), 0, self.distance)
        else:
            joint = pymunk.PinJoint(a, b, (0, 0), (0, 0))
        self._register(joint)


class FixedJoint2D(Joint2D):
    """Rigid connection — no relative movement between bodies."""

    def build(self) -> None:
        bodies = self._get_bodies()
        if bodies is None:
            return
        a, b = bodies
        # Use pivot + gear to lock both translation and rotation
        pivot = pymunk.PivotJoint(a, b, a.position)
        gear = pymunk.GearJoint(a, b, 0.0, 1.0)
        from src.engine.physics.physics_manager import PhysicsManager
        space = PhysicsManager.instance()._space
        space.add(pivot, gear)
        self._constraint = pivot  # Store one for cleanup
