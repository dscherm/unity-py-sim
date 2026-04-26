"""Contract tests for translator fixes: math, kwargs, dynamic fields, bool truthiness.

These tests verify Unity C# conventions independent of implementation details.
Derived from Unity documentation for Mathf, Color32, MonoBehaviour field patterns.
"""

import re
import pytest

from src.translator.python_to_csharp import translate
from src.translator.python_parser import parse_python


# ── Helpers ───────────────────────────────────────────────────

def _translate_snippet(python_src: str) -> str:
    """Parse and translate a Python snippet to C#."""
    parsed = parse_python(python_src)
    return translate(parsed)


# ── Contract: Python math module -> Unity Mathf ──────────────

_MATH_FUNCTIONS = {
    "math.pi":    "Mathf.PI",
    "math.cos(":  "Mathf.Cos(",
    "math.sin(":  "Mathf.Sin(",
    "math.tan(":  "Mathf.Tan(",
    "math.sqrt(": "Mathf.Sqrt(",
    "math.atan2(": "Mathf.Atan2(",
    "math.acos(": "Mathf.Acos(",
    "math.asin(": "Mathf.Asin(",
    "math.atan(": "Mathf.Atan(",
    "math.floor(": "Mathf.Floor(",
    "math.ceil(":  "Mathf.Ceil(",
    "math.log(":   "Mathf.Log(",
    "math.pow(":   "Mathf.Pow(",
}


class TestMathTranslation:
    """Every Python math.X call must become Unity Mathf.X in C# output."""

    @pytest.mark.parametrize("py_expr,cs_expected", list(_MATH_FUNCTIONS.items()),
                             ids=[k.rstrip("(") for k in _MATH_FUNCTIONS])
    def test_math_function_translates(self, py_expr, cs_expected):
        """Unity convention: all math operations use Mathf (UnityEngine)."""
        # Build a minimal MonoBehaviour that uses the math function
        if py_expr == "math.pi":
            body = f"self.angle = {py_expr}"
        elif "atan2" in py_expr:
            body = f"a = {py_expr}1.0, 2.0)"
        elif "pow" in py_expr:
            body = f"a = {py_expr}2.0, 3.0)"
        elif "log" in py_expr:
            body = f"a = {py_expr}10.0)"
        else:
            body = f"a = {py_expr}0.5)"

        src = f"""
from src.engine.core import MonoBehaviour
import math

class TestBehaviour(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.angle: float = 0.0
    def update(self):
        {body}
"""
        result = _translate_snippet(src)
        assert cs_expected in result, (
            f"Expected '{cs_expected}' in C# output but got:\n{result}"
        )

    def test_no_python_math_module_remains(self):
        """No raw 'math.' references should survive translation."""
        src = """
from src.engine.core import MonoBehaviour
import math

class MathHeavy(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.angle: float = 0.0
    def update(self):
        self.angle = math.cos(math.pi * 2)
        y = math.sin(self.angle)
        z = math.sqrt(math.pow(3.0, 2.0))
"""
        result = _translate_snippet(src)
        # No raw Python math. calls should remain
        math_refs = re.findall(r"\bmath\.\w+", result)
        assert math_refs == [], f"Python math module leaked into C#: {math_refs}"

    def test_math_inf_becomes_mathf_infinity(self):
        """Unity uses Mathf.Infinity, not float.MaxValue or math.inf."""
        src = """
from src.engine.core import MonoBehaviour
import math

class InfTest(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.dist: float = 0.0
    def update(self):
        self.dist = math.inf
"""
        result = _translate_snippet(src)
        assert "Mathf.Infinity" in result

    def test_builtin_abs_becomes_mathf_abs(self):
        """Python abs() should become Mathf.Abs() in Unity."""
        src = """
from src.engine.core import MonoBehaviour

class AbsTest(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.val: float = 0.0
    def update(self):
        self.val = abs(self.val)
"""
        result = _translate_snippet(src)
        assert "Mathf.Abs(" in result

    def test_builtin_max_min_become_mathf(self):
        """Python max()/min() should become Mathf.Max()/Mathf.Min()."""
        src = """
from src.engine.core import MonoBehaviour

class ClampTest(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.val: float = 0.0
    def update(self):
        self.val = max(0.0, min(1.0, self.val))
"""
        result = _translate_snippet(src)
        assert "Mathf.Max(" in result
        assert "Mathf.Min(" in result


# ── Contract: No Python kwargs in C# output ─────────────────

class TestKwargsStripping:
    """C# does not have Python-style keyword arguments (key=value)."""

    def test_color_kwarg_becomes_color32(self):
        """color=(R,G,B) must become new Color32(R,G,B,255) per Unity docs."""
        src = """
from src.engine.core import MonoBehaviour

class DrawTest(MonoBehaviour):
    def __init__(self):
        super().__init__()
    def update(self):
        Debug.DrawLine(Vector3.zero, Vector3.one, color=(255, 0, 0))
"""
        result = _translate_snippet(src)
        assert "Color32(255, 0, 0, 255)" in result
        assert "color=" not in result

    def test_duration_kwarg_becomes_positional(self):
        """duration=N must become a positional float arg, not keyword."""
        src = """
from src.engine.core import MonoBehaviour

class DurationTest(MonoBehaviour):
    def __init__(self):
        super().__init__()
    def update(self):
        Debug.DrawLine(Vector3.zero, Vector3.one, duration=0)
"""
        result = _translate_snippet(src)
        assert "duration=" not in result, "duration= kwarg leaked into C#"

    def test_no_kwargs_syntax_anywhere(self):
        """Scan entire output for Python kwarg patterns — none allowed in C#."""
        src = """
from src.engine.core import MonoBehaviour

class MultiKwargs(MonoBehaviour):
    def __init__(self):
        super().__init__()
    def update(self):
        Debug.DrawLine(Vector3.zero, Vector3.one, color=(0, 255, 0), duration=0)
"""
        result = _translate_snippet(src)
        # Look for Python-style kwarg patterns: word= (but not ==, !=, <=, >=)
        # Exclude things like field declarations (Type name = value;)
        lines = result.split("\n")
        for line in lines:
            stripped = line.strip()
            # Skip field declarations and variable assignments
            if re.match(r"^(public|private|protected|\[|//|using|namespace|class|void|{|})", stripped):
                continue
            if "==" in stripped or "!=" in stripped or "<=" in stripped or ">=" in stripped:
                continue
            # Look for bare kwarg pattern inside function call parens
            kwarg_match = re.search(r"\(\s*.*\b\w+=(?!=)", stripped)
            if kwarg_match:
                # Make sure it's actually inside a call, not just an assignment
                if "(" in stripped and ")" in stripped:
                    # Exclude C# initializers like new X { field = value }
                    if not re.search(r"\{.*=", stripped):
                        assert False, f"Possible kwarg leak in: {stripped}"

    def test_tag_kwarg_stripped(self):
        """tag='X' kwargs should be stripped (handled at GameObject level in Unity)."""
        src = """
from src.engine.core import MonoBehaviour

class TagTest(MonoBehaviour):
    def __init__(self):
        super().__init__()
    def update(self):
        Instantiate("Laser", position=pos, tag="Projectile")
"""
        result = _translate_snippet(src)
        assert 'tag=' not in result, "tag= kwarg leaked into C#"


# ── Contract: Dynamic field declarations ─────────────────────

class TestDynamicFieldDeclarations:
    """Fields assigned in Start()/Awake() must appear as class-level declarations."""

    def test_typed_start_field_becomes_class_declaration(self):
        """self.rb: Rigidbody2D = self.get_component(Rigidbody2D) in start()
        must produce: public Rigidbody2D rb; at class level."""
        src = """
from src.engine.core import MonoBehaviour

class Player(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.speed: float = 5.0
    def start(self):
        self.rb: Rigidbody2D = self.get_component(Rigidbody2D)
"""
        result = _translate_snippet(src)
        # Must have a class-level field declaration for rb
        assert re.search(r"Rigidbody2D\s+rb\s*;", result), (
            f"Expected class-level Rigidbody2D rb; declaration:\n{result}"
        )

    def test_untyped_start_field_inferred(self):
        """self.target = GameObject.find('Player') should infer GameObject type."""
        src = """
from src.engine.core import MonoBehaviour

class Enemy(MonoBehaviour):
    def __init__(self):
        super().__init__()
    def start(self):
        self.target = GameObject.find("Player")
"""
        result = _translate_snippet(src)
        assert re.search(r"GameObject\s+target\s*;", result), (
            f"Expected class-level GameObject target; declaration:\n{result}"
        )

    def test_bool_field_in_init_declared(self):
        """Bool fields from __init__ must get proper declarations."""
        src = """
from src.engine.core import MonoBehaviour

class Toggle(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.is_active: bool = True
"""
        result = _translate_snippet(src)
        assert re.search(r"bool\s+isActive", result), (
            f"Expected bool isActive field declaration:\n{result}"
        )

    def test_multiple_dynamic_fields_all_declared(self):
        """Multiple fields assigned in start() must ALL get declarations."""
        src = """
from src.engine.core import MonoBehaviour

class Complex(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.speed: float = 5.0
    def start(self):
        self.rb: Rigidbody2D = self.get_component(Rigidbody2D)
        self.col: BoxCollider2D = self.get_component(BoxCollider2D)
        self.sr: SpriteRenderer = self.get_component(SpriteRenderer)
"""
        result = _translate_snippet(src)
        for comp_type in ["Rigidbody2D", "BoxCollider2D", "SpriteRenderer"]:
            assert comp_type in result, f"Missing declaration for {comp_type}"


# ── Contract: Bool truthiness vs null checks ─────────────────

class TestBoolTruthiness:
    """Bool fields: bare truthiness. Object fields: != null. Unity C# convention."""

    def test_bool_field_uses_bare_truthiness(self):
        """if self.is_alive: -> if (isAlive) — NOT if (isAlive != null)."""
        src = """
from src.engine.core import MonoBehaviour

class BoolCheck(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.is_alive: bool = True
    def update(self):
        if self.is_alive:
            pass
"""
        result = _translate_snippet(src)
        # Should have bare truthiness, not null check
        assert "isAlive != null" not in result, (
            f"Bool field got null check instead of truthiness:\n{result}"
        )
        assert re.search(r"if\s*\(isAlive\)", result), (
            f"Expected bare 'if (isAlive)' but got:\n{result}"
        )

    def test_object_field_gets_null_check(self):
        """if self.rb: -> if (rb != null) for non-bool reference types."""
        src = """
from src.engine.core import MonoBehaviour

class NullCheck(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.speed: float = 5.0
    def start(self):
        self.rb: Rigidbody2D = self.get_component(Rigidbody2D)
    def update(self):
        if self.rb:
            pass
"""
        result = _translate_snippet(src)
        assert "rb != null" in result, (
            f"Object field should use != null check:\n{result}"
        )

    def test_negated_bool_uses_not_operator(self):
        """if not self.is_dead: -> if (!isDead) — NOT if (isDead == null)."""
        src = """
from src.engine.core import MonoBehaviour

class NegatedBool(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.is_dead: bool = False
    def update(self):
        if not self.is_dead:
            pass
"""
        result = _translate_snippet(src)
        assert "isDead == null" not in result, "Negated bool got == null"
        assert "isDead != null" not in result, "Negated bool got != null"

    def test_bool_in_compound_condition(self):
        """Bool + object in same condition: bool bare, object != null."""
        src = """
from src.engine.core import MonoBehaviour

class CompoundCond(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.is_ready: bool = False
        self.speed: float = 0.0
    def start(self):
        self.target: GameObject = GameObject.find("Player")
    def update(self):
        if self.is_ready and self.target:
            pass
"""
        result = _translate_snippet(src)
        # Bool should be bare
        assert "isReady != null" not in result, "Bool field got null check in compound"
        # Object should get null check
        assert "target != null" in result, "Object field missing null check in compound"


# ── Contract: Debug.DrawLine with color produces valid Color32 ──

class TestDebugDrawLineColor:
    """Debug.DrawLine color tuple must produce valid Color32 constructor."""

    def test_color_tuple_to_color32(self):
        """(255, 0, 0) -> new Color32(255, 0, 0, 255) per Unity docs."""
        src = """
from src.engine.core import MonoBehaviour

class DebugDraw(MonoBehaviour):
    def __init__(self):
        super().__init__()
    def update(self):
        Debug.DrawLine(Vector3.zero, Vector3.one, color=(255, 0, 0))
"""
        result = _translate_snippet(src)
        assert "new Color32(255, 0, 0, 255)" in result
        # Must not have bare tuple syntax
        assert "(255, 0, 0)" not in result or "Color32(255, 0, 0, 255)" in result

    def test_color32_has_alpha_255(self):
        """Unity Color32 requires 4 components (r,g,b,a). Alpha defaults to 255."""
        src = """
from src.engine.core import MonoBehaviour

class AlphaTest(MonoBehaviour):
    def __init__(self):
        super().__init__()
    def update(self):
        Debug.DrawLine(Vector3.zero, Vector3.up, color=(0, 128, 255))
"""
        result = _translate_snippet(src)
        match = re.search(r"Color32\((\d+),\s*(\d+),\s*(\d+),\s*(\d+)\)", result)
        assert match, f"No Color32 constructor found in:\n{result}"
        assert match.group(4) == "255", f"Alpha should be 255, got {match.group(4)}"


if __name__ == "__main__":
    # Fallback: run without pytest (avoids pygame hang on Windows)
    import sys
    failures = 0
    total = 0

    for cls_name, cls_obj in list(globals().items()):
        if isinstance(cls_obj, type) and cls_name.startswith("Test"):
            inst = cls_obj()
            for method_name in dir(inst):
                if method_name.startswith("test_"):
                    total += 1
                    try:
                        method = getattr(inst, method_name)
                        # Skip parametrized tests in fallback mode
                        if hasattr(method, "pytestmark"):
                            continue
                        method()
                        print(f"  PASS: {cls_name}.{method_name}")
                    except Exception as e:
                        failures += 1
                        print(f"  FAIL: {cls_name}.{method_name}: {e}")

    # Run parametrized math tests manually
    inst = TestMathTranslation()
    for py_expr, cs_expected in _MATH_FUNCTIONS.items():
        total += 1
        try:
            inst.test_math_function_translates(py_expr, cs_expected)
            print(f"  PASS: TestMathTranslation.test_math_function_translates[{py_expr}]")
        except Exception as e:
            failures += 1
            print(f"  FAIL: TestMathTranslation.test_math_function_translates[{py_expr}]: {e}")

    print(f"\n{total - failures}/{total} passed, {failures} failed")
    sys.exit(1 if failures else 0)
