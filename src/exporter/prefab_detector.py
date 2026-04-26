"""Prefab detector — analyzes Python game source to classify GameObjects.

Parses Python files with the ast module and classifies GameObject() creations as:
- **prefab**: created inside a for/while loop (dynamically instantiated at runtime)
- **scene_object**: created outside loops (placed in the scene during setup)

For each prefab, lists the components added via add_component() calls.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import Any


def detect_prefabs(directory: str) -> dict[str, list[dict[str, Any]]]:
    """Analyze Python files in *directory* for GameObject creation patterns.

    Returns ``{"prefabs": [...], "scene_objects": [...]}`` where each prefab
    entry has ``class_name`` and ``components`` list, and each scene_object
    entry has ``name``.
    """
    py_files = _collect_python_files(directory)
    prefabs: list[dict[str, Any]] = []
    scene_objects: list[dict[str, Any]] = []
    seen_prefab_names: set[str] = set()
    seen_scene_names: set[str] = set()

    for filepath in py_files:
        try:
            source = Path(filepath).read_text(encoding="utf-8")
            tree = ast.parse(source, filename=filepath)
        except (SyntaxError, UnicodeDecodeError):
            continue

        go_infos = _find_game_objects(tree)

        for info in go_infos:
            if info["in_loop"]:
                class_name = _derive_class_name(info["name_expr"])
                if class_name not in seen_prefab_names:
                    seen_prefab_names.add(class_name)
                    prefabs.append({
                        "class_name": class_name,
                        "components": info["components"],
                    })
            else:
                obj_name = _extract_name(info["name_expr"])
                if obj_name not in seen_scene_names:
                    seen_scene_names.add(obj_name)
                    scene_objects.append({"name": obj_name})

    return {"prefabs": prefabs, "scene_objects": scene_objects}


# ── Helpers ──────────────────────────────────────────────────────


def _collect_python_files(directory: str) -> list[str]:
    """Recursively collect .py files from *directory*."""
    results: list[str] = []
    for root, _dirs, files in os.walk(directory):
        for f in files:
            if f.endswith(".py"):
                results.append(os.path.join(root, f))
    return results


def _extract_name(name_expr: ast.expr | None) -> str:
    """Extract a human-readable name from the first argument to GameObject()."""
    if name_expr is None:
        return "Unknown"
    if isinstance(name_expr, ast.Constant) and isinstance(name_expr.value, str):
        return name_expr.value
    if isinstance(name_expr, ast.JoinedStr):
        parts: list[str] = []
        for value in name_expr.values:
            if isinstance(value, ast.Constant):
                parts.append(str(value.value))
            else:
                parts.append("{...}")
        return "".join(parts)
    # S7-4: never return `ast.dump(...)` — the raw repr ``Name(id='name', ctx=Load())``
    # was leaking into prefab filenames in breakout debug 2026-04-13.
    if isinstance(name_expr, ast.Name):
        # Variable reference — use the variable name as the prefab stem
        return name_expr.id.capitalize() or "Unknown"
    if isinstance(name_expr, ast.Attribute):
        return name_expr.attr.capitalize() or "Unknown"
    if isinstance(name_expr, ast.Call):
        # e.g. str(x), use the callable's name if resolvable
        func = name_expr.func
        if isinstance(func, ast.Name):
            return func.id.capitalize()
        if isinstance(func, ast.Attribute):
            return func.attr.capitalize()
    return "Unknown"


# Characters disallowed in generated prefab class names / filenames.
# ``ast.dump`` output always contains at least one of these, so rejecting them
# guards against any future AST-repr leakage.
_UNSAFE_NAME_CHARS = set("()=',:[]<>\\/\"")


def _sanitize_class_name(name: str) -> str:
    """Guard: reject names containing AST-repr characters, return safe fallback."""
    if not name or any(ch in _UNSAFE_NAME_CHARS for ch in name):
        return "Unknown"
    # Also strip whitespace runs to single char — Unity prefab paths can't have spaces reliably
    return name.strip().replace(" ", "_") or "Unknown"


def _derive_class_name(name_expr: ast.expr | None) -> str:
    """Derive a prefab class name from the name pattern.

    For f-strings like ``f"Brick_{row}_{col}"``, extracts ``Brick``.
    For plain strings, returns the string as-is.
    For variable refs, uses the variable name. For unknown expressions,
    returns ``Unknown`` (never the raw ``ast.dump`` repr — see S7-4).
    """
    raw = _extract_name(name_expr)
    # Strip dynamic f-string parts: "Brick_{...}_{...}" -> "Brick"
    base = raw.split("_{")[0]
    if base != raw:
        return _sanitize_class_name(base)
    return _sanitize_class_name(raw)


# ── AST Analysis ─────────────────────────────────────────────────


def _is_gameobject_call(node: ast.expr) -> bool:
    """Check if *node* is a call to ``GameObject(...)``."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Name) and func.id == "GameObject":
        return True
    if isinstance(func, ast.Attribute) and func.attr == "GameObject":
        return True
    return False


def _get_first_arg(call: ast.Call) -> ast.expr | None:
    """Get the first positional argument from a Call node."""
    if call.args:
        return call.args[0]
    return None


def _get_assign_var(node: ast.Assign) -> str | None:
    """Get variable name from assignment target (simple name only)."""
    if node.targets and isinstance(node.targets[0], ast.Name):
        return node.targets[0].id
    return None


def _find_add_component_calls(stmts: list[ast.stmt], var_name: str, start_line: int) -> list[str]:
    """Find ``var_name.add_component(ComponentClass)`` calls after *start_line* in *stmts*.

    Also follows indirect patterns like ``comp = var_name.add_component(...)``
    and direct ``var_name.add_component(...)`` expression statements.
    """
    components: list[str] = []
    for stmt in stmts:
        if stmt.lineno <= start_line:
            continue
        # Direct: var.add_component(Cls) as expression or assignment
        calls = _extract_add_component_on(stmt, var_name)
        components.extend(calls)
    return components


def _extract_add_component_on(node: ast.stmt, var_name: str) -> list[str]:
    """Extract component class names from add_component calls on var_name within a statement."""
    results: list[str] = []
    for child in ast.walk(node):
        if not isinstance(child, ast.Call):
            continue
        func = child.func
        if (isinstance(func, ast.Attribute)
                and func.attr == "add_component"
                and isinstance(func.value, ast.Name)
                and func.value.id == var_name):
            if child.args:
                arg = child.args[0]
                if isinstance(arg, ast.Name):
                    results.append(arg.id)
                elif isinstance(arg, ast.Attribute):
                    results.append(arg.attr)
    return results


def _find_game_objects(tree: ast.Module) -> list[dict[str, Any]]:
    """Find all GameObject() creations in an AST tree.

    Returns a list of dicts with keys: name_expr, in_loop, components, var_name.
    """
    results: list[dict[str, Any]] = []
    # Track simple variable assignments: var_name -> ast.expr (for resolving
    # patterns like ``name = f"Brick_{row}_{col}"; go = GameObject(name)``)
    var_bindings: dict[str, ast.expr] = {}

    def _resolve_name_expr(expr: ast.expr | None) -> ast.expr | None:
        """If *expr* is a Name referencing a known variable, resolve it."""
        if isinstance(expr, ast.Name) and expr.id in var_bindings:
            return var_bindings[expr.id]
        return expr

    def _scan_body(stmts: list[ast.stmt], loop_depth: int) -> None:
        for stmt in stmts:
            # Handle loops
            if isinstance(stmt, (ast.For, ast.While)):
                _scan_body(stmt.body, loop_depth + 1)
                if hasattr(stmt, "orelse") and stmt.orelse:
                    _scan_body(stmt.orelse, loop_depth)
                continue

            # Handle if/elif/else
            if isinstance(stmt, ast.If):
                _scan_body(stmt.body, loop_depth)
                if stmt.orelse:
                    _scan_body(stmt.orelse, loop_depth)
                continue

            # Handle with statements
            if isinstance(stmt, ast.With):
                _scan_body(stmt.body, loop_depth)
                continue

            # Handle try/except
            if isinstance(stmt, (ast.Try,)):
                _scan_body(stmt.body, loop_depth)
                for handler in stmt.handlers:
                    _scan_body(handler.body, loop_depth)
                if stmt.orelse:
                    _scan_body(stmt.orelse, loop_depth)
                if stmt.finalbody:
                    _scan_body(stmt.finalbody, loop_depth)
                continue

            # Handle function definitions — scan their bodies
            if isinstance(stmt, ast.FunctionDef):
                _scan_body(stmt.body, loop_depth)
                continue

            # Track simple variable assignments for name resolution
            if isinstance(stmt, ast.Assign):
                target_name = _get_assign_var(stmt)
                if target_name and not _is_gameobject_call(stmt.value):
                    var_bindings[target_name] = stmt.value

            # Check for assignments: var = GameObject(...)
            if isinstance(stmt, ast.Assign) and _is_gameobject_call(stmt.value):
                var_name = _get_assign_var(stmt)
                name_expr = _resolve_name_expr(_get_first_arg(stmt.value))

                # Find components in the enclosing body after this statement
                components: list[str] = []
                if var_name:
                    components = _find_add_component_calls(
                        stmts, var_name, stmt.lineno
                    )

                results.append({
                    "name_expr": name_expr,
                    "in_loop": loop_depth > 0,
                    "components": components,
                    "var_name": var_name,
                })

    _scan_body(tree.body, 0)
    return results
