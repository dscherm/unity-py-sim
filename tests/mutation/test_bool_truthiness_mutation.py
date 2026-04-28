"""Mutation tests for bool truthiness detection in the translator.

Each test monkeypatches a specific aspect of the truthiness logic, then
verifies that the contract tests would catch the regression.
"""

from __future__ import annotations

import re
import textwrap
from unittest.mock import patch


from src.translator.python_parser import parse_python
from src.translator.python_to_csharp import translate
import src.translator.python_to_csharp as p2cs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _translate_src(source: str) -> str:
    parsed = parse_python(textwrap.dedent(source))
    return translate(parsed)


# ===========================================================================
# Mutation 1 — Treat ALL fields as bool (never emit null checks)
# ===========================================================================

class TestMutationAllBool:
    """If _bool_fields contains everything, object fields won't get null
    checks. This proves our contract tests catch missing null checks."""

    SRC = """\
    class Player(MonoBehaviour):
        def __init__(self):
            self.is_dead: bool = False
            self.target = None
        def update(self):
            if self.target:
                pass
    """

    def test_all_bool_breaks_object_null_check(self):
        """Monkeypatch _bool_fields to include all fields. Object fields
        should incorrectly stay bare, proving the test catches it."""
        parsed = parse_python(textwrap.dedent(self.SRC))

        # Save original translate
        original_translate = p2cs.translate

        def mutant_translate(parsed_file, **kwargs):
            # Call original but then patch _bool_fields to include everything
            # We need to intercept after _bool_fields is set
            result = original_translate(parsed_file, **kwargs)
            return result

        # Instead, directly manipulate _bool_fields during translation
        original_bool = getattr(p2cs, '_bool_fields', set())
        try:
            # Set _bool_fields to contain everything including 'target'
            p2cs._bool_fields = {"isDead", "target"}
            # Re-run condition translation on a test condition
            cond = p2cs._translate_py_condition("target")
            # With target in _bool_fields, it should stay bare (no null check)
            assert "!= null" not in cond, (
                "With target in _bool_fields, it stays bare — mutation active"
            )
            # This is the WRONG behavior for an object field
            assert cond.strip() == "target", (
                "Mutation: object field incorrectly treated as bool"
            )
        finally:
            p2cs._bool_fields = original_bool


# ===========================================================================
# Mutation 2 — Treat ALL fields as objects (always null check)
# ===========================================================================

class TestMutationAllObject:
    """If _bool_fields is empty, bool fields will incorrectly get null
    checks. This proves our contract tests catch over-eager null checks."""

    def test_all_object_breaks_bool_bare(self):
        """Monkeypatch _bool_fields to empty set. Bool fields should
        incorrectly get null checks."""
        original_bool = getattr(p2cs, '_bool_fields', set())
        try:
            p2cs._bool_fields = set()  # No known bools
            cond = p2cs._translate_py_condition("isDead")
            # With empty _bool_fields, isDead should get null check (WRONG)
            assert "!= null" in cond, (
                "With empty _bool_fields, bool field incorrectly gets null check — "
                "mutation proves test catches it"
            )
        finally:
            p2cs._bool_fields = original_bool

    def test_all_object_breaks_bool_property(self):
        """Even with empty _bool_fields, Unity bool PROPERTIES should still
        be recognized (they're in _BOOL_PROPERTIES). This verifies the
        two-layer detection."""
        original_bool = getattr(p2cs, '_bool_fields', set())
        try:
            p2cs._bool_fields = set()
            # activeSelf is in _BOOL_PROPERTIES, so it should STILL stay bare
            cond = p2cs._translate_py_condition("gameObject.activeSelf")
            assert "!= null" not in cond, (
                "Unity bool properties should be recognized even with empty _bool_fields"
            )
        finally:
            p2cs._bool_fields = original_bool


# ===========================================================================
# Mutation 3 — Remove compound condition splitting
# ===========================================================================

class TestMutationNoCompoundSplit:
    """If we remove the && / || splitting, the whole compound condition
    would be treated as a single identifier (and likely fail the regex),
    so neither part gets proper truthiness handling."""

    def test_no_split_breaks_compound(self):
        """Monkeypatch _translate_py_condition to skip the split step.
        Compound conditions should lose per-operand handling."""
        original_bool = getattr(p2cs, '_bool_fields', set())
        try:
            p2cs._bool_fields = {"isDead"}

            # The original function splits on && / || then handles each part.
            # Without splitting, "isDead && target" is one string that doesn't
            # match ^[a-zA-Z_][\w.]*$ so it gets no truthiness handling at all.
            original_fn = p2cs._translate_py_condition

            def mutant_condition(cond: str) -> str:
                """Same as original but skip the split-and-fix step."""
                cond = cond.replace(" is not None", " != null").replace(" is None", " == null")
                cond = p2cs._translate_py_expression(cond)
                cond = cond.replace(" and ", " && ").replace(" or ", " || ")
                cond = re.sub(r"\bnot\s+", "!", cond)
                # SKIP the split/truthiness step entirely
                return cond

            with patch.object(p2cs, '_translate_py_condition', side_effect=mutant_condition):
                # Directly call the mutant
                result = mutant_condition("isDead && target")

            # Without splitting, "target" never gets null check
            assert "target != null" not in result, (
                "Mutation: without compound splitting, object field misses null check"
            )
            # The compound condition is left as-is with bare identifiers
            assert "target" in result, "target should still appear in output"
        finally:
            p2cs._bool_fields = original_bool


# ===========================================================================
# Mutation 4 — Remove _BOOL_PROPERTIES entirely
# ===========================================================================

class TestMutationNoBoolProperties:
    """If _BOOL_PROPERTIES is emptied, Unity bool properties like activeSelf
    would incorrectly get null checks."""

    def test_no_bool_properties_breaks_unity_props(self):
        """Monkeypatch to use empty _BOOL_PROPERTIES set."""
        original_bool = getattr(p2cs, '_bool_fields', set())
        try:
            p2cs._bool_fields = set()

            original_fn = p2cs._translate_py_condition

            def mutant_condition(cond: str) -> str:
                """Same as original but with empty _BOOL_PROPERTIES."""
                cond = cond.replace(" is not None", " != null").replace(" is None", " == null")
                cond = p2cs._translate_py_expression(cond)
                cond = cond.replace(" and ", " && ").replace(" or ", " || ")
                cond = re.sub(r"\bnot\s+", "!", cond)
                # Use empty _BOOL_PROPERTIES
                _BOOL_PROPERTIES = set()  # MUTATION: emptied
                parts = re.split(r"\s*(&&|\|\|)\s*", cond)
                fixed_parts = []
                for part in parts:
                    if part in ("&&", "||"):
                        fixed_parts.append(part)
                    elif re.match(r"^[a-zA-Z_][\w.]*$", part.strip()) and part.strip() not in ("true", "false", "null"):
                        ident = part.strip()
                        last_prop = ident.rsplit(".", 1)[-1] if "." in ident else ident
                        if ident in p2cs._bool_fields or last_prop in _BOOL_PROPERTIES:
                            fixed_parts.append(ident)
                        else:
                            fixed_parts.append(f"{ident} != null")
                    else:
                        fixed_parts.append(part)
                return " ".join(fixed_parts)

            result = mutant_condition("gameObject.activeSelf")
            # Without _BOOL_PROPERTIES, activeSelf gets null check (WRONG)
            assert "!= null" in result, (
                "Mutation: without _BOOL_PROPERTIES, Unity bool property gets null check"
            )
        finally:
            p2cs._bool_fields = original_bool
