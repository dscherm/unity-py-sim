"""Passage — tunnel teleporter connecting two sides of the maze.

Line-by-line port of Passage.cs from zigurous/unity-pacman-tutorial.
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2
from src.engine.transform import Transform


class Passage(MonoBehaviour):
    connection: Transform | None = None  # Transform of the exit passage

    def on_trigger_enter_2d(self, other) -> None:
        position = Vector2(
            self.connection.position.x,
            self.connection.position.y,
        )
        other.game_object.transform.position = position
