"""Input Transition — IDLE -> RUNNING when horizontal input is non-zero."""

from __future__ import annotations

from fsm_platformer_python.fsm import FSMState, FSMTransition


class InputTransition(FSMTransition):
    """Fires when the player has horizontal input."""

    def __init__(self, target_state: FSMState, player_input_handler) -> None:
        super().__init__(target_state)
        self.player = player_input_handler

    def is_valid(self, current_state: FSMState) -> bool:
        return self.player.horizontal_input != 0
