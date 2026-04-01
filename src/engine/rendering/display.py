"""Pygame display management."""

from __future__ import annotations

from typing import Any


class DisplayManager:
    """Manages the pygame display surface and event loop."""

    _instance: DisplayManager | None = None

    def __init__(self, width: int = 800, height: int = 600, title: str = "Unity-Py-Sim") -> None:
        self._width = width
        self._height = height
        self._title = title
        self._surface: Any = None
        self._should_quit = False
        self._headless = False

    @classmethod
    def instance(cls) -> DisplayManager:
        if cls._instance is None:
            cls._instance = DisplayManager()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def should_quit(self) -> bool:
        return self._should_quit

    def init(self, headless: bool = False) -> None:
        """Initialize pygame display. Set headless=True for testing."""
        self._headless = headless
        if not headless:
            import pygame
            pygame.init()
            self._surface = pygame.display.set_mode((self._width, self._height))
            pygame.display.set_caption(self._title)

    def clear(self, color: tuple[int, int, int] = (0, 0, 0)) -> None:
        """Clear the display."""
        if self._surface is not None:
            self._surface.fill(color)

    def flip(self) -> None:
        """Swap display buffers."""
        if not self._headless:
            import pygame
            pygame.display.flip()

    def poll_events(self) -> None:
        """Poll pygame events and update Input state."""
        if self._headless:
            return
        import pygame
        from src.engine.input_manager import Input
        Input._begin_frame()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._should_quit = True
            elif event.type == pygame.KEYDOWN:
                key_name = pygame.key.name(event.key)
                Input._set_key_state(key_name, True)
            elif event.type == pygame.KEYUP:
                key_name = pygame.key.name(event.key)
                Input._set_key_state(key_name, False)
            elif event.type == pygame.MOUSEMOTION:
                Input._set_mouse_position(float(event.pos[0]), float(event.pos[1]))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                Input._set_mouse_button(event.button - 1, True)  # pygame 1-indexed, Unity 0-indexed
            elif event.type == pygame.MOUSEBUTTONUP:
                Input._set_mouse_button(event.button - 1, False)

    def quit(self) -> None:
        if not self._headless:
            import pygame
            pygame.quit()

    def request_quit(self) -> None:
        self._should_quit = True
