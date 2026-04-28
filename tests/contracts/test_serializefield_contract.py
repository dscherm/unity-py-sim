"""Contract tests for [SerializeField] emission in the Python-to-C# translator.

Unity convention:
- Fields referencing MonoBehaviours, GameObjects, or prefabs must emit
  `[SerializeField] private T field;` with concrete types.
- Value-type fields with defaults (float, int, bool, string) remain
  `public T field = value;`.
- No field should ever emit `public object` when a concrete type annotation
  exists in the Python source.

These tests derive from Unity C# conventions, NOT from what the translator
currently does.  They are expected to FAIL (TDD red phase) until
SerializeField emission logic is implemented.
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
    """Build a minimal PyFile with one MonoBehaviour class."""
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
# 1. Reference-type fields must emit [SerializeField] private
# ===========================================================================

class TestSerializeFieldOnReferenceTypes:
    """Fields whose type is a MonoBehaviour subclass, GameObject, or other
    Unity reference type must be serialized with [SerializeField] private,
    not plain `public object`."""

    def test_gameobject_field_has_serializefield_attribute(self):
        """self.target: GameObject = None -> [SerializeField] private GameObject target;"""
        parsed = _make_monobehaviour("Enemy", [
            PyField(name="target", type_annotation="GameObject", default_value="None"),
        ])
        cs = _translate(parsed)
        assert "[SerializeField]" in cs, (
            "GameObject field must have [SerializeField] attribute"
        )
        assert "private GameObject target;" in cs, (
            "GameObject field must be 'private GameObject target;'"
        )

    def test_monobehaviour_ref_field_has_serializefield(self):
        """self.game_manager: GameManager = None -> [SerializeField] private GameManager gameManager;"""
        parsed = _make_monobehaviour("Player", [
            PyField(name="game_manager", type_annotation="GameManager", default_value="None"),
        ])
        cs = _translate(parsed)
        assert "[SerializeField]" in cs, (
            "MonoBehaviour reference field must have [SerializeField]"
        )
        assert "private GameManager gameManager;" in cs, (
            "MonoBehaviour ref field must be 'private GameManager gameManager;'"
        )

    def test_list_of_monobehaviours_becomes_array_with_serializefield(self):
        """self.ghosts: list[Ghost] = [] -> [SerializeField] private Ghost[] ghosts;"""
        parsed = _make_monobehaviour("GameManager", [
            PyField(name="ghosts", type_annotation="list[Ghost]", default_value="[]"),
        ])
        cs = _translate(parsed)
        # Must have the attribute
        assert "[SerializeField]" in cs, (
            "List of MonoBehaviour refs must have [SerializeField]"
        )
        # The field line itself must be private with concrete array type
        assert re.search(r"private\s+Ghost\[\]\s+ghosts;", cs), (
            f"Expected 'private Ghost[] ghosts;' but got:\n{cs}"
        )

    def test_optional_monobehaviour_ref_has_serializefield(self):
        """self.pacman: Pacman | None = None -> [SerializeField] private Pacman pacman;"""
        parsed = _make_monobehaviour("GameManager", [
            PyField(name="pacman", type_annotation="Pacman | None", default_value="None"),
        ])
        cs = _translate(parsed)
        assert "[SerializeField]" in cs
        assert "private Pacman pacman;" in cs, (
            "Optional MonoBehaviour ref must emit 'private Pacman pacman;'"
        )


# ===========================================================================
# 2. Value-type fields must stay public without [SerializeField]
# ===========================================================================

class TestValueTypeFieldsRemainPublic:
    """Primitive / value-type fields with defaults should remain public
    and should NOT have [SerializeField] (Unity auto-serializes public fields)."""

    def test_float_field_stays_public(self):
        """self.speed: float = 5.0 -> public float speed = 5.0f;"""
        parsed = _make_monobehaviour("Player", [
            PyField(name="speed", type_annotation="float", default_value="5.0"),
        ])
        cs = _translate(parsed)
        assert "public float speed = 5.0f;" in cs

    def test_int_field_stays_public(self):
        """self.score: int = 0 -> public int score = 0;"""
        parsed = _make_monobehaviour("GameManager", [
            PyField(name="score", type_annotation="int", default_value="0"),
        ])
        cs = _translate(parsed)
        assert "public int score = 0;" in cs

    def test_bool_field_stays_public(self):
        """self.is_alive: bool = True -> public bool isAlive = true;"""
        parsed = _make_monobehaviour("Player", [
            PyField(name="is_alive", type_annotation="bool", default_value="True"),
        ])
        cs = _translate(parsed)
        assert "public bool isAlive = true;" in cs

    def test_string_field_stays_public(self):
        """self.player_name: str = 'hero' -> public string playerName = \"hero\";"""
        parsed = _make_monobehaviour("Player", [
            PyField(name="player_name", type_annotation="str", default_value="'hero'"),
        ])
        cs = _translate(parsed)
        assert 'public string playerName = "hero";' in cs


# ===========================================================================
# 3. No 'public object' for typed fields
# ===========================================================================

class TestNoPublicObjectForTypedFields:
    """If a Python field has a concrete type annotation, the C# output must
    NEVER emit 'public object fieldName'.  This is the hallmark bug."""

    def test_gameobject_field_not_object(self):
        parsed = _make_monobehaviour("Spawner", [
            PyField(name="target", type_annotation="GameObject", default_value="None"),
        ])
        cs = _translate(parsed)
        assert "public object target" not in cs, (
            "Typed field must never emit 'public object'"
        )

    def test_monobehaviour_ref_not_object(self):
        parsed = _make_monobehaviour("UI", [
            PyField(name="game_manager", type_annotation="GameManager", default_value="None"),
        ])
        cs = _translate(parsed)
        assert "public object gameManager" not in cs, (
            "MonoBehaviour ref must never emit 'public object'"
        )

    def test_list_field_not_object(self):
        parsed = _make_monobehaviour("Arena", [
            PyField(name="enemies", type_annotation="list[Enemy]", default_value="[]"),
        ])
        cs = _translate(parsed)
        assert "public object enemies" not in cs

    def test_no_public_object_anywhere_for_typed_fields(self):
        """Translate a class with multiple typed fields — none should be 'object'."""
        parsed = _make_monobehaviour("TestClass", [
            PyField(name="speed", type_annotation="float", default_value="5.0"),
            PyField(name="target", type_annotation="GameObject", default_value="None"),
            PyField(name="ghosts", type_annotation="list[Ghost]", default_value="[]"),
            PyField(name="score", type_annotation="int", default_value="0"),
            PyField(name="manager", type_annotation="GameManager", default_value="None"),
        ])
        cs = _translate(parsed)
        assert "object" not in cs, (
            f"No 'object' type should appear for any typed field. Got:\n{cs}"
        )


# ===========================================================================
# 4. Prefab fields from Instantiate() must emit [SerializeField] private GameObject
# ===========================================================================

class TestPrefabFieldSerializeField:
    """When Instantiate(laser_prefab, ...) is used in a method, the translator
    discovers a prefab field.  It must emit [SerializeField] private."""

    def test_prefab_field_has_serializefield(self):
        parsed = _make_monobehaviour("Shooter", [
            PyField(name="speed", type_annotation="float", default_value="10.0"),
        ], methods=[
            PyMethod(
                name="fire",
                body_source="obj = instantiate(self.laser_prefab, self.transform.position)",
            ),
        ])
        cs = _translate(parsed)
        # The translator should discover laserPrefab from Instantiate() usage
        assert "laserPrefab" in cs, "Prefab field must be discovered from Instantiate()"
        assert "[SerializeField]" in cs, "Prefab field must have [SerializeField]"
        assert re.search(r"private\s+GameObject\s+laserPrefab;", cs), (
            f"Prefab must emit 'private GameObject laserPrefab;' Got:\n{cs}"
        )


# ===========================================================================
# 5. Access modifier correctness — private for refs, public for values
# ===========================================================================

class TestAccessModifierCorrectness:
    """In Unity, reference fields assigned via Inspector are [SerializeField] private.
    Value fields with defaults are public.  No field should emit `public` for a
    null-initialized reference type."""

    def test_null_ref_field_is_not_public(self):
        """A field initialized to None with a reference type must not be public."""
        parsed = _make_monobehaviour("Controller", [
            PyField(name="target", type_annotation="GameObject", default_value="None"),
        ])
        cs = _translate(parsed)
        # Must NOT have "public GameObject target"
        assert "public GameObject target" not in cs, (
            "Reference field must be [SerializeField] private, not public"
        )

    def test_mixed_fields_correct_access(self):
        """A class with both value and reference fields must have correct access."""
        parsed = _make_monobehaviour("Mixed", [
            PyField(name="speed", type_annotation="float", default_value="5.0"),
            PyField(name="target", type_annotation="GameObject", default_value="None"),
            PyField(name="lives", type_annotation="int", default_value="3"),
            PyField(name="enemy", type_annotation="Enemy", default_value="None"),
        ])
        cs = _translate(parsed)
        # Value types: public
        assert "public float speed" in cs
        assert "public int lives" in cs
        # Reference types: private with [SerializeField]
        assert "public GameObject target" not in cs
        assert "public Enemy enemy" not in cs
        assert "private GameObject target;" in cs
        assert "private Enemy enemy;" in cs
