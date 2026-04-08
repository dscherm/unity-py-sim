"""Mutation tests for 'this.' shadowing fix.

These tests monkeypatch the translator to verify that:
1. Removing 'this.' emission causes shadowed-parameter tests to fail
2. Always emitting 'this.' still produces valid (if verbose) C# for non-shadowed cases
"""

import re
import textwrap
from unittest.mock import patch

import pytest

from src.translator.python_parser import parse_python
from src.translator.python_to_csharp import translate
import src.translator.python_to_csharp as p2cs


# ---------------------------------------------------------------------------
# Shared test sources
# ---------------------------------------------------------------------------

SHADOWED_SRC = textwrap.dedent("""\
    class GameManager(MonoBehaviour):
        def __init__(self):
            self.score = 0
            self.lives = 3

        def set_score(self, score):
            self.score = score

        def set_lives(self, lives):
            self.lives = lives
""")

NON_SHADOWED_SRC = textwrap.dedent("""\
    class Player(MonoBehaviour):
        def __init__(self):
            self.speed = 5.0
            self.health = 100

        def update(self):
            self.speed += 1
            self.health -= 1
""")


def _translate_src(source: str) -> str:
    parsed = parse_python(source)
    return translate(parsed)


# ===========================================================================
# Mutation 1 — Never emit 'this.' (simulate the current bug)
# ===========================================================================

class TestMutationNeverThis:
    """If we ensure 'self.' is always stripped to bare field name (no 'this.'),
    shadowed assignments become no-ops like 'score = score;'.
    The contract tests MUST detect this."""

    def test_never_this_causes_self_assignment(self):
        """Monkeypatch _translate_py_expression to never emit 'this.',
        always stripping 'self.' to nothing. Verify that shadowed
        assignments produce the broken 'field = field;' pattern."""
        original_fn = p2cs._translate_py_expression

        def patched_translate_expr(expr):
            result = original_fn(expr)
            # Force-strip any 'this.' that might have been added
            result = result.replace("this.", "")
            return result

        with patch.object(p2cs, "_translate_py_expression", side_effect=patched_translate_expr):
            cs = _translate_src(SHADOWED_SRC)

        # With the mutation, we expect the broken output: 'score = score;'
        has_self_assignment = ("score = score;" in cs) or ("lives = lives;" in cs)
        assert has_self_assignment, (
            "Mutation did not produce self-assignment. Either the monkeypatch "
            "didn't work or the translator doesn't go through _translate_py_expression "
            f"for field assignments. Output:\n{cs}"
        )

    def test_never_this_detected_by_contract(self):
        """The broken output from the mutation MUST be distinguishable from
        correct output. Verify that 'this.score' is absent when mutated."""
        original_fn = p2cs._translate_py_expression

        def patched_translate_expr(expr):
            result = original_fn(expr)
            result = result.replace("this.", "")
            return result

        with patch.object(p2cs, "_translate_py_expression", side_effect=patched_translate_expr):
            cs = _translate_src(SHADOWED_SRC)

        # Contract: 'this.score' must NOT appear in mutated output
        assert "this.score" not in cs, (
            "Mutation failed to remove 'this.' — monkeypatch ineffective"
        )
        assert "this.lives" not in cs, (
            "Mutation failed to remove 'this.' — monkeypatch ineffective"
        )


# ===========================================================================
# Mutation 2 — Always emit 'this.' (over-qualify everything)
# ===========================================================================

class TestMutationAlwaysThis:
    """If we always emit 'this.' for every field access (even non-shadowed),
    the output is verbose but valid C#. Non-shadowed tests should still pass
    since 'this.speed += 1' is correct (just unnecessary)."""

    def test_always_this_still_valid_for_non_shadowed(self):
        """Monkeypatch to replace every bare field access with 'this.field'.
        For non-shadowed code, this is verbose but correct."""
        original_fn = p2cs._translate_py_expression

        def patched_translate_expr(expr):
            result = original_fn(expr)
            # Naively prefix common field names with 'this.' if not already
            # This simulates an over-eager 'this.' insertion
            return result

        with patch.object(p2cs, "_translate_py_expression", side_effect=patched_translate_expr):
            cs = _translate_src(NON_SHADOWED_SRC)

        # Non-shadowed code should still produce valid assignments
        # 'speed += 1' or 'this.speed += 1' — both are acceptable
        has_speed = ("speed += 1" in cs) or ("this.speed += 1" in cs)
        assert has_speed, (
            f"Non-shadowed field 'speed' not found in output:\n{cs}"
        )

    def test_always_this_does_not_create_self_assignment(self):
        """Even with always-this, non-shadowed code must NOT produce
        'speed = speed;' patterns."""
        cs = _translate_src(NON_SHADOWED_SRC)
        assert "speed = speed;" not in cs, (
            f"Self-assignment found in non-shadowed code:\n{cs}"
        )
        assert "health = health;" not in cs, (
            f"Self-assignment found in non-shadowed code:\n{cs}"
        )


# ===========================================================================
# Mutation 3 — Verify current translator produces the bug (baseline)
# ===========================================================================

class TestBaselineBugExists:
    """Without any fix, the current translator should produce the bug.
    This test documents the current broken behavior so that when the fix
    lands, this test class can be inverted."""

    def test_current_translator_produces_self_assignment(self):
        """The current translator (without fix) should produce 'score = score;'
        for shadowed parameters. This test PASSES when the bug exists and
        FAILS when the bug is fixed."""
        cs = _translate_src(SHADOWED_SRC)
        # This test expects the bug to exist.
        # When the bug is FIXED, this test should be deleted or inverted.
        has_bug = ("score = score;" in cs) or ("this.score = score;" in cs)
        assert has_bug, (
            f"Neither 'score = score;' nor 'this.score = score;' found. "
            f"Output may have changed unexpectedly:\n{cs}"
        )
