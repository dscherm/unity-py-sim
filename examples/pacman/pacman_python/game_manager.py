"""GameManager — singleton managing score, lives, and game flow.

Line-by-line port of GameManager.cs from zigurous/unity-pacman-tutorial.
Task 3 implements: pellet_eaten, power_pellet_eaten, has_remaining_pellets.
Task 5 will add: lives, ghost multiplier, pacman_eaten, ghost_eaten, UI.
"""

from src.engine.core import MonoBehaviour, GameObject


class GameManager(MonoBehaviour):
    instance: 'GameManager | None' = None

    score: int = 0
    lives: int = 3
    _ghost_multiplier: int = 1

    # Assigned in run_pacman.py
    pacman: object | None = None  # Pacman component
    pellets_parent: GameObject | None = None  # Parent GO holding all pellets

    def awake(self) -> None:
        if GameManager.instance is not None:
            self.game_object.active = False
            return
        GameManager.instance = self

    def on_destroy(self) -> None:
        if GameManager.instance is self:
            GameManager.instance = None

    def start(self) -> None:
        self.new_game()

    def new_game(self) -> None:
        self.score = 0
        self.lives = 3
        self.new_round()

    def new_round(self) -> None:
        # Reactivate all pellets
        for go in GameObject.find_game_objects_with_tag("Pellet"):
            go.active = True
        for go in GameObject.find_game_objects_with_tag("PowerPellet"):
            go.active = True
        self._update_title()

    def pellet_eaten(self, pellet) -> None:
        pellet.game_object.active = False
        self.score += pellet.points
        self._update_title()

        if not self.has_remaining_pellets():
            self.new_round()

    def power_pellet_eaten(self, pellet) -> None:
        # TODO Task 4: enable frightened mode on all ghosts
        # for ghost in ghosts: ghost.frightened.enable(pellet.duration)
        self.pellet_eaten(pellet)
        self._ghost_multiplier = 1

    def has_remaining_pellets(self) -> bool:
        for go in GameObject.find_game_objects_with_tag("Pellet"):
            if go.active:
                return True
        for go in GameObject.find_game_objects_with_tag("PowerPellet"):
            if go.active:
                return True
        return False

    def _update_title(self) -> None:
        try:
            import pygame
            pygame.display.set_caption(
                f"Pacman — Score: {self.score}  Lives: {self.lives}"
            )
        except Exception:
            pass
