"""Invader — single alien with score value and 2-frame color animation.

Maps to: zigurous/Invader.cs
"""

from src.engine.core import MonoBehaviour
from src.engine.time_manager import Time
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.math.vector import Vector2


class Invader(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.score: int = 10
        self.animation_colors: list[tuple] = [(255, 255, 255), (200, 200, 255)]
        self.animation_time: float = 1.0
        self._frame: int = 0
        self._timer: float = 0.0

    def update(self):
        self._timer += Time.delta_time
        if self._timer >= self.animation_time:
            self._timer -= self.animation_time
            self._frame = (self._frame + 1) % len(self.animation_colors)
            sr = self.get_component(SpriteRenderer)
            if sr:
                sr.color = self.animation_colors[self._frame]

    def on_trigger_enter_2d(self, other):
        from space_invaders_python.player import LAYER_LASER, LAYER_BOUNDARY

        if other.layer == LAYER_LASER:
            from space_invaders_python.game_manager import GameManager
            if GameManager._instance:
                GameManager._instance.on_invader_killed(self)
        elif other.layer == LAYER_BOUNDARY:
            from space_invaders_python.game_manager import GameManager
            if GameManager._instance:
                GameManager._instance.on_boundary_reached()
