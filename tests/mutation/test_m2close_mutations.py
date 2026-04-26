"""Mutation tests proving the three M-2 close fixes are protected.

For each of the three fixes, we:

  1. Read `src/translator/csharp_to_python.py` as a string.
  2. Apply a string substitution that REVERTS that fix (or breaks it).
  3. Load the mutated source as a fresh module via importlib.
  4. Run a tiny C# fragment through the mutated translate() and assert the
     output now exhibits the bug — proving the contract test would catch a
     real regression.

Sentinel-string choices (why each is robust):

  - Mutation A: we insert an early return after the variable-decl regex match
    that re-imposes the old allowlist. The sentinel is the literal regex
    string `r"^(\\w+)\\s+(\\w+)\\s*=\\s*(.+)$"` — any reformatting that
    preserves the regex preserves the sentinel. We splice a guard block
    immediately AFTER the match groups are unpacked.

  - Mutation B: we replace the cast-strip line by its anchor — the regex
    `r"\\(([A-Z]\\w*)\\)\\s*(?=[A-Za-z_(])"`. Removing the whole `expr =
    re.sub(...)` line drops the cast strip entirely.

  - Mutation C: we replace the explicit double-replace expression
    `expr.replace("&&", " and ").replace("||", " or ")` with a no-op
    `expr.replace("__never__", "__never__")`. The sentinel is the unique
    `"&&", " and "` chain — no other call in the file uses both `&&` and
    ` and ` in a single replace chain.

The mutated module is loaded into a tmp directory; the real
`src/translator/csharp_to_python.py` is never modified.

Test agent does not touch src/.
"""

from __future__ import annotations

import importlib.util
import shutil
import sys
import textwrap
import types
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC_FILE = ROOT / "src" / "translator" / "csharp_to_python.py"


# Sentinels — literal substrings of the real file. Each test asserts the
# substring exists before mutating, so a rewording of the source forces the
# test author to update the sentinel intentionally.

SENTINEL_VAR_DECL_REGEX = r'decl_match = re.match(r"^(\w+)\s+(\w+)\s*=\s*(.+)$", result)'
SENTINEL_CAST_REGEX_LINE = r'expr = re.sub(r"\(([A-Z]\w*)\)\s*(?=[A-Za-z_(])", "", expr)'
SENTINEL_LOGICAL_REPLACE = 'expr.replace("&&", " and ").replace("||", " or ")'


def _load_mutated(mutated_source: str, tmp_path: Path) -> types.ModuleType:
    """Write `mutated_source` next to a copy of the rules dir, then
    `spec_from_file_location` it into a fresh module."""
    # The real translator imports relatively from `src.translator.*` so we
    # need its dependencies on sys.path. Use the real csharp_parser /
    # type_mapper — we're only mutating csharp_to_python.py.
    mutant_path = tmp_path / "csharp_to_python_mutant.py"
    mutant_path.write_text(mutated_source, encoding="utf-8")

    # The source uses `Path(__file__).parent / "rules"` to find translation
    # rules. Mirror the rules dir next to the mutant file.
    real_rules = SRC_FILE.parent / "rules"
    shutil.copytree(real_rules, tmp_path / "rules")

    spec = importlib.util.spec_from_file_location(
        "csharp_to_python_mutant", mutant_path
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    # Stash on sys.modules so internal `from src.translator...` style imports
    # in the mutant work — they actually resolve against the still-installed
    # real package (sys.path includes the project root via conftest).
    sys.modules["csharp_to_python_mutant"] = mod
    spec.loader.exec_module(mod)
    return mod


def _wrap_method(body: str, *, base: str = "MonoBehaviour") -> str:
    body = textwrap.indent(body.strip(), "        ")
    return (
        "using UnityEngine;\n"
        f"public class Foo : {base} {{\n"
        "    void Run() {\n"
        f"{body}\n"
        "    }\n"
        "}\n"
    )


@pytest.fixture
def real_source() -> str:
    return SRC_FILE.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Mutation A — re-impose the variable-decl allowlist.
# ---------------------------------------------------------------------------


def test_mutation_a_var_decl_allowlist_breaks_user_type(
    tmp_path: Path, real_source: str
) -> None:
    """If we re-impose the legacy allowlist, `PlayerInputHandler player = ...`
    no longer matches the decl branch — the type prefix leaks back in via the
    fallthrough assignment / expression branch."""
    assert SENTINEL_VAR_DECL_REGEX in real_source, (
        "Sentinel VAR_DECL_REGEX line not found — update the test."
    )

    # Splice a guard block right after the decl-match unpacking so only the
    # legacy allowlist proceeds. Any other type falls through to the
    # statement-level "Method call" branch — same as pre-fix behavior.
    old = (
        '    decl_match = re.match(r"^(\\w+)\\s+(\\w+)\\s*=\\s*(.+)$", result)\n'
        "    if decl_match:\n"
        "        _var_type, var_name, value = decl_match.groups()\n"
    )
    new = (
        '    decl_match = re.match(r"^(\\w+)\\s+(\\w+)\\s*=\\s*(.+)$", result)\n'
        "    if decl_match:\n"
        "        _var_type, var_name, value = decl_match.groups()\n"
        '        if _var_type not in ("int","float","double","bool","string","var","Vector2","Vector3","GameObject","Rigidbody2D","BallController","Collision2D"):\n'
        "            decl_match = None\n"
        "    if decl_match:\n"
        "        _var_type, var_name, value = decl_match.groups()\n"
    )
    assert old in real_source, "Decl block not found verbatim — update the patch."
    mutated = real_source.replace(old, new, 1)
    assert mutated != real_source

    mod = _load_mutated(mutated, tmp_path)

    from src.translator.csharp_parser import parse_csharp

    src = _wrap_method("PlayerInputHandler player = owner;")
    out = mod.translate(parse_csharp(src))

    # With the allowlist re-imposed, the decl branch refuses to match;
    # the fallthrough leaves the C# type prefix intact in the output.
    assert "PlayerInputHandler player" in out, (
        "Mutation A should have re-introduced the type-prefix leak;\n"
        f"output:\n{out}"
    )


# ---------------------------------------------------------------------------
# Mutation B — drop the cast-strip regex entirely.
# ---------------------------------------------------------------------------


def test_mutation_b_drop_cast_strip_leaks_cast(
    tmp_path: Path, real_source: str
) -> None:
    """If we delete the cast-strip line, `(Vector2)pos` survives into the
    Python output and breaks parse-back."""
    assert SENTINEL_CAST_REGEX_LINE in real_source, (
        "Sentinel CAST_REGEX_LINE not found — update the test."
    )

    mutated = real_source.replace(
        SENTINEL_CAST_REGEX_LINE, "pass  # cast-strip removed by mutation B", 1
    )
    assert mutated != real_source

    mod = _load_mutated(mutated, tmp_path)

    from src.translator.csharp_parser import parse_csharp

    src = _wrap_method("var p = (Vector2)pos;")
    out = mod.translate(parse_csharp(src))

    # Cast must now be visible in output — the contract test would catch this.
    assert "(Vector2)" in out, (
        f"Mutation B should leak the (Vector2) cast; output:\n{out}"
    )


# ---------------------------------------------------------------------------
# Mutation C — drop the &&/|| logical-operator replacement.
# ---------------------------------------------------------------------------


def test_mutation_c_drop_logical_replace_leaves_amp_and_pipe(
    tmp_path: Path, real_source: str
) -> None:
    """If we no-op the `expr.replace("&&", " and ").replace("||", " or ")`
    line, raw `&&` / `||` survive into the Python output and break parse-back.
    """
    assert SENTINEL_LOGICAL_REPLACE in real_source, (
        "Sentinel LOGICAL_REPLACE not found — update the test."
    )

    mutated = real_source.replace(
        SENTINEL_LOGICAL_REPLACE,
        'expr.replace("__m2close_no_op__", "__m2close_no_op__")',
        1,
    )
    assert mutated != real_source

    mod = _load_mutated(mutated, tmp_path)

    from src.translator.csharp_parser import parse_csharp

    # Use an EXPRESSION-context fragment so the substitution path under test
    # is `_translate_expression`'s own replace call (Fix 3). The if-condition
    # path uses `_extract_condition`, which has its own (redundant) replace —
    # we don't want to mutate that one for this test.
    src = _wrap_method("bool x = a && b;\nbool y = c || d;")
    out = mod.translate(parse_csharp(src))

    # `&&` and `||` must now appear in the output (un-translated).
    assert "&&" in out or "||" in out, (
        f"Mutation C should leak `&&` / `||`; output:\n{out}"
    )
