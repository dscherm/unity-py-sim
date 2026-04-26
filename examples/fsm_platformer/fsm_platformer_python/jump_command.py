"""Jump Command — applies upward impulse when grounded."""

from __future__ import annotations

from src.engine.math.vector import Vector2

from fsm_platformer_python.command import Command

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fsm_platformer_python.player_input_handler import PlayerInputHandler


class JumpCommand(Command):
    """Applies vertical jump force. Only valid when grounded."""

    def __init__(self, player_input_handler: PlayerInputHandler) -> None:
        super().__init__(player_input_handler)

    def is_valid(self) -> bool:
        return self.player_input_handler.is_grounded

    def do_before_entering(self) -> None:
        pass

    def act(self) -> None:
        player = self.player_input_handler
        if player.is_grounded:
            rb = player.rb
            rb.velocity = Vector2(rb.velocity.x, player.jump_force)
