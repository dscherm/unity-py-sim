"""Contract tests for translator round-2 fixes.

Validates Unity C# conventions independently of implementation.
Derived from Unity documentation and C# language spec, NOT from reading existing tests.
"""

from __future__ import annotations

import re
import pytest

from src.translator.python_parser import parse_python
from src.translator.python_to_csharp import translate


# ── Helpers ────────────────────────────────────────────────────

def _translate_src(source: str, namespace: str | None = None) -> str:
    """Parse + translate a Python source string to C#."""
    parsed = parse_python(source)
    return translate(parsed, namespace=namespace)


def _lines(text: str) -> list[str]:
    """Return non-blank stripped lines."""
    return [l.strip() for l in text.splitlines() if l.strip()]


# ═══════════════════════════════════════════════════════════════
# Fix 1: Multi-class using directives
#   C# spec: `using` directives must appear before namespace/class
# ═══════════════════════════════════════════════════════════════

class TestMultiClassUsings:
    """Using directives must be hoisted to the top, before any class definition."""

    MULTI_CLASS_SOURCE = """\
from enum import IntEnum

class Layers(IntEnum):
    DEFAULT = 0
    PLAYER = 1
    ENEMY = 2

class Player(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.speed: float = 5.0

    def start(self):
        self.rb = self.game_object.get_component(Rigidbody2D)
"""

    def test_using_before_namespace(self):
        """All using directives must come before the namespace declaration."""
        cs = _translate_src(self.MULTI_CLASS_SOURCE, namespace="SpaceGame")
        ns_idx = cs.find("namespace SpaceGame")
        assert ns_idx != -1, "namespace declaration expected"
        # Every 'using' line must appear before the namespace
        for i, line in enumerate(cs.splitlines()):
            stripped = line.strip()
            if stripped.startswith("using ") and stripped.endswith(";"):
                assert cs.find(stripped) < ns_idx, (
                    f"using directive '{stripped}' appears after namespace declaration"
                )

    def test_no_using_between_classes(self):
        """No using directive should appear between class definitions."""
        cs = _translate_src(self.MULTI_CLASS_SOURCE)
        # Find first class/enum definition
        first_class = re.search(r"(public\s+(enum|class)\s+\w+)", cs)
        assert first_class, "Expected at least one class/enum"
        after_first_class = cs[first_class.start():]
        # No using directives in the remainder after the first class
        using_in_body = re.findall(r"^\s*using\s+\w+", after_first_class, re.MULTILINE)
        assert using_in_body == [], f"Using directives found between classes: {using_in_body}"

    def test_usings_deduplicated(self):
        """Duplicate using directives should be collapsed."""
        cs = _translate_src(self.MULTI_CLASS_SOURCE)
        using_lines = [l.strip() for l in cs.splitlines() if l.strip().startswith("using ")]
        assert len(using_lines) == len(set(using_lines)), (
            f"Duplicate usings: {using_lines}"
        )


# ═══════════════════════════════════════════════════════════════
# Fix 2: Color tuple translation
#   Unity convention: Color32 uses byte components (0-255), alpha defaults 255
# ═══════════════════════════════════════════════════════════════

class TestColorTupleTranslation:
    """Python color tuples (R,G,B) must translate to Color32 in C#."""

    def test_field_default_color(self):
        """self.color = (255, 0, 0) becomes Color32 field with alpha 255."""
        src = """\
class Player(MonoBehaviour):

    def awake(self):
        self.color = (255, 0, 0)
"""
        cs = _translate_src(src)
        assert "Color32" in cs, "Expected Color32 type in output"
        assert "new Color32(255, 0, 0, 255)" in cs, (
            "Expected new Color32(255, 0, 0, 255) constructor call"
        )

    def test_color_array(self):
        """Array of color tuples becomes Color32[]."""
        src = """\
class Player(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.colors: list[tuple[int,int,int]] = [(50, 255, 50), (80, 200, 80)]
"""
        cs = _translate_src(src)
        assert "Color32" in cs
        assert "new Color32(50, 255, 50, 255)" in cs
        assert "new Color32(80, 200, 80, 255)" in cs

    def test_color_expression_assignment(self):
        """sr.color = (0, 255, 0) must use Color32 in expression."""
        src = """\
class Player(MonoBehaviour):

    def start(self):
        self.sr = self.game_object.get_component(SpriteRenderer)
        self.sr.color = (0, 255, 0)
"""
        cs = _translate_src(src)
        assert "new Color32(0, 255, 0, 255)" in cs

    def test_tuple_type_annotation_maps_to_color32(self):
        """tuple[int,int,int] type annotation maps to Color32."""
        src = """\
class Player(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.tint: tuple[int,int,int] = (128, 128, 255)
"""
        cs = _translate_src(src)
        assert "Color32" in cs

    def test_color32_has_four_components(self):
        """Color32 constructor must always have 4 args (R, G, B, A)."""
        src = """\
class Player(MonoBehaviour):

    def update(self):
        color = (100, 200, 50)
"""
        cs = _translate_src(src)
        # Find all Color32 constructor calls
        matches = re.findall(r"new Color32\(([^)]+)\)", cs)
        for match in matches:
            args = [a.strip() for a in match.split(",")]
            assert len(args) == 4, f"Color32 must have 4 args, got: {args}"


# ═══════════════════════════════════════════════════════════════
# Fix 3: Simulator-only property stripping
#   Unity uses Inspector-assigned references, not string paths
# ═══════════════════════════════════════════════════════════════

class TestSimulatorStripping:
    """Simulator-only properties and calls must be stripped from C# output."""

    def test_clip_ref_stripped(self):
        """audio.clip_ref = 'sound' is simulator-only, must not appear in C#."""
        src = """\
class Player(MonoBehaviour):

    def start(self):
        self.audio = self.game_object.get_component(AudioSource)
        self.audio.clip_ref = "explosion"
"""
        cs = _translate_src(src)
        assert "clip_ref" not in cs.lower().replace("clipref", "clip_ref"), (
            "clip_ref should be stripped"
        )
        assert "clipRef" not in cs, "clipRef should be stripped"
        assert "explosion" not in cs, "clip_ref value should be stripped"

    def test_asset_ref_stripped(self):
        """sr.asset_ref = 'sprite' is simulator-only."""
        src = """\
class Player(MonoBehaviour):

    def start(self):
        self.sr = self.game_object.get_component(SpriteRenderer)
        self.sr.asset_ref = "player_sprite"
"""
        cs = _translate_src(src)
        assert "assetRef" not in cs, "assetRef should be stripped"
        assert "player_sprite" not in cs, "asset_ref value should be stripped"

    def test_sync_from_transform_stripped(self):
        """rb._sync_from_transform() is simulator-only physics sync."""
        src = """\
class Player(MonoBehaviour):

    def start(self):
        self.rb = self.game_object.get_component(Rigidbody2D)
        self.rb._sync_from_transform()
"""
        cs = _translate_src(src)
        assert "_sync_from_transform" not in cs
        assert "SyncFromTransform" not in cs
        assert "syncFromTransform" not in cs

    def test_display_manager_stripped(self):
        """DisplayManager is simulator-only, Unity handles display natively."""
        src = """\
class GameManager(MonoBehaviour):

    def start(self):
        dm = DisplayManager.instance()
        dm.set_resolution(800, 600)
"""
        cs = _translate_src(src)
        assert "DisplayManager" not in cs


# ═══════════════════════════════════════════════════════════════
# Fix 4: Trigger callback signatures
#   Unity doc: OnTriggerEnter2D receives Collider2D, not GameObject
# ═══════════════════════════════════════════════════════════════

class TestTriggerCallbackSignatures:
    """Trigger callbacks must always use Collider2D parameter type."""

    def test_on_trigger_enter_2d_collider2d(self):
        """OnTriggerEnter2D must have Collider2D param, even if Python says GameObject."""
        src = """\
class Player(MonoBehaviour):

    def on_trigger_enter_2d(self, other: GameObject):
        pass
"""
        cs = _translate_src(src)
        assert "Collider2D" in cs, "OnTriggerEnter2D must receive Collider2D"
        # Should NOT have GameObject as param type
        # (Note: GameObject may appear elsewhere, just not as the param type)
        match = re.search(r"void\s+OnTriggerEnter2D\((\w+)\s+", cs)
        assert match, "Expected OnTriggerEnter2D method signature"
        assert match.group(1) == "Collider2D", (
            f"Expected Collider2D param, got {match.group(1)}"
        )

    def test_on_trigger_exit_2d_collider2d(self):
        """OnTriggerExit2D must also use Collider2D."""
        src = """\
class Player(MonoBehaviour):

    def on_trigger_exit_2d(self, other: GameObject):
        pass
"""
        cs = _translate_src(src)
        match = re.search(r"void\s+OnTriggerExit2D\((\w+)\s+", cs)
        assert match, "Expected OnTriggerExit2D method signature"
        assert match.group(1) == "Collider2D"

    def test_on_trigger_stay_2d_collider2d(self):
        """OnTriggerStay2D must also use Collider2D."""
        src = """\
class Player(MonoBehaviour):

    def on_trigger_stay_2d(self, other):
        pass
"""
        cs = _translate_src(src)
        match = re.search(r"void\s+OnTriggerStay2D\((\w+)\s+", cs)
        assert match, "Expected OnTriggerStay2D method signature"
        assert match.group(1) == "Collider2D"

    def test_trigger_body_uses_other_for_gameobject(self):
        """When accessing .tag on the collider other, it should use other.gameObject."""
        src = """\
class Player(MonoBehaviour):

    def on_trigger_enter_2d(self, other: GameObject):
        if other.layer == 1:
            pass
"""
        cs = _translate_src(src)
        # In Unity, Collider2D doesn't have .layer directly — need .gameObject.layer
        assert "other.gameObject.layer" in cs or "other.gameObject" in cs, (
            "Collider2D access to .layer should go through .gameObject"
        )


# ═══════════════════════════════════════════════════════════════
# Fix 5: .Count vs .Length
#   C# spec: arrays use .Length, List<T> uses .Count
# ═══════════════════════════════════════════════════════════════

class TestCountVsLength:
    """len() must translate to .Length for arrays and .Count for Lists."""

    def test_array_uses_length(self):
        """Color32[] field — len(self.colors) should use .Length."""
        src = """\
class Player(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.colors: list[tuple[int,int,int]] = [(255,0,0), (0,255,0)]

    def update(self):
        count = len(self.colors)
"""
        cs = _translate_src(src)
        # colors should be a Color32[] array
        assert ".Length" in cs, "Array field should use .Length"

    def test_list_uses_count(self):
        """List<T> field — len(self.items) should use .Count."""
        src = """\
class Player(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.items: list[GameObject] = []

    def update(self):
        self.items.append(self.game_object)
        count = len(self.items)
"""
        cs = _translate_src(src)
        assert ".Count" in cs, "List<T> field should use .Count"


# ═══════════════════════════════════════════════════════════════
# Fix 6: Enum value casing
#   Unity convention: enum values are PascalCase, not UPPER_SNAKE
# ═══════════════════════════════════════════════════════════════

class TestEnumValueCasing:
    """UPPER_SNAKE enum values must become PascalCase in both declaration and usage."""

    ENUM_SOURCE = """\
from enum import IntEnum

class PowerUpType(IntEnum):
    WIDE_PADDLE = 0
    EXTRA_LIFE = 1
    SPEED_BOOST = 2

class Player(MonoBehaviour):

    def awake(self):
        self.power_up = PowerUpType.WIDE_PADDLE

    def update(self):
        if self.power_up == PowerUpType.EXTRA_LIFE:
            pass
"""

    def test_enum_declaration_pascal_case(self):
        """Enum values in declaration must be PascalCase."""
        cs = _translate_src(self.ENUM_SOURCE)
        assert "WidePaddle" in cs, "WIDE_PADDLE should become WidePaddle"
        assert "ExtraLife" in cs, "EXTRA_LIFE should become ExtraLife"
        assert "SpeedBoost" in cs, "SPEED_BOOST should become SpeedBoost"

    def test_enum_usage_pascal_case(self):
        """Enum references in expressions must also be PascalCase."""
        cs = _translate_src(self.ENUM_SOURCE)
        assert "PowerUpType.WidePaddle" in cs, (
            "Usage of WIDE_PADDLE should become PowerUpType.WidePaddle"
        )
        assert "PowerUpType.ExtraLife" in cs, (
            "Usage of EXTRA_LIFE should become PowerUpType.ExtraLife"
        )

    def test_no_upper_snake_in_output(self):
        """No UPPER_SNAKE enum values should remain in the output."""
        cs = _translate_src(self.ENUM_SOURCE)
        assert "WIDE_PADDLE" not in cs, "WIDE_PADDLE should not appear in C# output"
        assert "EXTRA_LIFE" not in cs, "EXTRA_LIFE should not appear in C# output"
        assert "SPEED_BOOST" not in cs, "SPEED_BOOST should not appear in C# output"

    def test_mathf_pi_not_clobbered(self):
        """Mathf.PI must NOT be converted by the enum regex."""
        src = """\
class Player(MonoBehaviour):

    def update(self):
        angle = math.pi * 2
"""
        cs = _translate_src(src)
        assert "Mathf.PI" in cs, "Mathf.PI should remain as-is, not be PascalCased"
        assert "Mathf.Pi" not in cs, "Mathf.PI should not become Mathf.Pi"

    def test_builtin_enum_casing(self):
        """Built-in Unity enums (RigidbodyType2D) should also be PascalCase."""
        src = """\
class Player(MonoBehaviour):

    def start(self):
        self.rb = self.game_object.get_component(Rigidbody2D)
        self.rb.body_type = RigidbodyType2D.KINEMATIC
"""
        cs = _translate_src(src)
        assert "RigidbodyType2D.Kinematic" in cs
        assert "KINEMATIC" not in cs


# ═══════════════════════════════════════════════════════════════
# Fix 7: Dynamic field discovery regex
#   Regex must not match across line boundaries
# ═══════════════════════════════════════════════════════════════

class TestDynamicFieldRegex:
    """Dynamic field discovery must not create false matches across lines."""

    def test_no_cross_line_false_type(self):
        """Fields should only infer types from their own line, not subsequent lines."""
        src = """\
class Player(MonoBehaviour):

    def start(self):
        self.score = 0
        self.name = "player"
        self.position = Vector2(0, 0)
"""
        cs = _translate_src(src)
        # score should be int, not contaminated by the next line
        # The output should compile — score should be an int field
        assert "int" in cs.lower() or "score" in cs, "score field should be present"
        # name should be string, not Vector2
        # position should be Vector2, not something else
        # Key test: no field should have a type from a different line's value
        lines = cs.splitlines()
        for line in lines:
            stripped = line.strip()
            # Check no field has Vector2 type when it shouldn't
            if "score" in stripped.lower() and "Vector2" in stripped:
                pytest.fail("score field got wrong type from cross-line match")

    def test_multiline_method_body_no_leak(self):
        """Multiple self.X assignments in one method should each infer independently."""
        src = """\
class Player(MonoBehaviour):

    def awake(self):
        self.health = 100
        self.is_alive = True
        self.speed = 5.5
"""
        cs = _translate_src(src)
        # health should be int, is_alive should be bool, speed should be float
        # None should have leaked types from other assignments
        assert "int" in cs, "health should be int"
        assert "bool" in cs, "isAlive should be bool"
        assert "float" in cs, "speed should be float"
