"""Structural gate — validates generated C# parses correctly with tree-sitter."""

from __future__ import annotations

from dataclasses import dataclass

import tree_sitter_c_sharp as ts_cs
import tree_sitter as ts

_lang = ts.Language(ts_cs.language())
_parser = ts.Parser(_lang)


@dataclass
class StructuralResult:
    valid: bool
    class_count: int
    method_count: int
    error_count: int
    errors: list[str]


def validate_csharp(source: str) -> StructuralResult:
    """Validate that C# source parses correctly with tree-sitter."""
    tree = _parser.parse(source.encode("utf-8"))
    root = tree.root_node

    errors = []
    class_count = 0
    method_count = 0
    error_count = 0

    def walk(node, depth=0):
        nonlocal class_count, method_count, error_count
        if node.type == "ERROR":
            error_count += 1
            text = node.text.decode("utf-8")[:80] if node.text else ""
            errors.append(f"Parse error at {node.start_point}: {text}")
        if node.type == "class_declaration":
            class_count += 1
        if node.type == "method_declaration":
            method_count += 1
        for child in node.children:
            walk(child, depth + 1)

    walk(root)

    return StructuralResult(
        valid=error_count == 0,
        class_count=class_count,
        method_count=method_count,
        error_count=error_count,
        errors=errors,
    )
