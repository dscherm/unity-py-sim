"""Physics manager wrapping pymunk.Space for Unity-style 2D physics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import pymunk

from src.engine.math.vector import Vector2

if TYPE_CHECKING:
    from src.engine.core import GameObject


@dataclass
class ContactPoint2D:
    """A single contact point in a collision."""
    point: Vector2
    normal: Vector2


@dataclass
class Collision2D:
    """Collision data passed to MonoBehaviour callbacks."""
    game_object: GameObject
    contacts: list[ContactPoint2D] = field(default_factory=list)
    relative_velocity: Vector2 = field(default_factory=lambda: Vector2(0, 0))


class PhysicsManager:
    """Singleton managing the pymunk physics space."""

    _instance: PhysicsManager | None = None

    def __init__(self) -> None:
        self._space = pymunk.Space()
        self._space.gravity = (0, -9.81)
        self._body_map: dict[int, 'Rigidbody2D'] = {}  # pymunk body hash -> Rigidbody2D
        self._trigger_shapes: set[int] = set()  # shape ids that are triggers

        # Set up collision handlers (pymunk 7.x API)
        self._space.on_collision(
            begin=self._on_collision_begin,
            pre_solve=self._on_pre_solve,
            separate=self._on_collision_separate,
        )

    @classmethod
    def instance(cls) -> PhysicsManager:
        if cls._instance is None:
            cls._instance = PhysicsManager()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    @property
    def space(self) -> pymunk.Space:
        return self._space

    @property
    def gravity(self) -> Vector2:
        g = self._space.gravity
        return Vector2(g[0], g[1])

    @gravity.setter
    def gravity(self, value: Vector2) -> None:
        self._space.gravity = (value.x, value.y)

    def register_body(self, rb: 'Rigidbody2D') -> None:
        """Register a Rigidbody2D's pymunk body and shapes with the space."""
        if rb._body not in self._space.bodies:
            self._space.add(rb._body)
        for shape in rb._shapes:
            if shape not in self._space.shapes:
                self._space.add(shape)
        self._body_map[id(rb._body)] = rb

    def unregister_body(self, rb: 'Rigidbody2D') -> None:
        """Remove a Rigidbody2D from the space."""
        for shape in rb._shapes:
            if shape in self._space.shapes:
                self._space.remove(shape)
        if rb._body in self._space.bodies:
            self._space.remove(rb._body)
        self._body_map.pop(id(rb._body), None)

    def mark_trigger(self, shape: pymunk.Shape) -> None:
        self._trigger_shapes.add(id(shape))

    def is_trigger(self, shape: pymunk.Shape) -> bool:
        return id(shape) in self._trigger_shapes

    def step(self, dt: float) -> None:
        """Step the physics simulation."""
        self._space.step(dt)
        # Sync positions back to transforms
        for rb in self._body_map.values():
            if rb._body.body_type == pymunk.Body.DYNAMIC:
                rb._sync_to_transform()

    def _get_rb_from_body(self, body: pymunk.Body) -> 'Rigidbody2D | None':
        return self._body_map.get(id(body))

    def _on_collision_begin(self, arbiter: pymunk.Arbiter, space, data) -> None:
        shape_a, shape_b = arbiter.shapes
        rb_a = self._get_rb_from_body(shape_a.body)
        rb_b = self._get_rb_from_body(shape_b.body)

        is_trigger = self.is_trigger(shape_a) or self.is_trigger(shape_b)

        if rb_a and rb_b:
            if is_trigger:
                self._dispatch_trigger_enter(rb_a, rb_b)
                arbiter.process_collision = False  # Triggers don't resolve physics
            else:
                self._dispatch_collision_enter(rb_a, rb_b, arbiter)

    def _on_pre_solve(self, arbiter: pymunk.Arbiter, space, data) -> None:
        shape_a, shape_b = arbiter.shapes
        if self.is_trigger(shape_a) or self.is_trigger(shape_b):
            arbiter.process_collision = False

    def _on_collision_separate(self, arbiter: pymunk.Arbiter, space, data) -> None:
        shape_a, shape_b = arbiter.shapes
        rb_a = self._get_rb_from_body(shape_a.body)
        rb_b = self._get_rb_from_body(shape_b.body)

        is_trigger = self.is_trigger(shape_a) or self.is_trigger(shape_b)

        if rb_a and rb_b:
            if is_trigger:
                self._dispatch_trigger_exit(rb_a, rb_b)
            else:
                self._dispatch_collision_exit(rb_a, rb_b)

    def _dispatch_collision_enter(self, rb_a: 'Rigidbody2D', rb_b: 'Rigidbody2D',
                                   arbiter: pymunk.Arbiter) -> None:
        from src.engine.core import MonoBehaviour

        contacts = []
        for cp in arbiter.contact_point_set.points:
            contacts.append(ContactPoint2D(
                point=Vector2(cp.point_a[0], cp.point_a[1]),
                normal=Vector2(arbiter.contact_point_set.normal[0], arbiter.contact_point_set.normal[1]),
            ))

        collision_for_a = Collision2D(
            game_object=rb_b.game_object,
            contacts=contacts,
            relative_velocity=Vector2(
                rb_a._body.velocity[0] - rb_b._body.velocity[0],
                rb_a._body.velocity[1] - rb_b._body.velocity[1],
            ),
        )
        collision_for_b = Collision2D(
            game_object=rb_a.game_object,
            contacts=contacts,
            relative_velocity=Vector2(
                rb_b._body.velocity[0] - rb_a._body.velocity[0],
                rb_b._body.velocity[1] - rb_a._body.velocity[1],
            ),
        )

        for comp in rb_a.game_object.get_components(MonoBehaviour):
            comp.on_collision_enter_2d(collision_for_a)
        for comp in rb_b.game_object.get_components(MonoBehaviour):
            comp.on_collision_enter_2d(collision_for_b)

    def _dispatch_collision_exit(self, rb_a: 'Rigidbody2D', rb_b: 'Rigidbody2D') -> None:
        from src.engine.core import MonoBehaviour

        collision_for_a = Collision2D(game_object=rb_b.game_object)
        collision_for_b = Collision2D(game_object=rb_a.game_object)

        for comp in rb_a.game_object.get_components(MonoBehaviour):
            comp.on_collision_exit_2d(collision_for_a)
        for comp in rb_b.game_object.get_components(MonoBehaviour):
            comp.on_collision_exit_2d(collision_for_b)

    def _dispatch_trigger_enter(self, rb_a: 'Rigidbody2D', rb_b: 'Rigidbody2D') -> None:
        from src.engine.core import MonoBehaviour
        for comp in rb_a.game_object.get_components(MonoBehaviour):
            comp.on_trigger_enter_2d(rb_b.game_object)
        for comp in rb_b.game_object.get_components(MonoBehaviour):
            comp.on_trigger_enter_2d(rb_a.game_object)

    def _dispatch_trigger_exit(self, rb_a: 'Rigidbody2D', rb_b: 'Rigidbody2D') -> None:
        from src.engine.core import MonoBehaviour
        for comp in rb_a.game_object.get_components(MonoBehaviour):
            comp.on_trigger_exit_2d(rb_b.game_object)
        for comp in rb_b.game_object.get_components(MonoBehaviour):
            comp.on_trigger_exit_2d(rb_a.game_object)


# Import here to avoid circular — used by type hints above
from src.engine.physics.rigidbody import Rigidbody2D  # noqa: E402, F401
