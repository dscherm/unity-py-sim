from __future__ import annotations
"""Passage — tunnel teleporter connecting two sides of the maze.

Port of zigurous Passage.cs.

Lesson applied from v1: engine fires on_trigger_enter_2d every physics step
(not just initial contact like Unity). Must track recent teleports with cooldown
to prevent instant re-teleport at the exit passage.

Lesson applied from v1: teleporting must sync Rigidbody2D (rb.move_position)
or Movement.fixed_update overwrites position with stale pymunk body.
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2
from src.engine.physics.rigidbody import Rigidbody2D
from src.engine.time_manager import Time


# Shared across all passages — tracks (object_id, time) of recent teleports
_recent_teleports: dict[int, float] = {}
_TELEPORT_COOLDOWN: float = 0.5  # seconds


class Passage(MonoBehaviour):
    connection: GameObject | None = None

    def on_trigger_enter_2d(self, other) -> None:
        if self.connection is None:
            return

        other_go = getattr(other, "game_object", other)
        obj_id = id(other_go)
        now = Time.time

        # Skip if recently teleported (prevents instant re-teleport at exit)
        if obj_id in _recent_teleports:
            if now - _recent_teleports[obj_id] < _TELEPORT_COOLDOWN:
                return

        _recent_teleports[obj_id] = now

        conn_pos = self.connection.transform.position
        new_pos = Vector2(conn_pos.x, conn_pos.y)

        other_go.transform.position = new_pos

        # Sync rigidbody to prevent stale position overwrite
        rb = other_go.get_component(Rigidbody2D)
        if rb:
            rb.move_position(new_pos)
