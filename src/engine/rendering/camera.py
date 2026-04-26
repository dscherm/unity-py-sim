"""Unity-compatible Camera component."""

from __future__ import annotations

from src.engine.core import Component
from src.engine.math.vector import Vector2, Vector3


class Camera(Component):
    """Camera component for world-to-screen coordinate conversion."""

    main: Camera | None = None  # The first active camera

    def __init__(self) -> None:
        super().__init__()
        self._orthographic_size: float = 5.0  # Half-height in world units
        self._background_color: tuple[int, int, int] = (49, 77, 121)  # Unity default blue

    def awake(self) -> None:
        if Camera.main is None:
            Camera.main = self

    @property
    def orthographic_size(self) -> float:
        return self._orthographic_size

    @orthographic_size.setter
    def orthographic_size(self, value: float) -> None:
        self._orthographic_size = value

    @property
    def background_color(self) -> tuple[int, int, int]:
        return self._background_color

    @background_color.setter
    def background_color(self, value: tuple[int, int, int]) -> None:
        self._background_color = value

    def world_to_screen(self, world_point: Vector2, screen_width: int, screen_height: int) -> tuple[int, int]:
        """Convert a world-space point to screen pixel coordinates."""
        cam_pos = self.transform.position
        # Pixels per world unit
        ppu = screen_height / (2.0 * self._orthographic_size)
        # World offset from camera
        dx = world_point.x - cam_pos.x
        dy = world_point.y - cam_pos.y
        # Screen center + offset
        sx = int(screen_width / 2.0 + dx * ppu)
        sy = int(screen_height / 2.0 - dy * ppu)  # Y flipped (screen Y goes down)
        return (sx, sy)

    def screen_to_world(self, screen_point: tuple[int, int], screen_width: int, screen_height: int) -> Vector2:
        """Convert screen pixel coordinates to world space."""
        cam_pos = self.transform.position
        ppu = screen_height / (2.0 * self._orthographic_size)
        wx = cam_pos.x + (screen_point[0] - screen_width / 2.0) / ppu
        wy = cam_pos.y - (screen_point[1] - screen_height / 2.0) / ppu
        return Vector2(wx, wy)

    def screen_to_world_point(self, screen_point: Vector3, screen_width: int = 800, screen_height: int = 600) -> Vector3:
        """Convert screen pixel coordinates to world space. Matches Unity's Camera.ScreenToWorldPoint.

        Takes a Vector3 where x,y are screen pixels and z is distance from camera (ignored in 2D).
        Returns a Vector3 in world space.
        """
        result = self.screen_to_world(
            (int(screen_point.x), int(screen_point.y)),
            screen_width, screen_height
        )
        return Vector3(result.x, result.y, 0)

    @staticmethod
    def _reset_main() -> None:
        Camera.main = None
