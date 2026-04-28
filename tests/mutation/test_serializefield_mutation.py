"""Mutation tests for [SerializeField] emission.

These tests monkeypatch the translator to simulate regressions and verify
that the contract tests would catch them.

NOTE: These tests are written for the FUTURE correct behavior. They will
fail until SerializeField emission is implemented, because the monkeypatching
assumes the correct code path exists.
"""

from __future__ import annotations

import re


from src.translator.python_parser import PyFile, PyClass, PyField, PyMethod
from src.translator.python_to_csharp import translate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_monobehaviour(
    class_name: str,
    fields: list[PyField],
    methods: list[PyMethod] | None = None,
) -> PyFile:
    return PyFile(
        classes=[
            PyClass(
                name=class_name,
                base_classes=["MonoBehaviour"],
                is_monobehaviour=True,
                fields=fields,
                methods=methods or [],
            )
        ]
    )


def _translate(parsed: PyFile, **kwargs) -> str:
    return translate(parsed, unity_version=5, input_system="legacy", **kwargs)


# ===========================================================================
# 1. Mutation: emit 'public' instead of '[SerializeField] private'
# ===========================================================================

class TestMutationPublicInsteadOfSerializeField:
    """If someone removes [SerializeField] and makes reference fields public,
    our contract tests must detect it."""

    def test_detect_missing_serializefield_on_gameobject(self):
        """Translate a GameObject field.  The output must contain [SerializeField].
        If it does not, this test flags the mutation."""
        parsed = _make_monobehaviour("Enemy", [
            PyField(name="target", type_annotation="GameObject", default_value="None"),
        ])
        cs = _translate(parsed)

        # The CORRECT output should have [SerializeField].
        # If this assertion passes, the feature works.
        # If it fails, a mutation (or missing feature) is detected.
        has_serialize = "[SerializeField]" in cs
        has_private = "private GameObject target;" in cs
        has_wrong_public = "public GameObject target" in cs

        # At least one of these must detect the problem:
        assert has_serialize or (not has_wrong_public), (
            "Mutation detected: reference field is public without [SerializeField]"
        )
        # Stronger: it MUST have the attribute
        assert has_serialize, (
            "Mutation detected: [SerializeField] attribute missing from reference field"
        )

    def test_detect_missing_serializefield_on_monobehaviour_ref(self):
        parsed = _make_monobehaviour("Player", [
            PyField(name="game_manager", type_annotation="GameManager", default_value="None"),
        ])
        cs = _translate(parsed)
        assert "[SerializeField]" in cs, (
            "Mutation detected: MonoBehaviour ref field missing [SerializeField]"
        )
        assert "private GameManager gameManager;" in cs, (
            "Mutation detected: MonoBehaviour ref field not private"
        )


# ===========================================================================
# 2. Mutation: emit 'object' type instead of concrete type
# ===========================================================================

class TestMutationObjectTypeInsteadOfConcrete:
    """If someone breaks type resolution so that reference fields emit 'object'
    instead of the concrete type, these tests catch it."""

    def test_detect_object_type_for_gameobject(self):
        parsed = _make_monobehaviour("Spawner", [
            PyField(name="target", type_annotation="GameObject", default_value="None"),
        ])
        cs = _translate(parsed)
        assert "object target" not in cs, (
            "Mutation detected: GameObject field emitted as 'object'"
        )
        # Must use the concrete type
        assert "GameObject target" in cs or "GameObject target;" in cs, (
            "Mutation detected: concrete type 'GameObject' missing from field declaration"
        )

    def test_detect_object_type_for_custom_monobehaviour(self):
        parsed = _make_monobehaviour("Controller", [
            PyField(name="enemy", type_annotation="Enemy", default_value="None"),
        ])
        cs = _translate(parsed)
        assert "object enemy" not in cs, (
            "Mutation detected: custom type field emitted as 'object'"
        )
        assert "Enemy enemy" in cs or "Enemy enemy;" in cs

    def test_detect_object_type_for_list(self):
        parsed = _make_monobehaviour("Arena", [
            PyField(name="ghosts", type_annotation="list[Ghost]", default_value="[]"),
        ])
        cs = _translate(parsed)
        assert "object ghosts" not in cs, (
            "Mutation detected: list field emitted as 'object'"
        )
        # Must have a concrete collection type
        assert re.search(r"(Ghost\[\]|List<Ghost>)", cs), (
            "Mutation detected: list field missing concrete element type"
        )


# ===========================================================================
# 3. Mutation: value-type field incorrectly gets [SerializeField] private
# ===========================================================================

class TestMutationValueTypeNotOverSerialized:
    """Value types (int, float, bool) with defaults should stay public.
    If a mutation makes ALL fields [SerializeField] private, catch it."""

    def test_float_field_stays_public(self):
        parsed = _make_monobehaviour("Player", [
            PyField(name="speed", type_annotation="float", default_value="5.0"),
        ])
        cs = _translate(parsed)
        assert "public float speed" in cs, (
            "Mutation detected: value-type field incorrectly made private"
        )

    def test_int_field_stays_public(self):
        parsed = _make_monobehaviour("Score", [
            PyField(name="points", type_annotation="int", default_value="0"),
        ])
        cs = _translate(parsed)
        assert "public int points" in cs, (
            "Mutation detected: int field incorrectly made private"
        )
