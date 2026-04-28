"""Mutation tests for translator fixes: break each fix and verify tests catch it.

Each test monkeypatches a specific translation rule to simulate a regression,
then verifies the output is detectably wrong.
"""

import re
from unittest.mock import patch

from src.translator.python_to_csharp import translate
from src.translator.python_parser import parse_python


# ── Helpers ───────────────────────────────────────────────────

def _translate_snippet(python_src: str) -> str:
    parsed = parse_python(python_src)
    return translate(parsed)


_MATH_SNIPPET = """
from src.engine.core import MonoBehaviour
import math

class MathTest(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.angle: float = 0.0
    def update(self):
        self.angle = math.cos(math.pi * 0.5)
        y = math.sin(self.angle)
        z = math.sqrt(4.0)
        w = math.atan2(1.0, 0.0)
"""

_KWARGS_SNIPPET = """
from src.engine.core import MonoBehaviour

class KwargsTest(MonoBehaviour):
    def __init__(self):
        super().__init__()
    def update(self):
        Debug.DrawLine(Vector3.zero, Vector3.one, color=(255, 0, 0), duration=0)
"""

_BOOL_SNIPPET = """
from src.engine.core import MonoBehaviour

class BoolTest(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.is_alive: bool = True
        self.speed: float = 5.0
    def start(self):
        self.rb: Rigidbody2D = self.get_component(Rigidbody2D)
    def update(self):
        if self.is_alive:
            pass
        if self.rb:
            pass
"""

_DYNAMIC_FIELD_SNIPPET = """
from src.engine.core import MonoBehaviour

class FieldTest(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.speed: float = 5.0
    def start(self):
        self.rb: Rigidbody2D = self.get_component(Rigidbody2D)
        self.col: BoxCollider2D = self.get_component(BoxCollider2D)
"""


# ── Mutation: Break math translation ─────────────────────────

class TestMathMutation:
    """Break math->Mathf translation and verify output regresses."""

    def test_broken_math_cos_leaks_python(self):
        """If math.cos translation is disabled, raw Python math.cos leaks."""
        import src.translator.python_to_csharp as mod

        original_fn = mod._translate_py_expression

        def broken_translate_expr(expr):
            result = original_fn(expr)
            # Undo the Mathf.Cos replacement to simulate the bug
            result = result.replace("Mathf.Cos(", "math.cos(")
            return result

        with patch.object(mod, '_translate_py_expression', side_effect=broken_translate_expr):
            result = _translate_snippet(_MATH_SNIPPET)

        # The mutation should cause math.cos to leak
        assert "math.cos" in result, (
            "Mutation failed to break math.cos translation — test cannot catch regression"
        )

    def test_broken_math_pi_leaks_python(self):
        """If math.pi translation is disabled, raw Python math.pi leaks."""
        import src.translator.python_to_csharp as mod

        original_fn = mod._translate_py_expression

        def broken_translate_expr(expr):
            result = original_fn(expr)
            result = result.replace("Mathf.PI", "math.pi")
            return result

        with patch.object(mod, '_translate_py_expression', side_effect=broken_translate_expr):
            result = _translate_snippet(_MATH_SNIPPET)

        assert "math.pi" in result, (
            "Mutation failed to break math.pi translation"
        )

    def test_correct_math_has_no_python_refs(self):
        """Baseline: unmutated translator produces no math. references."""
        result = _translate_snippet(_MATH_SNIPPET)
        python_math = re.findall(r"\bmath\.\w+", result)
        assert python_math == [], f"Unmutated translator leaked: {python_math}"
        assert "Mathf.Cos(" in result
        assert "Mathf.PI" in result
        assert "Mathf.Sin(" in result
        assert "Mathf.Sqrt(" in result
        assert "Mathf.Atan2(" in result


# ── Mutation: Break kwargs stripping ─────────────────────────

class TestKwargsMutation:
    """Break kwargs removal and verify Python kwargs leak into C#."""

    def test_broken_color_kwarg_leaks(self):
        """If color kwarg translation is disabled, color= leaks into C#."""
        import src.translator.python_to_csharp as mod

        original_fn = mod._translate_py_expression

        def broken_translate_expr(expr):
            result = original_fn(expr)
            # Re-inject the color kwarg to simulate breakage
            result = result.replace("new Color32(255, 0, 0, 255)", "color=(255, 0, 0)")
            return result

        with patch.object(mod, '_translate_py_expression', side_effect=broken_translate_expr):
            result = _translate_snippet(_KWARGS_SNIPPET)

        assert "color=" in result, (
            "Mutation failed to break color kwarg stripping"
        )

    def test_broken_duration_kwarg_leaks(self):
        """If duration kwarg translation is disabled, duration= leaks."""
        import src.translator.python_to_csharp as mod

        original_fn = mod._translate_py_expression

        def broken_translate_expr(expr):
            result = original_fn(expr)
            # Replace the positional result back with kwarg form
            result = re.sub(r",\s*0f\b", ", duration=0", result)
            return result

        with patch.object(mod, '_translate_py_expression', side_effect=broken_translate_expr):
            result = _translate_snippet(_KWARGS_SNIPPET)

        assert "duration=" in result, (
            "Mutation failed to break duration kwarg stripping"
        )

    def test_correct_kwargs_fully_stripped(self):
        """Baseline: unmutated translator strips all kwargs."""
        result = _translate_snippet(_KWARGS_SNIPPET)
        assert "color=" not in result
        assert "duration=" not in result
        assert "Color32(" in result


# ── Mutation: Break bool field tracking ──────────────────────

class TestBoolMutation:
    """Break bool field tracking so bool gets wrong null check."""

    def test_empty_bool_fields_causes_null_check(self):
        """If _bool_fields is empty, bool field gets != null (wrong)."""
        import src.translator.python_to_csharp as mod

        # Save original
        original_translate = mod._translate_monobehaviour

        def broken_translate_mono(cls, parsed):
            # Clear bool fields tracking to simulate the bug
            mod._bool_fields = set()
            result = original_translate(cls, parsed)
            return result

        # We need to intercept after _bool_fields is populated but before condition translation
        # Instead, directly test by clearing _bool_fields after the class is built
        original_translate_condition = mod._translate_py_condition

        def broken_condition(cond):
            saved = mod._bool_fields.copy()
            mod._bool_fields = set()  # Break: pretend no fields are bool
            result = original_translate_condition(cond)
            mod._bool_fields = saved  # Restore to not pollute other tests
            return result

        with patch.object(mod, '_translate_py_condition', side_effect=broken_condition):
            result = _translate_snippet(_BOOL_SNIPPET)

        # With broken bool tracking, isAlive should get != null (wrong)
        assert "isAlive != null" in result, (
            f"Mutation: expected isAlive != null when bool tracking broken, got:\n{result}"
        )

    def test_correct_bool_no_null_check(self):
        """Baseline: unmutated translator uses bare bool truthiness."""
        result = _translate_snippet(_BOOL_SNIPPET)
        assert "isAlive != null" not in result, "Bool field got null check"
        assert re.search(r"if\s*\(isAlive\)", result), "Missing bare bool check"
        assert "rb != null" in result, "Object field missing null check"


# ── Mutation: Break dynamic field discovery ──────────────────

class TestDynamicFieldMutation:
    """Break dynamic field discovery and verify fields go undeclared."""

    def test_broken_discovery_missing_declarations(self):
        """If _discover_dynamic_fields returns empty, start() fields undeclared."""
        import src.translator.python_to_csharp as mod

        original_fn = mod._discover_dynamic_fields

        def broken_discover(cls):
            return []  # Return no dynamic fields

        with patch.object(mod, '_discover_dynamic_fields', side_effect=broken_discover):
            result = _translate_snippet(_DYNAMIC_FIELD_SNIPPET)

        # With dynamic discovery broken, Rigidbody2D rb should NOT appear as a field
        # It may still appear in method body, but not as a class-level declaration
        lines = result.split("\n")
        field_decls = [l for l in lines if re.search(r"Rigidbody2D\s+rb\s*;", l)]
        assert len(field_decls) == 0, (
            f"Mutation: dynamic field discovery broken but field still declared: {field_decls}"
        )

    def test_correct_dynamic_fields_declared(self):
        """Baseline: unmutated translator declares dynamic fields."""
        result = _translate_snippet(_DYNAMIC_FIELD_SNIPPET)
        assert re.search(r"Rigidbody2D\s+rb\s*;", result), (
            f"Missing Rigidbody2D rb declaration:\n{result}"
        )
        assert re.search(r"BoxCollider2D\s+col\s*;", result), (
            f"Missing BoxCollider2D col declaration:\n{result}"
        )


if __name__ == "__main__":
    # Fallback: run without pytest (avoids pygame hang on Windows)
    import sys
    failures = 0
    total = 0

    for cls_name, cls_obj in list(globals().items()):
        if isinstance(cls_obj, type) and cls_name.startswith("Test"):
            inst = cls_obj()
            for method_name in sorted(dir(inst)):
                if method_name.startswith("test_"):
                    total += 1
                    try:
                        getattr(inst, method_name)()
                        print(f"  PASS: {cls_name}.{method_name}")
                    except Exception as e:
                        failures += 1
                        print(f"  FAIL: {cls_name}.{method_name}: {e}")

    print(f"\n{total - failures}/{total} passed, {failures} failed")
    sys.exit(1 if failures else 0)
