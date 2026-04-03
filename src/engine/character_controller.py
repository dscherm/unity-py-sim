"""2D Character Controller — raycast-based movement with ground detection.

Replaces raw Rigidbody2D.velocity manipulation for platformers.
Uses raycasts for collision detection, supporting slopes and one-way platforms.

Usage:
    cc = go.add_component(CharacterController2D)
    cc.skin_width = 0.02
    cc.slope_limit = 45
    # In update:
    cc.move(Vector2(h * speed, velocity_y) * Time.delta_time)
    if cc.is_grounded:
        velocity_y = 0
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.engine.core import Component
from src.engine.math.vector import Vector2
from src.engine.physics.physics_manager import Physics2D, RaycastHit2D


@dataclass
class ControllerColliderHit:
    """Data passed to on_controller_collider_hit callbacks."""
    point: Vector2
    normal: Vector2
    move_direction: Vector2
    game_object: object | None = None


class CharacterController2D(Component):
    """Raycast-based 2D character controller."""

    def __init__(self):
        super().__init__()
        self.skin_width: float = 0.02
        self.slope_limit: float = 45.0  # degrees
        self.step_offset: float = 0.1
        self.ground_layer_mask: int = -1
        self.horizontal_ray_count: int = 3
        self.vertical_ray_count: int = 3
        self.one_way_platform_tag: str = "OneWayPlatform"

        self._is_grounded: bool = False
        self._is_colliding_above: bool = False
        self._is_colliding_left: bool = False
        self._is_colliding_right: bool = False
        self._velocity: Vector2 = Vector2(0, 0)
        self._ground_normal: Vector2 = Vector2(0, 1)

        self.on_controller_collider_hit: list = []  # list of callables

    @property
    def is_grounded(self) -> bool:
        return self._is_grounded

    @property
    def is_colliding_above(self) -> bool:
        return self._is_colliding_above

    @property
    def is_colliding_left(self) -> bool:
        return self._is_colliding_left

    @property
    def is_colliding_right(self) -> bool:
        return self._is_colliding_right

    @property
    def velocity(self) -> Vector2:
        return self._velocity

    @property
    def ground_normal(self) -> Vector2:
        return self._ground_normal

    def move(self, motion: Vector2) -> None:
        """Move the controller with collision detection."""
        self._is_grounded = False
        self._is_colliding_above = False
        self._is_colliding_left = False
        self._is_colliding_right = False
        self._velocity = motion

        pos = Vector2(self.transform.position.x, self.transform.position.y)

        # Vertical movement
        if abs(motion.y) > 0.001:
            pos = self._move_vertical(pos, motion.y)

        # Horizontal movement
        if abs(motion.x) > 0.001:
            pos = self._move_horizontal(pos, motion.x)

        # Ground check (even when not moving vertically)
        if not self._is_grounded:
            self._check_ground(pos)

        self.transform.position = pos

    def _move_vertical(self, pos: Vector2, dy: float) -> Vector2:
        """Handle vertical movement with collision."""
        direction = Vector2(0, 1 if dy > 0 else -1)
        distance = abs(dy) + self.skin_width
        origin = Vector2(pos.x, pos.y)

        hit = Physics2D.raycast(origin, direction, distance, self.ground_layer_mask)
        if hit:
            # One-way platform: only collide from above
            if (direction.y < 0 and hit.game_object and
                hasattr(hit.game_object, 'tag') and
                hit.game_object.tag == self.one_way_platform_tag and dy > 0):
                return Vector2(pos.x, pos.y + dy)

            actual_dist = hit.distance - self.skin_width
            actual_dy = actual_dist * (1 if dy > 0 else -1)

            if dy < 0:
                self._is_grounded = True
                self._ground_normal = hit.normal if hit.normal else Vector2(0, 1)
            else:
                self._is_colliding_above = True

            self._fire_hit(hit, direction)
            return Vector2(pos.x, pos.y + actual_dy)

        return Vector2(pos.x, pos.y + dy)

    def _move_horizontal(self, pos: Vector2, dx: float) -> Vector2:
        """Handle horizontal movement with collision."""
        direction = Vector2(1 if dx > 0 else -1, 0)
        distance = abs(dx) + self.skin_width
        origin = Vector2(pos.x, pos.y)

        hit = Physics2D.raycast(origin, direction, distance, self.ground_layer_mask)
        if hit:
            # Check slope angle
            if hit.normal:
                slope_angle = math.degrees(math.acos(min(1.0, abs(hit.normal.y))))
                if slope_angle <= self.slope_limit and slope_angle > 0:
                    # Climb slope
                    move_dist = abs(dx)
                    slope_dy = math.sin(math.radians(slope_angle)) * move_dist
                    slope_dx = math.cos(math.radians(slope_angle)) * move_dist * (1 if dx > 0 else -1)
                    return Vector2(pos.x + slope_dx, pos.y + slope_dy)

            actual_dist = hit.distance - self.skin_width
            actual_dx = actual_dist * (1 if dx > 0 else -1)

            if dx > 0:
                self._is_colliding_right = True
            else:
                self._is_colliding_left = True

            self._fire_hit(hit, direction)
            return Vector2(pos.x + actual_dx, pos.y)

        return Vector2(pos.x + dx, pos.y)

    def _check_ground(self, pos: Vector2) -> None:
        """Raycast downward to check if grounded."""
        hit = Physics2D.raycast(
            Vector2(pos.x, pos.y),
            Vector2(0, -1),
            self.skin_width + 0.05,
            self.ground_layer_mask,
        )
        if hit:
            self._is_grounded = True
            self._ground_normal = hit.normal if hit.normal else Vector2(0, 1)

    def _fire_hit(self, hit: RaycastHit2D, direction: Vector2) -> None:
        """Notify listeners of a collision."""
        hit_data = ControllerColliderHit(
            point=hit.point if hit.point else Vector2(0, 0),
            normal=hit.normal if hit.normal else Vector2(0, 0),
            move_direction=direction,
            game_object=getattr(hit, 'game_object', None),
        )
        for callback in self.on_controller_collider_hit:
            callback(hit_data)
