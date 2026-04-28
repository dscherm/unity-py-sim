"""Contract: translated Keyboard.current / Mouse.current accesses MUST
be null-safe.

Background: Unity New Input System returns null for `Keyboard.current`
and `Mouse.current` when no input device is currently attached — the
default state during `Unity -batchmode -runTests` runs on the home-
machine self-hosted runner. The translator previously emitted bare
`Keyboard.current.spaceKey.wasPressedThisFrame` etc., which threw
NullReferenceException on every Update() tick under that environment.

Surfaced 2026-04-27 by M-7 phase 2 PlayMode tests on workflow runs
24971232854 (breakout) and 24971807340 (flappy_bird):
  - breakout PaddleController.Update — `Keyboard.current.dKey/aKey`
  - breakout BallController.Update    — `Keyboard.current.spaceKey`
  - flappy_bird Player.Update          — `Keyboard.current.spaceKey`
                                        `Mouse.current.leftButton`

The Boolean-coerced null-conditional pattern
    Keyboard.current?.spaceKey.wasPressedThisFrame == true
collapses `bool?` to `bool` so the result is usable in `if`, `||`,
`&&`, and ternary expressions without further work, AND gracefully
no-ops when the device is missing. Vector2 reads (`Mouse.current.
position.ReadValue()`) coalesce against `Vector2.zero` so they're
still Vector2 (not Vector2?).
"""

from __future__ import annotations


from src.translator.python_parser import parse_python
from src.translator.python_to_csharp import translate


PROLOGUE = (
    "from src.engine.core import MonoBehaviour\n"
    "from src.engine.input_manager import Input\n"
    "class Foo(MonoBehaviour):\n"
    "    def update(self):\n"
)


def _translate_new(src_body: str) -> str:
    return translate(parse_python(PROLOGUE + src_body), input_system="new")


class TestKeyboardNullGuard:
    """Every Keyboard.current.X access must be guarded with `?.`."""

    def test_key_pressed_uses_null_conditional(self):
        result = _translate_new("        if Input.get_key('space'):\n            pass\n")
        # Required: `Keyboard.current?.spaceKey...` (no bare `Keyboard.current.`).
        assert "Keyboard.current?.spaceKey.isPressed == true" in result
        # Negative: must NOT contain the unguarded form.
        assert "Keyboard.current.spaceKey.isPressed" not in result

    def test_key_down_uses_null_conditional(self):
        result = _translate_new("        if Input.get_key_down('space'):\n            pass\n")
        assert "Keyboard.current?.spaceKey.wasPressedThisFrame == true" in result
        assert "Keyboard.current.spaceKey.wasPressedThisFrame" not in result

    def test_key_up_uses_null_conditional(self):
        result = _translate_new("        if Input.get_key_up('escape'):\n            pass\n")
        assert "Keyboard.current?.escapeKey.wasReleasedThisFrame == true" in result
        assert "Keyboard.current.escapeKey.wasReleasedThisFrame" not in result

    def test_no_unguarded_keyboard_anywhere(self):
        """Smoke check: a snippet with several keyboard reads emits ZERO
        unguarded `Keyboard.current.` accesses (the `.` after `current`
        without `?` preceding it is the failure mode)."""
        body = (
            "        if Input.get_key('space'): pass\n"
            "        if Input.get_key_down('a'): pass\n"
            "        if Input.get_key_up('escape'): pass\n"
        )
        result = _translate_new(body)
        # Strip every `Keyboard.current?.` then look for any `Keyboard.current.` left.
        residual = result.replace("Keyboard.current?.", "")
        assert "Keyboard.current." not in residual, (
            f"Found unguarded Keyboard.current. access in:\n{result}"
        )


class TestMouseNullGuard:
    """Every Mouse.current.X access must be guarded with `?.`."""

    def test_mouse_button_pressed_uses_null_conditional(self):
        result = _translate_new("        if Input.get_mouse_button(0):\n            pass\n")
        assert "Mouse.current?.leftButton.isPressed == true" in result
        assert "Mouse.current.leftButton.isPressed" not in result

    def test_mouse_button_down_uses_null_conditional(self):
        result = _translate_new("        if Input.get_mouse_button_down(0):\n            pass\n")
        assert "Mouse.current?.leftButton.wasPressedThisFrame == true" in result
        assert "Mouse.current.leftButton.wasPressedThisFrame" not in result

    def test_mouse_button_up_uses_null_conditional(self):
        result = _translate_new("        if Input.get_mouse_button_up(1):\n            pass\n")
        assert "Mouse.current?.rightButton.wasReleasedThisFrame == true" in result
        assert "Mouse.current.rightButton.wasReleasedThisFrame" not in result

    def test_mouse_position_coalesces_to_vector2_zero(self):
        """`Mouse.current?.position.ReadValue()` returns Vector2?, which
        breaks every caller expecting Vector2.  Coalesce with
        `Vector2.zero` so the result type stays Vector2 even when the
        device is missing.
        """
        result = _translate_new("        p = Input.mouse_position\n")
        assert "Mouse.current?.position.ReadValue() ?? Vector2.zero" in result
        # Negative: bare unguarded access must be gone.
        assert "Mouse.current.position.ReadValue()" not in result

    def test_no_unguarded_mouse_anywhere(self):
        body = (
            "        if Input.get_mouse_button(0): pass\n"
            "        if Input.get_mouse_button_down(1): pass\n"
            "        if Input.get_mouse_button_up(2): pass\n"
            "        p = Input.mouse_position\n"
        )
        result = _translate_new(body)
        residual = result.replace("Mouse.current?.", "")
        assert "Mouse.current." not in residual, (
            f"Found unguarded Mouse.current. access in:\n{result}"
        )


class TestAxisEmulationNullGuard:
    """The keyboard-axis emulation for `Input.get_axis()` builds a
    ternary with two `Keyboard.current.X.isPressed` reads — both must
    be the `?.` + `== true` coerced form.
    """

    def test_horizontal_axis_uses_null_conditional(self):
        result = _translate_new("        h = Input.get_axis('Horizontal')\n")
        assert "Keyboard.current?.dKey.isPressed == true" in result
        assert "Keyboard.current?.aKey.isPressed == true" in result
        # Old form must be entirely gone.
        assert "Keyboard.current.dKey.isPressed ? 1f" not in result
        assert "Keyboard.current.aKey.isPressed ? 1f" not in result

    def test_vertical_axis_uses_null_conditional(self):
        result = _translate_new("        v = Input.get_axis('Vertical')\n")
        assert "Keyboard.current?.wKey.isPressed == true" in result
        assert "Keyboard.current?.sKey.isPressed == true" in result
        assert "Keyboard.current.wKey.isPressed ? 1f" not in result
        assert "Keyboard.current.sKey.isPressed ? 1f" not in result


class TestLegacyInputUnchanged:
    """The legacy `UnityEngine.Input` shim doesn't have null-current
    semantics — it returns false / Vector3.zero for missing devices
    silently.  Don't apply the null-conditional fix to legacy output.
    """

    def test_legacy_keyboard_pattern_unchanged(self):
        result = translate(
            parse_python(PROLOGUE + "        if Input.get_key('space'):\n            pass\n"),
            input_system="legacy",
        )
        assert "Input.GetKey" in result
        # No new-input artifacts in legacy.
        assert "Keyboard.current" not in result
        assert "?." not in result.split("Input.GetKey")[1].splitlines()[0]
