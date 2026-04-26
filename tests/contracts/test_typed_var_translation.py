"""Contract tests for Task 9: typed variable declaration translation.

Validates that Python typed annotations translate to correct C# declarations.
Derived from Unity/C# language spec, NOT from implementation details.
"""
from __future__ import annotations

import re
import textwrap
from pathlib import Path

import pytest

from src.translator.python_to_csharp import translate_file, translate
from src.translator.python_parser import parse_python_file


# ── Helpers ──────────────────────────────────────────────────────

def _translate_snippet(python_code: str) -> str:
    """Write a temp Python file and translate it, returning C# output."""
    import tempfile, os
    code = textwrap.dedent(python_code).strip()
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        f.flush()
        path = f.name
    try:
        return translate_file(path)
    finally:
        os.unlink(path)


# ── 1. Basic typed local: Vector2 ───────────────────────────────

class TestTypedLocalVector2:
    def test_vector2_typed_declaration(self):
        """pos: Vector2 = transform.position -> Vector2 pos = transform.position;"""
        cs = _translate_snippet("""
from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2

class Foo(MonoBehaviour):
    def update(self):
        pos: Vector2 = self.transform.position
        self.transform.position = pos
""")
        assert "Vector2 pos = transform.position;" in cs


# ── 2. Basic typed local: float ─────────────────────────────────

class TestTypedLocalFloat:
    def test_float_typed_declaration(self):
        """x: float = 5.0 -> float x = 5f;"""
        cs = _translate_snippet("""
from src.engine.core import MonoBehaviour

class Foo(MonoBehaviour):
    def update(self):
        x: float = 5.0
""")
        # Should declare as float, not var
        assert re.search(r"float\s+x\s*=\s*5\.?0?f;", cs), f"Expected 'float x = 5f;' or 'float x = 5.0f;' in:\n{cs}"


# ── 3. Nullable stripped: GameObject | None ──────────────────────

class TestNullableStripped:
    def test_nullable_union_stripped(self):
        """go: GameObject | None = ... -> GameObject go = ...;"""
        cs = _translate_snippet("""
from src.engine.core import MonoBehaviour, GameObject

class Foo(MonoBehaviour):
    def start(self):
        go: GameObject | None = GameObject.find("test")
""")
        # Should NOT contain " | None" or "| null"
        assert "| None" not in cs
        assert "| null" not in cs
        assert "GameObject" in cs
        # Should have a typed declaration
        assert re.search(r"GameObject\s+go\s*=", cs), f"Expected 'GameObject go = ...' in:\n{cs}"


# ── 4. self.field annotation stripped ────────────────────────────

class TestSelfFieldAnnotationStripped:
    def test_self_field_annotation_becomes_assignment(self):
        """self._timer: float = 0.0 in __init__ -> field declaration, not local typed var."""
        cs = _translate_snippet("""
from src.engine.core import MonoBehaviour

class Foo(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self._timer: float = 0.0
""")
        # The annotation should NOT appear in the method body as "float _timer ="
        # Instead it should be a field declared at class level
        # The C# body should NOT contain Python-style ": float" syntax
        assert ": float" not in cs, f"Python annotation leaked into C#:\n{cs}"


# ── 5. Mixed typed and untyped vars ─────────────────────────────

class TestMixedTypedUntyped:
    def test_both_typed_and_untyped_work(self):
        """Method with typed and untyped locals translates both correctly."""
        cs = _translate_snippet("""
from src.engine.core import MonoBehaviour

class Foo(MonoBehaviour):
    def update(self):
        x: int = 10
        y = 20
""")
        assert re.search(r"int\s+x\s*=\s*10;", cs), f"Typed 'int x = 10;' missing:\n{cs}"
        # y should also be declared (with var or int)
        assert re.search(r"(var|int)\s+y\s*=\s*20;", cs), f"Untyped 'y = 20' not declared:\n{cs}"


# ── 6. Declaration without assignment ────────────────────────────

class TestDeclarationWithoutAssignment:
    def test_type_only_declaration(self):
        """var: Type (no =) -> Type var;"""
        cs = _translate_snippet("""
from src.engine.core import MonoBehaviour, GameObject

class Foo(MonoBehaviour):
    def start(self):
        target: GameObject
""")
        assert re.search(r"GameObject\s+target;", cs), f"Expected 'GameObject target;' in:\n{cs}"


# ── 7. No Python-style annotations in Space Invaders output ─────

class TestSpaceInvadersPlayer:
    """Translate the real player.py and verify no Python annotations survive."""

    def test_no_python_annotations_in_output(self):
        player_path = Path("examples/space_invaders/space_invaders_python/player.py")
        if not player_path.exists():
            pytest.skip("Space Invaders player.py not found")
        cs = translate_file(str(player_path))
        # No Python-style "var: Type" should survive (look for ": Vector2", ": float", etc.)
        # But C# legitimately uses ":" in ternary, casts, base class — so be specific
        annotation_pattern = re.compile(r"\b\w+\s*:\s*(Vector[23]|float|int|bool|str|GameObject)\s*[=;]")
        python_annotations = annotation_pattern.findall(cs)
        # Filter: only flag if it looks like Python annotation, not C# syntax
        # In C#, "Type var = ..." is correct; "var: Type = ..." is wrong
        colon_annotations = re.findall(r"\b\w+\s*:\s*\w+\s*=", cs)
        assert len(colon_annotations) == 0, (
            f"Python-style annotations found in C# output: {colon_annotations}\n\nFull output:\n{cs}"
        )

    def test_typed_locals_use_csharp_syntax(self):
        """Typed locals in player.py should produce 'Type var =' not 'var var ='."""
        player_path = Path("examples/space_invaders/space_invaders_python/player.py")
        if not player_path.exists():
            pytest.skip("Space Invaders player.py not found")
        cs = translate_file(str(player_path))
        # The player has: position: Vector2 = self.transform.position
        # Should become: Vector2 position = transform.position;
        assert "Vector2 position = transform.position;" in cs, (
            f"Expected 'Vector2 position = transform.position;' in:\n{cs}"
        )


# ── 8. str type maps to string ───────────────────────────────────

class TestStrToString:
    def test_str_becomes_string(self):
        """name: str = 'hello' -> string name = \"hello\";"""
        cs = _translate_snippet("""
from src.engine.core import MonoBehaviour

class Foo(MonoBehaviour):
    def start(self):
        name: str = "hello"
""")
        assert re.search(r'string\s+name\s*=\s*"hello";', cs), f"Expected 'string name = \"hello\";' in:\n{cs}"


# ── 9. bool type ─────────────────────────────────────────────────

class TestBoolType:
    def test_bool_typed_declaration(self):
        """done: bool = False -> bool done = false;"""
        cs = _translate_snippet("""
from src.engine.core import MonoBehaviour

class Foo(MonoBehaviour):
    def start(self):
        done: bool = False
""")
        assert re.search(r"bool\s+done\s*=\s*false;", cs), f"Expected 'bool done = false;' in:\n{cs}"


# ── 10. Redeclared variable only assigned (no duplicate Type) ────

class TestRedeclaredVariable:
    def test_second_assignment_skips_type(self):
        """If a typed var is assigned again later, don't re-declare it."""
        cs = _translate_snippet("""
from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2

class Foo(MonoBehaviour):
    def update(self):
        pos: Vector2 = Vector2(0, 0)
        pos = Vector2(1, 1)
""")
        # First should be "Vector2 pos = ..."
        # Second should be "pos = ..." (no type prefix)
        lines = [l.strip() for l in cs.splitlines() if "pos" in l and "=" in l]
        typed_decls = [l for l in lines if re.match(r"Vector2\s+pos\s*=", l)]
        bare_assigns = [l for l in lines if re.match(r"pos\s*=", l)]
        assert len(typed_decls) == 1, f"Expected exactly 1 typed decl, got {typed_decls}"
        assert len(bare_assigns) == 1, f"Expected exactly 1 bare assign, got {bare_assigns}"
