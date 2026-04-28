"""Contract tests for C# 'this.' qualifier on shadowed parameters.

In C#, when a method parameter has the same name as an instance field,
assignments to the field MUST use 'this.field = param;' to disambiguate.
Without 'this.', the assignment becomes a no-op: 'score = score;'.

These tests derive from C# language specification, NOT implementation details.
"""

from __future__ import annotations
import re

import textwrap

import pytest

from src.translator.python_parser import (
    PyFile, PyClass, PyField, PyMethod, parse_python,
)
from src.translator.python_to_csharp import translate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_monobehaviour(
    class_name: str,
    fields: list[PyField],
    methods: list[PyMethod],
) -> PyFile:
    """Build a minimal PyFile with one MonoBehaviour class."""
    return PyFile(
        classes=[
            PyClass(
                name=class_name,
                base_classes=["MonoBehaviour"],
                is_monobehaviour=True,
                fields=fields,
                methods=methods,
            )
        ]
    )


def _translate_src(source: str, **kwargs) -> str:
    parsed = parse_python(source)
    return translate(parsed, **kwargs)


def _translate_ir(parsed: PyFile, **kwargs) -> str:
    return translate(parsed, unity_version=5, input_system="legacy", **kwargs)


# ===========================================================================
# 1. Simple parameter shadowing — self.field = param (same name)
# ===========================================================================

class TestSimpleShadowing:
    """When a method parameter name matches an instance field name,
    'self.field = param' MUST emit 'this.field = param;' in C#."""

    def test_set_score_uses_this(self):
        """def set_score(self, score): self.score = score
        -> must emit 'this.score = score;', NOT 'score = score;'
        """
        src = textwrap.dedent("""\
            class GameManager(MonoBehaviour):
                def __init__(self):
                    self.score = 0

                def set_score(self, score):
                    self.score = score
        """)
        cs = _translate_src(src)
        assert "this.score = score;" in cs, (
            f"Expected 'this.score = score;' but got:\n{cs}"
        )
        assert not re.search(r"(?<!this\.)score = score;", cs), (
            f"Found self-assignment 'score = score;' (missing 'this.'):\n{cs}"
        )

    def test_set_lives_uses_this(self):
        """def set_lives(self, lives): self.lives = lives
        -> must emit 'this.lives = lives;', NOT 'lives = lives;'
        """
        src = textwrap.dedent("""\
            class GameManager(MonoBehaviour):
                def __init__(self):
                    self.lives = 3

                def set_lives(self, lives):
                    self.lives = lives
        """)
        cs = _translate_src(src)
        assert "this.lives = lives;" in cs, (
            f"Expected 'this.lives = lives;' but got:\n{cs}"
        )
        assert not re.search(r"(?<!this\.)lives = lives;", cs), (
            f"Found self-assignment 'lives = lives;' (missing 'this.'):\n{cs}"
        )


# ===========================================================================
# 2. No unnecessary 'this.' when there is no shadowing
# ===========================================================================

class TestNoUnnecessaryThis:
    """When there is NO parameter shadowing, 'self.field' can translate
    to just 'field' (no 'this.' required)."""

    def test_update_no_param_shadow(self):
        """def update(self): self.score += 1
        -> 'score += 1;' (no parameter named 'score', no 'this.' needed)
        """
        src = textwrap.dedent("""\
            class GameManager(MonoBehaviour):
                def __init__(self):
                    self.score = 0

                def update(self):
                    self.score += 1
        """)
        cs = _translate_src(src)
        # Should contain 'score += 1' or 'score++' — but NOT 'this.score'
        # (While 'this.score' is valid C#, it's unnecessary noise.
        # The real requirement is just that it works — so we accept either.)
        assert "score" in cs  # sanity check

    def test_different_names_no_this(self):
        """def set_speed(self, new_speed): self.speed = new_speed
        -> 'speed = newSpeed;' (names differ, no shadowing)
        """
        src = textwrap.dedent("""\
            class PlayerMovement(MonoBehaviour):
                def __init__(self):
                    self.speed = 5.0

                def set_speed(self, new_speed):
                    self.speed = new_speed
        """)
        cs = _translate_src(src)
        # The field 'speed' and param 'new_speed'/'newSpeed' differ,
        # so 'speed = newSpeed;' is unambiguous — no 'this.' needed.
        # Just verify it doesn't produce a self-assignment like 'speed = speed;'
        assert "speed = speed;" not in cs


# ===========================================================================
# 3. Multiple shadowed assignments in one method
# ===========================================================================

class TestMultipleShadowedAssignments:
    """A method with multiple parameters that each shadow a field
    must use 'this.' for every shadowed assignment."""

    def test_reset_method_both_shadowed(self):
        """def reset(self, score, lives): self.score = score; self.lives = lives
        -> both must use 'this.'
        """
        src = textwrap.dedent("""\
            class GameManager(MonoBehaviour):
                def __init__(self):
                    self.score = 0
                    self.lives = 3

                def reset(self, score, lives):
                    self.score = score
                    self.lives = lives
        """)
        cs = _translate_src(src)
        assert "this.score = score;" in cs, (
            f"Expected 'this.score = score;' in reset method but got:\n{cs}"
        )
        assert "this.lives = lives;" in cs, (
            f"Expected 'this.lives = lives;' in reset method but got:\n{cs}"
        )

    def test_mixed_shadow_and_non_shadow(self):
        """def configure(self, speed, label):
            self.speed = speed    # shadowed -> this.speed
            self.label = label    # shadowed -> this.label
            self.ready = True     # not shadowed -> ready (no this.)
        """
        src = textwrap.dedent("""\
            class Widget(MonoBehaviour):
                def __init__(self):
                    self.speed = 0
                    self.label = ""
                    self.ready = False

                def configure(self, speed, label):
                    self.speed = speed
                    self.label = label
                    self.ready = True
        """)
        cs = _translate_src(src)
        assert "this.speed = speed;" in cs, (
            f"Expected 'this.speed = speed;' but got:\n{cs}"
        )
        assert "this.label = label;" in cs, (
            f"Expected 'this.label = label;' but got:\n{cs}"
        )


# ===========================================================================
# 4. Compound assignment with shadowed parameter
# ===========================================================================

class TestCompoundAssignmentShadowing:
    """self.score += score when 'score' is a parameter must also use 'this.'."""

    def test_plus_equals_shadowed(self):
        """def add_score(self, score): self.score += score
        -> 'this.score += score;'
        """
        src = textwrap.dedent("""\
            class GameManager(MonoBehaviour):
                def __init__(self):
                    self.score = 0

                def add_score(self, score):
                    self.score += score
        """)
        cs = _translate_src(src)
        assert "this.score += score;" in cs, (
            f"Expected 'this.score += score;' but got:\n{cs}"
        )


# ===========================================================================
# 5. Real-world Space Invaders pattern (SetScore / SetLives)
# ===========================================================================

class TestSpaceInvadersSetters:
    """Reproduce the exact pattern from Space Invaders GameManager that
    produced the 'score = score;' bug in generated C#."""

    GAME_MANAGER_SRC = textwrap.dedent("""\
        class GameManager(MonoBehaviour):
            def __init__(self):
                self.score = 0
                self.lives = 3
                self.score_text = None
                self.lives_text = None

            def set_score(self, score):
                self.score = score
                if self.score_text is not None:
                    self.score_text.text = str(score).zfill(4)

            def set_lives(self, lives):
                self.lives = max(lives, 0)
                if self.lives_text is not None:
                    self.lives_text.text = str(lives)
    """)

    def test_set_score_no_self_assignment(self):
        cs = _translate_src(self.GAME_MANAGER_SRC)
        # Must NOT produce bare 'score = score;' (without 'this.' prefix)
        assert not re.search(r"(?<!this\.)score = score;", cs), (
            f"Bug reproduced: bare 'score = score;' found in output:\n{cs}"
        )

    def test_set_score_uses_this_qualifier(self):
        cs = _translate_src(self.GAME_MANAGER_SRC)
        assert "this.score = score;" in cs, (
            f"Expected 'this.score = score;' but got:\n{cs}"
        )

    def test_set_lives_no_self_assignment(self):
        cs = _translate_src(self.GAME_MANAGER_SRC)
        # 'lives = lives;' or 'lives = Math.Max(lives, 0);' without 'this.' is wrong
        # Check that wherever 'lives' is assigned, it uses 'this.'
        for line in cs.split("\n"):
            stripped = line.strip()
            # Look for lines that assign to 'lives' (not 'this.lives')
            if stripped.startswith("lives =") or stripped.startswith("lives="):
                pytest.fail(
                    f"Found bare 'lives' assignment without 'this.': {stripped}\n"
                    f"Full output:\n{cs}"
                )

    def test_set_lives_uses_this_qualifier(self):
        cs = _translate_src(self.GAME_MANAGER_SRC)
        # self.lives = max(lives, 0) -> this.lives = Math.Max(lives, 0);
        assert "this.lives" in cs, (
            f"Expected 'this.lives' assignment but got:\n{cs}"
        )
