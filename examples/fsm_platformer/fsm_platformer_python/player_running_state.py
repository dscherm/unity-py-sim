"""Player Running State — horizontal movement active."""

from __future__ import annotations

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2

from fsm_platformer_python.fsm import FSMState


class PlayerRunningState(FSMState):
    """Player is moving horizontally on the ground."""

    def act(self, owner: MonoBehaviour) -> None:
        from fsm_platformer_python.player_input_handler import PlayerInputHandler
        player: PlayerInputHandler = owner  # type: ignore

        direction = player.horizontal_input
        rb = player.rb
        rb.velocity = Vector2(direction * player.move_speed, rb.velocity.y)
