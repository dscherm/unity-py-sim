"""GameManager — singleton managing score, lives, and game flow.

Line-by-line port of GameManager.cs from zigurous/unity-pacman-tutorial.
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.coroutine import WaitForSeconds


class GameManager(MonoBehaviour):
    instance: 'GameManager | None' = None

    score: int = 0
    lives: int = 3
    _ghost_multiplier: int = 1

    # Assigned in run_pacman.py
    pacman: object | None = None   # Pacman component
    ghosts: list = None            # List of Ghost components
    _all_pellets: list = None      # All pellet GOs (including inactive)

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
        from src.engine.input_manager import Input
        if self.lives <= 0 and Input.get_key_down("return"):
            self.new_game()

    def new_game(self) -> None:
        self.score = 0
        self.lives = 3
        self.new_round()

    def new_round(self) -> None:
        # Reactivate all pellets (use stored list — tag lookup skips inactive GOs)
        for go in self._all_pellets:
            go.active = True
        self.reset_state()
        self._update_title()

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
        self._update_title()

    def pellet_eaten(self, pellet) -> None:
        pellet.game_object.active = False
        self.score += pellet.points
        self._update_title()

        if not self.has_remaining_pellets():
            if self.pacman is not None:
                self.pacman.game_object.active = False
            self.start_coroutine(self._new_round_delay(3.0))

    def power_pellet_eaten(self, pellet) -> None:
        # Enable frightened mode on all ghosts
        for ghost in self.ghosts:
            ghost.frightened.enable_behavior(pellet.duration)

        self.pellet_eaten(pellet)
        self._ghost_multiplier = 1

    def ghost_eaten(self, ghost) -> None:
        points = ghost.points * self._ghost_multiplier
        self.score += points
        self._ghost_multiplier *= 2
        self._update_title()

    def pacman_eaten(self) -> None:
        if self.pacman is not None:
            self.pacman.death_sequence_start()

        self.lives -= 1
        self._update_title()

        if self.lives > 0:
            self.start_coroutine(self._reset_state_delay(3.0))
        else:
            self.game_over()

    def has_remaining_pellets(self) -> bool:
        for go in self._all_pellets:
            if go.active:
                return True
        return False

    def _new_round_delay(self, delay: float):
        yield WaitForSeconds(delay)
        self.new_round()

    def _reset_state_delay(self, delay: float):
        yield WaitForSeconds(delay)
        self.reset_state()

    def _update_title(self) -> None:
        try:
            import pygame
            pygame.display.set_caption(
                f"Pacman — Score: {self.score}  Lives: {self.lives}"
            )
        except Exception:
            pass
