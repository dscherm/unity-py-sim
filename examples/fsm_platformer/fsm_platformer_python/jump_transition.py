"""Jump Transition — IDLE/RUNNING -> JUMPING when jump pressed and grounded."""

from __future__ import annotations

from fsm_platformer_python.fsm import FSMState, FSMTransition


class JumpTransition(FSMTransition):
    """Fires when the player presses jump while grounded."""

    def __init__(self, target_state: FSMState, player_input_handler) -> None:
        super().__init__(target_state)
        self.player = player_input_handler

    def is_valid(self, current_state: FSMState) -> bool:
        return self.player.jump_pressed and self.player.is_grounded
