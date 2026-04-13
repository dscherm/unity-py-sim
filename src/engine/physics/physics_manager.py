"""Physics manager wrapping pymunk.Space for Unity-style 2D physics."""

from __future__ import annotations

import math
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


@dataclass
class RaycastHit2D:
    """Result of a Physics2D raycast query."""
    point: Vector2
    normal: Vector2
    distance: float
    collider: object | None = None  # Collider2D
    rigidbody: object | None = None  # Rigidbody2D
    transform: object | None = None  # Transform


class PhysicsManager:
    """Singleton managing the pymunk physics space."""

    _instance: PhysicsManager | None = None

    def __init__(self) -> None:
        self._space = pymunk.Space()
        self._space.gravity = (0, -9.81)
        self._body_map: dict[int, 'Rigidbody2D'] = {}  # pymunk body hash -> Rigidbody2D
        self._trigger_shapes: set[int] = set()  # shape ids that are triggers
        # Track active contacts for Stay callbacks: (body_id_a, body_id_b) -> is_trigger
        self._active_contacts: dict[tuple[int, int], bool] = {}

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
        # Sync kinematic/static body positions from transforms before stepping
        # (Unity moves kinematic bodies via transform, physics reads their position)
        for rb in self._body_map.values():
            if rb._body.body_type in (pymunk.Body.KINEMATIC, pymunk.Body.STATIC):
                rb._sync_from_transform()
        self._space.step(dt)
        # Dispatch Stay callbacks for active contacts
        self._dispatch_stay_callbacks()
        # Sync dynamic body positions back to transforms
        for rb in self._body_map.values():
            if rb._body.body_type == pymunk.Body.DYNAMIC:
                rb._sync_to_transform()

    @staticmethod
    def _contact_key(rb_a: 'Rigidbody2D', rb_b: 'Rigidbody2D') -> tuple[int, int]:
        a, b = id(rb_a._body), id(rb_b._body)
        return (min(a, b), max(a, b))

    def _dispatch_stay_callbacks(self) -> None:
        """Dispatch Stay callbacks for all active contacts."""
        from src.engine.core import MonoBehaviour
        for (id_a, id_b), is_trigger in list(self._active_contacts.items()):
            rb_a = self._body_map.get(id_a)
            rb_b = self._body_map.get(id_b)
            if rb_a is None or rb_b is None:
                continue
            # Unity skips callbacks for inactive GameObjects
            if not rb_a.game_object.active or not rb_b.game_object.active:
                continue
            if is_trigger:
                for comp in rb_a.game_object.get_components(MonoBehaviour):
                    comp.on_trigger_stay_2d(rb_b.game_object)
                for comp in rb_b.game_object.get_components(MonoBehaviour):
                    comp.on_trigger_stay_2d(rb_a.game_object)
            else:
                col_a = Collision2D(game_object=rb_b.game_object)
                col_b = Collision2D(game_object=rb_a.game_object)
                for comp in rb_a.game_object.get_components(MonoBehaviour):
                    comp.on_collision_stay_2d(col_a)
                for comp in rb_b.game_object.get_components(MonoBehaviour):
                    comp.on_collision_stay_2d(col_b)

    def _get_rb_from_body(self, body: pymunk.Body) -> 'Rigidbody2D | None':
        return self._body_map.get(id(body))

    def _on_collision_begin(self, arbiter: pymunk.Arbiter, space, data) -> None:
        shape_a, shape_b = arbiter.shapes
        rb_a = self._get_rb_from_body(shape_a.body)
        rb_b = self._get_rb_from_body(shape_b.body)

        is_trigger = self.is_trigger(shape_a) or self.is_trigger(shape_b)

        if rb_a and rb_b:
            # Unity skips collision callbacks for inactive GameObjects
            if not rb_a.game_object.active or not rb_b.game_object.active:
                if is_trigger:
                    arbiter.process_collision = False
                return
            key = self._contact_key(rb_a, rb_b)
            if is_trigger:
                self._active_contacts[key] = True
                self._dispatch_trigger_enter(rb_a, rb_b)
                arbiter.process_collision = False  # Triggers don't resolve physics
            else:
                self._active_contacts[key] = False
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
            key = self._contact_key(rb_a, rb_b)
            self._active_contacts.pop(key, None)
            if is_trigger:
                self._dispatch_trigger_exit(rb_a, rb_b)
            else:
                self._dispatch_collision_exit(rb_a, rb_b)

    def _dispatch_collision_enter(self, rb_a: 'Rigidbody2D', rb_b: 'Rigidbody2D',
                                   arbiter: pymunk.Arbiter) -> None:
        from src.engine.core import MonoBehaviour
        # Unity skips callbacks for inactive GameObjects
        if not rb_a.game_object.active or not rb_b.game_object.active:
            return

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
        if not rb_a.game_object.active or not rb_b.game_object.active:
            return

        collision_for_a = Collision2D(game_object=rb_b.game_object)
        collision_for_b = Collision2D(game_object=rb_a.game_object)

        for comp in rb_a.game_object.get_components(MonoBehaviour):
            comp.on_collision_exit_2d(collision_for_a)
        for comp in rb_b.game_object.get_components(MonoBehaviour):
            comp.on_collision_exit_2d(collision_for_b)

    def _dispatch_trigger_enter(self, rb_a: 'Rigidbody2D', rb_b: 'Rigidbody2D') -> None:
        from src.engine.core import MonoBehaviour
        if not rb_a.game_object.active or not rb_b.game_object.active:
            return
        for comp in rb_a.game_object.get_components(MonoBehaviour):
            comp.on_trigger_enter_2d(rb_b.game_object)
        for comp in rb_b.game_object.get_components(MonoBehaviour):
            comp.on_trigger_enter_2d(rb_a.game_object)

    def _dispatch_trigger_exit(self, rb_a: 'Rigidbody2D', rb_b: 'Rigidbody2D') -> None:
        from src.engine.core import MonoBehaviour
        if not rb_a.game_object.active or not rb_b.game_object.active:
            return
        for comp in rb_a.game_object.get_components(MonoBehaviour):
            comp.on_trigger_exit_2d(rb_b.game_object)
        for comp in rb_b.game_object.get_components(MonoBehaviour):
            comp.on_trigger_exit_2d(rb_a.game_object)


class Physics2D:
    """Unity-compatible static class for 2D physics queries."""

    @staticmethod
    def raycast(origin: Vector2, direction: Vector2, distance: float = math.inf,
                layer_mask: int = -1) -> RaycastHit2D | None:
        """Cast a ray and return the first hit, or None."""
        pm = PhysicsManager.instance()
        d = direction.normalized
        end = Vector2(origin.x + d.x * distance, origin.y + d.y * distance)
        results = pm._space.segment_query(
            (origin.x, origin.y), (end.x, end.y), 0.0, pymunk.ShapeFilter()
        )
        if not results:
            return None
        # Find closest
        best = None
        best_dist = math.inf
        for info in results:
            if info.shape is None:
                continue
            dist = info.alpha * distance if distance != math.inf else info.alpha * 1e6
            if dist < best_dist:
                best_dist = dist
                best = info
        if best is None:
            return None

        hit_point = Vector2(best.point[0], best.point[1])
        hit_normal = Vector2(best.normal[0], best.normal[1])
        actual_dist = Vector2.distance(origin, hit_point)

        # Resolve collider/rigidbody/transform from shape
        collider_comp, rb_comp, transform_comp = Physics2D._resolve_components(best.shape, pm)

        return RaycastHit2D(
            point=hit_point,
            normal=hit_normal,
            distance=actual_dist,
            collider=collider_comp,
            rigidbody=rb_comp,
            transform=transform_comp,
        )

    @staticmethod
    def raycast_all(origin: Vector2, direction: Vector2, distance: float = math.inf,
                    layer_mask: int = -1) -> list[RaycastHit2D]:
        """Cast a ray and return all hits."""
        pm = PhysicsManager.instance()
        d = direction.normalized
        end = Vector2(origin.x + d.x * distance, origin.y + d.y * distance)
        results = pm._space.segment_query(
            (origin.x, origin.y), (end.x, end.y), 0.0, pymunk.ShapeFilter()
        )
        hits = []
        for info in results:
            if info.shape is None:
                continue
            hit_point = Vector2(info.point[0], info.point[1])
            hit_normal = Vector2(info.normal[0], info.normal[1])
            actual_dist = Vector2.distance(origin, hit_point)
            collider_comp, rb_comp, transform_comp = Physics2D._resolve_components(info.shape, pm)
            hits.append(RaycastHit2D(
                point=hit_point, normal=hit_normal, distance=actual_dist,
                collider=collider_comp, rigidbody=rb_comp, transform=transform_comp,
            ))
        hits.sort(key=lambda h: h.distance)
        return hits

    @staticmethod
    def overlap_circle(point: Vector2, radius: float, layer_mask: int = -1) -> 'Collider2D | None':
        """Check if any non-trigger collider overlaps a circle. Returns first found or None."""
        pm = PhysicsManager.instance()
        query = pm._space.point_query(
            (point.x, point.y), radius, pymunk.ShapeFilter()
        )
        for info in query:
            if info.shape is None:
                continue
            collider_comp, _, _ = Physics2D._resolve_components(info.shape, pm)
            if collider_comp is None:
                continue
            if collider_comp.is_trigger:
                continue
            if layer_mask != -1:
                go_layer = collider_comp.game_object.layer
                if not (layer_mask & (1 << go_layer)):
                    continue
            return collider_comp
        return None

    @staticmethod
    def overlap_circle_all(point: Vector2, radius: float, layer_mask: int = -1) -> list:
        """Return all non-trigger colliders overlapping a circle, filtered by layer_mask."""
        pm = PhysicsManager.instance()
        query = pm._space.point_query(
            (point.x, point.y), radius, pymunk.ShapeFilter()
        )
        colliders = []
        for info in query:
            if info.shape is None:
                continue
            collider_comp, _, _ = Physics2D._resolve_components(info.shape, pm)
            if collider_comp is None:
                continue
            if collider_comp.is_trigger:
                continue
            if layer_mask != -1:
                go_layer = collider_comp.game_object.layer
                if not (layer_mask & (1 << go_layer)):
                    continue
            colliders.append(collider_comp)
        return colliders

    @staticmethod
    def overlap_box(point: Vector2, size: Vector2, angle: float = 0.0,
                    layer_mask: int = -1) -> 'Collider2D | None':
        """Check if any non-trigger collider overlaps a box. Returns first found or None.

        Matches Unity behavior: ignores trigger colliders and filters by layer_mask.
        """
        pm = PhysicsManager.instance()
        hw, hh = size.x / 2, size.y / 2
        bb = pymunk.BB(point.x - hw, point.y - hh, point.x + hw, point.y + hh)
        query = pm._space.bb_query(bb, pymunk.ShapeFilter())
        for shape in query:
            collider_comp, _, _ = Physics2D._resolve_components(shape, pm)
            if collider_comp is None:
                continue
            # Skip trigger colliders (Unity's Physics2D queries ignore triggers)
            if collider_comp.is_trigger:
                continue
            # Filter by layer mask
            if layer_mask != -1:
                go_layer = collider_comp.game_object.layer
                if not (layer_mask & (1 << go_layer)):
                    continue
            return collider_comp
        return None

    @staticmethod
    def overlap_box_all(point: Vector2, size: Vector2, angle: float = 0.0,
                        layer_mask: int = -1) -> list:
        """Return all non-trigger colliders overlapping a box, filtered by layer_mask."""
        pm = PhysicsManager.instance()
        hw, hh = size.x / 2, size.y / 2
        bb = pymunk.BB(point.x - hw, point.y - hh, point.x + hw, point.y + hh)
        query = pm._space.bb_query(bb, pymunk.ShapeFilter())
        colliders = []
        for shape in query:
            collider_comp, _, _ = Physics2D._resolve_components(shape, pm)
            if collider_comp is None:
                continue
            if collider_comp.is_trigger:
                continue
            if layer_mask != -1:
                go_layer = collider_comp.game_object.layer
                if not (layer_mask & (1 << go_layer)):
                    continue
            colliders.append(collider_comp)
        return colliders

    @staticmethod
    def box_cast(origin: Vector2, size: Vector2, angle: float,
                 direction: Vector2, distance: float,
                 layer_mask: int = -1) -> 'object | None':
        """Cast a box along a direction. Returns first non-trigger hit or None.

        Matches Unity's Physics2D.BoxCast(origin, size, angle, direction, distance, layerMask).
        Implemented as multiple overlap_box samples along the sweep path.
        """
        # Sample at intervals along the sweep direction
        steps = max(1, int(distance / 0.25))  # sample every 0.25 units
        for i in range(steps + 1):
            t = (i / steps) * distance if steps > 0 else 0
            check_x = origin.x + direction.x * t
            check_y = origin.y + direction.y * t
            hit = Physics2D.overlap_box(
                Vector2(check_x, check_y), size, angle, layer_mask
            )
            if hit is not None:
                return hit
        return None

    @staticmethod
    def _resolve_components(shape: pymunk.Shape, pm: PhysicsManager):
        """Resolve Collider2D, Rigidbody2D, Transform from a pymunk shape."""
        from src.engine.physics.collider import Collider2D
        rb = pm._get_rb_from_body(shape.body)
        if rb is None:
            return None, None, None
        go = rb.game_object
        collider = None
        for col in go.get_components(Collider2D):
            if col._shape is shape:
                collider = col
                break
        return collider, rb, go.transform


# Import here to avoid circular — used by type hints above
from src.engine.physics.rigidbody import Rigidbody2D  # noqa: E402, F401
