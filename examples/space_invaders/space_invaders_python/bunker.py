"""Bunker — destructible shield.

Line-by-line port of: zigurous/Bunker.cs
Original uses Texture2D pixel manipulation. We use a cell grid as equivalent.
Structure and method signatures match the C# 1:1.
"""
from __future__ import annotations

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.collider import BoxCollider2D


class Bunker(MonoBehaviour):
    """[RequireComponent(typeof(SpriteRenderer))]
    [RequireComponent(typeof(BoxCollider2D))]"""

    # Grid dimensions (replaces Texture2D pixel grid in C#)
    GRID_COLS: int = 16
    GRID_ROWS: int = 12
    CELL_SIZE: float = 0.125  # world units per cell

    def __init__(self) -> None:
        super().__init__()
        # public Texture2D splat — splash radius for damage
        self.splat_radius: int = 2
        # private Texture2D originalTexture — we store original cell state
        self._original_cells: list[list[bool]] = []
        # private SpriteRenderer spriteRenderer
        self.sprite_renderer: SpriteRenderer | None = None
        # private BoxCollider2D boxCollider
        self.box_collider: BoxCollider2D | None = None
        # Cell grid (replaces texture pixels)
        self._cells: list[list[bool]] = []

    def awake(self) -> None:
        # spriteRenderer = GetComponent<SpriteRenderer>()
        self.sprite_renderer = self.get_component(SpriteRenderer)
        # boxCollider = GetComponent<BoxCollider2D>()
        self.box_collider = self.get_component(BoxCollider2D)
        # originalTexture = spriteRenderer.sprite.texture
        self._original_cells = [[True] * Bunker.GRID_COLS for _ in range(Bunker.GRID_ROWS)]

        self.reset_bunker()

    def reset_bunker(self) -> None:
        """public void ResetBunker()"""
        # CopyTexture(originalTexture) — restore cells from original
        self._cells = [row[:] for row in self._original_cells]
        # gameObject.SetActive(true)
        self.game_object.active = True

    def check_collision(self, other_collider: BoxCollider2D | None, hit_point: Vector2) -> bool:
        """public bool CheckCollision(BoxCollider2D other, Vector3 hitPoint)"""
        # Check center and edges of the colliding object
        if other_collider and hasattr(other_collider, 'size'):
            offset: Vector2 = Vector2(other_collider.size.x / 2, other_collider.size.y / 2)
            return (self._splat(hit_point) or
                    self._splat(Vector2(hit_point.x, hit_point.y - offset.y)) or
                    self._splat(Vector2(hit_point.x, hit_point.y + offset.y)) or
                    self._splat(Vector2(hit_point.x - offset.x, hit_point.y)) or
                    self._splat(Vector2(hit_point.x + offset.x, hit_point.y)))
        return self._splat(hit_point)

    def _splat(self, hit_point: Vector2) -> bool:
        """private bool Splat(Vector3 hitPoint)"""
        # if (!CheckPoint(hitPoint, out int px, out int py)) return false
        result: tuple[int, int] | None = self._check_point(hit_point)
        if result is None:
            return False
        px: int
        py: int
        px, py = result

        # Offset by half splat size to center the damage
        px -= self.splat_radius
        py -= self.splat_radius

        # Alpha mask the bunker with the splat
        for y in range(self.splat_radius * 2):
            for x in range(self.splat_radius * 2):
                cx: int = px + x
                cy: int = py + y
                if 0 <= cy < Bunker.GRID_ROWS and 0 <= cx < Bunker.GRID_COLS:
                    self._cells[cy][cx] = False

        return True

    def _check_point(self, hit_point: Vector2) -> tuple[int, int] | None:
        """private bool CheckPoint(Vector3 hitPoint, out int px, out int py)"""
        if self.box_collider is None:
            return None

        # Vector3 localPoint = transform.InverseTransformPoint(hitPoint)
        pos: Vector2 = self.transform.position
        local_x: float = hit_point.x - pos.x
        local_y: float = hit_point.y - pos.y

        # Offset to corner: localPoint.x += boxCollider.size.x / 2
        bw: float = self.box_collider.size.x
        bh: float = self.box_collider.size.y
        local_x += bw / 2
        local_y += bh / 2

        # Transform to grid coordinates
        px: int = int(local_x / bw * Bunker.GRID_COLS)
        py: int = int(local_y / bh * Bunker.GRID_ROWS)

        # Return true if pixel is not empty
        if 0 <= px < Bunker.GRID_COLS and 0 <= py < Bunker.GRID_ROWS and self._cells[py][px]:
            return (px, py)
        return None

    def on_trigger_enter_2d(self, other: GameObject) -> None:
        from space_invaders_python.player import Layers
        # if (other.gameObject.layer == LayerMask.NameToLayer("Invader"))
        if other.layer == Layers.INVADER:
            # gameObject.SetActive(false)
            self.game_object.active = False
