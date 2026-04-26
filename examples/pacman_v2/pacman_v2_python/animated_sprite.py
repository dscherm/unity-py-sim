from __future__ import annotations
"""AnimatedSprite — generic frame-based sprite animation.

Port of zigurous AnimatedSprite.cs. Uses timer in update() to advance frames.
Unlike v1 which used asset_ref strings, v2 uses actual pygame.Surface sprites
loaded from the zigurous PNG files.

Lesson applied: use timer in update() not invoke_repeating (engine doesn't have it).
"""

import os

import pygame

from src.engine.core import MonoBehaviour
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.time_manager import Time


SPRITES_DIR = os.path.join(os.path.dirname(__file__), "..", "sprites")


def load_sprite_file(name: str, size_px: int | None = None) -> pygame.Surface:
    """Load a PNG from the sprites directory."""
    if not pygame.get_init():
        pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1), pygame.NOFRAME)
    path = os.path.join(SPRITES_DIR, name)
    surf = pygame.image.load(path).convert_alpha()
    if size_px:
        surf = pygame.transform.scale(surf, (size_px, size_px))
    return surf


class AnimatedSprite(MonoBehaviour):
    sprites: list[pygame.Surface]
    animation_time: float = 0.25
    loop: bool = True

    _sprite_renderer: SpriteRenderer | None = None
    _animation_frame: int = 0
    _timer: float = 0.0

    def __init__(self) -> None:
        super().__init__()
        self.sprites = []

    def awake(self) -> None:
        self._sprite_renderer = self.get_component(SpriteRenderer)
        self._animation_frame = 0
        self._timer = 0.0

    def on_enable(self) -> None:
        if self._sprite_renderer:
            self._sprite_renderer.enabled = True

    def on_disable(self) -> None:
        if self._sprite_renderer:
            self._sprite_renderer.enabled = False

    def update(self) -> None:
        self._timer += Time.delta_time
        if self._timer >= self.animation_time:
            self._timer -= self.animation_time
            self._advance()

    def _advance(self) -> None:
        if self._sprite_renderer is None or not self._sprite_renderer.enabled:
            return

        self._animation_frame += 1

        if self._animation_frame >= len(self.sprites) and self.loop:
            self._animation_frame = 0

        if 0 <= self._animation_frame < len(self.sprites):
            self._sprite_renderer.sprite = self.sprites[self._animation_frame]

    def restart(self) -> None:
        self._animation_frame = -1
        self._timer = 0.0
        self._advance()
