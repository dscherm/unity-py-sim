"""Contract tests for bool truthiness detection in Python-to-C# translation.

Unity/C# conventions:
- Bool fields in if-conditions stay bare: ``if (isDead)``
- Object/component fields get null checks: ``if (target != null)``
- Negated bools: ``if (!isActive)``
- Negated objects: ``if (rb == null)``
- Compound conditions preserve per-operand treatment
- Bool fields can be inferred from True/False assignment in any method body

These tests derive from Unity C# conventions, NOT from implementation details.
"""

from __future__ import annotations

import textwrap

import pytest

from src.translator.python_parser import parse_python
from src.translator.python_to_csharp import translate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _translate_src(source: str) -> str:
    parsed = parse_python(textwrap.dedent(source))
    return translate(parsed)


# ===========================================================================
# 1. Explicit bool field stays bare in condition
# ===========================================================================

class TestExplicitBoolFieldBare:
    """A field annotated as bool or defaulting to True/False must NOT get
    a ``!= null`` check — it should remain bare in C# conditions."""

    SRC = """\
    class Player(MonoBehaviour):
        def __init__(self):
            self.is_dead: bool = False
            self.health = 100
        def update(self):
            if self.is_dead:
                self.health = 0
    """

    def test_bool_field_no_null_check(self):
        cs = _translate_src(self.SRC)
        # isDead should appear bare, NOT as "isDead != null"
        assert "isDead != null" not in cs, (
            "Bool field should stay bare in condition, not get null check"
        )

    def test_bool_field_bare_in_if(self):
        cs = _translate_src(self.SRC)
        assert "if (isDead)" in cs, (
            "Bool field should appear as bare 'if (isDead)'"
        )


# ===========================================================================
# 2. Object field gets null check
# ===========================================================================

class TestObjectFieldNullCheck:
    """A field typed as a class/None must get ``!= null`` in conditions."""

    SRC = """\
    class Player(MonoBehaviour):
        def __init__(self):
            self.target = None
            self.health = 100
        def update(self):
            if self.target:
                self.health = 50
    """

    def test_object_field_gets_null_check(self):
        cs = _translate_src(self.SRC)
        assert "target != null" in cs, (
            "Object field should get '!= null' check in condition"
        )


# ===========================================================================
# 3. Compound condition: bool AND object
# ===========================================================================

class TestCompoundBoolAndObject:
    """In ``if self.is_dead and self.target:``, the bool operand stays bare
    and the object operand gets ``!= null``."""

    SRC = """\
    class Player(MonoBehaviour):
        def __init__(self):
            self.is_dead: bool = False
            self.target = None
            self.health = 100
        def update(self):
            if self.is_dead and self.target:
                self.health = 0
    """

    def test_compound_bool_bare_object_null(self):
        cs = _translate_src(self.SRC)
        # Should contain: isDead && target != null
        assert "isDead" in cs, "Bool field should appear in compound condition"
        assert "isDead != null" not in cs, (
            "Bool operand in compound should NOT get null check"
        )
        assert "target != null" in cs, (
            "Object operand in compound should get null check"
        )


# ===========================================================================
# 4. Unity bool properties stay bare
# ===========================================================================

class TestUnityBoolPropertyBare:
    """Unity properties like activeSelf, enabled, isKinematic are bool —
    they must NOT get null checks."""

    SRC = """\
    class Player(MonoBehaviour):
        def __init__(self):
            self.health = 100
        def update(self):
            if self.game_object.active_self:
                self.health = 50
    """

    def test_active_self_no_null_check(self):
        cs = _translate_src(self.SRC)
        # activeSelf is a bool property — should stay bare
        assert "activeSelf != null" not in cs, (
            "activeSelf is a Unity bool property, should not get null check"
        )

    SRC_ENABLED = """\
    class Player(MonoBehaviour):
        def __init__(self):
            self.health = 100
        def update(self):
            if self.enabled:
                self.health = 50
    """

    def test_enabled_no_null_check(self):
        cs = _translate_src(self.SRC_ENABLED)
        assert "enabled != null" not in cs, (
            "enabled is a Unity bool property, should not get null check"
        )

    SRC_IS_KINEMATIC = """\
    class Player(MonoBehaviour):
        def __init__(self):
            self.health = 100
        def update(self):
            if self.rb.is_kinematic:
                self.health = 50
    """

    def test_is_kinematic_no_null_check(self):
        cs = _translate_src(self.SRC_IS_KINEMATIC)
        assert "isKinematic != null" not in cs, (
            "isKinematic is a Unity bool property, should not get null check"
        )


# ===========================================================================
# 5. Negated bool: ``not self.is_active`` -> ``!isActive``
# ===========================================================================

class TestNegatedBool:
    """Negating a bool field should produce ``!field``, not ``field == null``."""

    SRC = """\
    class Player(MonoBehaviour):
        def __init__(self):
            self.is_active: bool = True
            self.health = 100
        def update(self):
            if not self.is_active:
                self.health = 0
    """

    def test_negated_bool_uses_bang(self):
        cs = _translate_src(self.SRC)
        assert "!isActive" in cs, (
            "Negated bool should produce '!isActive'"
        )

    def test_negated_bool_no_null_check(self):
        cs = _translate_src(self.SRC)
        assert "isActive == null" not in cs, (
            "Negated bool should NOT produce '== null'"
        )
        assert "isActive != null" not in cs, (
            "Negated bool should NOT produce '!= null'"
        )


# ===========================================================================
# 6. Negated object: ``not self.rb`` -> ``rb == null``
# ===========================================================================

class TestNegatedObject:
    """Negating an object field should produce ``field == null``."""

    SRC = """\
    class Player(MonoBehaviour):
        def __init__(self):
            self.rb = None
            self.health = 100
        def update(self):
            if not self.rb:
                self.health = 0
    """

    def test_negated_object_uses_null_check(self):
        cs = _translate_src(self.SRC)
        assert "rb == null" in cs, (
            "Negated object should produce 'rb == null'"
        )

    def test_negated_object_no_bare_bang(self):
        cs = _translate_src(self.SRC)
        # Should not just be "!rb" — that's C-style, not idiomatic Unity C#
        # for object null checks. Should be "rb == null".
        # (Though "!rb" technically works in Unity due to operator overloading,
        # "== null" is the conventional pattern for object null checks.)
        assert "rb == null" in cs, (
            "Negated object should produce 'rb == null', not just '!rb'"
        )


# ===========================================================================
# 7. Inferred bool from True/False assignment in method body
# ===========================================================================

class TestInferredBoolFromMethodBody:
    """A field assigned True or False in awake/start/any method (not just
    __init__ defaults) should be detected as bool for truthiness."""

    SRC = """\
    class Player(MonoBehaviour):
        def __init__(self):
            self.health = 100
        def awake(self):
            self.grounded = True
        def update(self):
            if self.grounded:
                self.health = 50
    """

    def test_inferred_bool_stays_bare(self):
        cs = _translate_src(self.SRC)
        assert "grounded != null" not in cs, (
            "Field assigned True in awake() should be detected as bool, "
            "not get null check"
        )

    def test_inferred_bool_bare_in_condition(self):
        cs = _translate_src(self.SRC)
        # Should be bare 'grounded' in condition, not 'grounded != null'
        # Find the if-statement line
        lines = [l.strip() for l in cs.split("\n") if "grounded" in l and "if" in l.lower()]
        assert len(lines) >= 1, "Should have an if-statement with grounded"
        cond_line = lines[0]
        assert "!= null" not in cond_line, (
            "Inferred bool field should be bare in condition"
        )


# ===========================================================================
# 8. Bool default (no annotation) detected from True/False default
# ===========================================================================

class TestBoolDefaultNoAnnotation:
    """A field with True/False default but NO : bool annotation should
    still be detected as bool."""

    SRC = """\
    class Player(MonoBehaviour):
        def __init__(self):
            self.can_jump = False
            self.health = 100
        def update(self):
            if self.can_jump:
                self.health = 50
    """

    def test_bool_default_no_annotation_stays_bare(self):
        cs = _translate_src(self.SRC)
        assert "canJump != null" not in cs, (
            "Field defaulting to False should be detected as bool"
        )
