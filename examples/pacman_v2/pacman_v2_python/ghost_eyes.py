from __future__ import annotations
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

    _parent_go: 'GameObject | None' = None

    def awake(self) -> None:
        self._sprite_renderer = self.get_component(SpriteRenderer)
        # Get Movement from parent
        parent = self.transform.parent
        if parent:
            self._parent_go = parent.game_object
            from .movement import Movement
            self._movement = parent.game_object.get_component(Movement)

    def update(self) -> None:
        # Hide if parent ghost is inactive (engine doesn't propagate active to children)
        if self._parent_go and not self._parent_go.active:
            if self._sprite_renderer:
                self._sprite_renderer.enabled = False
            return
        elif self._parent_go and self._parent_go.active:
            if self._sprite_renderer and not self._sprite_renderer.enabled:
                self._sprite_renderer.enabled = True

        # Follow parent position (engine doesn't auto-sync child transforms)
        if self._parent_go:
            self.transform.position.x = self._parent_go.transform.position.x
            self.transform.position.y = self._parent_go.transform.position.y

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
