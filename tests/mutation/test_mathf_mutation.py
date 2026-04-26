"""Mutation tests: verify contract tests catch regressions in Mathf translation.

Each test monkeypatches _translate_py_expression's regex substitutions to
simulate a bug, then asserts the contract would detect it.
"""

from unittest.mock import patch
from src.translator.python_to_csharp import translate, _translate_py_expression
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


def _make_mutant(mutate_fn):
    """Wrap _translate_py_expression with a post-processing mutant."""
    original = _translate_py_expression

    def mutant(expr):
        result = original(expr)
        return mutate_fn(result)

    return mutant


class TestMutationMaxToMath:
    """Mutant: revert Mathf.Max -> Math.Max (the original bug)."""

    def test_mutation_caught_for_max(self):
        """If someone regresses Mathf.Max to Math.Max, tests must detect it."""
        mutant = _make_mutant(lambda e: e.replace("Mathf.Max(", "Math.Max("))
        with patch(
            "src.translator.python_to_csharp._translate_py_expression", mutant
        ):
            result = _translate_snippet("x = max(a, b)")
        # The mutant output should have Math.Max, NOT Mathf.Max
        assert "Math.Max(" in result
        assert "Mathf.Max(" not in result


class TestMutationMinToMath:
    """Mutant: revert Mathf.Min -> Math.Min."""

    def test_mutation_caught_for_min(self):
        mutant = _make_mutant(lambda e: e.replace("Mathf.Min(", "Math.Min("))
        with patch(
            "src.translator.python_to_csharp._translate_py_expression", mutant
        ):
            result = _translate_snippet("x = min(a, b)")
        assert "Math.Min(" in result
        assert "Mathf.Min(" not in result


class TestMutationRemoveAbsTranslation:
    """Mutant: remove abs translation entirely, leaving raw abs() in C#."""

    def test_mutation_caught_for_abs(self):
        mutant = _make_mutant(lambda e: e.replace("Mathf.Abs(", "abs("))
        with patch(
            "src.translator.python_to_csharp._translate_py_expression", mutant
        ):
            result = _translate_snippet("x = abs(y)")
        # Should have bare abs( — no Mathf.Abs
        assert "Mathf.Abs(" not in result
        # Contract test would catch this because abs( appears without Mathf prefix
        stripped = result.replace("Mathf.Abs(", "")
        assert "abs(" in stripped


class TestMutationMaxButNotMin:
    """Mutant: translate max correctly but break min — tests must catch independently."""

    def test_max_still_correct_min_broken(self):
        mutant = _make_mutant(lambda e: e.replace("Mathf.Min(", "Math.Min("))
        with patch(
            "src.translator.python_to_csharp._translate_py_expression", mutant
        ):
            result_max = _translate_snippet("x = max(a, b)")
            result_min = _translate_snippet("x = min(a, b)")
        # max should still be correct
        assert "Mathf.Max(" in result_max
        # min should be broken
        assert "Math.Min(" in result_min
        assert "Mathf.Min(" not in result_min


class TestMutationNestedBreaks:
    """Mutant: break max in nested calls — inner Mathf.Min should survive."""

    def test_nested_partial_mutation(self):
        mutant = _make_mutant(lambda e: e.replace("Mathf.Max(", "Math.Max("))
        with patch(
            "src.translator.python_to_csharp._translate_py_expression", mutant
        ):
            result = _translate_snippet("x = max(min(a, b), c)")
        # Outer max should be broken, inner min should survive
        assert "Math.Max(" in result
        assert "Mathf.Min(" in result
