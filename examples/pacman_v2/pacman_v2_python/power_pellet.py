"""PowerPellet — triggers frightened mode on all ghosts.

Port of zigurous PowerPellet.cs. Inherits from Pellet.
"""

from .pellet import Pellet


class PowerPellet(Pellet):
    points: int = 50
    duration: float = 8.0

    def eat(self) -> None:
        from .game_manager import GameManager
        if GameManager.instance:
            GameManager.instance.power_pellet_eaten(self)
