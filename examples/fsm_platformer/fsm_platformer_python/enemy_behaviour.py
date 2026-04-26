"""Enemy Behaviour — enemy AI MonoBehaviour with FSM (IdleState <-> WalkState)."""

from __future__ import annotations

from src.engine.core import MonoBehaviour
from src.engine.physics.rigidbody import Rigidbody2D

from fsm_platformer_python.fsm import FSM
from fsm_platformer_python.enemy_idle_state import EnemyIdleState
from fsm_platformer_python.enemy_walk_state import EnemyWalkState
from fsm_platformer_python.time_transition import TimeTransition


class EnemyBehaviour(MonoBehaviour):
    """Enemy controller with simple two-state FSM."""

    def __init__(self) -> None:
        super().__init__()
        self.idle_time: float = 2.0
        self.walk_time: float = 3.0
        self.walk_speed: float = 1.5
        self.patrol_min_x: float = -6.0
        self.patrol_max_x: float = 6.0

        self.rb: Rigidbody2D | None = None  # type: ignore[assignment]
        self._fsm: FSM | None = None

    def start(self) -> None:
        self.rb = self.get_component(Rigidbody2D)
        self.rb._sync_from_transform()

        # Create states
        idle_state = EnemyIdleState()
        walk_state = EnemyWalkState(self.walk_speed)

        # Transitions
        idle_state.add_transition(TimeTransition(walk_state, self.idle_time))
        walk_state.add_transition(TimeTransition(idle_state, self.walk_time))

        # Build FSM
        self._fsm = FSM()
        self._fsm.add_state(idle_state)
        self._fsm.add_state(walk_state)

    def update(self) -> None:
        self._fsm.update(self)

    @property
    def state_name(self) -> str:
        """Return the current FSM state class name for display."""
        if self._fsm and self._fsm.current_state:
            return type(self._fsm.current_state).__name__
        return "None"
