"""FSM base classes — FSMState, FSMTransition, FSM.

These are game-specific pattern classes, not engine classes.
The FSM is generic: Act() takes MonoBehaviour so it works for
both Player and Enemy controllers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.engine.core import MonoBehaviour


class FSMState:
    """Base class for finite state machine states."""

    def __init__(self) -> None:
        self.transitions: list[FSMTransition] = []
        self.time_state: float = 0.0

    def add_transition(self, transition: FSMTransition) -> None:
        """Register a transition that can fire from this state."""
        self.transitions.append(transition)

    def check_transitions(self) -> FSMState | None:
        """Check all transitions; return the first valid target state, or None."""
        for t in self.transitions:
            if t.is_valid(self):
                return t.target_state
        return None

    def do_before_entering(self) -> None:
        """Called when the FSM transitions into this state. Resets time_state."""
        self.time_state = 0.0

    def do_before_leaving(self) -> None:
        """Called when the FSM transitions out of this state."""
        pass

    def act(self, owner: MonoBehaviour) -> None:
        """Execute per-frame logic for this state.

        Args:
            owner: The MonoBehaviour that owns this FSM (e.g. PlayerInputHandler
                   or EnemyBehaviour). Subclasses cast as needed.
        """
        raise NotImplementedError


class FSMTransition:
    """Base class for transitions between FSM states."""

    def __init__(self, target_state: FSMState) -> None:
        self.target_state: FSMState = target_state

    def is_valid(self, current_state: FSMState) -> bool:
        """Return True if this transition should fire from the current state."""
        raise NotImplementedError


class FSM:
    """Finite state machine that manages a set of states."""

    def __init__(self) -> None:
        self.states: list[FSMState] = []
        self.current_state: FSMState | None = None

    def add_state(self, state: FSMState) -> None:
        """Add a state. The first state added becomes the initial state."""
        self.states.append(state)
        if self.current_state is None:
            self.current_state = state
            self.current_state.do_before_entering()

    def update(self, owner: MonoBehaviour) -> None:
        """Tick the FSM: accumulate time, check transitions, call act().

        Args:
            owner: The MonoBehaviour that owns this FSM.
        """
        if self.current_state is None:
            return

        from src.engine.time_manager import Time
        self.current_state.time_state += Time.delta_time

        next_state = self.current_state.check_transitions()
        if next_state is not None:
            self.current_state.do_before_leaving()
            self.current_state = next_state
            self.current_state.do_before_entering()

        self.current_state.act(owner)
