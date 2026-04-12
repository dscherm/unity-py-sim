from __future__ import annotations
"""Passage — tunnel teleporter connecting two sides of the maze.

Line-by-line port of Passage.cs from zigurous/unity-pacman-tutorial.

Note: Added _recent_teleports tracking because our physics engine fires
on_trigger_enter_2d on each physics step overlap, unlike Unity which only
fires on initial contact. This prevents the exit passage from immediately
re-teleporting the object back.
"""

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2
from src.engine.transform import Transform
from src.engine.time_manager import Time


# Shared across all passages — tracks (object_id, time) of recent teleports
_recent_teleports: dict[int, float] = {}
_TELEPORT_COOLDOWN: float = 0.5  # seconds


class Passage(MonoBehaviour):
    connection: Transform | None = None  # Transform of the exit passage

    def on_trigger_enter_2d(self, other) -> None:
        obj_id = id(other)
        now = Time.time

        # Skip if this object was recently teleported
        if obj_id in _recent_teleports:
            if now - _recent_teleports[obj_id] < _TELEPORT_COOLDOWN:
                return

        _recent_teleports[obj_id] = now

        position = Vector2(
            self.connection.position.x,
            self.connection.position.y,
        )
        other.transform.position = position
        # Also update the rigidbody so Movement.fixed_update doesn't overwrite
        from src.engine.physics.rigidbody import Rigidbody2D
        rb = other.get_component(Rigidbody2D)
        if rb is not None:
            rb.move_position(position)
