"""Contract tests for translator fixes: static field leak, UPPER_CASE constants,
pass stripping, docstring stripping, forward reference resolution, and Pacman
full-project translation.

These tests derive from Unity/C# conventions, NOT from implementation details.
"""

from __future__ import annotations

import textwrap

import pytest

from src.translator.python_parser import PyFile, PyClass, PyField, PyMethod
from src.translator.python_to_csharp import translate, translate_file
from src.translator.project_translator import translate_project
from src.gates.structural_gate import validate_csharp


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


def _make_plain_class(
    class_name: str,
    fields: list[PyField],
    methods: list[PyMethod] | None = None,
) -> PyFile:
    """Build a minimal PyFile with one plain (non-MonoBehaviour) class."""
    return PyFile(
        classes=[
            PyClass(
                name=class_name,
                fields=fields,
                methods=methods or [],
            )
        ]
    )


def _translate(parsed: PyFile, **kwargs) -> str:
    return translate(parsed, unity_version=5, input_system="legacy", **kwargs)


# ===========================================================================
# 1. No static field leak on instance fields
# ===========================================================================

class TestNoStaticFieldLeak:
    """Instance fields (snake_case or camelCase) must NOT get 'static' modifier.

    Unity convention: only UPPER_CASE class-level constants are static.
    A field like `speed: float = 8.0` in a MonoBehaviour is a serialized
    instance field, not a static one.
    """

    def test_instance_field_not_static(self):
        """speed: float = 8.0 -> 'public float speed = ...' with no 'static'."""
        parsed = _make_monobehaviour(
            "PlayerMovement",
            fields=[
                PyField(name="speed", type_annotation="float", default_value="8.0", is_class_level=False),
            ],
        )
        cs = _translate(parsed)
        # Must contain the field declaration
        assert "float speed" in cs
        # Must NOT contain 'static float speed'
        assert "static float speed" not in cs

    def test_multiple_instance_fields_not_static(self):
        """Multiple instance fields should all be non-static."""
        parsed = _make_monobehaviour(
            "Enemy",
            fields=[
                PyField(name="health", type_annotation="int", default_value="100", is_class_level=False),
                PyField(name="move_speed", type_annotation="float", default_value="3.5", is_class_level=False),
                PyField(name="is_alive", type_annotation="bool", default_value="True", is_class_level=False),
            ],
        )
        cs = _translate(parsed)
        assert "static int health" not in cs
        assert "static float moveSpeed" not in cs
        assert "static bool isAlive" not in cs

    def test_class_level_lowercase_field_not_static(self):
        """Even class-level fields that are NOT UPPER_CASE should not be static."""
        parsed = _make_monobehaviour(
            "Config",
            fields=[
                PyField(name="default_speed", type_annotation="float", default_value="5.0", is_class_level=True),
            ],
        )
        cs = _translate(parsed)
        assert "static float defaultSpeed" not in cs


# ===========================================================================
# 2. UPPER_CASE constants ARE static
# ===========================================================================

class TestUpperCaseConstantsStatic:
    """UPPER_CASE class-level fields should be emitted as public static."""

    def test_upper_case_is_static(self):
        """PACMAN_LAYER: int = 7 -> 'public static int PACMAN_LAYER = 7;'"""
        parsed = _make_monobehaviour(
            "GameSettings",
            fields=[
                PyField(name="PACMAN_LAYER", type_annotation="int", default_value="7", is_class_level=True),
            ],
        )
        cs = _translate(parsed)
        assert "public static int PACMAN_LAYER" in cs

    def test_upper_case_preserves_name(self):
        """UPPER_CASE name is not converted to camelCase."""
        parsed = _make_monobehaviour(
            "GameSettings",
            fields=[
                PyField(name="MAX_SPEED", type_annotation="float", default_value="10.0", is_class_level=True),
            ],
        )
        cs = _translate(parsed)
        assert "MAX_SPEED" in cs
        # Should NOT be converted to maxSpeed
        assert "maxSpeed" not in cs

    def test_plain_class_upper_case_static(self):
        """UPPER_CASE in plain classes also static."""
        parsed = _make_plain_class(
            "Constants",
            fields=[
                PyField(name="TILE_SIZE", type_annotation="int", default_value="16", is_class_level=True),
            ],
        )
        cs = _translate(parsed)
        assert "public static int TILE_SIZE" in cs


# ===========================================================================
# 3. pass statement stripped
# ===========================================================================

class TestPassStripped:
    """Python 'pass' must not appear as 'pass;' in C# output."""

    def test_pass_only_body(self):
        """A method with only 'pass' should produce an empty body, not 'pass;'."""
        parsed = _make_monobehaviour(
            "Stub",
            fields=[],
            methods=[
                PyMethod(name="on_enable", body_source="pass", is_lifecycle=True),
            ],
        )
        cs = _translate(parsed)
        assert "pass;" not in cs

    def test_pass_in_conditional(self):
        """'pass' inside a branch should not leak into C#."""
        body = textwrap.dedent("""\
            if self.active:
                pass
            else:
                self.speed = 0""")
        parsed = _make_monobehaviour(
            "Toggle",
            fields=[
                PyField(name="active", type_annotation="bool", default_value="True"),
                PyField(name="speed", type_annotation="float", default_value="5.0"),
            ],
            methods=[
                PyMethod(name="update", body_source=body, is_lifecycle=True),
            ],
        )
        cs = _translate(parsed)
        assert "pass;" not in cs


# ===========================================================================
# 4. Docstring stripped
# ===========================================================================

class TestDocstringStripped:
    """Triple-quoted docstrings must not appear in C# output."""

    def test_single_line_docstring(self):
        """'''Move the player.''' should not appear in output."""
        body = '"""Move the player."""\nself.speed = 5'
        parsed = _make_monobehaviour(
            "Player",
            fields=[
                PyField(name="speed", type_annotation="float", default_value="0"),
            ],
            methods=[
                PyMethod(name="start", body_source=body, is_lifecycle=True),
            ],
        )
        cs = _translate(parsed)
        assert "Move the player" not in cs
        assert '"""' not in cs

    def test_multiline_docstring(self):
        """Multi-line docstrings should be completely stripped."""
        body = '"""Handle movement.\n\nThis is a long docstring\nwith multiple lines."""\nself.speed = 10'
        parsed = _make_monobehaviour(
            "Mover",
            fields=[
                PyField(name="speed", type_annotation="float", default_value="0"),
            ],
            methods=[
                PyMethod(name="start", body_source=body, is_lifecycle=True),
            ],
        )
        cs = _translate(parsed)
        assert "Handle movement" not in cs
        assert "long docstring" not in cs
        assert '"""' not in cs


# ===========================================================================
# 5. Forward reference type resolved
# ===========================================================================

class TestForwardReferenceResolved:
    """Forward reference types like 'MyClass | None' (quoted) must resolve
    to C# nullable types like MyClass?, not literal quote strings.
    """

    def test_quoted_optional_resolves(self):
        """'GameManager | None' -> GameManager?"""
        parsed = _make_monobehaviour(
            "Player",
            fields=[
                PyField(name="manager", type_annotation="'GameManager | None'"),
            ],
        )
        cs = _translate(parsed)
        assert "GameManager?" in cs or "GameManager " in cs
        # Must NOT contain the literal quoted string
        assert "'GameManager | None'" not in cs
        assert '"GameManager | None"' not in cs

    def test_quoted_bare_type_resolves(self):
        """'Ghost' -> Ghost (strip quotes)."""
        parsed = _make_monobehaviour(
            "Pacman",
            fields=[
                PyField(name="target", type_annotation="'Ghost'"),
            ],
        )
        cs = _translate(parsed)
        # The type should be Ghost, not 'Ghost'
        assert "Ghost " in cs or "Ghost?" in cs
        assert "'Ghost'" not in cs

    def test_type_mapper_strips_quotes(self):
        """TypeMapper.python_to_csharp should strip forward reference quotes."""
        from src.translator.type_mapper import TypeMapper
        mapper = TypeMapper()
        assert mapper.python_to_csharp("'GameManager | None'") == "GameManager?"
        assert mapper.python_to_csharp("'Ghost'") == "Ghost"


# ===========================================================================
# 6. Re-translate Pacman — full project structural gate
# ===========================================================================

class TestPacmanFullTranslation:
    """Translate the entire Pacman project and run structural gate validation."""

    def test_translate_pacman_project(self):
        """translate_project on pacman_python/ should produce valid C#."""
        results = translate_project(
            "examples/pacman/pacman_python/",
            input_system="legacy",
            unity_version=5,
        )
        # Filter out non-C# results (like _required_packages.json)
        cs_files = {k: v for k, v in results.items() if k.endswith(".cs")}

        # Should have multiple C# files
        assert len(cs_files) >= 10, f"Expected >= 10 C# files, got {len(cs_files)}: {list(cs_files.keys())}"

        # Run structural gate on each
        pass_count = 0
        fail_details = []
        for filename, code in cs_files.items():
            result = validate_csharp(code)
            if result.valid:
                pass_count += 1
            else:
                fail_details.append(f"{filename}: {result.errors[:3]}")

        total = len(cs_files)
        # Contract: at least 14 out of 15 must pass structural gate
        threshold = min(14, total - 1)  # At most 1 failure allowed
        assert pass_count >= threshold, (
            f"Structural gate: {pass_count}/{total} passed (need >= {threshold}).\n"
            f"Failures:\n" + "\n".join(fail_details)
        )

    def test_pacman_no_pass_semicolons(self):
        """No 'pass;' should appear in any translated Pacman C# file."""
        results = translate_project(
            "examples/pacman/pacman_python/",
            input_system="legacy",
            unity_version=5,
        )
        for filename, code in results.items():
            if filename.endswith(".cs"):
                assert "pass;" not in code, f"'pass;' found in {filename}"

    def test_pacman_no_docstrings(self):
        """No triple-quoted docstrings should appear in any Pacman C# output."""
        results = translate_project(
            "examples/pacman/pacman_python/",
            input_system="legacy",
            unity_version=5,
        )
        for filename, code in results.items():
            if filename.endswith(".cs"):
                assert '"""' not in code, f'Triple-quote docstring found in {filename}'
                assert "'''" not in code, f"Triple-quote docstring found in {filename}"

    def test_pacman_no_static_leak_on_instance_fields(self):
        """Instance fields in Pacman classes must not have 'static' modifier."""
        results = translate_project(
            "examples/pacman/pacman_python/",
            input_system="legacy",
            unity_version=5,
        )
        for filename, code in results.items():
            if not filename.endswith(".cs"):
                continue
            for line in code.split("\n"):
                stripped = line.strip()
                # If a line declares a public static field, its name must be UPPER_CASE
                if stripped.startswith("public static") and not stripped.startswith("public static void") \
                        and not stripped.startswith("public static int ") and "(" in stripped:
                    continue  # skip method declarations
                import re
                m = re.match(r"public static \w+ (\w+)", stripped)
                if m:
                    field_name = m.group(1)
                    # Static fields must be UPPER_CASE (constants), singleton 'Instance',
                    # or method names (PascalCase with parens)
                    # Allow PascalCase for static methods/properties
                    singleton_names = {"Instance", "instance"}
                    if not field_name.isupper() and field_name not in singleton_names and "(" not in stripped:
                        # Check it's not a method (methods have parens on the line)
                        assert False, (
                            f"Non-UPPER_CASE field '{field_name}' is declared static in {filename}: {stripped}"
                        )
