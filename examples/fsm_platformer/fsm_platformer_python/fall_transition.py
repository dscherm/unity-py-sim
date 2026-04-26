"""Fall Transition — JUMPING -> FALLING when vertical velocity <= 0."""

from __future__ import annotations

from fsm_platformer_python.fsm import FSMState, FSMTransition


class FallTransition(FSMTransition):
    """Fires when the player's vertical velocity becomes non-positive (apex of jump)."""

    def __init__(self, target_state: FSMState, player_input_handler) -> None:
        super().__init__(target_state)
        self.player = player_input_handler

    def is_valid(self, current_state: FSMState) -> bool:
        return self.player.rb.velocity.y <= 0
