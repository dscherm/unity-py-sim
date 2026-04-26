"""Command pattern base classes — Command and CommandProcessor.

Commands encapsulate player actions (walk, jump) and are gated by
the FSM state via is_valid().
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fsm_platformer_python.player_input_handler import PlayerInputHandler


class Command:
    """Abstract command that operates on a PlayerInputHandler."""

    def __init__(self, player_input_handler: PlayerInputHandler) -> None:
        self.player_input_handler: PlayerInputHandler = player_input_handler

    def is_valid(self) -> bool:
        """Return True if this command can execute in the current game state."""
        raise NotImplementedError

    def do_before_entering(self) -> None:
        """Called when this command becomes the active command."""
        pass

    def act(self) -> None:
        """Execute per-frame logic for this command."""
        raise NotImplementedError

    def do_before_leaving(self) -> None:
        """Called when this command is replaced by another."""
        pass


class CommandProcessor:
    """Manages the currently active command."""

    def __init__(self) -> None:
        self.current_command: Command | None = None

    def execute(self, command: Command | None) -> None:
        """Switch to a new command, calling lifecycle hooks."""
        if command is None:
            if self.current_command is not None:
                self.current_command.do_before_leaving()
            self.current_command = None
            return

        if not command.is_valid():
            return

        if self.current_command is not None:
            self.current_command.do_before_leaving()

        self.current_command = command
        self.current_command.do_before_entering()

    def act(self) -> None:
        """Tick the current command."""
        if self.current_command is not None:
            self.current_command.act()
