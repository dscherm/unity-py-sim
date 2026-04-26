"""Sprite atlas — extract sub-sprites from sprite sheets.

SpriteAtlas defines named sub-regions within an image for use with
SpriteRenderer and SpriteAnimator.

Usage:
    atlas = SpriteAtlas("characters")
    atlas.add_sprite("idle_0", Rect(0, 0, 32, 32))
    atlas.add_sprite("idle_1", Rect(32, 0, 32, 32))
    # Or slice a grid:
    atlas.slice_grid(cols=4, rows=2, cell_width=32, cell_height=32)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Rect:
    """Rectangle region within a sprite sheet (pixels)."""
    x: int
    y: int
    width: int
    height: int


@dataclass
class SpriteData:
    """Named sub-sprite within an atlas."""
    name: str
    rect: Rect
    pivot_x: float = 0.5
    pivot_y: float = 0.5


class SpriteAtlas:
    """Collection of named sub-sprites from a sprite sheet."""

    def __init__(self, name: str = "", image_path: str | None = None):
        self.name = name
        self.image_path = image_path
        self._sprites: dict[str, SpriteData] = {}

    def add_sprite(self, name: str, rect: Rect, pivot_x: float = 0.5, pivot_y: float = 0.5) -> None:
        """Add a named sub-sprite region."""
        self._sprites[name] = SpriteData(name=name, rect=rect, pivot_x=pivot_x, pivot_y=pivot_y)

    def get_sprite(self, name: str) -> SpriteData | None:
        return self._sprites.get(name)

    def get_all_names(self) -> list[str]:
        return list(self._sprites.keys())

    @property
    def sprite_count(self) -> int:
        return len(self._sprites)

    def slice_grid(
        self,
        cols: int,
        rows: int,
        cell_width: int,
        cell_height: int,
        offset_x: int = 0,
        offset_y: int = 0,
        prefix: str = "",
    ) -> list[str]:
        """Auto-slice a grid into named sprites (prefix_0, prefix_1, ...)."""
        names = []
        index = 0
        for row in range(rows):
            for col in range(cols):
                name = f"{prefix}{index}" if prefix else f"sprite_{index}"
                rect = Rect(
                    x=offset_x + col * cell_width,
                    y=offset_y + row * cell_height,
                    width=cell_width,
                    height=cell_height,
                )
                self.add_sprite(name, rect)
                names.append(name)
                index += 1
        return names
