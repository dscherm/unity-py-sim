"""Mutation tests for M-2 phase-2a field-initializer translation fix.

Strategy: load src/translator/csharp_to_python.py as text, mutate the three
critical regex passes inside _translate_literal, hot-load the mutated source
as a fresh module, and assert that translating a field initializer no longer
produces the expected Python.

This proves the contract tests in
tests/contracts/test_m2p2a_field_initializer_contract.py would catch a
regression that removed each of the three fixes individually.

NEVER modifies the real source file — all mutations land in a tmp copy that
is loaded via importlib.util.spec_from_file_location.
"""

from __future__ import annotations

import importlib.util
import sys
import textwrap
from pathlib import Path
from types import ModuleType

import pytest


_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_TRANSLATOR_SRC = _PROJECT_ROOT / "src" / "translator" / "csharp_to_python.py"


def _load_mutated_translator(mutated_text: str, tmp_path: Path) -> ModuleType:
    """Write mutated_text to tmp_path/csharp_to_python.py and import it.

    The mutated module reuses the real csharp_parser and type_mapper modules
    (no need to copy those — the bug surface is _translate_literal only).

    The translator module computes ``_RULES_DIR = Path(__file__).parent /
    "rules"`` at import time. When we load it from tmp_path, that path is
    bogus, so we rewrite the line to point at the real rules dir before
    exec_module runs. This is a surgical patch; the regex/literal handling
    code under test is untouched.
    """
    real_rules_dir = (
        _PROJECT_ROOT / "src" / "translator" / "rules"
    ).as_posix()
    rewired = mutated_text.replace(
        '_RULES_DIR = Path(__file__).parent / "rules"',
        f'_RULES_DIR = Path(r"{real_rules_dir}")',
    )
    assert rewired != mutated_text, (
        "Failed to rewire _RULES_DIR — translator source layout changed."
    )

    mutated_file = tmp_path / "mutated_csharp_to_python.py"
    mutated_file.write_text(rewired, encoding="utf-8")

    spec = importlib.util.spec_from_file_location(
        "tests.mutation._mutated_csharp_to_python", str(mutated_file)
    )
    assert spec and spec.loader, "spec_from_file_location returned None"
    module = importlib.util.module_from_spec(spec)
    # Inject into sys.modules under a unique name so the loader can resolve
    # any internal references during exec_module.
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(spec.name, None)
        raise
    return module


def _wrap(field_decl: str) -> str:
    return f"public class Foo : MonoBehaviour {{ {field_decl} }}"


def _translate_with(mutated: ModuleType, field_decl: str) -> str:
    # The mutated module re-exports `parse_csharp_file` indirectly via its
    # imports, but for our purposes we use the real parser + the mutated
    # translate function.
    from src.translator.csharp_parser import parse_csharp

    parsed = parse_csharp(_wrap(field_decl))
    return mutated.translate(parsed)


# ── Read source once ─────────────────────────────────────────────────


@pytest.fixture(scope="module")
def translator_source() -> str:
    return _TRANSLATOR_SRC.read_text(encoding="utf-8")


# ── Sanity: mutated-module loader works on un-mutated source ────────


def test_loader_baseline_unmutated_source(translator_source, tmp_path):
    """Sanity: loading the un-mutated source through our harness must still
    translate field initializers correctly. If this fails, the harness is
    broken and the mutation results below are meaningless."""
    mod = _load_mutated_translator(translator_source, tmp_path)
    py = _translate_with(mod, "private Vector2 v = new Vector2(0, 0.6f);")
    assert "Vector2(0, 0.6)" in py
    assert "new Vector2" not in py
    py2 = _translate_with(mod, "private float speed = 6f;")
    assert "self.speed: float = 6.0" in py2
    py3 = _translate_with(mod, "private float speed = 0.6f;")
    assert "self.speed: float = 0.6" in py3


# ── Mutation A: drop the embedded-`new` strip ───────────────────────


def test_mutation_A_drop_new_strip_breaks_vector_field(
    translator_source, tmp_path
):
    """Removing the `\\bnew\\s+` strip in _translate_literal must cause
    `new Vector2(...)` to leak through into the Python output."""
    target = 'value = _sub_outside_strings(r"\\bnew\\s+", "", value)'
    assert target in translator_source, (
        "Could not find the embedded-new strip line — mutation A target moved."
    )
    mutated = translator_source.replace(target, "# MUTATION A: removed", 1)
    assert mutated != translator_source

    mod = _load_mutated_translator(mutated, tmp_path)
    py = _translate_with(mod, "private Vector2 v = new Vector2(0, 0.6f);")
    # The fix is GONE — `new` should now appear in the output
    assert "new Vector2" in py, (
        "Mutation A did not flip the contract — `new` strip is somehow still "
        f"happening:\n{py}"
    )


# ── Mutation B: drop the decimal-float-suffix regex ─────────────────


def test_mutation_B_drop_decimal_suffix_strip_breaks_decimal_field(
    translator_source, tmp_path
):
    """Removing `(\\d+\\.\\d+)[fF]\\b` must leave `0.6f` un-stripped."""
    # Match the exact line as written in the source.
    target = 'value = _sub_outside_strings(r"(\\d+\\.\\d+)[fF]\\b", r"\\1", value)'
    assert target in translator_source, (
        "Could not find the decimal-float-suffix line — mutation B target moved."
    )
    mutated = translator_source.replace(target, "# MUTATION B: removed", 1)
    assert mutated != translator_source

    mod = _load_mutated_translator(mutated, tmp_path)
    # `convert_float_literal` only handles whole-string `0.6f` -> `0.6`,
    # which actually applies for a bare-value initializer. So probe a
    # compound case where the literal is embedded inside a constructor
    # call, where convert_float_literal is a no-op.
    py = _translate_with(mod, "private Vector2 v = new Vector2(0, 0.6f);")
    # When the decimal-suffix regex is removed, the surviving int-suffix
    # regex `\b(\d+)[fF]\b` runs first and matches `6f` inside `0.6f`
    # (the `\b` at `.|6` allows it). It rewrites the substring to `6.0`,
    # corrupting the literal to `0.6.0` — invalid Python syntax.
    # Either symptom (`0.6f` left intact OR `0.6.0` corruption) proves
    # the contract test would catch the regression.
    contract_violated = (
        "0.6f" in py
        or "0.6.0" in py
        or "self.v: Vector2 = Vector2(0, 0.6)" not in py
    )
    assert contract_violated, (
        "Mutation B did not flip the contract — `0.6f` was somehow still "
        f"correctly translated:\n{py}"
    )


# ── Mutation C: drop the int-float-suffix regex ─────────────────────


def test_mutation_C_drop_int_suffix_strip_breaks_int_form(
    translator_source, tmp_path
):
    """Removing `\\b(\\d+)[fF]\\b` leaves `6f` (int form) un-converted when
    embedded in a constructor."""
    target = (
        'value = _sub_outside_strings(r"\\b(\\d+)[fF]\\b", '
        'lambda m: m.group(1) + ".0", value)'
    )
    assert target in translator_source, (
        "Could not find the int-float-suffix line — mutation C target moved."
    )
    mutated = translator_source.replace(target, "# MUTATION C: removed", 1)
    assert mutated != translator_source

    mod = _load_mutated_translator(mutated, tmp_path)
    # Embedded `6f` inside a constructor — convert_float_literal can't
    # touch this because the whole value is `Vector3(0f, 1.5f, 2f)`.
    py = _translate_with(mod, "private Vector3 v = new Vector3(0f, 1.5f, 2f);")
    assert "0f" in py or "2f" in py, (
        "Mutation C did not flip the contract — int-form `Nf` should leak "
        f"through when the int-suffix regex is removed:\n{py}"
    )


# ── Defensive: each mutation must isolate to its specific failure ───


def test_mutations_do_not_cross_pollute(translator_source, tmp_path):
    """Mutation A removing the `new` strip must NOT also break the float
    handling — they live on separate lines and are independent."""
    target = 'value = _sub_outside_strings(r"\\bnew\\s+", "", value)'
    mutated = translator_source.replace(target, "# MUTATION A: removed", 1)
    mod = _load_mutated_translator(mutated, tmp_path)

    # Float handling on a non-`new` field must still work
    py = _translate_with(mod, "private float speed = 0.6f;")
    assert "self.speed: float = 0.6" in py
    py2 = _translate_with(mod, "private float speed = 6f;")
    assert "self.speed: float = 6.0" in py2
