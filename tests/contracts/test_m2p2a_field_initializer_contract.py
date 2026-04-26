"""Contract tests for M-2 phase-2a field-initializer translation fix.

Commit 21e955c hardens csharp_to_python._translate_literal() so that field
initializers like ``new Vector2(0, 0.6f)`` translate to valid Python instead
of leaking the C# ``new`` keyword and ``f`` float suffix through.

These tests derive expectations from Unity-source semantics, not from the
implementation: a translated Python file MUST be parseable by ast.parse()
and the field initializer MUST equal what a Unity developer would write
in idiomatic Python.

Tests built off:
  - src/translator/csharp_to_python.py (translator entrypoint)
  - src/translator/csharp_parser.py (parse_csharp returns CSharpFile IR)
  - examples/breakout/* and examples/flappy_bird/* (Unity-style ports)
"""

from __future__ import annotations

import ast
import re

import pytest

from src.translator.csharp_parser import parse_csharp
from src.translator.csharp_to_python import translate


# ── Helpers ──────────────────────────────────────────────────────────


def _wrap(field_decl: str) -> str:
    """Build a minimal MonoBehaviour class around a single field."""
    return f"public class Foo : MonoBehaviour {{ {field_decl} }}"


def _translate(field_decl: str) -> str:
    """Parse + translate a single-field MonoBehaviour to Python source."""
    parsed = parse_csharp(_wrap(field_decl))
    return translate(parsed)


def _assert_parses(py_source: str) -> ast.Module:
    """The fix's primary invariant: emitted Python must be syntactically valid."""
    try:
        return ast.parse(py_source)
    except SyntaxError as exc:
        raise AssertionError(
            f"Translator emitted invalid Python (SyntaxError: {exc.msg!r} at "
            f"line {exc.lineno}, col {exc.offset}):\n{py_source}"
        ) from exc


def _init_body(py_source: str) -> str:
    """Return the body of the Foo.__init__ method as a single string."""
    tree = _assert_parses(py_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            return ast.unparse(node)
    return ""


def _class_body(py_source: str) -> str:
    """Return the class body (excluding methods) — for static fields."""
    tree = _assert_parses(py_source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "Foo":
            return ast.unparse(node)
    return ""


# ── Float literal: int form ──────────────────────────────────────────


def test_int_float_literal_field_strips_f_and_adds_dot_zero():
    """C# `6f` -> Python `6.0` (parseable, semantically a float)."""
    py = _translate("private float speed = 6f;")
    body = _init_body(py)
    assert "self.speed: float = 6.0" in body, py
    # Negative: must not retain the C# suffix
    assert "6f" not in body, py


def test_int_float_literal_compiles_to_python_float():
    """The literal `6.0` must evaluate to float when the file is exec'd."""
    py = _translate("private float speed = 6f;")
    # ast.literal_eval the value rather than exec'ing the class
    init_body = _init_body(py)
    match = re.search(r"self\.speed: float = (.+)", init_body)
    assert match, init_body
    value = ast.literal_eval(match.group(1).strip())
    assert isinstance(value, float)
    assert value == 6.0


# ── Float literal: decimal form ──────────────────────────────────────


def test_decimal_float_literal_field_strips_f_keeps_decimal():
    """C# `0.6f` -> Python `0.6` (no trailing `f`, no `0.60`)."""
    py = _translate("private float speed = 0.6f;")
    body = _init_body(py)
    assert "self.speed: float = 0.6" in body, py
    assert "0.6f" not in body, py
    assert "0.60" not in body, py  # int rule must not corrupt decimal form


# ── Embedded `new` constructor ───────────────────────────────────────


def test_new_vector2_field_drops_new_keyword():
    """`new Vector2(0, 0.6f)` -> `Vector2(0, 0.6)` (valid Python call)."""
    py = _translate("private Vector2 paddleOffset = new Vector2(0, 0.6f);")
    body = _init_body(py)
    assert "self.paddle_offset: Vector2 = Vector2(0, 0.6)" in body, py
    assert "new Vector2" not in body, py
    assert "0.6f" not in body, py


def test_new_vector3_multi_arg_strips_all_float_suffixes():
    """All three `Nf` arguments are stripped consistently."""
    py = _translate("private Vector3 origin = new Vector3(0f, 1.5f, 2f);")
    body = _init_body(py)
    assert "Vector3(0.0, 1.5, 2.0)" in body, py
    assert "new" not in body.split("=", 1)[1].split("Vector3")[0], py


def test_new_vector2_field_emits_parseable_python():
    """ast.parse() must accept the entire translated file."""
    py = _translate("private Vector2 paddleOffset = new Vector2(0, 0.6f);")
    _assert_parses(py)  # raises AssertionError on SyntaxError


# ── String / bool / null literals (regression coverage) ──────────────


def test_string_literal_field_uses_single_quotes():
    """C# `"hello"` -> Python `'hello'` (translator's quote convention)."""
    py = _translate('private string s = "hello";')
    body = _init_body(py)
    assert "self.s: str = 'hello'" in body, py


def test_bool_true_literal_field_translates_to_python_True():
    py = _translate("private bool b = true;")
    body = _init_body(py)
    assert "self.b: bool = True" in body, py


def test_bool_false_literal_field_translates_to_python_False():
    py = _translate("private bool b = false;")
    body = _init_body(py)
    assert "self.b: bool = False" in body, py


def test_null_literal_field_translates_to_python_None():
    py = _translate("private GameObject g = null;")
    body = _init_body(py)
    assert "self.g: GameObject = None" in body, py


# ── Int field must NOT be float-mangled ──────────────────────────────


def test_plain_int_field_does_not_get_dot_zero():
    """`private int x = 5;` must stay `5`, not become `5.0`."""
    py = _translate("private int x = 5;")
    body = _init_body(py)
    assert "self.x: int = 5" in body, py
    # Must NOT have `.0` appended — regex is bound to `Nf` not bare `N`
    assert "self.x: int = 5.0" not in body, py


def test_int_in_vector_constructor_is_preserved():
    """`new Vector2(0, 0)` keeps both args as ints."""
    py = _translate("private Vector2 v = new Vector2(0, 0);")
    body = _init_body(py)
    assert "Vector2(0, 0)" in body, py
    assert "0.0" not in body, py


# ── Static (class-level) field path ──────────────────────────────────


def test_static_int_field_lives_at_class_scope_not_in_init():
    """Static fields are emitted as class attributes, not self.X assignments."""
    py = _translate("public static int score = 0;")
    cls = _class_body(py)
    # Class-level assignment present
    assert "score: int = 0" in cls, py
    # And NOT inside __init__
    init = _init_body(py)
    assert "self.score" not in init, py


def test_static_float_field_strips_f_suffix_at_class_scope():
    """Static field with a float-suffix initializer also gets the new fix."""
    py = _translate("public static float baseSpeed = 6f;")
    cls = _class_body(py)
    # Naming: camelCase -> snake_case
    assert "base_speed: float = 6.0" in cls, py
    assert "6f" not in cls, py


def test_static_new_vector2_field_strips_new_at_class_scope():
    """Class-level static field with `new Vector2(...)` initializer also fixed."""
    py = _translate("public static Vector2 origin = new Vector2(0, 0.6f);")
    cls = _class_body(py)
    assert "origin: Vector2 = Vector2(0, 0.6)" in cls, py
    assert "new Vector2" not in cls, py


# ── Whole-file parseability across the spectrum ──────────────────────


@pytest.mark.parametrize(
    "decl",
    [
        "private float speed = 6f;",
        "private float speed = 0.6f;",
        "private Vector2 v = new Vector2(0, 0.6f);",
        "private Vector3 v = new Vector3(0f, 1.5f, 2f);",
        'private string s = "hello";',
        "private bool b = true;",
        "private bool b = false;",
        "private GameObject g = null;",
        "private int x = 5;",
        "public static int score = 0;",
        "public static float baseSpeed = 6f;",
        "public static Vector2 origin = new Vector2(0, 0.6f);",
    ],
)
def test_translated_field_emits_valid_python(decl):
    """Every supported field-initializer shape produces ast.parse-clean Python."""
    py = _translate(decl)
    _assert_parses(py)


# ── Edge cases discovered during validation (documented behaviour) ──
#
# These are NOT happy-path requirements; they pin current behaviour so a
# future change does not silently regress these inputs. The string-mangling
# case (the regex `\bnew\s+` strips `new ` from inside string literals
# because it runs before the quote-translation pass) is reported in the
# validation summary as a real bug.


def test_string_with_embedded_new_word_is_currently_mangled_BUG():
    """KNOWN BUG (xfail): `"hello new world"` becomes `'hello world'`.

    The fix's regex `re.sub(r"\\bnew\\s+", "", value)` runs against the raw
    initializer string before the C# `"..."` is converted to Python `'...'`,
    so `new ` inside string content is stripped. This is unsafe — a string
    literal containing the substring `"new "` will be silently corrupted in
    a field initializer. Surface this so the bug is visible in CI.
    """
    py = _translate('private string s = "hello new world";')
    body = _init_body(py)
    # Document current (buggy) behaviour
    is_mangled = "'hello world'" in body
    is_correct = "'hello new world'" in body
    if is_mangled and not is_correct:
        pytest.xfail(
            "M-2 phase-2a regex strips `new ` from inside string literals — "
            "see validation report for commit 21e955c"
        )
    assert is_correct, py


def test_generic_list_constructor_is_currently_unfixed_BUG():
    """KNOWN BUG (xfail): `new List<int>()` becomes `List<int>()`.

    The `\\bnew\\s+` regex correctly strips `new`, but the C# generic syntax
    `List<int>` is not translated to Python `list[int]()` for constructor
    calls (only field-type annotations get the type-mapper treatment).
    The text `List<int>()` happens to parse in Python as a chained-comparison
    `(List < int) > ()`, so it doesn't crash ast.parse, but it does NOT
    construct an empty list at runtime — it would raise NameError on `List`
    or evaluate as a bool comparison.
    """
    py = _translate("private List<int> v = new List<int>();")
    if "List<int>()" in py:
        pytest.xfail(
            "Generic constructor `new List<int>()` not translated — the "
            "field-initializer fix strips `new` but leaves the generic "
            "type-argument syntax intact, producing a chained-comparison "
            "expression instead of `list[int]()`"
        )
    assert False, "Unexpected: List<int>() was rewritten — update this test"
