"""Unity-compatible Input static class backed by pygame."""

from __future__ import annotations


# Pygame key constants will be mapped at runtime.
# We keep a string-based key system so tests can run without pygame display.

# Axis definitions matching Unity defaults
_AXIS_DEFINITIONS: dict[str, dict[str, list[str]]] = {
    "Horizontal": {"positive": ["d", "right"], "negative": ["a", "left"]},
    "Vertical": {"positive": ["w", "up"], "negative": ["s", "down"]},
    "Vertical1": {"positive": ["w"], "negative": ["s"]},
    "Vertical2": {"positive": ["up"], "negative": ["down"]},
}


class Input:
    """Static class mirroring Unity's Input system."""

    _current_keys: set[str] = set()
    _previous_keys: set[str] = set()
    _mouse_position: tuple[float, float] = (0.0, 0.0)
    _current_mouse_buttons: set[int] = set()
    _previous_mouse_buttons: set[int] = set()

    @staticmethod
    def get_key(key_name: str) -> bool:
        """Returns true while the key is held down."""
        return key_name.lower() in Input._current_keys

    @staticmethod
    def get_key_down(key_name: str) -> bool:
        """Returns true on the frame the key was pressed."""
        k = key_name.lower()
        return k in Input._current_keys and k not in Input._previous_keys

    @staticmethod
    def get_key_up(key_name: str) -> bool:
        """Returns true on the frame the key was released."""
        k = key_name.lower()
        return k not in Input._current_keys and k in Input._previous_keys

    @staticmethod
    def get_axis(axis_name: str) -> float:
        """Returns -1 to 1 for the named axis."""
        axis = _AXIS_DEFINITIONS.get(axis_name)
        if axis is None:
            return 0.0

        value = 0.0
        for key in axis["positive"]:
            if key in Input._current_keys:
                value += 1.0
                break
        for key in axis["negative"]:
            if key in Input._current_keys:
                value -= 1.0
                break
        return value

    @staticmethod
    def get_mouse_position() -> tuple[float, float]:
        return Input._mouse_position

    @staticmethod
    def get_mouse_button(button: int) -> bool:
        """Returns true while the mouse button is held. 0=left, 1=right, 2=middle."""
        return button in Input._current_mouse_buttons

    @staticmethod
    def get_mouse_button_down(button: int) -> bool:
        return button in Input._current_mouse_buttons and button not in Input._previous_mouse_buttons

    @staticmethod
    def get_mouse_button_up(button: int) -> bool:
        """Returns true on the frame the mouse button was released."""
        return button not in Input._current_mouse_buttons and button in Input._previous_mouse_buttons

    @staticmethod
    def _begin_frame() -> None:
        """Called at the start of each frame to snapshot previous state."""
        Input._previous_keys = set(Input._current_keys)
        Input._previous_mouse_buttons = set(Input._current_mouse_buttons)

    @staticmethod
    def _set_key_state(key_name: str, pressed: bool) -> None:
        """Set a key's state (used by display layer or tests)."""
        k = key_name.lower()
        if pressed:
            Input._current_keys.add(k)
        else:
            Input._current_keys.discard(k)

    @staticmethod
    def _set_mouse_position(x: float, y: float) -> None:
        Input._mouse_position = (x, y)

    @staticmethod
    def _set_mouse_button(button: int, pressed: bool) -> None:
        if pressed:
            Input._current_mouse_buttons.add(button)
        else:
            Input._current_mouse_buttons.discard(button)

    @staticmethod
    def _reset() -> None:
        Input._current_keys.clear()
        Input._previous_keys.clear()
        Input._mouse_position = (0.0, 0.0)
        Input._current_mouse_buttons.clear()
        Input._previous_mouse_buttons.clear()
