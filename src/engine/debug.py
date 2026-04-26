"""Unity-compatible Debug static class for logging and visual debugging."""

from __future__ import annotations

import sys
from typing import Any

from src.engine.math.vector import Vector2, Vector3


class _DebugLine:
    """Internal: a debug line to render."""

    def __init__(self, start: Vector2 | Vector3, end: Vector2 | Vector3,
                 color: tuple, duration: float) -> None:
        self.start = start
        self.end = end
        self.color = color
        self.duration = duration
        self.elapsed = 0.0


class Debug:
    """Unity-compatible Debug static class."""

    _lines: list[_DebugLine] = []
    _log_handler = None  # Override for testing: callable(level, message)

    @staticmethod
    def log(message: Any) -> None:
        """Log a message (equivalent to Debug.Log in Unity)."""
        msg = str(message)
        if Debug._log_handler:
            Debug._log_handler("log", msg)
        else:
            print(f"[Log] {msg}")

    @staticmethod
    def log_warning(message: Any) -> None:
        """Log a warning message."""
        msg = str(message)
        if Debug._log_handler:
            Debug._log_handler("warning", msg)
        else:
            print(f"[Warning] {msg}", file=sys.stderr)

    @staticmethod
    def log_error(message: Any) -> None:
        """Log an error message."""
        msg = str(message)
        if Debug._log_handler:
            Debug._log_handler("error", msg)
        else:
            print(f"[Error] {msg}", file=sys.stderr)

    @staticmethod
    def draw_line(start: Vector2 | Vector3, end: Vector2 | Vector3,
                  color: tuple = (0, 255, 0), duration: float = 0.0) -> None:
        """Draw a debug line in world space. Visible for `duration` seconds (0 = one frame)."""
        Debug._lines.append(_DebugLine(start, end, color, duration))

    @staticmethod
    def draw_ray(start: Vector2 | Vector3, direction: Vector2 | Vector3,
                 color: tuple = (0, 255, 0), duration: float = 0.0) -> None:
        """Draw a debug ray from start in direction."""
        if isinstance(start, Vector2):
            end = Vector2(start.x + direction.x, start.y + direction.y)
        else:
            end = Vector3(start.x + direction.x, start.y + direction.y, start.z + direction.z)
        Debug._lines.append(_DebugLine(start, end, color, duration))

    @staticmethod
    def get_lines() -> list[_DebugLine]:
        """Get active debug lines for rendering."""
        return Debug._lines

    @staticmethod
    def tick(delta_time: float) -> None:
        """Update debug line lifetimes. Call once per frame."""
        remaining = []
        for line in Debug._lines:
            line.elapsed += delta_time
            if line.duration > 0 and line.elapsed < line.duration:
                remaining.append(line)
            # duration=0 lines are removed after one frame (elapsed > 0 after first tick)
            elif line.duration == 0 and line.elapsed == 0:
                remaining.append(line)
        Debug._lines = remaining

    @staticmethod
    def _reset() -> None:
        """Reset all debug state. Used in tests."""
        Debug._lines.clear()
        Debug._log_handler = None
