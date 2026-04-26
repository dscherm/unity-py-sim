"""Node — intersection decision point for ghost AI.

Port of zigurous Node.cs. Placed at every intersection/turn in the maze.
Uses BoxCast to detect available directions at Start().
Ghosts use OnTriggerEnter2D to pick directions at nodes.
"""

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2
from src.engine.physics.physics_manager import Physics2D

from .movement import OBSTACLE_LAYER


class Node(MonoBehaviour):
    obstacle_layer: int = OBSTACLE_LAYER
    available_directions: list[Vector2]

    def __init__(self) -> None:
        super().__init__()
        self.available_directions = []

    def start(self) -> None:
        self.available_directions.clear()
        self._check_direction(Vector2(0, 1))   # up
        self._check_direction(Vector2(0, -1))  # down
        self._check_direction(Vector2(-1, 0))  # left
        self._check_direction(Vector2(1, 0))   # right

    def _check_direction(self, direction: Vector2) -> None:
        pos = self.transform.position
        check_pos = Vector2(
            pos.x + direction.x * 1.0,
            pos.y + direction.y * 1.0,
        )
        hit = Physics2D.overlap_box(
            point=check_pos,
            size=Vector2(0.5, 0.5),
            angle=0.0,
            layer_mask=1 << self.obstacle_layer,
        )
        if hit is None:
            self.available_directions.append(direction)
