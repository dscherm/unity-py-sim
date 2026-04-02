"""Player Falling State — downward arc (vy <= 0)."""

from __future__ import annotations

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2

from fsm_platformer_python.fsm import FSMState


class PlayerFallingState(FSMState):
    """Player is falling downward."""

    def act(self, owner: MonoBehaviour) -> None:
        from fsm_platformer_python.player_input_handler import PlayerInputHandler
        player: PlayerInputHandler = owner  # type: ignore

        # Allow horizontal control while falling
        rb = player.rb
        h = player.horizontal_input
        rb.velocity = Vector2(h * player.move_speed, rb.velocity.y)
