"""Passage — tunnel teleporter matching zigurous Passage.cs.

Simpler than v1: no cooldown tracking, just teleports on trigger enter.

Lesson applied: teleporting must sync Rigidbody2D (set rb.move_position too).
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2
from src.engine.physics.rigidbody import Rigidbody2D


class Passage(MonoBehaviour):
    connection: GameObject | None = None  # The other end of the passage

    def on_trigger_enter_2d(self, other) -> None:
        other_go = getattr(other, "game_object", other)
        if self.connection is None:
            return

        conn_pos = self.connection.transform.position
        new_pos = Vector2(conn_pos.x, conn_pos.y)

        other_go.transform.position = new_pos

        # Sync rigidbody to prevent stale position overwrite
        rb = other_go.get_component(Rigidbody2D)
        if rb:
            rb.move_position(new_pos)
