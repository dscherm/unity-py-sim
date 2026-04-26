"""2D Tilemap system — grid-based level building.

Tile: data for a single cell (color, asset_ref, collider type).
Tilemap: grid storage with set_tile/get_tile.
TilemapCollider2D: auto-generates box colliders for solid tiles.

Usage:
    tilemap = go.add_component(Tilemap)
    tilemap.cell_size = Vector2(1, 1)
    tilemap.set_tile(0, 0, Tile(color=(100, 100, 100), collider_type=ColliderType.FULL))
    tilemap.set_tile(1, 0, Tile(color=(150, 100, 50)))
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from src.engine.core import Component
from src.engine.math.vector import Vector2


class ColliderType(Enum):
    NONE = "none"
    FULL = "full"


@dataclass
class Tile:
    """Data for a single tilemap cell."""
    color: tuple = (255, 255, 255)
    asset_ref: str | None = None
    collider_type: ColliderType = ColliderType.NONE
    is_walkable: bool = True


class Tilemap(Component):
    """Grid-based tile storage."""

    def __init__(self):
        super().__init__()
        self.cell_size: Vector2 = Vector2(1, 1)
        self._tiles: dict[tuple[int, int], Tile] = {}

    def set_tile(self, x: int, y: int, tile: Tile | None) -> None:
        """Set a tile at grid coordinates. Pass None to clear."""
        if tile is None:
            self._tiles.pop((x, y), None)
        else:
            self._tiles[(x, y)] = tile

    def get_tile(self, x: int, y: int) -> Tile | None:
        return self._tiles.get((x, y))

    def has_tile(self, x: int, y: int) -> bool:
        return (x, y) in self._tiles

    def clear_all_tiles(self) -> None:
        self._tiles.clear()

    @property
    def tile_count(self) -> int:
        return len(self._tiles)

    def get_all_positions(self) -> list[tuple[int, int]]:
        return list(self._tiles.keys())

    @property
    def bounds_min(self) -> tuple[int, int]:
        if not self._tiles:
            return (0, 0)
        xs = [k[0] for k in self._tiles]
        ys = [k[1] for k in self._tiles]
        return (min(xs), min(ys))

    @property
    def bounds_max(self) -> tuple[int, int]:
        if not self._tiles:
            return (0, 0)
        xs = [k[0] for k in self._tiles]
        ys = [k[1] for k in self._tiles]
        return (max(xs), max(ys))

    def cell_to_world(self, x: int, y: int) -> Vector2:
        """Convert grid coordinates to world position (tile center)."""
        origin = self.transform.position if self.game_object else Vector2(0, 0)
        return Vector2(
            origin.x + x * self.cell_size.x + self.cell_size.x / 2,
            origin.y + y * self.cell_size.y + self.cell_size.y / 2,
        )

    def world_to_cell(self, world_pos: Vector2) -> tuple[int, int]:
        """Convert world position to grid coordinates."""
        origin = self.transform.position if self.game_object else Vector2(0, 0)
        x = int((world_pos.x - origin.x) / self.cell_size.x)
        y = int((world_pos.y - origin.y) / self.cell_size.y)
        return (x, y)


class TilemapRenderer(Component):
    """Renders all tiles in a Tilemap as colored rectangles."""

    def __init__(self):
        super().__init__()
        self.sorting_order: int = -10
        self.sorting_layer_name: str = "Background"

    def get_render_data(self) -> list[dict]:
        """Get tile render info (for RenderManager integration)."""
        tilemap = self.get_component(Tilemap) if self.game_object else None
        if tilemap is None:
            return []
        data = []
        for (x, y), tile in tilemap._tiles.items():
            world_pos = tilemap.cell_to_world(x, y)
            data.append({
                "position": world_pos,
                "size": tilemap.cell_size,
                "color": tile.color,
                "asset_ref": tile.asset_ref,
            })
        return data
