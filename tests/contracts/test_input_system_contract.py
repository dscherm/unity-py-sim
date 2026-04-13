"""Contract tests for Input System translation (New Input System vs Legacy).

ROOT CAUSE OF 60+ EXISTING TEST FAILURES:
    All existing input system tests in test_python_to_csharp.py use
    `if Input.get_key_down('space'): pass` as the test body. The translator
    correctly strips `pass` statements (line 814 in python_to_csharp.py), then
    the empty-body-if cleanup (lines 832-848) removes the entire `if` block
    since it has no remaining children. The translated Input call disappears
    from the output entirely. Tests that use a real statement in the body
    (like `h = Input.get_axis('Horizontal')` in test_new_input_axis_emits_todo)
    pass fine. The fix is to use a real statement body (e.g. `self.do_thing()`)
    instead of `pass` in the if-block.
"""

import pytest
from src.translator.python_parser import parse_python
from src.translator.python_to_csharp import translate, translate_file
import tempfile, os


# ── Helpers ──────────────────────────────────────────────────────────

def _make_input_source(input_call: str, *, as_condition: bool = True) -> str:
    """Build a minimal MonoBehaviour source with an Input call.

    Uses `self.do_thing()` as body so the if-block is not stripped.
    """
    if as_condition:
        return (
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.input_manager import Input\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            f"        if {input_call}:\n"
            "            self.do_thing()\n"
        )
    else:
        # Assignment form: `val = Input.get_axis('Horizontal')`
        return (
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.input_manager import Input\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            f"        val = {input_call}\n"
        )


def _translate_source(source: str, *, input_system: str = "new") -> str:
    parsed = parse_python(source)
    return translate(parsed, input_system=input_system)


def _translate_via_file(source: str, *, input_system: str = "new") -> str:
    """Write source to a temp file and translate via translate_file()."""
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(source)
        return translate_file(path, input_system=input_system)
    finally:
        os.unlink(path)


# ══════════════════════════════════════════════════════════════════════
#  NEW INPUT SYSTEM — Keyboard
# ══════════════════════════════════════════════════════════════════════

class TestNewInputKeyboard:
    """Verify Keyboard.current.* translations for the new input system."""

    def test_get_key_down_space(self):
        result = _translate_source(
            _make_input_source("Input.get_key_down('space')")
        )
        assert "Keyboard.current.spaceKey.wasPressedThisFrame" in result

    def test_get_key_down_escape(self):
        result = _translate_source(
            _make_input_source("Input.get_key_down('escape')")
        )
        assert "Keyboard.current.escapeKey.wasPressedThisFrame" in result

    def test_get_key_pressed_escape(self):
        """get_key (held) should map to isPressed."""
        result = _translate_source(
            _make_input_source("Input.get_key('escape')")
        )
        assert "Keyboard.current.escapeKey.isPressed" in result

    def test_get_key_up_space(self):
        result = _translate_source(
            _make_input_source("Input.get_key_up('space')")
        )
        assert "Keyboard.current.spaceKey.wasReleasedThisFrame" in result

    def test_get_key_down_arrow_keys(self):
        for py_key, cs_key in [
            ("left", "leftArrowKey"),
            ("right", "rightArrowKey"),
            ("up", "upArrowKey"),
            ("down", "downArrowKey"),
        ]:
            result = _translate_source(
                _make_input_source(f"Input.get_key_down('{py_key}')")
            )
            assert f"Keyboard.current.{cs_key}.wasPressedThisFrame" in result, (
                f"Arrow key '{py_key}' should map to {cs_key}"
            )

    def test_get_key_down_letter_a(self):
        result = _translate_source(
            _make_input_source("Input.get_key_down('a')")
        )
        assert "Keyboard.current.aKey.wasPressedThisFrame" in result

    def test_get_key_return_maps_to_enter(self):
        result = _translate_source(
            _make_input_source("Input.get_key_down('return')")
        )
        assert "Keyboard.current.enterKey.wasPressedThisFrame" in result


# ══════════════════════════════════════════════════════════════════════
#  NEW INPUT SYSTEM — Mouse
# ══════════════════════════════════════════════════════════════════════

class TestNewInputMouse:
    """Verify Mouse.current.* translations for the new input system."""

    def test_mouse_button_down_left(self):
        result = _translate_source(
            _make_input_source("Input.get_mouse_button_down(0)")
        )
        assert "Mouse.current.leftButton.wasPressedThisFrame" in result

    def test_mouse_button_down_right(self):
        result = _translate_source(
            _make_input_source("Input.get_mouse_button_down(1)")
        )
        assert "Mouse.current.rightButton.wasPressedThisFrame" in result

    def test_mouse_button_down_middle(self):
        result = _translate_source(
            _make_input_source("Input.get_mouse_button_down(2)")
        )
        assert "Mouse.current.middleButton.wasPressedThisFrame" in result

    def test_mouse_button_up_left(self):
        result = _translate_source(
            _make_input_source("Input.get_mouse_button_up(0)")
        )
        assert "Mouse.current.leftButton.wasReleasedThisFrame" in result

    def test_mouse_button_held_left(self):
        result = _translate_source(
            _make_input_source("Input.get_mouse_button(0)")
        )
        assert "Mouse.current.leftButton.isPressed" in result

    def test_mouse_position_method(self):
        result = _translate_source(
            _make_input_source("Input.get_mouse_position()", as_condition=False)
        )
        assert "Mouse.current.position.ReadValue()" in result

    def test_mouse_position_property(self):
        result = _translate_source(
            _make_input_source("Input.mouse_position", as_condition=False)
        )
        assert "Mouse.current.position.ReadValue()" in result


# ══════════════════════════════════════════════════════════════════════
#  NEW INPUT SYSTEM — Axis (TODO fallback)
# ══════════════════════════════════════════════════════════════════════

class TestNewInputAxis:
    def test_axis_emits_keyboard(self):
        result = _translate_source(
            _make_input_source("Input.get_axis('Horizontal')", as_condition=False)
        )
        assert "Keyboard.current.dKey.isPressed" in result
        assert "Keyboard.current.aKey.isPressed" in result


# ══════════════════════════════════════════════════════════════════════
#  USING DIRECTIVE
# ══════════════════════════════════════════════════════════════════════

class TestInputSystemUsings:
    """Verify using UnityEngine.InputSystem is added/absent correctly."""

    def test_new_input_adds_using(self):
        result = _translate_source(
            _make_input_source("Input.get_key_down('space')"),
            input_system="new",
        )
        assert "using UnityEngine.InputSystem;" in result

    def test_legacy_does_not_add_using(self):
        result = _translate_source(
            _make_input_source("Input.get_key_down('space')"),
            input_system="legacy",
        )
        assert "UnityEngine.InputSystem" not in result

    def test_new_input_using_only_when_input_used(self):
        """If no Input calls, don't add the using even if input_system='new'."""
        source = (
            "from src.engine.core import MonoBehaviour\n"
            "class Bar(MonoBehaviour):\n"
            "    def update(self):\n"
            "        x = 1\n"
        )
        result = _translate_source(source, input_system="new")
        assert "UnityEngine.InputSystem" not in result


# ══════════════════════════════════════════════════════════════════════
#  LEGACY INPUT SYSTEM
# ══════════════════════════════════════════════════════════════════════

class TestLegacyInput:
    """Verify legacy Input.Get* translations."""

    def test_legacy_get_key_down(self):
        result = _translate_source(
            _make_input_source("Input.get_key_down('space')"),
            input_system="legacy",
        )
        assert "Input.GetKeyDown(" in result
        # Legacy uses KeyCode enum, not Keyboard.current
        assert "Keyboard.current" not in result

    def test_legacy_get_key(self):
        result = _translate_source(
            _make_input_source("Input.get_key('escape')"),
            input_system="legacy",
        )
        assert "Input.GetKey(" in result

    def test_legacy_get_mouse_button_down(self):
        result = _translate_source(
            _make_input_source("Input.get_mouse_button_down(0)"),
            input_system="legacy",
        )
        assert "Input.GetMouseButtonDown(" in result
        assert "Mouse.current" not in result

    def test_legacy_get_axis(self):
        result = _translate_source(
            _make_input_source("Input.get_axis('Horizontal')", as_condition=False),
            input_system="legacy",
        )
        assert "Input.GetAxis(" in result
        assert "TODO" not in result

    def test_legacy_mouse_position(self):
        result = _translate_source(
            _make_input_source("Input.get_mouse_position()", as_condition=False),
            input_system="legacy",
        )
        assert "Input.mousePosition" in result


# ══════════════════════════════════════════════════════════════════════
#  translate_file() entry point
# ══════════════════════════════════════════════════════════════════════

class TestTranslateFileEntryPoint:
    """Ensure translate_file() properly forwards input_system parameter."""

    def test_translate_file_new_input(self):
        source = _make_input_source("Input.get_key_down('space')")
        result = _translate_via_file(source, input_system="new")
        assert "Keyboard.current.spaceKey.wasPressedThisFrame" in result
        assert "using UnityEngine.InputSystem;" in result

    def test_translate_file_legacy_input(self):
        source = _make_input_source("Input.get_key_down('space')")
        result = _translate_via_file(source, input_system="legacy")
        assert "Input.GetKeyDown(" in result
        assert "UnityEngine.InputSystem" not in result

    def test_translate_file_default_is_new(self):
        """Default input_system should be 'new'."""
        source = _make_input_source("Input.get_key_down('space')")
        result = _translate_via_file(source)  # no input_system kwarg
        assert "Keyboard.current.spaceKey.wasPressedThisFrame" in result
