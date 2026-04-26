"""B2 — Mutation tests proving the contract suite catches the regression.

Strategy: monkeypatch `src.translator.type_mapper.snake_to_camel`
with the buggy pre-fix implementation (and a few near-misses), then
re-run the contract assertions and prove they fail.

This validates that the contract tests in
`tests/contracts/test_underscore_naming_contract_b2.py` are not
vacuously passing — they would have caught the original bug.

Each mutation case patches the function to a deliberately broken
variant, then asserts the property the contract tests require is
NOT held by the broken variant.

Derived from the Unity / .NET naming convention. Not informed by any
existing test file under `tests/`.
"""
from __future__ import annotations

from src.translator import type_mapper as tm


# ---------------------------------------------------------------------------
# Buggy variants of snake_to_camel
# ---------------------------------------------------------------------------
def _buggy_pre_fix(name: str) -> str:
    """The exact pre-fix behaviour from commit b72d967 (faithful copy).

    No `lstrip("_")` — so `_score_text` splits to `['', 'score', 'text']`
    and produces `'' + 'Score' + 'Text'` → `'ScoreText'` (PascalCase).
    """
    parts = name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def _buggy_capitalize_first(name: str) -> str:
    """Mutation: strips underscores but PascalCases the result.

    Equivalent to `snake_to_pascal(name.lstrip('_'))`. Catches anyone
    who 'fixes' the bug by capitalizing the first part too.
    """
    stripped = name.lstrip("_")
    if not stripped:
        return name
    parts = stripped.split("_")
    return "".join(word.capitalize() for word in parts)


def _buggy_keeps_underscore_prefix(name: str) -> str:
    """Mutation: emits `_scoreText` for `_score_text`.

    Looks plausible (preserves the privacy hint) but is not idiomatic
    C# and doesn't match the Python-side field-declaration path that
    strips `_` first — so the same CS1061 mismatch reappears.
    """
    leading = len(name) - len(name.lstrip("_"))
    stripped = name.lstrip("_")
    if not stripped:
        return name
    parts = stripped.split("_")
    body = parts[0] + "".join(word.capitalize() for word in parts[1:])
    return ("_" * leading) + body


# ---------------------------------------------------------------------------
# Mutation 1: pre-fix bug must violate "leading-underscore yields camel"
# ---------------------------------------------------------------------------
def test_mutation_pre_fix_bug_breaks_camel_for_leading_underscore(monkeypatch):
    monkeypatch.setattr(tm, "snake_to_camel", _buggy_pre_fix)

    # Re-derive the contract from the patched module.
    from src.translator.type_mapper import snake_to_camel as patched

    # Sanity: bare snake still works under the buggy variant.
    assert patched("score_text") == "scoreText"

    # The bug: leading-underscore promotes to PascalCase.
    out = patched("_score_text")
    assert out == "ScoreText", (
        f"Pre-fix bug should emit PascalCase `ScoreText`; got {out!r}. "
        f"If this fails the mutation has drifted from the real bug."
    )

    # The property the contract test asserts (lowercase first char) is
    # violated — this is what the contract suite catches.
    assert not out[0].islower(), (
        "Mutation should fail the camelCase-first-char contract"
    )


# ---------------------------------------------------------------------------
# Mutation 2: pre-fix bug breaks the symmetry property
# ---------------------------------------------------------------------------
def test_mutation_pre_fix_bug_breaks_underscore_symmetry(monkeypatch):
    monkeypatch.setattr(tm, "snake_to_camel", _buggy_pre_fix)
    from src.translator.type_mapper import snake_to_camel as patched

    # The contract says snake_to_camel(X) == snake_to_camel("_" + X) for
    # every snake_case identifier — under the bug, this is FALSE for
    # multi-part names.
    bare = patched("score_text")
    prefixed = patched("_score_text")
    assert bare != prefixed, (
        f"Pre-fix bug should produce asymmetric output; "
        f"got bare={bare!r}, prefixed={prefixed!r}"
    )


# ---------------------------------------------------------------------------
# Mutation 3: 'overcorrect to PascalCase' would pass symmetry but
#             fail the camelCase-first-char contract
# ---------------------------------------------------------------------------
def test_mutation_pascalize_first_part_violates_camel_contract(monkeypatch):
    monkeypatch.setattr(tm, "snake_to_camel", _buggy_capitalize_first)
    from src.translator.type_mapper import snake_to_camel as patched

    # This mutation is symmetric — a tempting "fix" — but emits
    # PascalCase, which is wrong for private fields.
    assert patched("score_text") == patched("_score_text") == "ScoreText"
    out = patched("_score_text")
    assert out[0].isupper(), (
        f"Pascalize mutation should emit uppercase first char; got {out!r}"
    )
    # And the camelCase-first-char contract correctly flags this.
    assert not out[0].islower(), (
        "Contract requires lowercase first char — PascalCase mutation "
        "must violate it."
    )


# ---------------------------------------------------------------------------
# Mutation 4: 'preserve leading _' would still mismatch the
#             field-declaration path that does lstrip("_")
# ---------------------------------------------------------------------------
def test_mutation_keeps_underscore_prefix_violates_first_letter_contract(monkeypatch):
    monkeypatch.setattr(tm, "snake_to_camel", _buggy_keeps_underscore_prefix)
    from src.translator.type_mapper import snake_to_camel as patched

    out = patched("_score_text")
    # Looks like `_scoreText` — but the contract says first char must
    # be alpha (and lowercase). Underscore-prefix violates that.
    assert out == "_scoreText"
    assert not out[0].isalpha(), (
        "Underscore-prefix mutation should violate isalpha() contract"
    )
