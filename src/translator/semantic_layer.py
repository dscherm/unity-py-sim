"""Semantic post-processor for translated C# — rewrites patterns that compile but don't run in Unity.

The AST translator handles syntax (Python -> C#) but not semantics (simulator -> Unity patterns).
This module applies regex-based rewrites to strip simulator artifacts and fix Unity-incompatible
constructs in the translated output.

Usage:
    from src.translator.semantic_layer import transform

    clean_cs = transform(raw_cs_code)
"""

from __future__ import annotations

import re


# C# value types whose nullable form (int?, float?, etc.) is intentional
_VALUE_TYPES = frozenset({
    "int", "float", "double", "bool", "byte", "sbyte",
    "short", "ushort", "uint", "long", "ulong", "decimal",
    "char", "Vector2", "Vector3", "Vector4", "Quaternion",
    "Color", "Color32", "Rect", "Bounds",
})


def transform(cs_source: str) -> str:
    """Apply semantic rewrites to translated C#.

    Processes the C# source in priority order:
    1. Strip simulator-only code (pygame, pymunk, simulator managers)
    2. Rewrite Python type hints that leaked through translation
    3. Annotate constructor patterns
    4. Annotate singleton patterns
    """
    if not cs_source:
        return cs_source

    cs_source = _strip_simulator_code(cs_source)
    cs_source = _rewrite_type_hints(cs_source)
    cs_source = _annotate_constructors(cs_source)
    cs_source = _annotate_singletons(cs_source)
    cs_source = _clean_empty_lines(cs_source)

    return cs_source


def _strip_simulator_code(cs: str) -> str:
    """Priority 1: Remove pygame, pymunk, and simulator manager references."""

    # --- pygame references ---
    # Replace pygame.Surface type with Sprite
    cs = re.sub(r'pygame\.Surface\??\s*\[\]', 'Sprite[]', cs)
    cs = re.sub(r'pygame\.Surface\??', 'Sprite', cs)

    # Strip entire lines containing pygame references (calls, init, etc.)
    cs = re.sub(r'[^\n]*\bpygame\b[^\n]*\n?', '', cs)

    # --- pymunk references ---
    cs = re.sub(r'[^\n]*\bpymunk\b[^\n]*\n?', '', cs)

    # --- Simulator managers ---
    cs = re.sub(r'[^\n]*\bLifecycleManager\b[^\n]*\n?', '', cs)
    cs = re.sub(r'[^\n]*\bPhysicsManager\b[^\n]*\n?', '', cs)
    cs = re.sub(r'[^\n]*\bDisplayManager\b[^\n]*\n?', '', cs)

    # Strip variable stubs left behind by manager stripping (e.g., lm.Something())
    cs = re.sub(r'\s*var lm = [^;]*;\n?', '', cs)
    cs = re.sub(r'[^\n]*\blm\.[^\n]*\n?', '', cs)
    cs = re.sub(r'\s*var pm = [^;]*;\n?', '', cs)
    cs = re.sub(r'[^\n]*\bpm\.[^\n]*\n?', '', cs)
    cs = re.sub(r'\s*var dm = [^;]*;\n?', '', cs)
    cs = re.sub(r'[^\n]*\bdm\.[^\n]*\n?', '', cs)

    # --- app.run() ---
    cs = re.sub(r'[^\n]*\bapp\.run\s*\([^)]*\)\s*;[^\n]*\n?', '', cs)

    return cs


def _rewrite_type_hints(cs: str) -> str:
    """Priority 2: Fix Python type annotations that leaked into C#."""

    # Strip nullable ? on reference types (not value types)
    # Match: public TypeName? fieldName  or  private TypeName? fieldName
    # But preserve int?, float?, Vector3?, etc.
    def _strip_nullable_ref(m: re.Match) -> str:
        prefix = m.group(1)   # visibility + optional modifiers
        type_name = m.group(2)  # the type
        suffix = m.group(3)     # field name + rest
        if type_name in _VALUE_TYPES:
            return m.group(0)  # keep as-is
        return f"{prefix}{type_name} {suffix}"

    cs = re.sub(
        r'((?:public|private|protected)\s+(?:static\s+)?(?:readonly\s+)?)(\w+)\?\s+(\w+)',
        _strip_nullable_ref,
        cs,
    )

    # Also strip standalone ClassName? in return types and local vars
    # e.g., GameManager? in "return GameManager.Instance;"
    # This is handled by the field pattern above for declarations

    # Rewrite !in operator: "if (item !in collection)" -> "if (!collection.Contains(item))"
    cs = re.sub(
        r'if\s*\(\s*(\w+)\s+!in\s+(\w+)\s*\)',
        r'if (!\2.Contains(\1))',
        cs,
    )

    return cs


def _annotate_constructors(cs: str) -> str:
    """Priority 3: Annotate new GameObject() calls with TODO comment."""

    # Match: new GameObject("...") — but not GameObject.Find, etc.
    # Add comment on the same line
    def _add_constructor_comment(m: re.Match) -> str:
        line = m.group(0)
        comment = " // TODO: wire via Inspector or Instantiate"
        # Don't double-add
        if "// TODO:" in line:
            return line
        return line.rstrip() + comment

    cs = re.sub(
        r'[^\n]*new\s+GameObject\s*\([^\n]*',
        _add_constructor_comment,
        cs,
    )

    return cs


def _annotate_singletons(cs: str) -> str:
    """Priority 4: Detect and annotate singleton pattern."""

    # Match: public static ClassName instance (with or without assignment)
    def _add_singleton_comment(m: re.Match) -> str:
        line = m.group(0)
        comment = "// Singleton \u2014 wire via Inspector [SerializeField] on dependents"
        if "Singleton" in line:
            return line
        return f"    {comment}\n{line}"

    cs = re.sub(
        r'^(\s*public\s+static\s+\w+\s+instance\b[^\n]*)',
        _add_singleton_comment,
        cs,
        flags=re.MULTILINE,
    )

    return cs


def _clean_empty_lines(cs: str) -> str:
    """Remove excessive blank lines left after stripping."""
    # Collapse 3+ consecutive blank lines to 2
    cs = re.sub(r'\n{4,}', '\n\n\n', cs)
    return cs
