"""Unity-compatible UI system: Canvas, RectTransform, Text, Image, Button."""

from __future__ import annotations

from enum import Enum
from typing import Callable

from src.engine.core import Component
from src.engine.math.vector import Vector2


class RenderMode(Enum):
    SCREEN_SPACE_OVERLAY = "screen_space_overlay"
    SCREEN_SPACE_CAMERA = "screen_space_camera"
    WORLD_SPACE = "world_space"


class TextAnchor(Enum):
    UPPER_LEFT = "upper_left"
    UPPER_CENTER = "upper_center"
    UPPER_RIGHT = "upper_right"
    MIDDLE_LEFT = "middle_left"
    MIDDLE_CENTER = "middle_center"
    MIDDLE_RIGHT = "middle_right"
    LOWER_LEFT = "lower_left"
    LOWER_CENTER = "lower_center"
    LOWER_RIGHT = "lower_right"


class RectTransform(Component):
    """UI-specific transform with anchoring and sizing (replaces Transform for UI elements)."""

    def __init__(self) -> None:
        super().__init__()
        self._anchored_position: Vector2 = Vector2(0, 0)
        self._size_delta: Vector2 = Vector2(100, 30)
        self._anchor_min: Vector2 = Vector2(0.5, 0.5)
        self._anchor_max: Vector2 = Vector2(0.5, 0.5)
        self._pivot: Vector2 = Vector2(0.5, 0.5)

    @property
    def anchored_position(self) -> Vector2:
        return self._anchored_position

    @anchored_position.setter
    def anchored_position(self, value: Vector2) -> None:
        self._anchored_position = value

    @property
    def size_delta(self) -> Vector2:
        return self._size_delta

    @size_delta.setter
    def size_delta(self, value: Vector2) -> None:
        self._size_delta = value

    @property
    def anchor_min(self) -> Vector2:
        return self._anchor_min

    @anchor_min.setter
    def anchor_min(self, value: Vector2) -> None:
        self._anchor_min = value

    @property
    def anchor_max(self) -> Vector2:
        return self._anchor_max

    @anchor_max.setter
    def anchor_max(self, value: Vector2) -> None:
        self._anchor_max = value

    @property
    def pivot(self) -> Vector2:
        return self._pivot

    @pivot.setter
    def pivot(self, value: Vector2) -> None:
        self._pivot = value

    def get_screen_rect(self, canvas_width: float, canvas_height: float) -> tuple[float, float, float, float]:
        """Calculate pixel rect (x, y, width, height) on screen."""
        anchor_x = (self._anchor_min.x + self._anchor_max.x) / 2 * canvas_width
        anchor_y = (self._anchor_min.y + self._anchor_max.y) / 2 * canvas_height
        x = anchor_x + self._anchored_position.x - self._size_delta.x * self._pivot.x
        y = anchor_y + self._anchored_position.y - self._size_delta.y * self._pivot.y
        return (x, y, self._size_delta.x, self._size_delta.y)


class Canvas(Component):
    """Root UI container. All UI elements must be children of a Canvas."""

    _instances: list[Canvas] = []

    def __init__(self) -> None:
        super().__init__()
        self._render_mode = RenderMode.SCREEN_SPACE_OVERLAY
        self._sort_order: int = 0
        Canvas._instances.append(self)

    @property
    def render_mode(self) -> RenderMode:
        return self._render_mode

    @render_mode.setter
    def render_mode(self, value: RenderMode) -> None:
        self._render_mode = value

    @property
    def sort_order(self) -> int:
        return self._sort_order

    @sort_order.setter
    def sort_order(self, value: int) -> None:
        self._sort_order = value

    @classmethod
    def get_all(cls) -> list[Canvas]:
        return [c for c in cls._instances if c.enabled]

    @classmethod
    def reset(cls) -> None:
        cls._instances.clear()

    def on_destroy(self) -> None:
        if self in Canvas._instances:
            Canvas._instances.remove(self)


class Text(Component):
    """UI text display component."""

    def __init__(self) -> None:
        super().__init__()
        self._text: str = ""
        self._font_size: int = 14
        self._color: tuple = (255, 255, 255)
        self._alignment: TextAnchor = TextAnchor.UPPER_LEFT

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    @property
    def font_size(self) -> int:
        return self._font_size

    @font_size.setter
    def font_size(self, value: int) -> None:
        self._font_size = value

    @property
    def color(self) -> tuple:
        return self._color

    @color.setter
    def color(self, value: tuple) -> None:
        self._color = value

    @property
    def alignment(self) -> TextAnchor:
        return self._alignment

    @alignment.setter
    def alignment(self, value: TextAnchor) -> None:
        self._alignment = value


class Image(Component):
    """UI image/panel component."""

    def __init__(self) -> None:
        super().__init__()
        self._color: tuple = (255, 255, 255)
        self._sprite = None  # pygame.Surface or None

    @property
    def color(self) -> tuple:
        return self._color

    @color.setter
    def color(self, value: tuple) -> None:
        self._color = value

    @property
    def sprite(self):
        return self._sprite

    @sprite.setter
    def sprite(self, value) -> None:
        self._sprite = value


class Button(Component):
    """UI button with click callback."""

    def __init__(self) -> None:
        super().__init__()
        self._interactable: bool = True
        self._on_click: Callable[[], None] | None = None

    @property
    def interactable(self) -> bool:
        return self._interactable

    @interactable.setter
    def interactable(self, value: bool) -> None:
        self._interactable = value

    @property
    def on_click(self) -> Callable[[], None] | None:
        return self._on_click

    @on_click.setter
    def on_click(self, value: Callable[[], None] | None) -> None:
        self._on_click = value

    def click(self) -> None:
        """Simulate a button click."""
        if self._interactable and self._on_click is not None:
            self._on_click()

    def hit_test(self, screen_x: float, screen_y: float,
                 canvas_width: float, canvas_height: float) -> bool:
        """Test if a screen point is inside this button's rect."""
        rect_transform = self.game_object.get_component(RectTransform)
        if rect_transform is None:
            return False
        x, y, w, h = rect_transform.get_screen_rect(canvas_width, canvas_height)
        return x <= screen_x <= x + w and y <= screen_y <= y + h
