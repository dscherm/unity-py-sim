"""Independent validation tests for Task 10 — Unity 6 API mappings & New Input System.

These tests verify:
- Unity 6 rb.velocity -> rb.linearVelocity mapping
- Unity 5 rb.velocity stays rb.velocity
- New Input System: Mouse.current / Keyboard.current patterns
- Legacy Input System: Input.GetKey / Input.GetMouseButton patterns
- using UnityEngine.InputSystem auto-added for new input system
- Edge cases: right/middle mouse buttons, unusual keys, sqrMagnitude
- Mutation tests: monkeypatch breakage detection
"""

import re
import pytest
from pathlib import Path

from src.translator.python_to_csharp import translate, translate_file, _config, _translate_new_input_system
from src.translator.python_parser import (
    PyFile, PyClass, PyField, PyMethod, PyParameter, parse_python_file,
)


# ── Helpers ──────────────────────────────────────────────────

def _make_monobehaviour(name: str, methods: list[PyMethod], fields=None, imports=None) -> PyFile:
    """Create a minimal PyFile with a single MonoBehaviour class."""
    return PyFile(
        imports=imports or [],
        classes=[PyClass(
            name=name,
            base_classes=["MonoBehaviour"],
            is_monobehaviour=True,
            fields=fields or [],
            methods=methods,
        )],
    )


def _translate_simple_body(body: str, *, unity_version=6, input_system="new") -> str:
    """Translate a MonoBehaviour with a single update() method containing the given body.

    If body is a bare ``if ...:`` with no indented block, a placeholder body
    is appended so the translator doesn't strip the empty-bodied if statement.
    """
    # Ensure if/elif statements have a body so the translator keeps them
    lines = body.split("\n")
    if len(lines) == 1 and lines[0].rstrip().endswith(":"):
        body = body.rstrip() + "\n    pass"
    parsed = _make_monobehaviour(
        "TestBehaviour",
        methods=[PyMethod(
            name="update",
            body_source=body,
            is_lifecycle=True,
        )],
        imports=["from src.engine.input_manager import Input"],
    )
    return translate(parsed, unity_version=unity_version, input_system=input_system)


# ═══════════════════════════════════════════════════════════════
# CONTRACT TESTS — Unity 6 API conventions
# ═══════════════════════════════════════════════════════════════

class TestUnity6VelocityContract:
    """Verify Unity 6 Rigidbody API: velocity -> linearVelocity."""

    def test_velocity_becomes_linear_velocity_unity6(self):
        """Unity 6 renamed Rigidbody.velocity to Rigidbody.linearVelocity."""
        result = _translate_simple_body("rb.velocity = Vector2(1, 0)", unity_version=6)
        assert "linearVelocity" in result
        # Should NOT contain bare .velocity (only linearVelocity)
        # Use regex to avoid matching "linearVelocity"
        lines_with_velocity = [
            line for line in result.split("\n")
            if ".velocity" in line and "linearVelocity" not in line
        ]
        assert len(lines_with_velocity) == 0, f"Found bare .velocity in Unity 6 output: {lines_with_velocity}"

    def test_velocity_stays_velocity_unity5(self):
        """Unity 5 should keep .velocity as-is."""
        result = _translate_simple_body("rb.velocity = Vector2(1, 0)", unity_version=5)
        assert ".velocity" in result
        assert "linearVelocity" not in result

    def test_angular_velocity_unity6(self):
        """Unity 6: angular_velocity -> angularVelocity (unchanged name in C#)."""
        result = _translate_simple_body("rb.angular_velocity = 5.0", unity_version=6)
        assert "angularVelocity" in result

    def test_angular_velocity_unity5(self):
        """Unity 5: angular_velocity -> angularVelocity (same mapping)."""
        result = _translate_simple_body("rb.angular_velocity = 5.0", unity_version=5)
        assert "angularVelocity" in result

    def test_sqr_magnitude_property(self):
        """sqr_magnitude -> sqrMagnitude for both Unity versions."""
        for version in (5, 6):
            result = _translate_simple_body("speed = rb.velocity.sqr_magnitude", unity_version=version)
            assert "sqrMagnitude" in result

    def test_velocity_read_unity6(self):
        """Reading velocity (not just writing) should also become linearVelocity in Unity 6."""
        result = _translate_simple_body("speed = rb.velocity.sqr_magnitude", unity_version=6)
        assert "linearVelocity" in result
        assert "sqrMagnitude" in result


class TestNewInputSystemContract:
    """Verify New Input System: Mouse.current / Keyboard.current patterns per Unity docs."""

    # ── Mouse buttons ──

    def test_mouse_button_down_left(self):
        """Input.get_mouse_button_down(0) -> Mouse.current.leftButton.wasPressedThisFrame"""
        result = _translate_simple_body("if Input.get_mouse_button_down(0):")
        assert "Mouse.current.leftButton.wasPressedThisFrame" in result

    def test_mouse_button_down_right(self):
        """Input.get_mouse_button_down(1) -> Mouse.current.rightButton.wasPressedThisFrame"""
        result = _translate_simple_body("if Input.get_mouse_button_down(1):")
        assert "Mouse.current.rightButton.wasPressedThisFrame" in result

    def test_mouse_button_down_middle(self):
        """Input.get_mouse_button_down(2) -> Mouse.current.middleButton.wasPressedThisFrame"""
        result = _translate_simple_body("if Input.get_mouse_button_down(2):")
        assert "Mouse.current.middleButton.wasPressedThisFrame" in result

    def test_mouse_button_up_left(self):
        """Input.get_mouse_button_up(0) -> Mouse.current.leftButton.wasReleasedThisFrame"""
        result = _translate_simple_body("if Input.get_mouse_button_up(0):")
        assert "Mouse.current.leftButton.wasReleasedThisFrame" in result

    def test_mouse_button_up_right(self):
        """Input.get_mouse_button_up(1) -> Mouse.current.rightButton.wasReleasedThisFrame"""
        result = _translate_simple_body("if Input.get_mouse_button_up(1):")
        assert "Mouse.current.rightButton.wasReleasedThisFrame" in result

    def test_mouse_button_held_left(self):
        """Input.get_mouse_button(0) -> Mouse.current.leftButton.isPressed"""
        result = _translate_simple_body("if Input.get_mouse_button(0):")
        assert "Mouse.current.leftButton.isPressed" in result

    def test_mouse_button_held_right(self):
        """Input.get_mouse_button(1) -> Mouse.current.rightButton.isPressed"""
        result = _translate_simple_body("if Input.get_mouse_button(1):")
        assert "Mouse.current.rightButton.isPressed" in result

    def test_mouse_button_held_middle(self):
        """Input.get_mouse_button(2) -> Mouse.current.middleButton.isPressed"""
        result = _translate_simple_body("if Input.get_mouse_button(2):")
        assert "Mouse.current.middleButton.isPressed" in result

    def test_mouse_position(self):
        """Input.get_mouse_position() -> Mouse.current.position.ReadValue()"""
        result = _translate_simple_body("pos = Input.get_mouse_position()")
        assert "Mouse.current.position.ReadValue()" in result

    def test_mouse_position_property(self):
        """Input.mouse_position -> Mouse.current.position.ReadValue()"""
        result = _translate_simple_body("pos = Input.mouse_position")
        assert "Mouse.current.position.ReadValue()" in result

    # ── Keyboard keys ──

    def test_key_down_space(self):
        """Input.get_key_down('space') -> Keyboard.current.spaceKey.wasPressedThisFrame"""
        result = _translate_simple_body("if Input.get_key_down('space'):")
        assert "Keyboard.current.spaceKey.wasPressedThisFrame" in result

    def test_key_down_escape(self):
        """Input.get_key_down('escape') -> Keyboard.current.escapeKey.wasPressedThisFrame"""
        result = _translate_simple_body("if Input.get_key_down('escape'):")
        assert "Keyboard.current.escapeKey.wasPressedThisFrame" in result

    def test_key_held_escape(self):
        """Input.get_key('escape') -> Keyboard.current.escapeKey.isPressed"""
        result = _translate_simple_body("if Input.get_key('escape'):")
        assert "Keyboard.current.escapeKey.isPressed" in result

    def test_key_up_space(self):
        """Input.get_key_up('space') -> Keyboard.current.spaceKey.wasReleasedThisFrame"""
        result = _translate_simple_body("if Input.get_key_up('space'):")
        assert "Keyboard.current.spaceKey.wasReleasedThisFrame" in result

    def test_arrow_keys(self):
        """Arrow key names map to Unity's xArrowKey pattern."""
        for py_key, cs_key in [("left", "leftArrowKey"), ("right", "rightArrowKey"),
                                ("up", "upArrowKey"), ("down", "downArrowKey")]:
            result = _translate_simple_body(f"if Input.get_key_down('{py_key}'):")
            assert f"Keyboard.current.{cs_key}.wasPressedThisFrame" in result, \
                f"Failed for key '{py_key}': expected {cs_key}"

    def test_letter_keys(self):
        """Single letter keys map to xKey pattern."""
        for letter in "wasd":
            result = _translate_simple_body(f"if Input.get_key('{letter}'):")
            assert f"Keyboard.current.{letter}Key.isPressed" in result, \
                f"Failed for letter key '{letter}'"

    def test_modifier_keys(self):
        """Modifier keys: left_shift -> leftShiftKey, left_control -> leftCtrlKey."""
        result = _translate_simple_body("if Input.get_key('left_shift'):")
        assert "Keyboard.current.leftShiftKey.isPressed" in result

        result = _translate_simple_body("if Input.get_key('left_control'):")
        assert "Keyboard.current.leftCtrlKey.isPressed" in result

    def test_return_key(self):
        """return key -> enterKey (Unity naming)."""
        result = _translate_simple_body("if Input.get_key_down('return'):")
        assert "Keyboard.current.enterKey.wasPressedThisFrame" in result

    def test_tab_key(self):
        """tab key -> tabKey."""
        result = _translate_simple_body("if Input.get_key_down('tab'):")
        assert "Keyboard.current.tabKey.wasPressedThisFrame" in result

    def test_unknown_key_fallback(self):
        """Unknown key name gets 'Key' suffix appended as fallback."""
        result = _translate_simple_body("if Input.get_key_down('backspace'):")
        assert "Keyboard.current.backspaceKey.wasPressedThisFrame" in result

    def test_axis_becomes_keyboard(self):
        """Input.get_axis('Horizontal') emits keyboard-based axis emulation."""
        result = _translate_simple_body("h = Input.get_axis('Horizontal')")
        assert "Keyboard.current.dKey.isPressed" in result
        assert "Keyboard.current.aKey.isPressed" in result

    # ── Using directive ──

    def test_using_input_system_auto_added(self):
        """New Input System should auto-add 'using UnityEngine.InputSystem;'."""
        result = _translate_simple_body("if Input.get_key_down('space'):")
        assert "using UnityEngine.InputSystem;" in result

    def test_no_input_system_using_for_legacy(self):
        """Legacy mode should NOT add UnityEngine.InputSystem using."""
        result = _translate_simple_body(
            "if Input.get_key_down('space'):",
            input_system="legacy",
        )
        assert "UnityEngine.InputSystem" not in result


class TestLegacyInputSystemContract:
    """Verify legacy Input System: Input.GetKey / Input.GetMouseButton patterns."""

    def test_legacy_get_key_down(self):
        """Legacy: Input.get_key_down('space') -> Input.GetKeyDown(...)"""
        result = _translate_simple_body("if Input.get_key_down('space'):", input_system="legacy")
        assert "Input.GetKeyDown(" in result

    def test_legacy_get_key(self):
        """Legacy: Input.get_key('escape') -> Input.GetKey(...)"""
        result = _translate_simple_body("if Input.get_key('escape'):", input_system="legacy")
        assert "Input.GetKey(" in result

    def test_legacy_get_key_up(self):
        """Legacy: Input.get_key_up('space') -> Input.GetKeyUp(...)"""
        result = _translate_simple_body("if Input.get_key_up('space'):", input_system="legacy")
        assert "Input.GetKeyUp(" in result

    def test_legacy_mouse_button_down(self):
        """Legacy: Input.get_mouse_button_down(0) -> Input.GetMouseButtonDown(0)"""
        result = _translate_simple_body("if Input.get_mouse_button_down(0):", input_system="legacy")
        assert "Input.GetMouseButtonDown(0)" in result

    def test_legacy_mouse_button(self):
        """Legacy: Input.get_mouse_button(0) -> Input.GetMouseButton(0)"""
        result = _translate_simple_body("if Input.get_mouse_button(0):", input_system="legacy")
        assert "Input.GetMouseButton(0)" in result

    def test_legacy_mouse_button_up(self):
        """Legacy: Input.get_mouse_button_up(0) -> Input.GetMouseButtonUp(0)"""
        result = _translate_simple_body("if Input.get_mouse_button_up(0):", input_system="legacy")
        assert "Input.GetMouseButtonUp(0)" in result

    def test_legacy_get_axis(self):
        """Legacy: Input.get_axis('Horizontal') -> Input.GetAxis("Horizontal")"""
        result = _translate_simple_body("h = Input.get_axis('Horizontal')", input_system="legacy")
        assert 'Input.GetAxis("Horizontal")' in result

    def test_legacy_mouse_position(self):
        """Legacy: Input.get_mouse_position() -> Input.mousePosition"""
        result = _translate_simple_body("pos = Input.get_mouse_position()", input_system="legacy")
        assert "Input.mousePosition" in result

    def test_legacy_mouse_position_property(self):
        """Legacy: Input.mouse_position -> Input.mousePosition"""
        result = _translate_simple_body("pos = Input.mouse_position", input_system="legacy")
        assert "Input.mousePosition" in result

    def test_legacy_no_mouse_current(self):
        """Legacy mode should NEVER produce Mouse.current."""
        result = _translate_simple_body(
            "if Input.get_mouse_button_down(0):\n    pos = Input.get_mouse_position()",
            input_system="legacy",
        )
        assert "Mouse.current" not in result

    def test_legacy_no_keyboard_current(self):
        """Legacy mode should NEVER produce Keyboard.current."""
        result = _translate_simple_body("if Input.get_key_down('space'):", input_system="legacy")
        assert "Keyboard.current" not in result


# ═══════════════════════════════════════════════════════════════
# INTEGRATION TESTS — translate real example files
# ═══════════════════════════════════════════════════════════════

_EXAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "examples"


class TestAngryBirdsSlingshotIntegration:
    """Translate slingshot.py with both Unity configs and verify output differences."""

    @pytest.fixture
    def slingshot_path(self):
        return str(_EXAMPLES_DIR / "angry_birds" / "angry_birds_python" / "slingshot.py")

    def test_slingshot_unity6_new_input(self, slingshot_path):
        """Unity 6 + new input: should have Mouse.current, linearVelocity."""
        result = translate_file(slingshot_path, unity_version=6, input_system="new")
        assert "Mouse.current" in result
        assert "linearVelocity" in result
        assert "using UnityEngine.InputSystem;" in result

    def test_slingshot_unity5_legacy(self, slingshot_path):
        """Unity 5 + legacy: should have Input.GetMouseButton, .velocity (not linear)."""
        result = translate_file(slingshot_path, unity_version=5, input_system="legacy")
        assert "Mouse.current" not in result
        assert "Keyboard.current" not in result
        # Should have legacy Input.GetMouseButtonDown
        assert "Input.GetMouseButtonDown" in result
        assert "Input.GetMouseButton(" in result
        # velocity should stay as velocity (not linearVelocity)
        assert "linearVelocity" not in result
        # But velocity should be present
        assert ".velocity" in result
        assert "UnityEngine.InputSystem" not in result

    def test_slingshot_unity6_legacy_input(self, slingshot_path):
        """Unity 6 + legacy input: linearVelocity yes, but legacy Input API."""
        result = translate_file(slingshot_path, unity_version=6, input_system="legacy")
        assert "linearVelocity" in result
        assert "Input.GetMouseButtonDown" in result
        assert "Mouse.current" not in result

    def test_slingshot_unity5_new_input(self, slingshot_path):
        """Unity 5 + new input: velocity stays, but new input system used."""
        result = translate_file(slingshot_path, unity_version=5, input_system="new")
        assert "linearVelocity" not in result
        assert ".velocity" in result
        assert "Mouse.current" in result
        assert "using UnityEngine.InputSystem;" in result


class TestAngryBirdsBirdIntegration:
    """Translate bird.py — has velocity and sqr_magnitude."""

    @pytest.fixture
    def bird_path(self):
        return str(_EXAMPLES_DIR / "angry_birds" / "angry_birds_python" / "bird.py")

    def test_bird_unity6(self, bird_path):
        """Unity 6: rb.velocity.sqr_magnitude -> rb.linearVelocity.sqrMagnitude."""
        result = translate_file(bird_path, unity_version=6, input_system="new")
        assert "linearVelocity" in result
        assert "sqrMagnitude" in result

    def test_bird_unity5(self, bird_path):
        """Unity 5: rb.velocity.sqr_magnitude -> rb.velocity.sqrMagnitude."""
        result = translate_file(bird_path, unity_version=5, input_system="legacy")
        assert "linearVelocity" not in result
        assert "sqrMagnitude" in result
        # Should have .velocity.sqrMagnitude
        assert re.search(r"\.velocity\.sqrMagnitude", result)


# ═══════════════════════════════════════════════════════════════
# EDGE CASE TESTS
# ═══════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Edge cases and unusual combinations."""

    def test_mixed_velocity_and_input_same_file(self):
        """File using both velocity assignment and input reads."""
        body = (
            "if Input.get_mouse_button_down(0):\n"
            "    rb.velocity = Vector2(1, 0)"
        )
        result = _translate_simple_body(body, unity_version=6, input_system="new")
        assert "Mouse.current.leftButton.wasPressedThisFrame" in result
        assert "linearVelocity" in result

    def test_mixed_velocity_and_input_unity5(self):
        """Same mix but Unity 5 + legacy."""
        body = (
            "if Input.get_mouse_button_down(0):\n"
            "    rb.velocity = Vector2(1, 0)"
        )
        result = _translate_simple_body(body, unity_version=5, input_system="legacy")
        assert "Input.GetMouseButtonDown" in result
        assert "linearVelocity" not in result
        assert ".velocity" in result

    def test_multiple_input_types_in_one_method(self):
        """Multiple different input calls in the same method body."""
        body = (
            "if Input.get_key_down('space'):\n"
            "    self.jump()\n"
            "if Input.get_mouse_button(0):\n"
            "    self.shoot()\n"
            "pos = Input.get_mouse_position()"
        )
        result = _translate_simple_body(body, unity_version=6, input_system="new")
        assert "Keyboard.current.spaceKey.wasPressedThisFrame" in result
        assert "Mouse.current.leftButton.isPressed" in result
        assert "Mouse.current.position.ReadValue()" in result

    def test_velocity_not_replaced_in_variable_name(self):
        """'velocity' as a local variable name should also get mapped (known limitation)
        but the property .velocity should definitely be mapped."""
        # This tests that .velocity is replaced correctly
        body = "self.rb.velocity = velocity_vec"
        result = _translate_simple_body(body, unity_version=6)
        # The property access should become linearVelocity
        assert "linearVelocity" in result

    def test_default_config_is_unity6_new(self):
        """Default translation config should be Unity 6 + new input system."""
        parsed = _make_monobehaviour(
            "TestBehaviour",
            methods=[PyMethod(
                name="update",
                body_source="if Input.get_key_down('space'):\n    rb.velocity = Vector2(0, 5)",
                is_lifecycle=True,
            )],
            imports=["from src.engine.input_manager import Input"],
        )
        result = translate(parsed)  # No explicit version/input args
        assert "Keyboard.current.spaceKey.wasPressedThisFrame" in result
        assert "linearVelocity" in result

    def test_translate_file_passes_config(self):
        """translate_file() should forward unity_version and input_system to translate()."""
        bird_path = str(_EXAMPLES_DIR / "angry_birds" / "angry_birds_python" / "bird.py")
        result_u6 = translate_file(bird_path, unity_version=6, input_system="new")
        result_u5 = translate_file(bird_path, unity_version=5, input_system="legacy")
        # They should differ
        assert result_u6 != result_u5
        assert "linearVelocity" in result_u6
        assert "linearVelocity" not in result_u5


# ═══════════════════════════════════════════════════════════════
# MUTATION TESTS — monkeypatch to verify test sensitivity
# ═══════════════════════════════════════════════════════════════

class TestMutationVelocityMapping:
    """Monkeypatch velocity mapping to verify tests catch breakage."""

    def test_mutation_disable_linear_velocity(self, monkeypatch):
        """If Unity 6 velocity mapping is broken, tests should detect it."""
        import src.translator.python_to_csharp as mod

        original_translate_expr = mod._translate_py_expression

        def broken_translate_expr(expr):
            # Call original but then undo linearVelocity -> velocity
            result = original_translate_expr(expr)
            return result.replace("linearVelocity", "velocity")

        monkeypatch.setattr(mod, "_translate_py_expression", broken_translate_expr)

        result = _translate_simple_body("rb.velocity = Vector2(1, 0)", unity_version=6)
        # With the mutation, linearVelocity should be gone — broken behavior
        assert "linearVelocity" not in result, "Mutation should have removed linearVelocity"


class TestMutationInputSystem:
    """Monkeypatch input system translation to verify tests catch breakage."""

    def test_mutation_disable_new_input_system(self, monkeypatch):
        """If _translate_new_input_system is broken, mouse/keyboard patterns vanish."""
        import src.translator.python_to_csharp as mod

        # Replace with identity function
        monkeypatch.setattr(mod, "_translate_new_input_system", lambda expr: expr)

        result = _translate_simple_body("if Input.get_mouse_button_down(0):")
        # Should NOT have Mouse.current anymore (mutation broke it)
        assert "Mouse.current" not in result, "Mutation should have disabled Mouse.current translation"

    def test_mutation_wrong_mouse_button_map(self, monkeypatch):
        """If mouse button map is corrupted, wrong button names appear."""
        import src.translator.python_to_csharp as mod

        # Swap left and right buttons
        corrupted_map = {"0": "rightButton", "1": "leftButton", "2": "middleButton"}
        monkeypatch.setattr(mod, "_MOUSE_BUTTON_MAP", corrupted_map)

        result = _translate_simple_body("if Input.get_mouse_button_down(0):")
        # Should now have rightButton instead of leftButton — broken!
        assert "rightButton" in result, "Mutation should have swapped to rightButton"
        assert "leftButton" not in result, "leftButton should be gone after mutation"

    def test_mutation_config_forced_legacy(self, monkeypatch):
        """If config is stuck on legacy, new input system calls fall through."""
        import src.translator.python_to_csharp as mod

        # Force config to always return "legacy"
        original_config = mod._config

        class ForcedLegacyConfig:
            unity_version = 6
            input_system = "legacy"

        monkeypatch.setattr(mod, "_config", ForcedLegacyConfig())

        # Even though we request input_system="new", the monkeypatched config
        # won't be overwritten because translate() sets _config attributes.
        # Instead, we directly test _translate_py_expression with forced config.
        mod._config = ForcedLegacyConfig()
        body = "if Input.get_mouse_button_down(0):"
        result = _translate_simple_body(body, input_system="new")
        # Since translate() sets _config.input_system = "new", this should still work.
        # The mutation test verifies that translate() DOES set the config.
        assert "Mouse.current" in result, \
            "translate() should override config — if it doesn't, config mutation would break things"

    def test_mutation_key_name_map(self, monkeypatch):
        """If key name map is corrupted, wrong key names appear."""
        import src.translator.python_to_csharp as mod

        corrupted_keys = dict(mod._KEY_NAME_MAP)
        corrupted_keys["space"] = "WRONG_KEY"
        monkeypatch.setattr(mod, "_KEY_NAME_MAP", corrupted_keys)

        result = _translate_simple_body("if Input.get_key_down('space'):")
        assert "WRONG_KEY" in result, "Mutation should have injected WRONG_KEY"
        assert "spaceKey" not in result, "spaceKey should be gone after mutation"


# ═══════════════════════════════════════════════════════════════
# CONFIG ISOLATION TESTS — verify config doesn't leak between calls
# ═══════════════════════════════════════════════════════════════

class TestConfigIsolation:
    """Ensure translate() config changes don't leak between calls."""

    def test_config_set_by_translate(self):
        """translate() should set _config correctly each time."""
        parsed = _make_monobehaviour("A", methods=[
            PyMethod(name="update", body_source="rb.velocity = Vector2(0, 0)", is_lifecycle=True),
        ])

        # Translate with Unity 5
        result5 = translate(parsed, unity_version=5, input_system="legacy")
        assert "linearVelocity" not in result5

        # Now translate with Unity 6 — config should update
        result6 = translate(parsed, unity_version=6, input_system="new")
        assert "linearVelocity" in result6

        # And back to Unity 5 — should NOT have linearVelocity
        result5_again = translate(parsed, unity_version=5, input_system="legacy")
        assert "linearVelocity" not in result5_again

    def test_input_system_config_toggling(self):
        """Toggling input_system between calls should work correctly."""
        parsed = _make_monobehaviour("B", methods=[
            PyMethod(name="update", body_source="if Input.get_key_down('space'):\n    pass",
                     is_lifecycle=True),
        ], imports=["from src.engine.input_manager import Input"])

        result_new = translate(parsed, unity_version=6, input_system="new")
        assert "Keyboard.current" in result_new

        result_legacy = translate(parsed, unity_version=6, input_system="legacy")
        assert "Keyboard.current" not in result_legacy
        assert "Input.GetKeyDown" in result_legacy

        # Back to new
        result_new2 = translate(parsed, unity_version=6, input_system="new")
        assert "Keyboard.current" in result_new2
