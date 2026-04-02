"""Time Transition — fires after a configurable duration."""

from __future__ import annotations

from fsm_platformer_python.fsm import FSMState, FSMTransition


class TimeTransition(FSMTransition):
    """Fires when the current state has been active for at least `duration` seconds."""

    def __init__(self, target_state: FSMState, duration: float = 3.0) -> None:
        super().__init__(target_state)
        self.duration: float = duration

    def is_valid(self, current_state: FSMState) -> bool:
        return current_state.time_state >= self.duration
