"""B2 — Independent contract tests for `snake_to_camel` underscore handling.

Derived from Unity / .NET naming convention, NOT from inspecting the
implementation:

  * Public C# fields and properties: PascalCase.
  * Private C# fields: camelCase. The leading-underscore prefix
    (`_field`) is a Python privacy marker; in C# the equivalent of a
    "private" field is just camelCase with NO underscore.
    See: https://learn.microsoft.com/dotnet/standard/design-guidelines/capitalization-conventions
    See: https://learn.microsoft.com/dotnet/standard/design-guidelines/names-of-type-members

The translator's `snake_to_camel` is the single function that converts
Python identifiers to the C# camelCase form used at field-declaration
sites AND at attribute-access sites (`inst.<attr>`). Whatever name it
emits MUST match between those two call paths — otherwise the generated
C# fails to compile with CS1061 ("does not contain a definition for X").

The bug this guards against: `snake_to_camel("_score_text")` returning
`"ScoreText"` (PascalCase) instead of `"scoreText"` (camelCase) because
splitting `_score_text` on `_` yields `['', 'score', 'text']` and
`parts[0] + Capitalize(rest)` becomes `"" + "Score" + "Text"`. That bug
broke breakout's `GameManager.cs` because the field-declaration path
already did `lstrip("_")` first while the symbol-table path used the
raw function output, producing `inst.ScoreText` for a field named
`scoreText`.

These contracts are deliberately written without reading any existing
test in `tests/translator/`, `tests/contracts/`, or `tests/mutation/`.
They are derived from C# language behaviour.
"""
from __future__ import annotations

import pytest

from src.translator.type_mapper import snake_to_camel


# ---------------------------------------------------------------------------
# Contract 1: identity for already-camel/lower identifiers
# ---------------------------------------------------------------------------
def test_no_underscore_identifier_is_unchanged():
    """`foo` → `foo`. No underscore means no transformation needed."""
    assert snake_to_camel("foo") == "foo"


def test_simple_snake_becomes_camel():
    """`score_text` → `scoreText` — baseline behaviour."""
    assert snake_to_camel("score_text") == "scoreText"


def test_three_part_snake_becomes_camel():
    """`first_second_third` → `firstSecondThird`."""
    assert snake_to_camel("first_second_third") == "firstSecondThird"


# ---------------------------------------------------------------------------
# Contract 2: leading underscore must NOT promote to PascalCase
# ---------------------------------------------------------------------------
def test_single_leading_underscore_yields_camel_not_pascal():
    """`_score_text` → `scoreText`, NOT `ScoreText`.

    This is the exact regression covered by commit b72d967.
    PascalCase output here would surface as a CS1061 between the
    field declaration (which strips the leading `_`) and the
    `inst.<attr>` access path (which used the raw function output).
    """
    result = snake_to_camel("_score_text")
    assert result == "scoreText"
    assert result[0].islower(), (
        f"camelCase must start with a lowercase letter; got {result!r}"
    )


def test_single_leading_underscore_no_split_part():
    """`_foo` → `foo` — single-part name still drops the leading `_`."""
    assert snake_to_camel("_foo") == "foo"


def test_dunder_leading_underscores_stripped_to_camel():
    """`__foo_bar` → `fooBar`. Python dunder convention has no C#
    equivalent; treating `__` as part of the first segment would emit
    `FooBar` (PascalCase) — same class of bug as the single-underscore
    case."""
    result = snake_to_camel("__foo_bar")
    assert result == "fooBar"
    assert result[0].islower()


# ---------------------------------------------------------------------------
# Contract 3: identical output regardless of underscore prefix
#   (this is the symmetry property the symbol-table relied on)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "py_name",
    [
        "score_text",
        "lives_text",
        "status_text",
        "ball_speed",
        "current_powerup",
    ],
)
def test_underscore_prefix_does_not_change_camel_output(py_name: str):
    """For any snake_case identifier `X`, `snake_to_camel(X)` must equal
    `snake_to_camel("_" + X)`. This is the property the cross-instance
    `inst.<attr>` path needs: declaration and access must round-trip."""
    bare = snake_to_camel(py_name)
    prefixed = snake_to_camel("_" + py_name)
    assert bare == prefixed, (
        f"Underscore-prefix asymmetry for {py_name!r}: "
        f"bare={bare!r} vs prefixed={prefixed!r}"
    )


@pytest.mark.parametrize(
    "py_name",
    ["foo", "bar", "x", "ball"],
)
def test_underscore_prefix_does_not_change_single_part_camel_output(py_name: str):
    """Same symmetry property for single-part identifiers."""
    assert snake_to_camel(py_name) == snake_to_camel("_" + py_name)


# ---------------------------------------------------------------------------
# Contract 4: degenerate inputs do not crash and stay reasonable
# ---------------------------------------------------------------------------
def test_single_underscore_returns_underscore():
    """`_` → `_` (the discard-loop convention; documented in source)."""
    assert snake_to_camel("_") == "_"


def test_all_underscores_does_not_crash():
    """`___` is degenerate but must not raise an IndexError. Whatever
    the function returns, it must be a string and must not be empty —
    an empty identifier would produce broken C# code."""
    out = snake_to_camel("___")
    assert isinstance(out, str)
    assert out != ""


# ---------------------------------------------------------------------------
# Contract 5: result must always be a valid C# identifier start character
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "py_name",
    [
        "_score_text",
        "_lives_text",
        "_status_text",
        "__double_under",
        "_x",
        "_a_b_c_d",
        "_canvas",
        "_score",
    ],
)
def test_underscore_prefixed_result_is_valid_csharp_identifier_start(py_name: str):
    """A camelCase C# identifier emitted from a `_`-prefixed Python
    name must start with a letter (lowercase) — never an uppercase
    letter (that would be PascalCase, the wrong convention for private
    fields) and never an underscore (the original input shouldn't pass
    through unchanged)."""
    out = snake_to_camel(py_name)
    assert out, f"empty result for {py_name!r}"
    assert out[0].isalpha(), (
        f"Result {out!r} from {py_name!r} must start with a letter, "
        f"not {out[0]!r}"
    )
    assert out[0].islower(), (
        f"Result {out!r} from {py_name!r} must start lowercase "
        f"(camelCase convention)"
    )
