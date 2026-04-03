"""Bunker — destructible shield with cell-based damage grid.

Maps to: zigurous/Bunker.cs
Simplified from texture-based pixel damage to cell grid.
"""

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2
from src.engine.rendering.renderer import SpriteRenderer


BUNKER_COLS = 8
BUNKER_ROWS = 6
CELL_SIZE = 0.25  # world units per cell


class Bunker(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self._cells: list[list[bool]] = []
        self._init_cells()

    def _init_cells(self):
        self._cells = [[True] * BUNKER_COLS for _ in range(BUNKER_ROWS)]

    def check_collision(self, hit_point: Vector2) -> bool:
        """Check if a projectile hits a solid cell. Damage nearby cells. Returns True if hit."""
        pos = self.transform.position
        # Convert world hit point to cell coordinates
        local_x = hit_point.x - (pos.x - BUNKER_COLS * CELL_SIZE / 2)
        local_y = hit_point.y - (pos.y - BUNKER_ROWS * CELL_SIZE / 2)

        col = int(local_x / CELL_SIZE)
        row = int(local_y / CELL_SIZE)

        if not (0 <= col < BUNKER_COLS and 0 <= row < BUNKER_ROWS):
            return False

        if not self._cells[row][col]:
            return False

        # Damage a 2x2 area around the hit
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                r, c = row + dr, col + dc
                if 0 <= r < BUNKER_ROWS and 0 <= c < BUNKER_COLS:
                    self._cells[r][c] = False

        return True

    def reset_bunker(self):
        self._init_cells()

    def get_alive_cell_count(self) -> int:
        return sum(1 for row in self._cells for cell in row if cell)

    def on_trigger_enter_2d(self, other):
        from space_invaders_python.player import LAYER_INVADER
        if other.layer == LAYER_INVADER:
            self.game_object.active = False
