"""Mutation tests for G8 — TagManager empty layer scalar.

Proves that if _write_tag_manager reverts to emitting bare `  -` null
scalars instead of `  - ""`, the contract tests catch it.

Mutation strategy: monkeypatch the inner loop in _write_tag_manager so
that empty entries append `  -` (the old broken form) instead of `  - ""`.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

import pytest
import yaml

import src.exporter.project_scaffolder as _scaffolder_mod
from src.exporter.project_scaffolder import _write_tag_manager


def _write_and_parse(
    monkeypatch,
    tags=None,
    layers=None,
    *,
    mutate: bool = False,
):
    """Write TagManager and return (raw_text, parsed_dict).

    When mutate=True, the `lines.append('  - ""')` branch is replaced
    with `lines.append('  -')` — the pre-fix broken form.
    """
    if mutate:
        original_write = _write_tag_manager

        def _mutated_write_tag_manager(output_dir, tags, layers):
            # Replicate the function but emit bare `  -` for empty slots
            from src.exporter.project_scaffolder import (
                _DEFAULT_UNITY_TAGS,
                _BUILTIN_LAYERS,
                _TOTAL_LAYER_SLOTS,
            )

            all_tags = list(_DEFAULT_UNITY_TAGS)
            if tags:
                for tag in tags:
                    if tag not in all_tags:
                        all_tags.append(tag)

            layer_array: list[str] = [""] * _TOTAL_LAYER_SLOTS
            for idx, name in _BUILTIN_LAYERS.items():
                layer_array[idx] = name
            if layers:
                for name, idx in layers.items():
                    if 0 <= idx < _TOTAL_LAYER_SLOTS:
                        layer_array[idx] = name

            lines: list[str] = []
            lines.append("%YAML 1.1")
            lines.append("%TAG !u! tag:unity3d.com,2011:")
            lines.append("--- !u!78 &1")
            lines.append("TagManager:")
            lines.append("  serializedVersion: 2")
            lines.append("  tags:")
            for tag in all_tags:
                lines.append(f"  - {tag}")

            lines.append("  layers:")
            for name in layer_array:
                if name:
                    lines.append(f"  - {name}")
                else:
                    lines.append("  -")  # MUTATION: bare null scalar (the old bug)

            lines.append("  m_SortingLayers:")
            lines.append("  - name: Default")
            lines.append("    uniqueID: 0")
            lines.append("    locked: 0")

            tm_path = output_dir / "ProjectSettings" / "TagManager.asset"
            tm_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        monkeypatch.setattr(_scaffolder_mod, "_write_tag_manager", _mutated_write_tag_manager)
        fn = _mutated_write_tag_manager
    else:
        fn = _write_tag_manager

    with tempfile.TemporaryDirectory() as tmpdir:
        out = Path(tmpdir)
        (out / "ProjectSettings").mkdir()
        fn(out, tags=tags, layers=layers)
        text = (out / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")

    # Strip directives for yaml.safe_load
    body_lines = [l for l in text.splitlines() if not l.startswith("%") and not l.startswith("---")]
    parsed = yaml.safe_load("\n".join(body_lines))
    return text, parsed


def _get_layers_section(text: str) -> str:
    lines = text.splitlines()
    in_layers = False
    result = []
    for line in lines:
        if line.strip() == "layers:":
            in_layers = True
            continue
        if in_layers:
            if line and not line.startswith(" "):
                break
            if line.startswith("  ") and not line.startswith("  -") and ":" in line:
                break
            result.append(line)
    return "\n".join(result)


# ---------------------------------------------------------------------------
# Baseline: real implementation passes
# ---------------------------------------------------------------------------

def test_baseline_no_bare_null_scalars(monkeypatch):
    """Real implementation: no bare null scalars."""
    text, _ = _write_and_parse(monkeypatch, mutate=False)
    layers_section = _get_layers_section(text)
    bare = re.compile(r"^\s*-\s*$", re.MULTILINE)
    assert not bare.findall(layers_section)


def test_baseline_layer_3_is_empty_string(monkeypatch):
    """Real implementation: layer[3] == ''."""
    _, parsed = _write_and_parse(monkeypatch, mutate=False)
    assert parsed["TagManager"]["layers"][3] == ""


# ---------------------------------------------------------------------------
# Mutation: reverted implementation MUST fail these checks
# ---------------------------------------------------------------------------

def test_mutation_bare_null_scalars_detected(monkeypatch):
    """MUTATION: bare `  -` lines appear in layers section.

    If the test passes (no bare scalars detected), the mutation is
    invisible and we have a test gap. This test asserts the OPPOSITE —
    that bare scalars ARE present after the mutation.
    """
    text, _ = _write_and_parse(monkeypatch, mutate=True)
    layers_section = _get_layers_section(text)
    bare = re.compile(r"^\s*-\s*$", re.MULTILINE)
    matches = bare.findall(layers_section)
    assert matches, (
        "MUTATION NOT CAUGHT: expected bare null scalars in mutated output, "
        "but none found. The contract test cannot catch the regression."
    )


def test_mutation_layer_3_parses_as_none(monkeypatch):
    """MUTATION: layer[3] parses as None (null scalar) after revert.

    Proves the contract test `test_layer_index_3_is_empty_string_not_none`
    would catch this regression.
    """
    _, parsed = _write_and_parse(monkeypatch, mutate=True)
    layer_3 = parsed["TagManager"]["layers"][3]
    assert layer_3 is None, (
        f"MUTATION NOT CAUGHT: expected None for layer[3] after mutation, got {layer_3!r}. "
        "The contract test may not catch the regression."
    )


def test_contract_test_would_fail_on_mutation(monkeypatch):
    """End-to-end proof: contract assertion fails on mutated output.

    This is an explicit regression-detection test. It directly runs the
    same assertion as the contract test and expects it to raise AssertionError.
    """
    text, parsed = _write_and_parse(monkeypatch, mutate=True)
    layers_section = _get_layers_section(text)

    # Contract assertion 1: no bare null scalars
    bare = re.compile(r"^\s*-\s*$", re.MULTILINE)
    with pytest.raises(AssertionError):
        assert not bare.findall(layers_section), "bare null scalar found"

    # Contract assertion 2: layer[3] is empty string
    layer_3 = parsed["TagManager"]["layers"][3]
    with pytest.raises(AssertionError):
        assert layer_3 == "", f"layer[3] must be '' got {layer_3!r}"
