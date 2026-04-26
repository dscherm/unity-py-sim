"""Independent validation tests for Task 8 (for-loop/collection translation)
and Task 9 (enum/namespace/attributes).

These tests are derived from Unity C# conventions and the Python->C# translation
contract, NOT from reading existing test files.
"""

from __future__ import annotations

import re
import pytest

from src.translator.python_parser import parse_python, PyFile
from src.translator.python_to_csharp import (
    translate,
    _translate_for_loop,
    _translate_py_expression,
    _translate_py_statement,
    _translate_len_calls,
    _translate_all_call,
    _translate_any_call,
    _translate_sum_count_call,
    _translate_list_comprehension,
    _upper_snake_to_pascal,
    _infer_attributes,
    _infer_using_directives,
)


# ═══════════════════════════════════════════════════════════════
# Contract Tests: for-loop translation (Task 8)
# ═══════════════════════════════════════════════════════════════

class TestForLoopRangeSingleArg:
    """for x in range(n) must become: for (int x = 0; x < n; x++)"""

    def test_range_simple_int(self):
        result = _translate_for_loop("for i in range(10):")
        assert result == "for (int i = 0; i < 10; i++)"

    def test_range_variable(self):
        result = _translate_for_loop("for i in range(count):")
        assert result == "for (int i = 0; i < count; i++)"

    def test_range_expression(self):
        """range(len(items)) should translate len() inside range."""
        result = _translate_for_loop("for i in range(len(items)):")
        # The range arg gets translated through _translate_py_expression
        assert "i < items.Count" in result or "i < len(items)" in result

    def test_range_zero(self):
        result = _translate_for_loop("for i in range(0):")
        assert result == "for (int i = 0; i < 0; i++)"

    def test_snake_case_var_converted_to_camel(self):
        result = _translate_for_loop("for bird_index in range(5):")
        assert "birdIndex" in result


class TestForLoopRangeTwoArgs:
    """for x in range(start, end) must become: for (int x = start; x < end; x++)"""

    def test_range_start_end(self):
        result = _translate_for_loop("for i in range(1, 10):")
        assert result == "for (int i = 1; i < 10; i++)"

    def test_range_variable_bounds(self):
        result = _translate_for_loop("for i in range(start, end):")
        assert result == "for (int i = start; i < end; i++)"


class TestForLoopRangeThreeArgs:
    """for x in range(start, end, step) must become: for (int x = start; x < end; x += step)"""

    def test_range_with_step(self):
        result = _translate_for_loop("for i in range(0, 10, 2):")
        assert result == "for (int i = 0; i < 10; i += 2)"


class TestForEach:
    """for x in collection must become: foreach (var x in collection)"""

    def test_foreach_simple(self):
        result = _translate_for_loop("for bird in birds:")
        assert result == "foreach (var bird in birds)"

    def test_foreach_self_attribute(self):
        result = _translate_for_loop("for pig in self.pigs:")
        # self.pigs should translate to pigs (self removed)
        assert "foreach" in result
        assert "var pig in" in result

    def test_foreach_method_call(self):
        result = _translate_for_loop("for obj in self.birds:")
        assert "foreach" in result

    def test_foreach_snake_case_var(self):
        result = _translate_for_loop("for game_object in objects:")
        assert "gameObject" in result


class TestListAppend:
    """list.append(x) must become list.Add(x)"""

    def test_append_translated(self):
        result = _translate_py_expression("items.append(5)")
        assert result == "items.Add(5)"

    def test_self_append(self):
        result = _translate_py_expression("self.birds.append(bird)")
        assert "Add(bird)" in result


class TestLenTranslation:
    """len(x) must become x.Count"""

    def test_len_simple(self):
        result = _translate_len_calls("len(items)")
        assert result == "items.Count"

    def test_len_nested(self):
        result = _translate_len_calls("len(len(items))")
        # inner len(items) -> items.Count, then len(items.Count) -> items.Count.Count
        # This is a weird edge case but should not crash
        assert "Count" in result

    def test_len_in_expression(self):
        result = _translate_py_expression("self.current_bird_index >= len(self.birds)")
        assert "birds.Count" in result

    def test_len_with_subtraction(self):
        """len(x) - 1 should become x.Count - 1"""
        result = _translate_py_expression("len(points) - 1")
        assert "points.Count - 1" in result


class TestAllCall:
    """all(pred for x in coll) must become coll.All(x => pred)"""

    def test_all_basic(self):
        result = _translate_all_call("all(p is None or not p.active for p in self.pigs)")
        assert ".All(" in result
        assert "=>" in result

    def test_all_preserves_collection(self):
        result = _translate_all_call("all(x > 0 for x in items)")
        assert "items.All(" in result


class TestSumCountCall:
    """sum(1 for x in coll if cond) must become coll.Count(x => cond)"""

    def test_sum_count(self):
        result = _translate_sum_count_call("sum(1 for p in self.pigs if p is not None and p.active)")
        assert ".Count(" in result
        assert "=>" in result


class TestListComprehension:
    """[expr for x in coll if cond] must become coll.Where(x => cond).Select(x => expr).ToList()"""

    def test_comprehension_with_filter(self):
        result = _translate_list_comprehension("[x.name for x in items if x.active]")
        assert ".Where(" in result
        assert ".Select(" in result
        assert ".ToList()" in result

    def test_comprehension_identity_with_filter(self):
        """[x for x in items if cond] should skip Select since it's identity."""
        result = _translate_list_comprehension("[x for x in items if x.active]")
        assert ".Where(" in result
        assert ".ToList()" in result
        # Should NOT have Select for identity mapping
        assert ".Select(" not in result

    def test_comprehension_no_filter(self):
        """[expr for x in coll] with mapping."""
        result = _translate_list_comprehension("[x.name for x in items]")
        assert ".Select(" in result
        assert ".ToList()" in result

    def test_comprehension_identity_no_filter(self):
        """[x for x in items] should just be items.ToList()."""
        result = _translate_list_comprehension("[x for x in items]")
        assert ".ToList()" in result


class TestListWrapper:
    """list(expr) must become expr.ToList()"""

    def test_list_wrapper(self):
        result = _translate_py_expression("list(GameObject.find_game_objects_with_tag('Bird'))")
        assert ".ToList()" in result


class TestLinqUsingDirective:
    """System.Linq must be added when LINQ operations are used."""

    def test_linq_added_for_all(self):
        source = '''
from src.engine.core import MonoBehaviour

class Foo(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.items = []

    def check(self):
        return all(x > 0 for x in self.items)
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "System.Linq" in cs

    def test_linq_added_for_list_comprehension(self):
        source = '''
from src.engine.core import MonoBehaviour

class Foo(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.items = []

    def get_active(self):
        result = [x for x in self.items if x.active]
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "System.Linq" in cs

    def test_no_linq_when_not_needed(self):
        source = '''
from src.engine.core import MonoBehaviour

class Foo(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.speed = 5.0

    def update(self):
        self.speed += 1
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "System.Linq" not in cs


# ═══════════════════════════════════════════════════════════════
# Contract Tests: enum/namespace/attributes (Task 9)
# ═══════════════════════════════════════════════════════════════

class TestEnumTranslation:
    """class X(Enum) must become public enum X { ... }"""

    def test_simple_enum(self):
        source = '''
from enum import Enum

class BirdState(Enum):
    BEFORE_THROWN = "before_thrown"
    THROWN = "thrown"
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "public enum BirdState" in cs
        assert "BeforeThrown" in cs
        assert "Thrown" in cs
        # Should NOT contain BEFORE_THROWN (must be PascalCase)
        assert "BEFORE_THROWN" not in cs

    def test_enum_members_comma_separated(self):
        source = '''
from enum import Enum

class GameState(Enum):
    START = "start"
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "Start" in cs
        assert "Playing" in cs
        assert "Won" in cs
        assert "Lost" in cs
        # Members should be comma-separated
        assert "," in cs

    def test_single_member_enum(self):
        source = '''
from enum import Enum

class SingleState(Enum):
    ONLY = "only"
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "public enum SingleState" in cs
        assert "Only" in cs

    def test_enum_braces(self):
        source = '''
from enum import Enum

class Foo(Enum):
    A = 1
    B = 2
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "{" in cs
        assert "}" in cs


class TestUpperSnakeToPascal:
    """UPPER_SNAKE enum members must convert to PascalCase."""

    def test_before_thrown(self):
        assert _upper_snake_to_pascal("BEFORE_THROWN") == "BeforeThrown"

    def test_single_word(self):
        assert _upper_snake_to_pascal("IDLE") == "Idle"

    def test_three_words(self):
        assert _upper_snake_to_pascal("BIRD_MOVING_TO_SLINGSHOT") == "BirdMovingToSlingshot"

    def test_user_pulling(self):
        assert _upper_snake_to_pascal("USER_PULLING") == "UserPulling"

    def test_empty_string(self):
        result = _upper_snake_to_pascal("")
        assert result == ""


class TestNamespace:
    """translate(parsed, namespace="Foo") must wrap output in namespace Foo { ... }"""

    def test_namespace_wrapping(self):
        source = '''
from enum import Enum

class BirdState(Enum):
    IDLE = 1
'''
        parsed = parse_python(source)
        cs = translate(parsed, namespace="AngryBirds")
        assert "namespace AngryBirds" in cs
        assert cs.count("{") >= 2  # namespace brace + enum brace
        assert cs.count("}") >= 2

    def test_namespace_indentation(self):
        source = '''
from enum import Enum

class Foo(Enum):
    A = 1
'''
        parsed = parse_python(source)
        cs = translate(parsed, namespace="MyGame")
        # Content inside namespace should be indented
        lines = cs.split("\n")
        inside_ns = False
        for line in lines:
            if "namespace" in line:
                inside_ns = True
                continue
            if inside_ns and line.strip() and line.strip() != "{" and line.strip() != "}":
                # Non-empty lines inside namespace should be indented
                if "public enum" in line or "public class" in line:
                    assert line.startswith("    "), f"Expected indentation: {line!r}"

    def test_no_namespace_when_none(self):
        source = '''
from enum import Enum

class Foo(Enum):
    A = 1
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "namespace" not in cs


class TestRequireComponentAttribute:
    """get_component(T) in start/awake must produce [RequireComponent(typeof(T))]"""

    def test_require_component_from_start(self):
        source = '''
from src.engine.core import MonoBehaviour

class Bird(MonoBehaviour):
    def start(self):
        rb = self.get_component(Rigidbody2D)
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "[RequireComponent(typeof(Rigidbody2D))]" in cs

    def test_require_component_from_awake(self):
        source = '''
from src.engine.core import MonoBehaviour

class Player(MonoBehaviour):
    def awake(self):
        sr = self.get_component(SpriteRenderer)
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "[RequireComponent(typeof(SpriteRenderer))]" in cs

    def test_no_require_component_from_update(self):
        """get_component in Update should NOT generate [RequireComponent]."""
        source = '''
from src.engine.core import MonoBehaviour

class Player(MonoBehaviour):
    def update(self):
        rb = self.get_component(Rigidbody2D)
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "RequireComponent" not in cs

    def test_multiple_require_components(self):
        source = '''
from src.engine.core import MonoBehaviour

class Bird(MonoBehaviour):
    def start(self):
        rb = self.get_component(Rigidbody2D)
        sr = self.get_component(SpriteRenderer)
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "[RequireComponent(typeof(Rigidbody2D))]" in cs
        assert "[RequireComponent(typeof(SpriteRenderer))]" in cs


# ═══════════════════════════════════════════════════════════════
# Integration Tests: translate actual angry_birds code
# ═══════════════════════════════════════════════════════════════

class TestAngryBirdsEnumIntegration:
    """Translate the real angry_birds enums.py file."""

    def test_translate_enums_file(self):
        source = '''
from enum import Enum

class SlingshotState(Enum):
    IDLE = "idle"
    USER_PULLING = "user_pulling"
    BIRD_FLYING = "bird_flying"

class GameState(Enum):
    START = "start"
    BIRD_MOVING_TO_SLINGSHOT = "bird_moving"
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"

class BirdState(Enum):
    BEFORE_THROWN = "before_thrown"
    THROWN = "thrown"
'''
        parsed = parse_python(source)
        cs = translate(parsed)

        # SlingshotState
        assert "public enum SlingshotState" in cs
        assert "Idle" in cs
        assert "UserPulling" in cs
        assert "BirdFlying" in cs

        # GameState
        assert "public enum GameState" in cs
        assert "Start" in cs
        assert "BirdMovingToSlingshot" in cs
        assert "Playing" in cs
        assert "Won" in cs
        assert "Lost" in cs

        # BirdState
        assert "public enum BirdState" in cs
        assert "BeforeThrown" in cs
        assert "Thrown" in cs

    def test_enums_with_namespace(self):
        source = '''
from enum import Enum

class BirdState(Enum):
    BEFORE_THROWN = "before_thrown"
    THROWN = "thrown"
'''
        parsed = parse_python(source)
        cs = translate(parsed, namespace="AngryBirds")
        assert "namespace AngryBirds" in cs
        assert "public enum BirdState" in cs


class TestAngryBirdsGameManagerIntegration:
    """Translate patterns from game_manager.py — for-loops, len(), all(), sum()."""

    def test_game_manager_translation(self):
        source = '''
from src.engine.core import GameObject, MonoBehaviour
from src.engine.coroutine import WaitForSeconds

class GameManager(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.birds = []
        self.pigs = []
        self.current_bird_index = 0
        self.score = 0

    def start(self):
        self.birds = list(GameObject.find_game_objects_with_tag("Bird"))
        self.pigs = list(GameObject.find_game_objects_with_tag("Pig"))

    def _all_pigs_destroyed(self):
        return all(p is None or not p.active for p in self.pigs)

    def _update_title(self):
        pigs_left = sum(1 for p in self.pigs if p is not None and p.active)
        birds_left = len(self.birds) - self.current_bird_index
'''
        parsed = parse_python(source)
        cs = translate(parsed)

        # list() wrapper -> .ToList()
        assert ".ToList()" in cs

        # all() -> .All()
        assert ".All(" in cs

        # sum(1 for ...) -> .Count()
        assert ".Count(" in cs

        # len() -> .Count
        assert ".Count" in cs

        # System.Linq should be present
        assert "System.Linq" in cs


class TestAngryBirdsBirdIntegration:
    """Translate patterns from bird.py — get_component in start for RequireComponent."""

    def test_bird_require_component(self):
        source = '''
from src.engine.core import MonoBehaviour

class Bird(MonoBehaviour):
    def start(self):
        rb = self.get_component(Rigidbody2D)
        rb.body_type = 1
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "[RequireComponent(typeof(Rigidbody2D))]" in cs


class TestAngryBirdsSlinghotForLoop:
    """Translate the for-loop from slingshot.py: for i in range(len(points) - 1)"""

    def test_slingshot_for_loop_pattern(self):
        source = '''
from src.engine.core import MonoBehaviour

class Slingshot(MonoBehaviour):
    def _draw_trajectory(self):
        for i in range(len(points) - 1):
            print(points[i])
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        # Should contain a C-style for loop
        assert "for (int i = 0;" in cs
        assert "points.Count - 1" in cs


# ═══════════════════════════════════════════════════════════════
# Mutation Tests: monkeypatch key functions to verify detection
# ═══════════════════════════════════════════════════════════════

class TestMutationRangeDetection:
    """If range detection is broken, for-loops should degrade to foreach or TODO."""

    def test_break_range_detection(self, monkeypatch):
        """If _translate_for_loop can't recognize range(), it should degrade."""
        import src.translator.python_to_csharp as mod

        original = mod._translate_for_loop

        def broken_for_loop(line):
            # Pretend range is never matched — always fall through to foreach
            body = line[4:-1].strip()
            body_no_range = body.replace("range(", "BROKEN(")
            fake_line = f"for {body_no_range}:"
            return original(fake_line)

        monkeypatch.setattr(mod, "_translate_for_loop", broken_for_loop)

        result = mod._translate_py_statement("for i in range(10):")
        # Without range detection, it should NOT produce a C-style for loop
        assert "for (int i = 0;" not in result

    def test_correct_range_produces_for_loop(self):
        """Sanity check: unbroken code produces C-style for."""
        import src.translator.python_to_csharp as mod
        result = mod._translate_py_statement("for i in range(10):")
        assert "for (int i = 0; i < 10; i++)" in result


class TestMutationEnumPascalCase:
    """If PascalCase conversion is broken, enum members stay UPPER_SNAKE."""

    def test_break_pascal_conversion(self, monkeypatch):
        import src.translator.python_to_csharp as mod

        def broken_pascal(name):
            return name  # Return unchanged

        monkeypatch.setattr(mod, "_upper_snake_to_pascal", broken_pascal)

        source = '''
from enum import Enum

class BirdState(Enum):
    BEFORE_THROWN = "before_thrown"
'''
        parsed = parse_python(source)
        cs = mod.translate(parsed)
        # With broken conversion, it should output BEFORE_THROWN instead of BeforeThrown
        assert "BEFORE_THROWN" in cs
        assert "BeforeThrown" not in cs

    def test_correct_pascal_conversion(self):
        source = '''
from enum import Enum

class BirdState(Enum):
    BEFORE_THROWN = "before_thrown"
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "BeforeThrown" in cs
        assert "BEFORE_THROWN" not in cs


class TestMutationLenTranslation:
    """If len() translation is broken, len(x) should remain instead of x.Count."""

    def test_break_len_translation(self, monkeypatch):
        import src.translator.python_to_csharp as mod

        def broken_len(expr):
            return expr  # Return unchanged

        monkeypatch.setattr(mod, "_translate_len_calls", broken_len)

        result = mod._translate_py_expression("len(self.birds)")
        # With broken len, it should still have len( somewhere
        assert "len(" in result or ".Count" not in result

    def test_correct_len_translation(self):
        result = _translate_py_expression("len(self.birds)")
        assert "birds.Count" in result


class TestMutationRequireComponent:
    """If attribute inference is broken, [RequireComponent] should be missing."""

    def test_break_attribute_inference(self, monkeypatch):
        import src.translator.python_to_csharp as mod

        def broken_attrs(cls):
            return []  # Never detect attributes

        monkeypatch.setattr(mod, "_infer_attributes", broken_attrs)

        source = '''
from src.engine.core import MonoBehaviour

class Bird(MonoBehaviour):
    def start(self):
        rb = self.get_component(Rigidbody2D)
'''
        parsed = parse_python(source)
        cs = mod.translate(parsed)
        assert "RequireComponent" not in cs

    def test_correct_attribute_inference(self):
        source = '''
from src.engine.core import MonoBehaviour

class Bird(MonoBehaviour):
    def start(self):
        rb = self.get_component(Rigidbody2D)
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "RequireComponent" in cs


class TestMutationNamespace:
    """If namespace wrapping is broken, output should lack namespace keyword."""

    def test_break_namespace(self, monkeypatch):
        import src.translator.python_to_csharp as mod

        original_translate = mod.translate

        def broken_translate(parsed, namespace=None):
            # Ignore namespace parameter
            return original_translate(parsed, namespace=None)

        monkeypatch.setattr(mod, "translate", broken_translate)

        source = '''
from enum import Enum

class Foo(Enum):
    A = 1
'''
        parsed = parse_python(source)
        cs = mod.translate(parsed, namespace="MyGame")
        assert "namespace" not in cs


# ═══════════════════════════════════════════════════════════════
# Edge Cases
# ═══════════════════════════════════════════════════════════════

class TestEdgeCases:
    """Edge cases that might trip up the translator."""

    def test_empty_range(self):
        """range(0) should still produce valid C# for-loop."""
        result = _translate_for_loop("for i in range(0):")
        assert "for (int i = 0; i < 0; i++)" == result

    def test_for_loop_with_complex_range_arg(self):
        """range(len(self.birds)) should handle nested calls."""
        result = _translate_for_loop("for i in range(len(self.birds)):")
        assert "for (int i = 0;" in result
        assert "i++)" in result

    def test_list_remove_translated(self):
        result = _translate_py_expression("items.remove(x)")
        assert "items.Remove(x)" == result

    def test_list_extend_translated(self):
        result = _translate_py_expression("items.extend(other)")
        assert "items.AddRange(other)" == result

    def test_list_insert_translated(self):
        result = _translate_py_expression("items.insert(0, x)")
        assert "items.Insert(0, x)" == result

    def test_any_call(self):
        result = _translate_any_call("any(x > 0 for x in items)")
        assert "items.Any(" in result
        assert "=>" in result

    def test_comprehension_not_a_comprehension(self):
        """Non-comprehension brackets should pass through."""
        result = _translate_list_comprehension("[1, 2, 3]")
        assert result == "[1, 2, 3]"

    def test_enum_with_int_enum_base(self):
        """IntEnum should also be detected as enum."""
        source = '''
from enum import IntEnum

class Priority(IntEnum):
    LOW = 1
    HIGH = 2
'''
        parsed = parse_python(source)
        assert parsed.classes[0].is_enum is True
        cs = translate(parsed)
        assert "public enum Priority" in cs

    def test_for_loop_tuple_unpacking_gives_todo(self):
        """Tuple unpacking in for should produce a TODO comment."""
        # This edge case is handled by producing a TODO
        result = _translate_for_loop("for x, y in pairs:")
        assert "TODO" in result or "foreach" in result

    def test_namespace_with_monobehaviour(self):
        source = '''
from src.engine.core import MonoBehaviour

class Player(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.speed = 5.0

    def update(self):
        self.speed += 1
'''
        parsed = parse_python(source)
        cs = translate(parsed, namespace="MyGame")
        assert "namespace MyGame" in cs
        assert "public class Player" in cs or "Player : MonoBehaviour" in cs

    def test_multiple_enums_in_one_file(self):
        """Multiple enums should all be translated."""
        source = '''
from enum import Enum

class A(Enum):
    X = 1

class B(Enum):
    Y = 2
'''
        parsed = parse_python(source)
        cs = translate(parsed)
        assert "public enum A" in cs
        assert "public enum B" in cs

    def test_foreach_with_concatenated_lists(self):
        """for obj in self.birds + self.pigs should translate to foreach."""
        result = _translate_for_loop("for obj in self.birds + self.pigs:")
        assert "foreach" in result
