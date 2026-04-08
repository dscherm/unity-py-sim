"""Contract tests: Python math builtins must translate to Unity Mathf, not System.Math.

Unity uses Mathf (UnityEngine.Mathf) for math operations, not System.Math.
Mathf operates on floats and is the standard in Unity scripts.
"""

import pytest
from src.translator.python_to_csharp import translate
from src.translator.python_parser import parse_python


def _translate_snippet(body: str) -> str:
    """Translate a MonoBehaviour with the given method body."""
    source = (
        "from src.engine.core import MonoBehaviour\n"
        "class Foo(MonoBehaviour):\n"
        "    def update(self):\n"
        f"        {body}\n"
    )
    parsed = parse_python(source)
    return translate(parsed)


class TestMathfMaxContract:
    """max() must translate to Mathf.Max, not Math.Max."""

    def test_max_produces_mathf(self):
        result = _translate_snippet("x = max(a, b)")
        assert "Mathf.Max(a, b)" in result

    def test_max_not_system_math(self):
        result = _translate_snippet("x = max(a, b)")
        assert "Math.Max(" not in result.replace("Mathf.Max(", "")


class TestMathfMinContract:
    """min() must translate to Mathf.Min, not Math.Min."""

    def test_min_produces_mathf(self):
        result = _translate_snippet("x = min(a, b)")
        assert "Mathf.Min(a, b)" in result

    def test_min_not_system_math(self):
        result = _translate_snippet("x = min(a, b)")
        assert "Math.Min(" not in result.replace("Mathf.Min(", "")


class TestMathfAbsContract:
    """abs() must translate to Mathf.Abs."""

    def test_abs_produces_mathf(self):
        result = _translate_snippet("x = abs(y)")
        assert "Mathf.Abs(y)" in result

    def test_abs_not_raw_python(self):
        """C# does not have a bare abs() function."""
        result = _translate_snippet("x = abs(y)")
        # After removing Mathf.Abs occurrences, no bare abs( should remain
        stripped = result.replace("Mathf.Abs(", "")
        assert "abs(" not in stripped


class TestMathfRoundContract:
    """round() must translate to Mathf.Round."""

    def test_round_produces_mathf(self):
        result = _translate_snippet("x = round(y)")
        assert "Mathf.Round(y)" in result

    def test_round_not_raw_python(self):
        result = _translate_snippet("x = round(y)")
        stripped = result.replace("Mathf.Round(", "")
        assert "round(" not in stripped


class TestMathfNestedCalls:
    """Nested math builtins must all use Mathf."""

    def test_max_of_min(self):
        result = _translate_snippet("x = max(min(a, b), c)")
        assert "Mathf.Max(Mathf.Min(a, b), c)" in result

    def test_min_of_abs(self):
        result = _translate_snippet("x = min(abs(a), b)")
        assert "Mathf.Min(Mathf.Abs(a), b)" in result

    def test_abs_of_max(self):
        result = _translate_snippet("x = abs(max(a, b))")
        assert "Mathf.Abs(Mathf.Max(a, b))" in result


class TestUsingUnityEngine:
    """Mathf lives in UnityEngine namespace — using directive must be present."""

    def test_using_unityengine_present(self):
        result = _translate_snippet("x = max(a, b)")
        assert "using UnityEngine;" in result

    def test_using_unityengine_present_for_abs(self):
        result = _translate_snippet("x = abs(y)")
        assert "using UnityEngine;" in result
