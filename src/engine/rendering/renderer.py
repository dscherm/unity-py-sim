"""Unity-compatible SpriteRenderer and RenderManager."""

from __future__ import annotations

from typing import Any

from src.engine.core import Component
from src.engine.math.vector import Vector2
from src.engine.rendering.camera import Camera


class SpriteRenderer(Component):
    """Renders a sprite or basic shape for a GameObject."""

    def __init__(self) -> None:
        super().__init__()
        self.color: tuple[int, int, int] = (255, 255, 255)
        self.sprite: Any = None  # pygame.Surface or None
        self.sorting_order: int = 0
        self.size: Vector2 = Vector2(1, 1)  # Size in world units (for shape fallback)
        self.asset_ref: str | None = None  # Symbolic asset name for Unity export (e.g. "bird_red")

    def render(self, surface: Any, camera: Camera, screen_width: int, screen_height: int) -> None:
        """Render this sprite to the given surface."""
        if not self.enabled or surface is None:
            return

        pos = Vector2(self.transform.position.x, self.transform.position.y)
        sx, sy = camera.world_to_screen(pos, screen_width, screen_height)
        ppu = screen_height / (2.0 * camera.orthographic_size)

        if self.sprite is not None:
            # Blit the sprite centered at screen position
            import pygame
            rect = self.sprite.get_rect(center=(sx, sy))
            surface.blit(self.sprite, rect)
        else:
            # Fallback: draw a colored rectangle
            import pygame
            w = int(self.size.x * ppu)
            h = int(self.size.y * ppu)
            rect = pygame.Rect(sx - w // 2, sy - h // 2, w, h)
            pygame.draw.rect(surface, self.color, rect)


class RenderManager:
    """Collects all SpriteRenderers and renders them in order."""

    @staticmethod
    def render_all(surface: Any, camera: Camera | None, screen_width: int, screen_height: int) -> None:
        """Render all active SpriteRenderers sorted by sorting_order."""
        if camera is None or surface is None:
            return

        from src.engine.core import _game_objects
        renderers: list[SpriteRenderer] = []
        for go in _game_objects.values():
            if go.active:
                for comp in go.get_components(SpriteRenderer):
                    if comp.enabled:
                        renderers.append(comp)

        renderers.sort(key=lambda r: r.sorting_order)
        for renderer in renderers:
            renderer.render(surface, camera, screen_width, screen_height)
