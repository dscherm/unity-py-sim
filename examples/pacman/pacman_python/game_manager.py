from __future__ import annotations
"""GameManager — singleton managing score, lives, and game flow.

Line-by-line port of GameManager.cs from zigurous/unity-pacman-tutorial.
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.input_manager import Input


class GameManager(MonoBehaviour):
    instance: 'GameManager | None' = None

    score: int = 0
    lives: int = 3
    _ghost_multiplier: int = 1

    # Assigned in run_pacman.py
    pacman: object | None = None   # Pacman component
    ghosts: list = None            # List of Ghost components
    _all_pellets: list = None      # Snapshot of all pellet GOs

    def __init__(self) -> None:
        super().__init__()
        self.ghosts = []
        self._all_pellets = []

    def awake(self) -> None:
        if GameManager.instance is not None:
            self.game_object.active = False
            return
        GameManager.instance = self

    def on_destroy(self) -> None:
        if GameManager.instance is self:
            GameManager.instance = None

    def start(self) -> None:
        # Snapshot all pellet GOs at start (before any are deactivated)
        self._all_pellets = (
            GameObject.find_game_objects_with_tag("Pellet")
            + GameObject.find_game_objects_with_tag("PowerPellet")
        )
        self.new_game()

    def update(self) -> None:
        if self.lives <= 0 and Input.get_key_down("return"):
            self.new_game()

    def new_game(self) -> None:
        self._set_score(0)
        self._set_lives(3)
        self.new_round()

    def new_round(self) -> None:
        # Reactivate all pellets
        for go in self._all_pellets:
            go.active = True
        self.reset_state()

    def reset_state(self) -> None:
        for ghost in self.ghosts:
            ghost.reset_state()
        if self.pacman is not None:
            self.pacman.reset_state()

    def game_over(self) -> None:
        for ghost in self.ghosts:
            ghost.game_object.active = False
        if self.pacman is not None:
            self.pacman.game_object.active = False

    def _set_lives(self, lives: int) -> None:
        self.lives = lives
        self._update_title()

    def _set_score(self, score: int) -> None:
        self.score = score
        self._update_title()

    def pacman_eaten(self) -> None:
        if self.pacman is not None:
            self.pacman.death_sequence_start()

        self._set_lives(self.lives - 1)

        if self.lives > 0:
            self.invoke("reset_state", 3.0)
        else:
            self.game_over()

    def ghost_eaten(self, ghost) -> None:
        points = ghost.points * self._ghost_multiplier
        self._set_score(self.score + points)
        self._ghost_multiplier *= 2
        # Send ghost home (matches GhostFrightened.Eaten() in C# reference)
        ghost.frightened.eaten()

    def pellet_eaten(self, pellet) -> None:
        pellet.game_object.active = False
        self._set_score(self.score + pellet.points)

        if not self.has_remaining_pellets():
            if self.pacman is not None:
                self.pacman.game_object.active = False
            self.invoke("new_round", 3.0)

    def power_pellet_eaten(self, pellet) -> None:
        # Enable frightened mode on all ghosts
        for ghost in self.ghosts:
            ghost.frightened.enable(pellet.duration)

        self.pellet_eaten(pellet)
        # Reset multiplier after power pellet duration expires
        self.cancel_invoke("reset_ghost_multiplier")
        self.invoke("reset_ghost_multiplier", pellet.duration)

    def has_remaining_pellets(self) -> bool:
        for go in self._all_pellets:
            if go.active:
                return True
        return False

    def reset_ghost_multiplier(self) -> None:
        self._ghost_multiplier = 1

    def _update_title(self) -> None:
        try:
            import pygame
            pygame.display.set_caption(
                f"Pacman — Score: {self.score}  Lives: {self.lives}"
            )
        except Exception:
            pass
