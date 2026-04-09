"""Pipes — Flappy Bird pipe obstacle.

Line-by-line translation of Pipes.cs from zigurous/unity-flappy-bird-tutorial.
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.transform import Transform
from src.engine.rendering.camera import Camera
from src.engine.time_manager import Time
from src.engine.math.vector import Vector3


class Pipes(MonoBehaviour):

    def __init__(self) -> None:
        super().__init__()
        self.top: Transform | None = None       # public Transform top
        self.bottom: Transform | None = None    # public Transform bottom
        self.speed: float = 5.0
        self.gap: float = 3.0

        self._left_edge: float = 0.0

    def start(self) -> None:
        if Camera.main is not None:
            # Camera.main.ScreenToWorldPoint(Vector3.zero).x - 1f
            world_point = Camera.main.screen_to_world_point(Vector3.zero)
            self._left_edge = world_point.x - 1.0
        else:
            self._left_edge = -10.0

        if self.top is not None:
            self.top.position = self.top.position + Vector3.up * (self.gap / 2)
        if self.bottom is not None:
            self.bottom.position = self.bottom.position + Vector3.down * (self.gap / 2)

    def update(self) -> None:
        self.transform.position = self.transform.position + Vector3.left * (self.speed * Time.delta_time)

        if self.transform.position.x < self._left_edge:
            GameObject.destroy(self.game_object)
