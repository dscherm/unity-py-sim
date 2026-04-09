"""Parallax — Flappy Bird background scrolling.

Line-by-line translation of Parallax.cs from zigurous/unity-flappy-bird-tutorial.
Original uses MeshRenderer.material.mainTextureOffset for UV scrolling.
Python substitute: scroll the transform position and wrap around for seamless looping.
"""

from src.engine.core import MonoBehaviour
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.time_manager import Time
from src.engine.math.vector import Vector3


class Parallax(MonoBehaviour):

    def __init__(self) -> None:
        super().__init__()
        self.animation_speed: float = 1.0
        # Width of the parallax element in world units (for wrapping)
        self.wrap_width: float = 20.0
        self._start_x: float = 0.0

    def awake(self) -> None:
        self._start_x = self.transform.position.x

    def update(self) -> None:
        # Scroll left by animation_speed (matches UV offset scrolling direction)
        pos = self.transform.position
        new_x = pos.x - self.animation_speed * Time.delta_time
        # Wrap around when scrolled past one full width
        if new_x < self._start_x - self.wrap_width:
            new_x += self.wrap_width
        self.transform.position = Vector3(new_x, pos.y, pos.z)
