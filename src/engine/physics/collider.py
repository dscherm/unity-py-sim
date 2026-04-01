"""Unity-compatible 2D colliders wrapping pymunk shapes."""

from __future__ import annotations

import pymunk

from src.engine.core import Component
from src.engine.math.vector import Vector2
from src.engine.physics.rigidbody import Rigidbody2D


class Collider2D(Component):
    """Base class for 2D colliders."""

    def __init__(self) -> None:
        super().__init__()
        self._offset: Vector2 = Vector2(0, 0)
        self._is_trigger: bool = False
        self._shape: pymunk.Shape | None = None

    @property
    def offset(self) -> Vector2:
        return self._offset

    @offset.setter
    def offset(self, value: Vector2) -> None:
        self._offset = value

    @property
    def is_trigger(self) -> bool:
        return self._is_trigger

    @is_trigger.setter
    def is_trigger(self, value: bool) -> None:
        self._is_trigger = value
        if self._shape is not None:
            from src.engine.physics.physics_manager import PhysicsManager
            pm = PhysicsManager.instance()
            if value:
                pm.mark_trigger(self._shape)
                self._shape.sensor = True

    def _get_or_create_body(self) -> pymunk.Body:
        """Get the Rigidbody2D's pymunk body, or create a static one."""
        rb = self.game_object.get_component(Rigidbody2D)
        if rb is not None:
            return rb._body
        # No rigidbody — use a static body
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        pos = self.game_object.transform.position
        body.position = (pos.x, pos.y)
        return body

    def _register_shape(self, shape: pymunk.Shape) -> None:
        """Register the shape with the physics manager."""
        self._shape = shape
        shape.friction = 0.5
        shape.elasticity = 0.5

        rb = self.game_object.get_component(Rigidbody2D)
        if rb is not None:
            rb._shapes.append(shape)
            from src.engine.physics.physics_manager import PhysicsManager
            pm = PhysicsManager.instance()
            pm.register_body(rb)
            if self._is_trigger:
                pm.mark_trigger(shape)
                shape.sensor = True


class BoxCollider2D(Collider2D):
    """Box-shaped 2D collider."""

    def __init__(self) -> None:
        super().__init__()
        self._size: Vector2 = Vector2(1, 1)

    @property
    def size(self) -> Vector2:
        return self._size

    @size.setter
    def size(self, value: Vector2) -> None:
        self._size = value

    def build(self) -> None:
        """Build the pymunk shape. Call after setting size and attaching to a GameObject."""
        body = self._get_or_create_body()
        hw, hh = self._size.x / 2.0, self._size.y / 2.0
        ox, oy = self._offset.x, self._offset.y
        vertices = [
            (ox - hw, oy - hh),
            (ox + hw, oy - hh),
            (ox + hw, oy + hh),
            (ox - hw, oy + hh),
        ]
        shape = pymunk.Poly(body, vertices)
        self._register_shape(shape)


class CircleCollider2D(Collider2D):
    """Circle-shaped 2D collider."""

    def __init__(self) -> None:
        super().__init__()
        self._radius: float = 0.5

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        self._radius = value

    def build(self) -> None:
        """Build the pymunk shape. Call after setting radius and attaching to a GameObject."""
        body = self._get_or_create_body()
        shape = pymunk.Circle(body, self._radius, offset=(self._offset.x, self._offset.y))
        self._register_shape(shape)
