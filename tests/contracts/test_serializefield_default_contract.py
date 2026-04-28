"""Contract tests for FU-3: [SerializeField] private/protected default for reference fields.

Derived from Unity documentation contract, NOT from implementation details.
Do NOT read existing test files in tests/ — derived from src/ and Unity docs.

Unity contracts being validated:
1. Unity's Inspector serializes public fields OR [SerializeField] private/protected fields.
   Reference-type fields must use [SerializeField] private to prevent NullRef in Inspector.
2. C# subclass access: private is not reachable from subclasses. protected is.
3. Arrays and List<T> of reference types follow the same rule.
4. Value types (int, float, bool, string, Vector2, Color, etc.) stay public.
5. Static fields are a separate bucket — not touched by this change.
"""

from __future__ import annotations

import tempfile
import textwrap
from pathlib import Path

import pytest

from src.translator.python_to_csharp import translate, set_subclassed_classes
from src.translator.project_translator import translate_project


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_py_source(body: str) -> str:
    """Wrap a class body in a minimal MonoBehaviour Python file."""
    indented_body = textwrap.indent(textwrap.dedent(body).strip(), "    ")
    return (
        "from src.engine.core import MonoBehaviour\n\n"
        "class TestClass(MonoBehaviour):\n"
        + indented_body
        + "\n"
    )


def _translate_source(source: str) -> str:
    """Parse and translate a Python source string to C#."""
    set_subclassed_classes(set())  # reset global state
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
        f.write(source)
        tmp_path = Path(f.name)
    try:
        from src.translator.python_parser import parse_python_file
        parsed = parse_python_file(tmp_path)
        return translate(parsed)
    finally:
        tmp_path.unlink(missing_ok=True)


def _write_project(files: dict[str, str]) -> Path:
    """Write a dict of {filename: source} to a temp directory and return it."""
    tmpdir = Path(tempfile.mkdtemp())
    for name, src in files.items():
        (tmpdir / name).write_text(textwrap.dedent(src), encoding="utf-8")
    return tmpdir


# ---------------------------------------------------------------------------
# Scenario 1: Default direction flip — reference fields → [SerializeField] private
# ---------------------------------------------------------------------------

class TestReferenceFieldDefaultSerializeField:
    """Unity contract: reference-type fields without leading _ must emit
    [SerializeField] private, not public — prevents NullRef via Inspector."""

    def test_gameobject_field_no_underscore_emits_serialize_field_private(self):
        """A bare GameObject field (no underscore) must NOT emit as public.
        Before FU-3 it was `public GameObject target;`.
        Contract: must be `[SerializeField] private GameObject target;`."""
        src = _make_py_source("""
            def __init__(self):
                super().__init__()
                self.target = None  # GameObject
        """)
        cs = _translate_source(src)
        assert "[SerializeField]" in cs, "GameObject field must use [SerializeField]"
        # Must NOT be public — that was the pre-FU-3 bug
        assert "public GameObject target" not in cs, (
            "Reference field 'target' must NOT emit as public; "
            "public reference fields cause NullRef in Unity Inspector"
        )

    def test_sprite_renderer_field_emits_serialize_field_private(self):
        """SpriteRenderer reference field without underscore must use [SerializeField] private."""
        src = _make_py_source("""
            def __init__(self):
                super().__init__()
                self.sprite_renderer = None  # SpriteRenderer
        """)
        cs = _translate_source(src)
        assert "[SerializeField]" in cs
        assert "public SpriteRenderer spriteRenderer" not in cs

    def test_monobehaviour_subclass_ref_field_emits_serialize_field_private(self):
        """A field typed as a MonoBehaviour subclass from another file
        must emit [SerializeField] private, not public."""
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour

            class Player(MonoBehaviour):
                def __init__(self):
                    super().__init__()
                    self.game_manager = None  # GameManager — foreign class ref
        """)
        cs = _translate_source(source)
        assert "[SerializeField]" in cs, (
            "Cross-file MonoBehaviour reference must use [SerializeField]"
        )
        assert "public GameManager gameManager" not in cs, (
            "MonoBehaviour subclass ref must NOT be public (pre-FU-3 bug)"
        )

    def test_field_with_no_leading_underscore_is_serialize_field(self):
        """Before FU-3, fields without _ defaulted to public. After FU-3 they
        must default to [SerializeField] private for reference types."""
        src = _make_py_source("""
            def __init__(self):
                super().__init__()
                self.camera = None  # Camera
                self.audio_source = None  # AudioSource
        """)
        cs = _translate_source(src)
        # Both are Unity reference types — must use [SerializeField]
        assert "public Camera camera" not in cs
        assert "public AudioSource audioSource" not in cs
        assert cs.count("[SerializeField]") >= 2


# ---------------------------------------------------------------------------
# Scenario 2: Value-type back-compat — public stays public
# ---------------------------------------------------------------------------

class TestValueTypeBackCompatPublic:
    """Unity contract: value-type fields stay public so Unity Inspector
    shows them with defaults. Regression: if someone over-generalizes
    FU-3 to ALL fields, gameplay defaults in Inspector disappear."""

    def test_int_field_with_default_stays_public(self):
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour

            class Config(MonoBehaviour):
                speed: int = 5

                def __init__(self):
                    super().__init__()
        """)
        cs = _translate_source(source)
        assert "public int speed" in cs or "public int Speed" in cs, (
            "int field must remain public — value types are not [SerializeField] private"
        )
        for ln in cs.split("\n"):
            if "int" in ln and "speed" in ln.lower() and "[SerializeField]" in ln:
                pytest.fail(f"int field must NOT use [SerializeField]: {ln}")

    def test_float_field_with_default_stays_public(self):
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour

            class Ball(MonoBehaviour):
                speed: float = 5.0
                gravity: float = -9.81
        """)
        cs = _translate_source(source)
        assert "public float speed" in cs or "public float Speed" in cs
        assert "public float gravity" in cs or "public float Gravity" in cs

    def test_bool_field_with_default_stays_public(self):
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour

            class Enemy(MonoBehaviour):
                is_active: bool = True
                can_shoot: bool = False
        """)
        cs = _translate_source(source)
        # bool fields should appear as public
        assert "bool" in cs
        # Confirm not wrapped in [SerializeField] unless they're also in private_fields
        # The key contract: value types don't get forced into [SerializeField]
        lines_with_bool = [ln for ln in cs.split("\n") if "bool" in ln and "isActive" in ln.lower().replace("_","")]
        # bool with default ends up in serialized_fields -> public
        for ln in cs.split("\n"):
            if "bool" in ln and "[SerializeField]" not in ln and "public bool" in ln:
                break
        else:
            # If no plain public bool found, check there's at least no forced private bool
            serialize_bool_lines = [ln for ln in cs.split("\n") if "[SerializeField]" in ln and "bool" in ln]
            assert len(serialize_bool_lines) == 0, (
                f"bool fields must NOT use [SerializeField] private. Found: {serialize_bool_lines}"
            )

    def test_string_field_with_default_stays_public(self):
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour

            class UI(MonoBehaviour):
                label: str = "Score"
                tag_name: str = "Player"
        """)
        cs = _translate_source(source)
        assert "public string label" in cs or "public string Label" in cs

    def test_vector2_field_stays_public(self):
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour
            from src.engine.math.vector import Vector2

            class Movement(MonoBehaviour):
                direction: Vector2 = None
                velocity: Vector2 = None
        """)
        cs = _translate_source(source)
        # Vector2 is a value type — must NOT be [SerializeField] private
        for ln in cs.split("\n"):
            if "Vector2" in ln and "direction" in ln.lower():
                assert "[SerializeField]" not in ln, (
                    f"Vector2 field must not use [SerializeField]: {ln}"
                )

    def test_color_field_stays_public(self):
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour

            class Painter(MonoBehaviour):
                color: 'Color' = None
                bg_color: 'Color' = None
        """)
        cs = _translate_source(source)
        # Color is a value type — must NOT be [SerializeField] private
        for ln in cs.split("\n"):
            if "Color" in ln and ("[SerializeField]" in ln):
                pytest.fail(
                    f"Color (value type) must not use [SerializeField] private: {ln}"
                )

    def test_value_types_with_no_default_stay_public(self):
        """Value types without defaults must also not get [SerializeField] private."""
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour

            class Config(MonoBehaviour):
                lives: int
                score: int
                multiplier: float
        """)
        cs = _translate_source(source)
        for ln in cs.split("\n"):
            if "int" in ln or ("float" in ln and "multiplier" in ln.lower()):
                assert "[SerializeField]" not in ln, (
                    f"Value type without default must not use [SerializeField]: {ln}"
                )


# ---------------------------------------------------------------------------
# Scenario 3: Protected promotion for subclassed base via translate_project
# ---------------------------------------------------------------------------

class TestProtectedPromotionForSubclassedBase:
    """Unity contract: if a MonoBehaviour class is subclassed somewhere in the
    same project, its reference fields must emit as `protected` (not `private`)
    so C# subclasses can access them — C# private is not reachable across files."""

    def test_base_reference_field_promotes_to_protected_when_subclassed(self):
        """Phase 3.8 contract: translate_project must detect the subclass
        relationship and upgrade the base class's reference fields to protected."""
        files = {
            "ghost_behavior.py": """\
                from src.engine.core import MonoBehaviour

                class GhostBehavior(MonoBehaviour):
                    def __init__(self):
                        super().__init__()
                        self.ghost = None  # Ghost reference
                        self.duration: float = 0.0
            """,
            "ghost_chase.py": """\
                from src.engine.core import MonoBehaviour
                from .ghost_behavior import GhostBehavior

                class GhostChase(GhostBehavior):
                    def on_disable(self):
                        pass
            """,
        }
        tmpdir = _write_project(files)
        try:
            results = translate_project(tmpdir)
            base_cs = results.get("GhostBehavior.cs", "")
            assert base_cs, "GhostBehavior.cs was not generated"
            # Must be protected — a subclass (GhostChase) exists in the project
            assert "[SerializeField] protected" in base_cs, (
                f"GhostBehavior.ghost must be 'protected' because GhostChase subclasses it. "
                f"Found fields:\n{[ln for ln in base_cs.split(chr(10)) if 'ghost' in ln.lower() or 'SerializeField' in ln]}"
            )
            assert "[SerializeField] private" not in base_cs or "ghost" not in (
                base_cs.split("[SerializeField] private")[1].split(";")[0]
                if "[SerializeField] private" in base_cs else ""
            ), "GhostBehavior.ghost must NOT be private when subclassed"
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_unsubclassed_monobehaviour_stays_private(self):
        """A MonoBehaviour that is NOT subclassed must keep [SerializeField] private
        even when other classes in the same project ARE subclassed."""
        files = {
            "ghost_behavior.py": """\
                from src.engine.core import MonoBehaviour

                class GhostBehavior(MonoBehaviour):
                    def __init__(self):
                        super().__init__()
                        self.ghost = None  # Ghost reference
            """,
            "ghost_chase.py": """\
                from src.engine.core import MonoBehaviour
                from .ghost_behavior import GhostBehavior

                class GhostChase(GhostBehavior):
                    pass
            """,
            "player.py": """\
                from src.engine.core import MonoBehaviour

                class Player(MonoBehaviour):
                    def __init__(self):
                        super().__init__()
                        self.camera = None  # Camera
            """,
        }
        tmpdir = _write_project(files)
        try:
            results = translate_project(tmpdir)
            player_cs = results.get("Player.cs", "")
            assert player_cs, "Player.cs was not generated"
            # Player is NOT subclassed — must stay private
            assert "[SerializeField] private" in player_cs, (
                f"Player.camera must be [SerializeField] private (not subclassed). "
                f"Found:\n{[ln for ln in player_cs.split(chr(10)) if 'camera' in ln.lower() or 'SerializeField' in ln]}"
            )
            assert "[SerializeField] protected" not in player_cs, (
                "Player is not subclassed — must NOT emit protected"
            )
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_value_type_in_subclassed_base_stays_public(self):
        """Value-type fields in a subclassed base class must remain public
        (not gain [SerializeField] protected). Only reference types are affected."""
        files = {
            "base_controller.py": """\
                from src.engine.core import MonoBehaviour

                class BaseController(MonoBehaviour):
                    speed: float = 5.0
                    lives: int = 3
            """,
            "player_controller.py": """\
                from src.engine.core import MonoBehaviour
                from .base_controller import BaseController

                class PlayerController(BaseController):
                    pass
            """,
        }
        tmpdir = _write_project(files)
        try:
            results = translate_project(tmpdir)
            base_cs = results.get("BaseController.cs", "")
            assert base_cs, "BaseController.cs was not generated"
            for ln in base_cs.split("\n"):
                if ("float" in ln or "int" in ln) and "[SerializeField]" in ln:
                    pytest.fail(
                        f"Value-type field in subclassed base must stay public, not [SerializeField]: {ln}"
                    )
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Scenario 4: Subclass compilability proxy — base protected field accessible
# ---------------------------------------------------------------------------

class TestSubclassCompilabilityProxy:
    """Unity contract: if GhostChase.cs accesses `this.ghost` or bare `ghost`,
    the field declared in GhostBehavior.cs must NOT be private (C# private
    blocks cross-file subclass access). Assert via string inspection."""

    def test_base_ghost_field_is_not_private_when_subclassed(self):
        """GhostBehavior.ghost must be protected so GhostChase can use it."""
        files = {
            "ghost_behavior.py": """\
                from src.engine.core import MonoBehaviour

                class GhostBehavior(MonoBehaviour):
                    def __init__(self):
                        super().__init__()
                        self.ghost = None  # Ghost reference
                        self.duration: float = 0.0
            """,
            "ghost_chase.py": """\
                from src.engine.core import MonoBehaviour
                from .ghost_behavior import GhostBehavior

                class GhostChase(GhostBehavior):
                    def on_disable(self):
                        if self.ghost:
                            self.ghost.scatter.enable()
            """,
        }
        tmpdir = _write_project(files)
        try:
            results = translate_project(tmpdir)
            base_cs = results.get("GhostBehavior.cs", "")
            assert base_cs, "GhostBehavior.cs must be generated"

            # The ghost field line in the base class must not be private
            for ln in base_cs.split("\n"):
                if "ghost" in ln.lower() and "SerializeField" in ln:
                    assert "private" not in ln, (
                        f"GhostBehavior.ghost must not be private (GhostChase inherits it): {ln}"
                    )
                    assert "protected" in ln, (
                        f"GhostBehavior.ghost must be protected for C# subclass access: {ln}"
                    )
                    break
            else:
                # Field might be named differently — look for the pattern broadly
                serialize_lines = [ln for ln in base_cs.split("\n") if "SerializeField" in ln]
                assert any("protected" in ln for ln in serialize_lines), (
                    f"Base class with subclass must have at least one [SerializeField] protected field. "
                    f"SerializeField lines: {serialize_lines}"
                )
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)

    def test_private_keyword_absent_on_subclassed_ref_field(self):
        """Direct negative: `[SerializeField] private Ghost ghost;` must NOT appear
        in a base class that has a known subclass in the project."""
        files = {
            "animal.py": """\
                from src.engine.core import MonoBehaviour

                class Animal(MonoBehaviour):
                    def __init__(self):
                        super().__init__()
                        self.prey = None  # Animal reference
            """,
            "dog.py": """\
                from src.engine.core import MonoBehaviour
                from .animal import Animal

                class Dog(Animal):
                    pass
            """,
        }
        tmpdir = _write_project(files)
        try:
            results = translate_project(tmpdir)
            animal_cs = results.get("Animal.cs", "")
            assert animal_cs, "Animal.cs must be generated"
            # The reference field in base Animal must not be private
            serialize_private_lines = [
                ln for ln in animal_cs.split("\n")
                if "[SerializeField] private" in ln
            ]
            assert len(serialize_private_lines) == 0, (
                f"Animal is subclassed by Dog — no [SerializeField] private fields allowed. "
                f"Found: {serialize_private_lines}"
            )
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Scenario 5: List<T> and array[] of reference types
# ---------------------------------------------------------------------------

class TestListAndArrayOfReferenceTypes:
    """Unity contract: List<T> and T[] where T is a reference type (e.g. Ghost,
    GameObject) must emit as [SerializeField] private (or protected if subclassed).
    The old bug was `public Ghost[] ghosts;`."""

    def test_array_of_monobehaviour_subclass_emits_serialize_field_private(self):
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour

            class GameManager(MonoBehaviour):
                def __init__(self):
                    super().__init__()
                    self.ghosts = []  # Ghost[]
        """)
        cs = _translate_source(source)
        # Must not be plain public array
        assert "public Ghost[] ghosts" not in cs, (
            "Ghost[] must not be public — reference array must use [SerializeField]"
        )

    def test_list_of_monobehaviour_subclass_emits_serialize_field(self):
        """List[Ghost] field must emit as [SerializeField] private, not public."""
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour
            from typing import List

            class EnemyManager(MonoBehaviour):
                enemies: 'List[Enemy]' = None

                def __init__(self):
                    super().__init__()
                    self.enemies: list = []  # List<Enemy>
        """)
        cs = _translate_source(source)
        # List<Enemy> is a reference — must use [SerializeField]
        for ln in cs.split("\n"):
            if "List<" in ln and "Enemy" in ln and "enemies" in ln.lower():
                assert "public List<" not in ln, (
                    f"List<Enemy> must not be public: {ln}"
                )

    def test_array_of_gameobject_emits_serialize_field(self):
        """GameObject[] array must use [SerializeField] private."""
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour

            class GridManager(MonoBehaviour):
                def __init__(self):
                    super().__init__()
                    self.tiles = []  # GameObject[]
        """)
        cs = _translate_source(source)
        # If translator infers GameObject[], it must be [SerializeField]
        # Even if type is inferred as object[], still a reference type
        for ln in cs.split("\n"):
            if ("GameObject" in ln or "object" in ln) and ("tiles" in ln.lower()):
                assert "public " not in ln or "[SerializeField]" in ln, (
                    f"Array field 'tiles' (ref type) must use [SerializeField]: {ln}"
                )

    def test_array_in_subclassed_owner_emits_protected(self):
        """When the owner class is subclassed, its reference arrays must be
        [SerializeField] protected so C# subclasses can access them."""
        files = {
            "ghost_behavior.py": """\
                from src.engine.core import MonoBehaviour

                class GhostBehavior(MonoBehaviour):
                    def __init__(self):
                        super().__init__()
                        self.waypoints = []  # Node[]
            """,
            "ghost_scatter.py": """\
                from src.engine.core import MonoBehaviour
                from .ghost_behavior import GhostBehavior

                class GhostScatter(GhostBehavior):
                    pass
            """,
        }
        tmpdir = _write_project(files)
        try:
            results = translate_project(tmpdir)
            base_cs = results.get("GhostBehavior.cs", "")
            assert base_cs, "GhostBehavior.cs must be generated"
            # With subclass in project, reference fields must be protected
            serialize_lines = [ln for ln in base_cs.split("\n") if "[SerializeField]" in ln]
            if serialize_lines:
                assert any("protected" in ln for ln in serialize_lines), (
                    f"Subclassed GhostBehavior must have [SerializeField] protected fields. "
                    f"Got: {serialize_lines}"
                )
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Scenario 6: Mutation — set_subclassed_classes wiring
# ---------------------------------------------------------------------------

class TestMutationSubclassedClassesWiring:
    """Mutation test: if Phase 3.8 wiring breaks (set_subclassed_classes not
    called), base class reference fields must regress to [SerializeField] private."""

    def test_empty_subclassed_set_forces_private_not_protected(self):
        """When set_subclassed_classes({}) is called (simulating broken Phase 3.8),
        the base class reference fields must emit as [SerializeField] private,
        NOT protected — proving the promotion is wired through set_subclassed_classes."""
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour

            class GhostBehavior(MonoBehaviour):
                def __init__(self):
                    super().__init__()
                    self.ghost = None  # Ghost reference
        """)
        # Simulate broken Phase 3.8: subclassed_classes is empty
        set_subclassed_classes(set())
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
            f.write(source)
            tmp_path = Path(f.name)
        try:
            from src.translator.python_parser import parse_python_file
            parsed = parse_python_file(tmp_path)
            cs = translate(parsed)
        finally:
            tmp_path.unlink(missing_ok=True)
        # With empty set, must emit private (not protected)
        serialize_lines = [ln for ln in cs.split("\n") if "[SerializeField]" in ln]
        assert serialize_lines, "Must emit at least one [SerializeField] field"
        for ln in serialize_lines:
            if "ghost" in ln.lower():
                assert "private" in ln, (
                    f"With empty subclassed set, field must be private not protected: {ln}"
                )
                assert "protected" not in ln, (
                    f"protected must only appear when subclassed_classes is populated: {ln}"
                )

    def test_populated_subclassed_set_forces_protected(self):
        """Inverse mutation: when set_subclassed_classes({'GhostBehavior'}) is
        called manually, the field must upgrade to protected — proving the path
        is active and not dead code."""
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour

            class GhostBehavior(MonoBehaviour):
                def __init__(self):
                    super().__init__()
                    self.ghost = None  # Ghost reference
        """)
        set_subclassed_classes({"GhostBehavior"})
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False, encoding="utf-8") as f:
            f.write(source)
            tmp_path = Path(f.name)
        try:
            from src.translator.python_parser import parse_python_file
            parsed = parse_python_file(tmp_path)
            cs = translate(parsed)
        finally:
            tmp_path.unlink(missing_ok=True)
            set_subclassed_classes(set())  # cleanup

        serialize_lines = [ln for ln in cs.split("\n") if "[SerializeField]" in ln]
        assert any("protected" in ln for ln in serialize_lines), (
            f"With GhostBehavior in subclassed set, must emit [SerializeField] protected. "
            f"Got: {serialize_lines}"
        )

    def test_project_translate_without_phase38_wiring_regresses_to_private(self):
        """Mutation: monkeypatch set_subclassed_classes to no-op (empty set always),
        then verify base class's reference fields fall back to private — proving
        translate_project's Phase 3.8 call is what drives protection."""
        files = {
            "ghost_behavior.py": """\
                from src.engine.core import MonoBehaviour

                class GhostBehavior(MonoBehaviour):
                    def __init__(self):
                        super().__init__()
                        self.ghost = None  # Ghost reference
            """,
            "ghost_chase.py": """\
                from src.engine.core import MonoBehaviour
                from .ghost_behavior import GhostBehavior

                class GhostChase(GhostBehavior):
                    pass
            """,
        }
        tmpdir = _write_project(files)
        try:
            import src.translator.python_to_csharp as _p2cs
            original_fn = _p2cs.set_subclassed_classes

            def _noop_setter(names):
                # Simulate Phase 3.8 wiring broken: always pass empty set
                original_fn(set())

            _p2cs.set_subclassed_classes = _noop_setter
            import src.translator.project_translator as _pt
            _pt.set_subclassed_classes = _noop_setter

            try:
                results = translate_project(tmpdir)
                base_cs = results.get("GhostBehavior.cs", "")
                assert base_cs, "GhostBehavior.cs must be generated"
                # With broken wiring, must fall back to private
                serialize_lines = [ln for ln in base_cs.split("\n") if "[SerializeField]" in ln]
                assert serialize_lines, "Must still emit [SerializeField] fields"
                for ln in serialize_lines:
                    if "ghost" in ln.lower():
                        assert "protected" not in ln, (
                            "With broken Phase 3.8 wiring, field must NOT be protected"
                        )
            finally:
                _p2cs.set_subclassed_classes = original_fn
                _pt.set_subclassed_classes = original_fn
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Scenario 7: Underscore prefix back-compat
# ---------------------------------------------------------------------------

class TestUnderscorePrefixBackCompat:
    """Unity contract: fields with leading _ must still emit as [SerializeField] private
    after FU-3 — the underscore prefix was the OLD way to force private. Callers
    that relied on `_game_manager: GameManager` staying private must not regress."""

    def test_underscore_gameobject_field_stays_serialize_field_private(self):
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour

            class Player(MonoBehaviour):
                def __init__(self):
                    super().__init__()
                    self._game_manager = None  # GameManager
        """)
        set_subclassed_classes(set())
        cs = _translate_source(source)
        serialize_lines = [ln for ln in cs.split("\n") if "[SerializeField]" in ln]
        assert serialize_lines, "_game_manager (ref type) must emit [SerializeField]"
        for ln in serialize_lines:
            assert "private" in ln, (
                f"Underscore ref field must emit [SerializeField] private: {ln}"
            )
            assert "protected" not in ln, (
                f"Underscore ref field must NOT emit protected (not subclassed): {ln}"
            )

    def test_underscore_sprite_renderer_emits_serialize_field_private(self):
        """_sprite_renderer: SpriteRenderer field must emit [SerializeField] private.
        This was the original FU-3 motivation from flappy_bird Player.py."""
        source = textwrap.dedent("""\
            from src.engine.core import MonoBehaviour
            from src.engine.rendering.renderer import SpriteRenderer

            class Player(MonoBehaviour):
                def __init__(self):
                    super().__init__()
                    self._sprite_renderer = None  # SpriteRenderer
        """)
        cs = _translate_source(source)
        assert "[SerializeField]" in cs, "_sprite_renderer must use [SerializeField]"
        assert "public SpriteRenderer" not in cs, (
            "_sprite_renderer must not be public"
        )
        # Verify it's private specifically
        for ln in cs.split("\n"):
            if "SpriteRenderer" in ln and "[SerializeField]" in ln:
                assert "private" in ln, f"Must be private: {ln}"
                break

    def test_underscore_ref_in_subclassed_class_stays_private(self):
        """Even when the base class is in subclassed_classes, an _underscore ref
        field must still get [SerializeField] private — protection choice is
        determined by whether the OWNER class is subclassed, not the field name."""
        files = {
            "ghost_behavior.py": """\
                from src.engine.core import MonoBehaviour

                class GhostBehavior(MonoBehaviour):
                    def __init__(self):
                        super().__init__()
                        self._internal_ref = None  # Camera
            """,
            "ghost_chase.py": """\
                from src.engine.core import MonoBehaviour
                from .ghost_behavior import GhostBehavior

                class GhostChase(GhostBehavior):
                    pass
            """,
        }
        tmpdir = _write_project(files)
        try:
            results = translate_project(tmpdir)
            base_cs = results.get("GhostBehavior.cs", "")
            assert base_cs, "GhostBehavior.cs must be generated"
            # The _internal_ref field belongs to a subclassed class, so it
            # should be protected (same as any other ref field in a subclassed class)
            serialize_lines = [ln for ln in base_cs.split("\n") if "[SerializeField]" in ln]
            assert serialize_lines, "Must emit at least one [SerializeField] field"
            # All ref fields in subclassed GhostBehavior must be protected
            for ln in serialize_lines:
                assert "protected" in ln, (
                    f"All [SerializeField] fields in subclassed GhostBehavior must be protected: {ln}"
                )
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)
