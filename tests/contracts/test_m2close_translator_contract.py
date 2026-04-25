"""Contract tests locking in the three M-2 close fixes in src/translator/csharp_to_python.py.

The fixes (commit 0078c16) collectively pushed the 37-pair roundtrip corpus from
62.2% -> 89.2% compile and 37.8% -> 59.5% AST equivalence:

  Fix 1: variable-decl matcher accepts ANY single-identifier C# type (not just
         the previous int/float/Vector2/... allowlist), so user-defined types
         like `PlayerInputHandler player = ...` no longer leak the type prefix
         into the Python output.

  Fix 2: `_translate_expression` strips C# casts of the form `(PascalType)expr`
         so e.g. `(Vector2)pos` -> `pos`.  The regex deliberately requires
         PascalCase + an identifier-start follower so legitimate
         parenthesized arithmetic like `(a + b) * c` is preserved.

  Fix 3: `&&` -> ` and `, `||` -> ` or ` in `_translate_expression`.

These tests run real C# fragments through `parse_csharp` + `translate`, assert
the relevant substrings appear / are absent, and finish with `ast.parse` on the
generated Python to prove the output is parseable — which is the whole point of
the M-2 close.

Test agent does not touch src/.
"""

from __future__ import annotations

import ast
import re
import textwrap

import pytest

from src.translator.csharp_parser import parse_csharp
from src.translator.csharp_to_python import translate, _translate_expression


def _wrap(method_body: str, *, class_name: str = "Foo", base: str = "MonoBehaviour") -> str:
    """Wrap a C# method body in a minimal class so parse_csharp can consume it."""
    body = textwrap.indent(method_body.strip(), "        ")
    return (
        f"using UnityEngine;\n"
        f"public class {class_name} : {base} {{\n"
        f"    void Run() {{\n"
        f"{body}\n"
        f"    }}\n"
        f"}}\n"
    )


def _translate(src: str) -> str:
    return translate(parse_csharp(src))


def _assert_parses(py_src: str) -> None:
    """The generated Python must be syntactically valid — that's the contract."""
    try:
        ast.parse(py_src)
    except SyntaxError as e:  # pragma: no cover — failure path
        pytest.fail(f"Generated Python failed to parse: {e}\n--- source ---\n{py_src}")


def _run_body(py_src: str) -> str:
    """Return the body of the Run method (post-translation) as a string slice.

    The generated output uses `def run(self):` per the snake_case convention.
    """
    m = re.search(r"def run\(self\):\n([\s\S]*)$", py_src)
    return m.group(1) if m else py_src


# ---------------------------------------------------------------------------
# Fix 1 — variable-decl matcher accepts any type identifier
# ---------------------------------------------------------------------------


class TestFix1VarDeclAnyType:
    """`Type name = value;` translates to `name = value` regardless of Type."""

    def test_user_defined_type_decl_drops_type_prefix(self) -> None:
        src = _wrap("PlayerInputHandler player = owner;")
        out = _translate(src)
        body = _run_body(out)

        # The bug we are guarding: the C# type identifier must NOT leak.
        assert "PlayerInputHandler player" not in body, (
            f"Expected `PlayerInputHandler` prefix to be dropped from decl;\n{out}"
        )
        assert "player = owner" in body, f"Expected clean assignment; got:\n{out}"
        _assert_parses(out)

    def test_arbitrary_user_type_with_int_init(self) -> None:
        src = _wrap("MyCustomType x = 5;")
        out = _translate(src)
        body = _run_body(out)
        assert "MyCustomType x" not in body
        assert "x = 5" in body
        _assert_parses(out)

    def test_legacy_int_decl_still_works(self) -> None:
        src = _wrap("int n = 5;")
        out = _translate(src)
        body = _run_body(out)
        assert "int n" not in body
        assert "n = 5" in body
        _assert_parses(out)

    def test_legacy_vector2_decl_still_works(self) -> None:
        src = _wrap("Vector2 v = somewhere;")
        out = _translate(src)
        body = _run_body(out)
        assert "Vector2 v" not in body
        assert "v = somewhere" in body
        _assert_parses(out)

    def test_dotted_assignment_is_not_misread_as_decl(self) -> None:
        """`obj.field = 5` — `obj.field` is a single token with a dot, so the
        decl regex (`(\\w+)\\s+(\\w+)\\s*=`) shouldn't match. The assignment
        branch should kick in instead."""
        # Pre-create the binding so a synthetic "obj" + ".field = 5" round-trips.
        src = _wrap("var obj = self;\nobj.field = 5;")
        out = _translate(src)
        body = _run_body(out)
        # The dotted target must survive the round-trip (no decl misfire that
        # would turn `obj.field = 5` into `field = 5` or similar).
        assert "obj.field = 5" in body, f"Dotted assignment should survive:\n{out}"
        _assert_parses(out)


# ---------------------------------------------------------------------------
# Fix 2 — C# cast strip `(PascalType)expr` -> `expr`
# ---------------------------------------------------------------------------


class TestFix2CastStrip:
    """`(Vector2)pos` -> `pos`. PascalCase + identifier-start follower required."""

    def test_vector2_cast_stripped_in_method_body(self) -> None:
        src = _wrap("var p = (Vector2)transform.position;")
        out = _translate(src)
        body = _run_body(out)
        assert "(Vector2)" not in body, f"Cast should be stripped:\n{out}"
        # And the inner expression must survive (post the
        # transform/.gameObject rewrites).
        assert ".position" in body
        assert "transform" in body  # rewritten to self.transform
        _assert_parses(out)

    def test_user_type_cast_stripped(self) -> None:
        src = _wrap("var x = (MyType)obj;")
        out = _translate(src)
        body = _run_body(out)
        assert "(MyType)" not in body
        # Note: pre-rewrite, the line is `var x = (MyType)obj;`. After cast
        # strip, it becomes `var x = obj;` which then becomes `x = obj`.
        assert "x = obj" in body
        _assert_parses(out)

    def test_lowercase_parens_arithmetic_NOT_stripped(self) -> None:
        """`(a + b) * c` — `a` is lowercase, so the regex must not match.

        We exercise `_translate_expression` directly because the surrounding
        statement-level translator would route this through other branches.
        """
        # Make a dummy class context (the function only uses the scoped class
        # for some downstream rewrites — here we don't touch members).
        from src.translator.csharp_parser import CSharpClass  # local import

        cls = CSharpClass(name="Tmp")
        out = _translate_expression("(a + b) * c", cls)
        # The opening paren on `(a` must survive — it's arithmetic, not a cast.
        assert "(a + b)" in out, (
            f"Arithmetic parens must NOT be stripped: got {out!r}"
        )

    def test_pascal_cast_followed_by_operator_NOT_stripped(self) -> None:
        """Lookahead requires `[A-Za-z_(]` after the close-paren. An operator
        like `+` must therefore leave the parens alone."""
        from src.translator.csharp_parser import CSharpClass

        cls = CSharpClass(name="Tmp")
        out = _translate_expression("(MyType) + 5", cls)
        # `(MyType)` followed by ` +` — the lookahead fails, no strip.
        assert "(MyType)" in out, (
            f"Cast NOT followed by identifier-start should be left alone; got {out!r}"
        )

    def test_cast_followed_by_open_paren_is_stripped(self) -> None:
        """Lookahead allows `(` as a follower — `(Vector2)(expr)` strips."""
        from src.translator.csharp_parser import CSharpClass

        cls = CSharpClass(name="Tmp")
        out = _translate_expression("(Vector2)(some_func())", cls)
        # `(Vector2)` is stripped; the inner `(some_func())` survives.
        assert "(Vector2)" not in out
        assert "some_func()" in out


# ---------------------------------------------------------------------------
# Fix 3 — &&/|| -> Python and/or
# ---------------------------------------------------------------------------


class TestFix3LogicalOperators:
    """`&&` -> ` and `, `||` -> ` or ` (with leading/trailing spaces baked in)."""

    def test_double_amp_in_if_becomes_and(self) -> None:
        src = _wrap("if (a && b) {\n    return;\n}")
        out = _translate(src)
        # The `if` translator routes through `_extract_condition`, which has
        # ITS OWN replacement (also covered) — but the contract is the same:
        # no `&&` survives.
        assert "&&" not in out, f"`&&` should be gone:\n{out}"
        assert " and " in out, f"Expected ` and ` substitution; got:\n{out}"
        _assert_parses(out)

    def test_double_pipe_in_if_becomes_or(self) -> None:
        src = _wrap("if (a || b) {\n    return;\n}")
        out = _translate(src)
        assert "||" not in out
        assert " or " in out
        _assert_parses(out)

    def test_double_amp_in_expression_context(self) -> None:
        """`bool x = a && b;` exercises `_translate_expression` directly,
        which is where Fix 3 lives (separate from the `if`-condition path)."""
        src = _wrap("bool x = a && b;")
        out = _translate(src)
        assert "&&" not in out
        assert " and " in out
        _assert_parses(out)

    def test_combined_and_or_in_assignment(self) -> None:
        src = _wrap("var z = a && b || c;")
        out = _translate(src)
        body = _run_body(out)
        assert "&&" not in body
        assert "||" not in body
        # Both substitutions land — order is preserved.
        assert " and " in body
        assert " or " in body
        _assert_parses(out)

    def test_logical_in_complex_condition(self) -> None:
        src = _wrap("if (player.alive && enemy.visible || timer > 0) {\n    return;\n}")
        out = _translate(src)
        assert "&&" not in out
        assert "||" not in out
        _assert_parses(out)

    def test_known_weak_point_string_literal_mangling(self) -> None:
        """KNOWN WEAK POINT: the Fix-3 `expr.replace("&&", ...)` is unconditional,
        so `&&` inside a string literal IS rewritten — `"hello && world"` becomes
        `'hello  and  world'`. This is documented in the commit and out of scope
        for the M-2 close. This test pins the CURRENT behavior so a future fix
        is forced to update both source and expectations together."""
        src = _wrap('string s = "hello && world";')
        out = _translate(src)
        body = _run_body(out)
        # Pin current (broken) behavior: the && inside the string gets
        # substituted. If a future fix repairs this, this assertion will fail
        # and the developer has to consciously update both.
        assert "and" in body, (
            "Expected current weak-point behavior (string-literal mangling) "
            f"to be observable; output:\n{out}"
        )
        # And the output STILL parses — that's the only thing we actually
        # promise downstream.
        _assert_parses(out)


# ---------------------------------------------------------------------------
# End-to-end: a fragment combining all three fixes parses cleanly.
# ---------------------------------------------------------------------------


def test_combined_fixes_parse_cleanly() -> None:
    """A single method body exercising all three fixes round-trips to
    parseable Python — the integration-y end of the contract."""
    src = _wrap(
        "PlayerInputHandler player = (PlayerInputHandler)owner;\n"
        "Vector2 pos = (Vector2)transform.position;\n"
        "if (player.alive && pos.x > 0 || override_) {\n"
        "    return;\n"
        "}"
    )
    out = _translate(src)
    body = _run_body(out)

    # Fix 1 — type prefix dropped
    assert "PlayerInputHandler player" not in body
    # Fix 2 — both casts gone
    assert "(PlayerInputHandler)" not in body
    assert "(Vector2)" not in body
    # Fix 3 — operators substituted
    assert "&&" not in out
    assert "||" not in out
    # Parseable Python
    _assert_parses(out)
