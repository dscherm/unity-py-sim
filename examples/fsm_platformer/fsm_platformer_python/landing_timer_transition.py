"""Landing Timer Transition — LANDING -> IDLE after 0.1s."""

from __future__ import annotations

from fsm_platformer_python.fsm import FSMState, FSMTransition

LANDING_DURATION = 0.1


class LandingTimerTransition(FSMTransition):
    """Fires when the landing state has lasted at least LANDING_DURATION seconds."""

    def __init__(self, target_state: FSMState) -> None:
        super().__init__(target_state)

    def is_valid(self, current_state: FSMState) -> bool:
        return current_state.time_state >= LANDING_DURATION
