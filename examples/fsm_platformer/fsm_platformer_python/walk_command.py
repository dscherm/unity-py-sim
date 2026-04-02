"""Walk Command — moves the player horizontally and flips sprite direction."""

from __future__ import annotations

from src.engine.math.vector import Vector2, Vector3

from fsm_platformer_python.command import Command

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fsm_platformer_python.player_input_handler import PlayerInputHandler


class WalkCommand(Command):
    """Applies horizontal movement based on input direction."""

    def __init__(self, player_input_handler: PlayerInputHandler) -> None:
        super().__init__(player_input_handler)

    def is_valid(self) -> bool:
        return True

    def do_before_entering(self) -> None:
        h = self.player_input_handler.horizontal_input
        scale = self.player_input_handler.transform.local_scale

        # Flip sprite to face movement direction
        if (h > 0 and scale.x < 0) or (h < 0 and scale.x > 0):
            self.player_input_handler.transform.local_scale = Vector3(
                -scale.x, scale.y, scale.z
            )

    def act(self) -> None:
        player = self.player_input_handler
        direction = 1.0 if player.transform.local_scale.x > 0 else -1.0
        rb = player.rb
        rb.velocity = Vector2(direction * player.move_speed, rb.velocity.y)

    def do_before_leaving(self) -> None:
        rb = self.player_input_handler.rb
        rb.velocity = Vector2(0, rb.velocity.y)
