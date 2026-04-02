"""Player Input Handler — main player controller MonoBehaviour.

Manages a 5-state FSM (IDLE, RUNNING, JUMPING, FALLING, LANDING) and
a CommandProcessor for walk/jump commands gated by FSM state.
"""

from __future__ import annotations

from src.engine.core import MonoBehaviour
from src.engine.physics.rigidbody import Rigidbody2D
from src.engine.input_manager import Input
from src.engine.math.vector import Vector2

from fsm_platformer_python.fsm import FSM
from fsm_platformer_python.command import CommandProcessor

# States
from fsm_platformer_python.player_idle_state import PlayerIdleState
from fsm_platformer_python.player_running_state import PlayerRunningState
from fsm_platformer_python.player_jumping_state import PlayerJumpingState
from fsm_platformer_python.player_falling_state import PlayerFallingState
from fsm_platformer_python.player_landing_state import PlayerLandingState

# Transitions
from fsm_platformer_python.input_transition import InputTransition
from fsm_platformer_python.no_input_transition import NoInputTransition
from fsm_platformer_python.jump_transition import JumpTransition
from fsm_platformer_python.fall_transition import FallTransition
from fsm_platformer_python.grounded_transition import GroundedTransition
from fsm_platformer_python.landing_timer_transition import LandingTimerTransition

# Commands
from fsm_platformer_python.walk_command import WalkCommand
from fsm_platformer_python.jump_command import JumpCommand


# Ground check threshold: if player Y is within this distance of ground surface,
# consider them grounded.
GROUND_CHECK_THRESHOLD = 0.15


class PlayerInputHandler(MonoBehaviour):
    """Player controller with FSM + Command pattern."""

    def __init__(self) -> None:
        super().__init__()
        self.move_speed: float = 3.0
        self.jump_force: float = 5.0
        self.horizontal_input: float = 0.0
        self.jump_pressed: bool = False
        self.is_grounded: bool = False
        self.ground_y: float = -3.0  # Set by scene setup

        self.rb: Rigidbody2D | None = None  # type: ignore[assignment]
        self._fsm: FSM | None = None
        self._command_processor: CommandProcessor | None = None
        self._walk_command: WalkCommand | None = None
        self._jump_command: JumpCommand | None = None

    def start(self) -> None:
        self.rb = self.get_component(Rigidbody2D)
        self.rb._sync_from_transform()

        # --- Create states ---
        idle_state = PlayerIdleState()
        running_state = PlayerRunningState()
        jumping_state = PlayerJumpingState()
        falling_state = PlayerFallingState()
        landing_state = PlayerLandingState()

        # --- Create transitions ---
        # IDLE transitions: input -> RUNNING, jump -> JUMPING
        idle_state.add_transition(JumpTransition(jumping_state, self))
        idle_state.add_transition(InputTransition(running_state, self))

        # RUNNING transitions: jump -> JUMPING, no input -> IDLE
        running_state.add_transition(JumpTransition(jumping_state, self))
        running_state.add_transition(NoInputTransition(idle_state, self))

        # JUMPING transitions: fall when vy <= 0 -> FALLING
        jumping_state.add_transition(FallTransition(falling_state, self))

        # FALLING transitions: grounded -> LANDING
        falling_state.add_transition(GroundedTransition(landing_state, self))

        # LANDING transitions: timer -> IDLE
        landing_state.add_transition(LandingTimerTransition(idle_state))

        # --- Build FSM (first state = initial) ---
        self._fsm = FSM()
        self._fsm.add_state(idle_state)
        self._fsm.add_state(running_state)
        self._fsm.add_state(jumping_state)
        self._fsm.add_state(falling_state)
        self._fsm.add_state(landing_state)

        # --- Commands ---
        self._walk_command = WalkCommand(self)
        self._jump_command = JumpCommand(self)
        self._command_processor = CommandProcessor()

    def update(self) -> None:
        # Read input
        self.horizontal_input = Input.get_axis("Horizontal")
        self.jump_pressed = Input.get_key_down("space")

        # Ground check: compare player Y position to ground surface
        player_y = self.transform.position.y
        # Player bottom edge is approximately at position.y - half_height
        # For a unit-sized player (1x1), half_height = 0.5
        player_bottom = player_y - 0.5
        self.is_grounded = player_bottom <= self.ground_y + GROUND_CHECK_THRESHOLD

        # Update FSM
        self._fsm.update(self)

        # Gate commands by FSM state
        current = self._fsm.current_state
        if isinstance(current, (PlayerIdleState, PlayerRunningState)):
            # Allow walk and jump commands on ground
            if self.horizontal_input != 0:
                self._command_processor.execute(self._walk_command)
            elif self._command_processor.current_command == self._walk_command:
                self._command_processor.execute(None)

            if self.jump_pressed:
                self._command_processor.execute(self._jump_command)
        elif isinstance(current, PlayerJumpingState):
            # Jump command applies force on first frame, then let physics handle it
            pass
        elif isinstance(current, PlayerFallingState):
            # No commands while falling — FSM states handle air control
            if self._command_processor.current_command is not None:
                self._command_processor.execute(None)
        elif isinstance(current, PlayerLandingState):
            # No commands during landing
            if self._command_processor.current_command is not None:
                self._command_processor.execute(None)

        # Tick the active command
        self._command_processor.act()

    @property
    def state_name(self) -> str:
        """Return the current FSM state class name for display."""
        if self._fsm and self._fsm.current_state:
            return type(self._fsm.current_state).__name__
        return "None"
