"""Player Landing State — brief transient state on ground contact (0.1s)."""

from __future__ import annotations

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2

from fsm_platformer_python.fsm import FSMState


class PlayerLandingState(FSMState):
    """Player has just landed. Zeros horizontal velocity for 0.1s."""

    def do_before_entering(self) -> None:
        super().do_before_entering()

    def act(self, owner: MonoBehaviour) -> None:
        from fsm_platformer_python.player_input_handler import PlayerInputHandler
        player: PlayerInputHandler = owner  # type: ignore

        # Zero horizontal velocity during landing recovery
        rb = player.rb
        rb.velocity = Vector2(0, rb.velocity.y)
