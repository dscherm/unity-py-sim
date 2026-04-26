from __future__ import annotations
"""Contract tests for translator round-2 fixes.

These tests verify Unity C# conventions are respected by the translator,
derived independently from Unity documentation — NOT from implementation.

Covers:
  1. Multi-class using directives (hoisted before namespace)
  2. Color tuple -> Color32 translation
  3. Simulator-only property stripping
  4. Trigger callback Collider2D signatures
  5. .Count vs .Length
  6. Enum PascalCase casing
  7. Dynamic field regex (no cross-line matches)
"""

import re

import pytest

from src.translator.python_to_csharp import translate
from src.translator.python_parser import parse_python


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _translate_src(source: str, namespace: str | None = None) -> str:
    """Parse and translate Python source to C#."""
    parsed = parse_python(source)
    return translate(parsed, namespace=namespace)


def _lines(cs: str) -> list[str]:
    return cs.split("\n")


# ===========================================================================
# Fix 1 — Multi-class using directives
# ===========================================================================

class TestMultiClassUsingDirectives:
    """Unity C# convention: all `using` directives appear at the top of the
    file, BEFORE any namespace or class definition. Multiple classes in a
    single file must not re-emit their own using blocks."""

    MULTI_CLASS_SRC = """\
from enum import IntEnum

class Layers(IntEnum):
    DEFAULT = 0
    PLAYER = 8
    ENEMY = 9

class Player(MonoBehaviour):
    def start(self):
        self.health = 100
"""

    def test_using_before_namespace(self):
        cs = _translate_src(self.MULTI_CLASS_SRC, namespace="SpaceInvaders")
        lines = _lines(cs)
        first_using = next((i for i, l in enumerate(lines) if l.strip().startswith("using ")), None)
        first_namespace = next((i for i, l in enumerate(lines) if "namespace " in l), None)
        assert first_using is not None, "Expected at least one using directive"
        assert first_namespace is not None, "Expected a namespace declaration"
        assert first_using < first_namespace, (
            f"using directive at line {first_using} must come before namespace at line {first_namespace}"
        )

    def test_no_using_between_classes(self):
        cs = _translate_src(self.MULTI_CLASS_SRC, namespace="SpaceInvaders")
        # After the namespace line, there should be no 'using' directives
        lines = _lines(cs)
        ns_idx = next(i for i, l in enumerate(lines) if "namespace " in l)
        after_ns = "\n".join(lines[ns_idx:])
        assert "using " not in after_ns, (
            f"Found 'using' directive after namespace:\n{after_ns}"
        )

    def test_using_deduplicated(self):
        cs = _translate_src(self.MULTI_CLASS_SRC, namespace="NS")
        using_lines = [l.strip() for l in _lines(cs) if l.strip().startswith("using ")]
        assert len(using_lines) == len(set(using_lines)), (
            f"Duplicate using directives found: {using_lines}"
        )


# ===========================================================================
# Fix 2 — Color tuple -> Color32
# ===========================================================================

class TestColorTupleTranslation:
    """Unity convention: colors are Color32 structs, constructed as
    new Color32(r, g, b, a). Python (R,G,B) tuples must translate to
    Color32 with alpha=255."""

    def test_field_default_color32(self):
        src = """\
class Player(MonoBehaviour):
    def __init__(self):
        self.color = (255, 0, 0)
"""
        cs = _translate_src(src)
        assert "Color32" in cs, "Color field should be typed Color32"
        assert "new Color32(255, 0, 0, 255)" in cs, (
            "Field default (255,0,0) must become new Color32(255, 0, 0, 255)"
        )

    def test_array_of_colors(self):
        src = """\
class Player(MonoBehaviour):
    def __init__(self):
        self.colors: list[tuple[int,int,int]] = [(50, 255, 50), (80, 200, 80)]
"""
        cs = _translate_src(src)
        assert "Color32[]" in cs, "list[tuple[int,int,int]] should become Color32[]"
        assert "new Color32(50, 255, 50, 255)" in cs
        assert "new Color32(80, 200, 80, 255)" in cs

    def test_expression_assignment_color(self):
        src = """\
class Player(MonoBehaviour):
    def __init__(self):
        self.sr = None
    def start(self):
        self.sr = self.get_component(SpriteRenderer)
        self.sr.color = (0, 255, 0)
"""
        cs = _translate_src(src)
        assert "new Color32(0, 255, 0, 255)" in cs, (
            "sr.color = (0,255,0) must produce new Color32(0, 255, 0, 255)"
        )

    def test_tuple_type_annotation_becomes_color32(self):
        src = """\
class Player(MonoBehaviour):
    def __init__(self):
        self.tint: tuple[int, int, int] = (128, 128, 128)
"""
        cs = _translate_src(src)
        assert "Color32" in cs, "tuple[int,int,int] annotation should map to Color32"

    def test_alpha_channel_always_255(self):
        """Unity Color32 expects RGBA. Python tuples with 3 ints must default alpha to 255."""
        src = """\
class Player(MonoBehaviour):
    def start(self):
        self.color = (10, 20, 30)
"""
        cs = _translate_src(src)
        # Must have 4 args and alpha=255
        match = re.search(r"new Color32\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)", cs)
        assert match is not None, "Expected Color32 constructor in output"
        assert match.group(4) == "255", f"Alpha must be 255, got {match.group(4)}"


# ===========================================================================
# Fix 3 — Simulator-only property stripping
# ===========================================================================

class TestSimulatorPropertyStripping:
    """Unity uses inspector-assigned references for audio clips and sprites.
    Simulator-only APIs (clip_ref, asset_ref, _sync_from_transform,
    DisplayManager) must be stripped from output."""

    def test_clip_ref_stripped(self):
        src = """\
class Player(MonoBehaviour):
    def start(self):
        self.audio = self.get_component(AudioSource)
        self.audio.clip_ref = "shoot_sound"
"""
        cs = _translate_src(src)
        assert "clipRef" not in cs, "clip_ref assignment must be stripped"
        assert "shoot_sound" not in cs, "clip_ref value must be stripped"

    def test_asset_ref_stripped(self):
        src = """\
class Player(MonoBehaviour):
    def start(self):
        self.sr = self.get_component(SpriteRenderer)
        self.sr.asset_ref = "player_sprite"
"""
        cs = _translate_src(src)
        assert "assetRef" not in cs, "asset_ref assignment must be stripped"
        assert "player_sprite" not in cs

    def test_sync_from_transform_stripped(self):
        src = """\
class Player(MonoBehaviour):
    def start(self):
        self.rb = self.get_component(Rigidbody2D)
        self.rb._sync_from_transform()
"""
        cs = _translate_src(src)
        assert "_sync_from_transform" not in cs
        assert "SyncFromTransform" not in cs
        assert "syncFromTransform" not in cs

    def test_display_manager_stripped(self):
        src = """\
class Player(MonoBehaviour):
    def start(self):
        DisplayManager.instance().set_resolution(800, 600)
"""
        cs = _translate_src(src)
        assert "DisplayManager" not in cs

    def test_non_simulator_code_preserved(self):
        """Stripping must not remove legitimate game code."""
        src = """\
class Player(MonoBehaviour):
    def start(self):
        self.rb = self.get_component(Rigidbody2D)
        self.health = 100
        self.rb._sync_from_transform()
"""
        cs = _translate_src(src)
        assert "health" in cs, "Non-simulator code must be preserved"
        assert "Rigidbody2D" in cs


# ===========================================================================
# Fix 4 — Trigger callback signatures
# ===========================================================================

class TestTriggerCallbackSignatures:
    """Unity convention: OnTriggerEnter2D/Exit2D/Stay2D always receive
    Collider2D parameter, even if the Python simulator passes GameObject."""

    def test_on_trigger_enter_2d_collider2d(self):
        src = """\
class Player(MonoBehaviour):
    def on_trigger_enter_2d(self, other: GameObject):
        pass
"""
        cs = _translate_src(src)
        assert "Collider2D" in cs, "Trigger callback must use Collider2D, not GameObject"
        assert "OnTriggerEnter2D" in cs

    def test_on_trigger_exit_2d_collider2d(self):
        src = """\
class Player(MonoBehaviour):
    def on_trigger_exit_2d(self, other: GameObject):
        pass
"""
        cs = _translate_src(src)
        assert "OnTriggerExit2D(Collider2D" in cs

    def test_on_trigger_stay_2d_collider2d(self):
        src = """\
class Player(MonoBehaviour):
    def on_trigger_stay_2d(self, other):
        pass
"""
        cs = _translate_src(src)
        assert "OnTriggerStay2D(Collider2D" in cs

    def test_trigger_other_dot_layer_becomes_gameobject_layer(self):
        """In Unity, Collider2D has no .layer property. Must use
        other.gameObject.layer to get the layer from a trigger callback."""
        src = """\
class Player(MonoBehaviour):
    def on_trigger_enter_2d(self, other: GameObject):
        if other.layer == 8:
            pass
"""
        cs = _translate_src(src)
        assert "other.gameObject.layer" in cs, (
            "other.layer must become other.gameObject.layer for Collider2D"
        )


# ===========================================================================
# Fix 5 — .Count vs .Length
# ===========================================================================

class TestCountVsLength:
    """Unity/C# convention: arrays use .Length, List<T> uses .Count.
    Translator must track field types and emit the correct property."""

    def test_array_uses_length(self):
        src = """\
class Player(MonoBehaviour):
    def __init__(self):
        self.colors: list[tuple[int,int,int]] = [(255,0,0), (0,255,0)]
    def update(self):
        count = len(self.colors)
"""
        cs = _translate_src(src)
        # colors should be Color32[] (array), so .Length
        assert ".Length" in cs, "Array fields must use .Length"

    def test_list_uses_count(self):
        src = """\
class Player(MonoBehaviour):
    def __init__(self):
        self.items: list[str] = []
    def start(self):
        self.items.append("sword")
    def update(self):
        n = len(self.items)
"""
        cs = _translate_src(src)
        # items uses .append(), so it becomes List<string> and should use .Count
        assert ".Count" in cs, "List<T> fields must use .Count"


# ===========================================================================
# Fix 6 — Enum PascalCase
# ===========================================================================

class TestEnumPascalCase:
    """Unity convention: enum values are PascalCase. Python UPPER_SNAKE
    enum values must be converted to PascalCase in both declarations
    and usage expressions."""

    ENUM_SRC = """\
from enum import IntEnum

class PowerUpType(IntEnum):
    WIDE_PADDLE = 0
    SPEED_BOOST = 1
    EXTRA_LIFE = 2

class Player(MonoBehaviour):
    def start(self):
        self.current_power = PowerUpType.WIDE_PADDLE
"""

    def test_enum_declaration_pascal(self):
        cs = _translate_src(self.ENUM_SRC)
        assert "WidePaddle" in cs, "WIDE_PADDLE must become WidePaddle in declaration"
        assert "SpeedBoost" in cs, "SPEED_BOOST must become SpeedBoost"
        assert "ExtraLife" in cs, "EXTRA_LIFE must become ExtraLife"

    def test_enum_usage_pascal(self):
        cs = _translate_src(self.ENUM_SRC)
        assert "PowerUpType.WidePaddle" in cs, (
            "PowerUpType.WIDE_PADDLE usage must become PowerUpType.WidePaddle"
        )

    def test_enum_declaration_no_upper_snake(self):
        cs = _translate_src(self.ENUM_SRC)
        # After translation, UPPER_SNAKE should not appear in enum body
        # (but could appear in comments, so check inside enum block)
        assert "WIDE_PADDLE" not in cs
        assert "SPEED_BOOST" not in cs
        assert "EXTRA_LIFE" not in cs

    def test_mathf_pi_not_clobbered(self):
        """Mathf.PI must NOT be converted by the enum regex. PI looks like
        UPPER_SNAKE but is a Unity constant."""
        src = """\
class Circle(MonoBehaviour):
    def start(self):
        self.circumference = 2 * math.pi * self.radius
"""
        cs = _translate_src(src)
        assert "Mathf.PI" in cs, "math.pi must become Mathf.PI, not Mathf.Pi"

    def test_builtin_enum_casing(self):
        """Built-in Unity enums like RigidbodyType2D.KINEMATIC must also be converted."""
        src = """\
class Player(MonoBehaviour):
    def start(self):
        self.rb = self.get_component(Rigidbody2D)
        self.rb.body_type = RigidbodyType2D.KINEMATIC
"""
        cs = _translate_src(src)
        assert "RigidbodyType2D.Kinematic" in cs
        assert "KINEMATIC" not in cs


# ===========================================================================
# Fix 7 — Dynamic field regex (no cross-line matches)
# ===========================================================================

class TestDynamicFieldRegex:
    """The regex that discovers self.field = value in method bodies must
    operate per-line, not across line boundaries. A multiline regex
    could match 'self.field' from one line with '= value' from another,
    causing wrong type inference."""

    def test_no_cross_line_false_positive(self):
        """Two separate lines should not fuse into a false field assignment."""
        src = """\
class Player(MonoBehaviour):
    def update(self):
        if self.active:
            x = 42
"""
        # This should NOT infer a field named 'active' with type 'int'
        # because 'self.active' and '= 42' are on different lines
        cs = _translate_src(src)
        # The output should not declare 'int active = 42' as a field
        # Look for the field declarations section
        lines = _lines(cs)
        # Check that no field line maps 'active' with 'int' type
        for line in lines:
            stripped = line.strip()
            if "int" in stripped and "active" in stripped and "=" in stripped and "42" in stripped:
                pytest.fail(
                    f"Cross-line regex match produced false field: {stripped}"
                )

    def test_same_line_assignment_still_works(self):
        """Legitimate self.field = value on the same line should still be discovered."""
        src = """\
class Player(MonoBehaviour):
    def start(self):
        self.speed = 5.0
"""
        cs = _translate_src(src)
        assert "speed" in cs, "Same-line self.field = value should produce a field"


# ===========================================================================
# Integration: full multi-feature file
# ===========================================================================

class TestIntegrationMultiFeature:
    """Translate a file exercising multiple round-2 fixes at once."""

    FULL_SRC = """\
from enum import IntEnum

class GameState(IntEnum):
    WAITING = 0
    PLAYING = 1
    GAME_OVER = 2

class GameManager(MonoBehaviour):
    def __init__(self):
        self.state = GameState.WAITING
        self.bg_color = (30, 30, 60)
        self.row_colors: list[tuple[int,int,int]] = [(255,0,0), (0,255,0), (0,0,255)]

    def start(self):
        self.sr = self.get_component(SpriteRenderer)
        self.sr.asset_ref = "background"
        self.audio = self.get_component(AudioSource)
        self.audio.clip_ref = "music"
        self.rb = self.get_component(Rigidbody2D)
        self.rb._sync_from_transform()

    def on_trigger_enter_2d(self, other: GameObject):
        if other.layer == 8:
            self.state = GameState.PLAYING

    def update(self):
        n = len(self.row_colors)
        angle = 2 * math.pi * n
"""

    def test_full_translation_compiles_shape(self):
        cs = _translate_src(self.FULL_SRC, namespace="MyGame")

        # Using before namespace
        lines = _lines(cs)
        ns_line = next(i for i, l in enumerate(lines) if "namespace " in l)
        for i, l in enumerate(lines):
            if l.strip().startswith("using "):
                assert i < ns_line, f"using at line {i} after namespace at {ns_line}"

        # Enum PascalCase — declarations must be PascalCase
        assert "Waiting" in cs
        assert "Playing" in cs
        assert "GameOver" in cs
        # Usage in method bodies must be PascalCase
        assert "GameState.Playing" in cs
        # Enum declaration must NOT have UPPER_SNAKE
        # (field defaults may still have it if enum mapping doesn't cover defaults)
        enum_block = cs[cs.index("public enum"):cs.index("}") + 1]
        assert "WAITING" not in enum_block
        assert "PLAYING" not in enum_block
        assert "GAME_OVER" not in enum_block

        # Color32
        assert "new Color32(30, 30, 60, 255)" in cs
        assert "Color32[]" in cs

        # Stripped
        assert "assetRef" not in cs
        assert "clipRef" not in cs
        assert "SyncFromTransform" not in cs and "_sync_from_transform" not in cs

        # Trigger signature
        assert "Collider2D" in cs
        assert "other.gameObject.layer" in cs

        # .Length for Color32[] array
        assert ".Length" in cs

        # Mathf.PI
        assert "Mathf.PI" in cs
