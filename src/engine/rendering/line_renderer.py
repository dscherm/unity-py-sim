"""LineRenderer and TrailRenderer components.

LineRenderer: persistent line drawn through a list of positions.
TrailRenderer: auto-records positions over time, fading trail effect.
"""

from __future__ import annotations

from src.engine.core import Component
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time


class LineRenderer(Component):
    """Renders a line through a list of world-space positions."""

    def __init__(self):
        super().__init__()
        self._positions: list[Vector2] = []
        self.width_start: float = 0.1
        self.width_end: float = 0.1
        self.color_start: tuple = (255, 255, 255)
        self.color_end: tuple = (255, 255, 255)
        self.sorting_order: int = 0

    @property
    def position_count(self) -> int:
        return len(self._positions)

    def set_positions(self, positions: list[Vector2]) -> None:
        self._positions = list(positions)

    def set_position(self, index: int, position: Vector2) -> None:
        if 0 <= index < len(self._positions):
            self._positions[index] = position

    def get_position(self, index: int) -> Vector2 | None:
        if 0 <= index < len(self._positions):
            return self._positions[index]
        return None

    def get_positions(self) -> list[Vector2]:
        return list(self._positions)


class TrailRenderer(Component):
    """Records transform positions over time to create a fading trail."""

    def __init__(self):
        super().__init__()
        self.trail_time: float = 1.0
        self.width_start: float = 0.2
        self.width_end: float = 0.0
        self.color_start: tuple = (255, 255, 255)
        self.color_end: tuple = (255, 255, 255, 0)
        self.min_vertex_distance: float = 0.1
        self.sorting_order: int = 0
        self._points: list[_TrailPoint] = []

    def update(self) -> None:
        """Record position and prune old points."""
        if self._game_object is None:
            return

        pos = self.transform.position
        current = Vector2(pos.x, pos.y)

        # Only add point if moved enough
        if self._points:
            last = self._points[-1].position
            dx = current.x - last.x
            dy = current.y - last.y
            if (dx * dx + dy * dy) < self.min_vertex_distance ** 2:
                # Still prune old points
                self._prune()
                return

        self._points.append(_TrailPoint(position=current, time=Time.time))
        self._prune()

    def _prune(self) -> None:
        """Remove points older than trail_time."""
        cutoff = Time.time - self.trail_time
        self._points = [p for p in self._points if p.time >= cutoff]

    def get_positions(self) -> list[Vector2]:
        """Get current trail positions (oldest first)."""
        return [p.position for p in self._points]

    @property
    def position_count(self) -> int:
        return len(self._points)

    def clear(self) -> None:
        self._points.clear()


class _TrailPoint:
    __slots__ = ("position", "time")

    def __init__(self, position: Vector2, time: float):
        self.position = position
        self.time = time
