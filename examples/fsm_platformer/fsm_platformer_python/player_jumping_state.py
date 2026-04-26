"""Player Jumping State — upward arc after jump."""

from __future__ import annotations

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2

from fsm_platformer_python.fsm import FSMState


class PlayerJumpingState(FSMState):
    """Player is in the ascending portion of a jump."""

    def do_before_entering(self) -> None:
        super().do_before_entering()

    def act(self, owner: MonoBehaviour) -> None:
        from fsm_platformer_python.player_input_handler import PlayerInputHandler
        player: PlayerInputHandler = owner  # type: ignore

        # Allow horizontal control while jumping
        rb = player.rb
        h = player.horizontal_input
        rb.velocity = Vector2(h * player.move_speed, rb.velocity.y)
