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

    # ── Rich text support ──

    rich_text: bool = False

    def get_visible_text(self) -> str:
        """Get text with rich text tags stripped (for length calculations)."""
        if not self.rich_text:
            return self._text
        import re
        return re.sub(r"<[^>]+>", "", self._text)

    def parse_rich_text(self) -> list[dict]:
        """Parse rich text into styled runs: [{'text': ..., 'color': ..., 'size': ...}].

        Supported tags: <color=#RRGGBB>text</color>, <b>bold</b>, <size=N>text</size>
        """
        if not self.rich_text:
            return [{"text": self._text, "color": self._color, "size": self._font_size, "bold": False}]

        import re
        runs = []
        color_stack = [self._color]
        size_stack = [self._font_size]
        bold_stack = [False]

        # Tokenize: split into text and tags
        parts = re.split(r"(<[^>]+>)", self._text)
        for part in parts:
            if not part:
                continue
            if part.startswith("<"):
                tag = part[1:-1].strip()
                if tag.startswith("color="):
                    hex_color = tag.split("=", 1)[1].strip("#\"'")
                    try:
                        r = int(hex_color[0:2], 16)
                        g = int(hex_color[2:4], 16)
                        b = int(hex_color[4:6], 16)
                        color_stack.append((r, g, b))
                    except (ValueError, IndexError):
                        pass
                elif tag == "/color":
                    if len(color_stack) > 1:
                        color_stack.pop()
                elif tag.startswith("size="):
                    try:
                        size_stack.append(int(tag.split("=", 1)[1]))
                    except ValueError:
                        pass
                elif tag == "/size":
                    if len(size_stack) > 1:
                        size_stack.pop()
                elif tag == "b":
                    bold_stack.append(True)
                elif tag == "/b":
                    if len(bold_stack) > 1:
                        bold_stack.pop()
            else:
                runs.append({
                    "text": part,
                    "color": color_stack[-1],
                    "size": size_stack[-1],
                    "bold": bold_stack[-1],
                })
        return runs

    # ── Typewriter effect ──

    reveal_speed: float = 0.0  # chars per second; 0 = instant
    _revealed_count: int = -1  # -1 = all revealed
    _reveal_timer: float = 0.0
    on_character_revealed: list = []  # callbacks(index)

    def start_reveal(self, speed: float = 30.0) -> None:
        """Start character-by-character reveal."""
        self.reveal_speed = speed
        self._revealed_count = 0
        self._reveal_timer = 0.0

    def get_revealed_text(self) -> str:
        """Get text up to current reveal position."""
        if self._revealed_count < 0:
            return self._text
        visible = self.get_visible_text()
        return visible[:self._revealed_count]

    @property
    def is_revealing(self) -> bool:
        if self._revealed_count < 0:
            return False
        return self._revealed_count < len(self.get_visible_text())

    def update_reveal(self, dt: float) -> None:
        """Advance reveal timer. Call from update() or LifecycleManager."""
        if self._revealed_count < 0 or self.reveal_speed <= 0:
            return
        visible_len = len(self.get_visible_text())
        self._reveal_timer += dt
        chars_per_tick = self._reveal_timer * self.reveal_speed
        new_count = min(visible_len, int(self._revealed_count + chars_per_tick))
        if new_count > self._revealed_count:
            for i in range(self._revealed_count, new_count):
                for cb in self.on_character_revealed:
                    cb(i)
            self._revealed_count = new_count
            self._reveal_timer = 0.0


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
