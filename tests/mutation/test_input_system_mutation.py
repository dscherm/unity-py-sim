"""Mutation tests for Input System translation.

These tests monkeypatch the translator internals to verify that
the contract tests would catch real bugs (wrong API, wrong key mapping).
"""

from unittest.mock import patch
from src.translator.python_parser import parse_python
from src.translator.python_to_csharp import translate
import src.translator.python_to_csharp as translator_mod


def _make_input_source(input_call: str) -> str:
    return (
        "from src.engine.core import MonoBehaviour\n"
        "from src.engine.input_manager import Input\n"
        "class Foo(MonoBehaviour):\n"
        "    def update(self):\n"
        f"        if {input_call}:\n"
        "            self.do_thing()\n"
    )


def _translate_new(source: str) -> str:
    parsed = parse_python(source)
    return translate(parsed, input_system="new")


def _translate_legacy(source: str) -> str:
    parsed = parse_python(source)
    return translate(parsed, input_system="legacy")


# ══════════════════════════════════════════════════════════════════════
#  Mutation: force legacy when new was requested
# ══════════════════════════════════════════════════════════════════════

class TestMutationForceLegacy:
    """If we break the config so 'new' acts like 'legacy', tests must catch it."""

    def test_forcing_legacy_produces_wrong_api(self):
        """Monkeypatch _config.input_system to 'legacy' even when 'new' requested.
        The result should NOT contain Keyboard.current (mutation detected)."""
        source = _make_input_source("Input.get_key_down('space')")
        parsed = parse_python(source)

        # Normal translation should produce new input system API
        normal_result = translate(parsed, input_system="new")
        assert "Keyboard.current?.spaceKey.wasPressedThisFrame == true" in normal_result

        # Mutant: override config after translate sets it
        original_translate_new = translator_mod._translate_new_input_system

        def mutant_translate_expr(expr):
            """Pretend new input system doesn't exist — return expr unchanged."""
            return expr

        with patch.object(translator_mod, "_translate_new_input_system", side_effect=mutant_translate_expr):
            mutant_result = translate(parsed, input_system="new")

        # The mutant should produce DIFFERENT output (no Keyboard.current)
        assert "Keyboard.current" not in mutant_result, (
            "Mutation not detected: forcing legacy path should remove Keyboard.current"
        )

    def test_mouse_mutation_detected(self):
        """Same mutation for mouse input."""
        source = _make_input_source("Input.get_mouse_button_down(0)")
        parsed = parse_python(source)

        normal_result = translate(parsed, input_system="new")
        assert "Mouse.current?.leftButton.wasPressedThisFrame == true" in normal_result

        def mutant_translate_expr(expr):
            return expr

        with patch.object(translator_mod, "_translate_new_input_system", side_effect=mutant_translate_expr):
            mutant_result = translate(parsed, input_system="new")

        assert "Mouse.current" not in mutant_result


# ══════════════════════════════════════════════════════════════════════
#  Mutation: wrong key name mapping
# ══════════════════════════════════════════════════════════════════════

class TestMutationWrongKeyMap:
    """If _KEY_NAME_MAP returns wrong values, tests must catch it."""

    def test_wrong_space_key_mapping(self):
        """Mutate 'space' to map to 'enterKey' instead of 'spaceKey'."""
        source = _make_input_source("Input.get_key_down('space')")
        parsed = parse_python(source)

        # Patch the key map
        original_map = translator_mod._KEY_NAME_MAP.copy()
        mutant_map = original_map.copy()
        mutant_map["space"] = "enterKey"  # WRONG mapping

        with patch.dict(translator_mod._KEY_NAME_MAP, mutant_map, clear=True):
            result = translate(parsed, input_system="new")

        # Should have the WRONG key
        assert "enterKey" in result, "Mutant map should produce enterKey"
        assert "spaceKey" not in result, "Mutant map should NOT produce spaceKey"

    def test_wrong_mouse_button_mapping(self):
        """Mutate mouse button 0 to map to 'rightButton' instead of 'leftButton'."""
        source = _make_input_source("Input.get_mouse_button_down(0)")
        parsed = parse_python(source)

        original_map = translator_mod._MOUSE_BUTTON_MAP.copy()
        mutant_map = original_map.copy()
        mutant_map["0"] = "rightButton"  # WRONG mapping

        with patch.dict(translator_mod._MOUSE_BUTTON_MAP, mutant_map, clear=True):
            result = translate(parsed, input_system="new")

        assert "rightButton" in result, "Mutant map should produce rightButton"
        assert "leftButton" not in result, "Mutant map should NOT produce leftButton"

    def test_correct_mapping_baseline(self):
        """Verify the correct mapping works (baseline for mutation comparison)."""
        source = _make_input_source("Input.get_key_down('space')")
        result = _translate_new(source)
        assert "spaceKey" in result
        assert "enterKey" not in result
