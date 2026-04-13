from __future__ import annotations
"""GameManager — singleton managing score, lives, game flow.

Port of zigurous GameManager.cs. DefaultExecutionOrder(-100).

Lesson applied: pellet reactivation bug — new_round must set pellet.active = True.
Lesson applied: ghost multiplier resets when frightened mode starts.
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.time_manager import Time

from .ghost import Ghost
from .pellet import Pellet
from .power_pellet import PowerPellet
from .pacman import Pacman


class GameManager(MonoBehaviour):
    instance: 'GameManager | None' = None

    ghosts: list[Ghost]
    pacman: Pacman | None = None
    _all_pellets: list[Pellet]

    score: int = 0
    lives: int = 3
    ghost_multiplier: int = 1

    # Deferred action timer — avoids calling reset_state/game_over from within
    # a coroutine tick, which breaks coroutine list consistency in the engine.
    _deferred_action: str | None = None
    _deferred_timer: float = 0.0

    def __init__(self) -> None:
        super().__init__()
        self.ghosts = []
        self._all_pellets = []

    def awake(self) -> None:
        GameManager.instance = self

    def update(self) -> None:
        if self._deferred_action is not None:
            self._deferred_timer -= Time.delta_time
            if self._deferred_timer <= 0:
                action = self._deferred_action
                self._deferred_action = None
                getattr(self, action)()

    def start(self) -> None:
        self.new_game()

    def new_game(self) -> None:
        self.score = 0
        self.lives = 3
        self.new_round()

    def new_round(self) -> None:
        # Reactivate all pellets
        for pellet in self._all_pellets:
            pellet.game_object.active = True

        self.reset_state()

    def reset_state(self) -> None:
        for ghost in self.ghosts:
            ghost.reset_state()
        if self.pacman:
            self.pacman.reset_state()

    def game_over(self) -> None:
        for ghost in self.ghosts:
            ghost.game_object.active = False
        if self.pacman:
            self.pacman.game_object.active = False

    def pellet_eaten(self, pellet: Pellet) -> None:
        pellet.game_object.active = False
        self._set_score(self.score + pellet.points)

        if not self._has_remaining_pellets():
            # Hide Pacman until new round starts (matches V1 behavior)
            if self.pacman:
                self.pacman.game_object.active = False
            self._deferred_action = "new_round"
            self._deferred_timer = 3.0

    def power_pellet_eaten(self, pellet: PowerPellet) -> None:
        # Enable frightened mode on all ghosts
        for ghost in self.ghosts:
            if ghost.frightened:
                ghost.frightened.enable(pellet.duration)

        # Reset ghost multiplier
        self.ghost_multiplier = 1

        # Handle pellet deactivation and remaining check (same as regular pellet)
        self.pellet_eaten(pellet)

    def ghost_eaten(self, ghost: Ghost) -> None:
        self._set_score(self.score + ghost.points * self.ghost_multiplier)
        self.ghost_multiplier += 1
        if ghost.frightened:
            ghost.frightened.eat()

    def pacman_eaten(self) -> None:
        if self.pacman:
            self.pacman.death_sequence_start()

        for ghost in self.ghosts:
            ghost.game_object.active = False

        self.lives -= 1
        if self.lives > 0:
            self._deferred_action = "reset_state"
            self._deferred_timer = 3.0
        else:
            self._deferred_action = "game_over"
            self._deferred_timer = 3.0

    def _has_remaining_pellets(self) -> bool:
        for pellet in self._all_pellets:
            if pellet.game_object.active:
                return True
        return False

    def _set_score(self, value: int) -> None:
        self.score = value
        # Update window title as simple UI
        try:
            import pygame
            pygame.display.set_caption(f"Pacman V2 — Score: {self.score}  Lives: {self.lives}")
        except Exception:
            pass

    def register_pellet(self, pellet: Pellet) -> None:
        if pellet not in self._all_pellets:
            self._all_pellets.append(pellet)

    def register_ghost(self, ghost: Ghost) -> None:
        if ghost not in self.ghosts:
            self.ghosts.append(ghost)
