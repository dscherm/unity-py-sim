"""Unity-compatible 2D colliders wrapping pymunk shapes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pymunk

from src.engine.core import Component
from src.engine.math.vector import Vector2
from src.engine.physics.rigidbody import Rigidbody2D

if TYPE_CHECKING:
    pass


class PhysicsMaterial2D:
    """Unity-compatible 2D physics material controlling bounciness and friction.

    Unity defaults: bounciness=0, friction=0.4.
    """

    def __init__(self, bounciness: float = 0.0, friction: float = 0.4) -> None:
        self._bounciness = bounciness
        self._friction = friction

    @property
    def bounciness(self) -> float:
        return self._bounciness

    @bounciness.setter
    def bounciness(self, value: float) -> None:
        self._bounciness = value

    @property
    def friction(self) -> float:
        return self._friction

    @friction.setter
    def friction(self, value: float) -> None:
        self._friction = value


@dataclass
class Bounds:
    """Axis-aligned bounding box."""
    center: Vector2
    size: Vector2

    @property
    def min(self) -> Vector2:
        return Vector2(self.center.x - self.size.x / 2, self.center.y - self.size.y / 2)

    @property
    def max(self) -> Vector2:
        return Vector2(self.center.x + self.size.x / 2, self.center.y + self.size.y / 2)

    @property
    def extents(self) -> Vector2:
        return Vector2(self.size.x / 2, self.size.y / 2)

    def contains(self, point: Vector2) -> bool:
        mn, mx = self.min, self.max
        return mn.x <= point.x <= mx.x and mn.y <= point.y <= mx.y


class Collider2D(Component):
    """Base class for 2D colliders."""

    def __init__(self) -> None:
        super().__init__()
        self._offset: Vector2 = Vector2(0, 0)
        self._is_trigger: bool = False
        self._shape: pymunk.Shape | None = None
        self._shared_material: PhysicsMaterial2D | None = None
        self._material: PhysicsMaterial2D | None = None

    def awake(self) -> None:
        """Auto-build the physics shape on awake, matching Unity's behavior.

        In Unity, colliders are automatically active once configured via inspector.
        This builds the pymunk shape after all properties have been set in scene setup.
        """
        if self._shape is None and self._game_object is not None:
            # Sync the pymunk body position from the transform BEFORE building
            # the shape, so the spatial hash is correct for static bodies.
            rb = self.game_object.get_component(Rigidbody2D)
            if rb is not None:
                rb._sync_from_transform()
            self.build()
            # Reindex static shapes so spatial queries find them immediately
            if rb is not None and rb._body.body_type == pymunk.Body.STATIC:
                from src.engine.physics.physics_manager import PhysicsManager
                PhysicsManager.instance()._space.reindex_shapes_for_body(rb._body)

    def build(self) -> None:
        """Build the pymunk shape. Override in subclasses.

        Safe to call multiple times — removes old shape before rebuilding.
        """
        pass

    def _cleanup_old_shape(self) -> None:
        """Remove old shape from physics if rebuilding."""
        if self._shape is not None:
            rb = self.game_object.get_component(Rigidbody2D)
            if rb is not None and self._shape in rb._shapes:
                rb._shapes.remove(self._shape)
                try:
                    from src.engine.physics.physics_manager import PhysicsManager
                    pm = PhysicsManager.instance()
                    if self._shape in pm._space.shapes:
                        pm._space.remove(self._shape)
                except Exception:
                    pass
            self._shape = None

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

    @property
    def shared_material(self) -> PhysicsMaterial2D | None:
        return self._shared_material

    @shared_material.setter
    def shared_material(self, value: PhysicsMaterial2D | None) -> None:
        self._shared_material = value
        self._apply_material()

    @property
    def material(self) -> PhysicsMaterial2D | None:
        return self._material

    @material.setter
    def material(self, value: PhysicsMaterial2D | None) -> None:
        self._material = value
        self._apply_material()

    @property
    def bounds(self) -> Bounds:
        """Return the AABB of this collider in world space."""
        if self._shape is not None:
            bb = self._shape.bb
            center = Vector2((bb.left + bb.right) / 2, (bb.bottom + bb.top) / 2)
            size = Vector2(bb.right - bb.left, bb.top - bb.bottom)
            return Bounds(center=center, size=size)
        pos = self.game_object.transform.position
        return Bounds(center=Vector2(pos.x, pos.y), size=Vector2(0, 0))

    def _get_effective_material(self) -> PhysicsMaterial2D:
        """Return instance material if set, else shared, else Unity defaults."""
        if self._material is not None:
            return self._material
        if self._shared_material is not None:
            return self._shared_material
        return PhysicsMaterial2D()  # Unity defaults: bounciness=0, friction=0.4

    def _apply_material(self) -> None:
        """Apply the current material properties to the pymunk shape."""
        if self._shape is None:
            return
        mat = self._get_effective_material()
        self._shape.elasticity = mat.bounciness
        self._shape.friction = mat.friction

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
        # Apply material properties (or defaults)
        mat = self._get_effective_material()
        shape.elasticity = mat.bounciness
        shape.friction = mat.friction

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
        """Build the pymunk box shape from current size."""
        self._cleanup_old_shape()
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
        """Build the pymunk circle shape from current radius."""
        self._cleanup_old_shape()
        body = self._get_or_create_body()
        shape = pymunk.Circle(body, self._radius, offset=(self._offset.x, self._offset.y))
        self._register_shape(shape)


class PolygonCollider2D(Collider2D):
    """Polygon-shaped 2D collider defined by vertex points."""

    def __init__(self) -> None:
        super().__init__()
        self._points: list[Vector2] = []

    @property
    def points(self) -> list[Vector2]:
        return list(self._points)

    @points.setter
    def points(self, value: list[Vector2]) -> None:
        self._points = list(value)

    def build(self) -> None:
        """Build the pymunk polygon shape from points."""
        if len(self._points) < 3:
            return
        self._cleanup_old_shape()
        body = self._get_or_create_body()
        vertices = [(p.x + self._offset.x, p.y + self._offset.y) for p in self._points]
        shape = pymunk.Poly(body, vertices)
        self._register_shape(shape)


class EdgeCollider2D(Collider2D):
    """Edge chain collider — connected line segments."""

    def __init__(self) -> None:
        super().__init__()
        self._points: list[Vector2] = []

    @property
    def points(self) -> list[Vector2]:
        return list(self._points)

    @points.setter
    def points(self, value: list[Vector2]) -> None:
        self._points = list(value)

    def build(self) -> None:
        """Build pymunk segment shapes for each edge."""
        if len(self._points) < 2:
            return
        self._cleanup_old_shape()
        body = self._get_or_create_body()
        for i in range(len(self._points) - 1):
            a = self._points[i]
            b = self._points[i + 1]
            segment = pymunk.Segment(
                body,
                (a.x + self._offset.x, a.y + self._offset.y),
                (b.x + self._offset.x, b.y + self._offset.y),
                radius=0.01,
            )
            self._register_shape(segment)
