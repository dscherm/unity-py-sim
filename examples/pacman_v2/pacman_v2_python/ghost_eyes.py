"""GhostEyes — visual-only sprite swap based on movement direction.

Port of zigurous GhostEyes.cs. Renders on a child GameObject.
"""

import pygame

from src.engine.core import MonoBehaviour
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.math.vector import Vector2


class GhostEyes(MonoBehaviour):
    sprite_up: pygame.Surface | None = None
    sprite_down: pygame.Surface | None = None
    sprite_left: pygame.Surface | None = None
    sprite_right: pygame.Surface | None = None

    _sprite_renderer: SpriteRenderer | None = None
    _movement: 'Movement | None' = None

    def awake(self) -> None:
        self._sprite_renderer = self.get_component(SpriteRenderer)
        # Get Movement from parent
        parent = self.transform.parent
        if parent:
            from .movement import Movement
            self._movement = parent.game_object.get_component(Movement)

    def update(self) -> None:
        if self._sprite_renderer is None or self._movement is None:
            return

        d = self._movement.direction
        if d.y > 0:
            self._sprite_renderer.sprite = self.sprite_up
        elif d.y < 0:
            self._sprite_renderer.sprite = self.sprite_down
        elif d.x < 0:
            self._sprite_renderer.sprite = self.sprite_left
        elif d.x > 0:
            self._sprite_renderer.sprite = self.sprite_right
