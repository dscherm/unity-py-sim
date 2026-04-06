"""PowerPellet — large pellet that triggers frightened mode on ghosts.

Line-by-line port of PowerPellet.cs from zigurous/unity-pacman-tutorial.
"""

from pacman_python.pellet import Pellet


class PowerPellet(Pellet):
    duration: float = 8.0

    def eat(self) -> None:
        """Override: triggers frightened mode via GameManager."""
        from pacman_python.game_manager import GameManager
        if GameManager.instance is not None:
            GameManager.instance.power_pellet_eaten(self)
        else:
            # No GameManager yet — just deactivate
            self.game_object.active = False
