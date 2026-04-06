"""Pellet — collectible dot that awards points when eaten by Pacman.

Line-by-line port of Pellet.cs from zigurous/unity-pacman-tutorial.
"""

from src.engine.core import MonoBehaviour

# Pacman is on layer 7 (set in run_pacman.py)
PACMAN_LAYER: int = 7


class Pellet(MonoBehaviour):
    points: int = 10

    def eat(self) -> None:
        """Called when Pacman eats this pellet. GameManager handles scoring."""
        from pacman_python.game_manager import GameManager
        if GameManager.instance is not None:
            GameManager.instance.pellet_eaten(self)
        else:
            # No GameManager yet — just deactivate
            self.game_object.active = False

    def on_trigger_enter_2d(self, other) -> None:
        if other.layer == PACMAN_LAYER:
            self.eat()
