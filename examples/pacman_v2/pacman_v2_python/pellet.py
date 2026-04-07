"""Pellet — collectible that notifies GameManager when eaten by Pacman.

Port of zigurous Pellet.cs. Trigger collider, deactivated on pickup.
"""

from src.engine.core import MonoBehaviour


PACMAN_LAYER: int = 3


class Pellet(MonoBehaviour):
    points: int = 10

    def eat(self) -> None:
        from .game_manager import GameManager
        if GameManager.instance:
            GameManager.instance.pellet_eaten(self)

    def on_trigger_enter_2d(self, other) -> None:
        other_go = getattr(other, "game_object", other)
        if other_go.layer == PACMAN_LAYER:
            self.eat()
