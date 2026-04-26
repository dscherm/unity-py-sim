"""Node — maze intersection point that determines available directions.

Line-by-line port of Node.cs from zigurous/unity-pacman-tutorial.
"""

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2
from src.engine.physics.physics_manager import Physics2D, PhysicsManager
from src.engine.physics.collider import BoxCollider2D

# Layer index for obstacles (walls)
OBSTACLE_LAYER: int = 6


class Node(MonoBehaviour):
    obstacle_layer: int = OBSTACLE_LAYER
    available_directions: list[Vector2]

    def __init__(self) -> None:
        super().__init__()
        self.available_directions = []

    def start(self) -> None:
        self.available_directions.clear()

        # Determine available directions by box casting for walls
        self._check_available_direction(Vector2(0, 1))   # up
        self._check_available_direction(Vector2(0, -1))  # down
        self._check_available_direction(Vector2(-1, 0))  # left
        self._check_available_direction(Vector2(1, 0))   # right

    def _check_available_direction(self, direction: Vector2) -> None:
        """Check for wall 1 unit in the given direction via overlap_box."""
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

        # If no collider is hit then there is no obstacle in that direction
        if hit is None:
            self.available_directions.append(direction)
