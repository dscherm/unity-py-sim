"""Python parser using stdlib ast — extracts simulator-aware IR from Python source."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.translator.type_mapper import snake_to_pascal, snake_to_camel


# ── IR Dataclasses (mirrors C# IR) ──────────────────────────

@dataclass
class PyField:
    name: str
    type_annotation: str = ""
    default_value: str | None = None
    is_class_level: bool = False
    source_line: str = ""  # raw source line, so downstream can read trailing `# T[]` hints

@dataclass
class PyParameter:
    name: str
    type_annotation: str = ""
    default_value: str | None = None

@dataclass
class PyMethod:
    name: str
    parameters: list[PyParameter] = field(default_factory=list)
    body_source: str = ""
    return_annotation: str = ""
    is_static: bool = False
    is_lifecycle: bool = False
    is_coroutine: bool = False
    decorators: list[str] = field(default_factory=list)

@dataclass
class PyClass:
    name: str
    base_classes: list[str] = field(default_factory=list)
    is_monobehaviour: bool = False
    is_enum: bool = False
    is_scriptable_object: bool = False
    create_asset_menu: dict | None = None
    fields: list[PyField] = field(default_factory=list)
    methods: list[PyMethod] = field(default_factory=list)

@dataclass
class PyFile:
    imports: list[str] = field(default_factory=list)
    classes: list[PyClass] = field(default_factory=list)
    module_constants: list[PyField] = field(default_factory=list)
    module_functions: list[PyMethod] = field(default_factory=list)


# ── Known lifecycle methods ──────────────────────────────────

_LIFECYCLE_METHODS = {
    "awake", "start", "update", "fixed_update", "late_update",
    "on_destroy", "on_enable", "on_disable",
    "on_collision_enter_2d", "on_collision_exit_2d", "on_collision_stay_2d",
    "on_trigger_enter_2d", "on_trigger_exit_2d", "on_trigger_stay_2d",
}

# ── Known simulator API calls ───────────────────────────────

_SIMULATOR_API_CALLS = {
    "get_component", "add_component", "find", "find_with_tag",
    "find_game_objects_with_tag", "destroy",
}


def _get_source_segment(source_lines: list[str], node: ast.AST) -> str:
    """Extract source text for an AST node."""
    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
        start = node.lineno - 1
        end = node.end_lineno
        lines = source_lines[start:end]
        if lines:
            # Dedent
            first_indent = len(lines[0]) - len(lines[0].lstrip())
            return "\n".join(line[first_indent:] if len(line) > first_indent else line
                           for line in lines)
    return ""


def _annotation_to_str(node: ast.expr | None) -> str:
    """Convert an annotation AST node to a string."""
    if node is None:
        return ""
    return ast.unparse(node)


def _value_to_str(node: ast.expr | None) -> str | None:
    """Convert a default value AST node to a string."""
    if node is None:
        return None
    return ast.unparse(node)


def _source_line_for(stmt: ast.AST, source_lines: list[str]) -> str:
    """Return the raw source line for a statement (1-indexed lineno -> 0-indexed list)."""
    lineno = getattr(stmt, "lineno", None)
    if lineno is None or lineno <= 0 or lineno > len(source_lines):
        return ""
    return source_lines[lineno - 1]


def _parse_init_fields(func: ast.FunctionDef, source_lines: list[str]) -> list[PyField]:
    """Extract self.X = value assignments from __init__."""
    fields = []
    for stmt in ast.walk(func):
        if isinstance(stmt, ast.AnnAssign):
            # self.name: type = value
            if (isinstance(stmt.target, ast.Attribute) and
                isinstance(stmt.target.value, ast.Name) and
                stmt.target.value.id == "self"):
                fields.append(PyField(
                    name=stmt.target.attr,
                    type_annotation=_annotation_to_str(stmt.annotation),
                    default_value=_value_to_str(stmt.value),
                    is_class_level=False,
                    source_line=_source_line_for(stmt, source_lines),
                ))
        elif isinstance(stmt, ast.Assign):
            # self.name = value (without annotation)
            for target in stmt.targets:
                if (isinstance(target, ast.Attribute) and
                    isinstance(target.value, ast.Name) and
                    target.value.id == "self"):
                    fields.append(PyField(
                        name=target.attr,
                        type_annotation="",
                        default_value=_value_to_str(stmt.value),
                        is_class_level=False,
                        source_line=_source_line_for(stmt, source_lines),
                    ))
    return fields


def _parse_class_fields(cls_node: ast.ClassDef, source_lines: list[str]) -> list[PyField]:
    """Extract class-level field assignments (not in methods)."""
    fields = []
    for stmt in cls_node.body:
        if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
            fields.append(PyField(
                name=stmt.target.id,
                type_annotation=_annotation_to_str(stmt.annotation),
                default_value=_value_to_str(stmt.value),
                is_class_level=True,
                source_line=_source_line_for(stmt, source_lines),
            ))
        elif isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    fields.append(PyField(
                        name=target.id,
                        type_annotation="",
                        default_value=_value_to_str(stmt.value),
                        is_class_level=True,
                        source_line=_source_line_for(stmt, source_lines),
                    ))
    return fields


def _parse_method(func: ast.FunctionDef, source_lines: list[str]) -> PyMethod:
    """Parse a method definition into PyMethod."""
    decorators = [ast.unparse(d) for d in func.decorator_list]
    is_static = "staticmethod" in decorators

    params = []
    had_self = False
    for arg in func.args.args:
        if arg.arg == "self":
            had_self = True
            continue
        params.append(PyParameter(
            name=arg.arg,
            type_annotation=_annotation_to_str(arg.annotation),
        ))

    # Handle defaults (aligned from the right).
    # S11-1: only decrement for `self` if we actually skipped one — module-level
    # functions have no `self` and were getting defaults assigned to the wrong
    # param, producing `(string name = null, int? sizePx)` when the Python was
    # `(name: str, size_px: int | None = None)`.
    defaults = func.args.defaults
    if defaults:
        offset = len(func.args.args) - len(defaults)
        if had_self:
            offset -= 1
        for i, default in enumerate(defaults):
            param_idx = offset + i
            if 0 <= param_idx < len(params):
                params[param_idx].default_value = _value_to_str(default)

    # Extract body source
    body_lines = []
    for stmt in func.body:
        body_lines.append(_get_source_segment(source_lines, stmt))
    body_source = "\n".join(body_lines)

    # Detect coroutines — methods containing yield statements
    is_coroutine = _has_yield(func)

    # Return type annotation (e.g., -> int, -> bool, -> GameObject)
    return_annotation = _annotation_to_str(func.returns) if func.returns else ""

    return PyMethod(
        name=func.name,
        parameters=params,
        body_source=body_source,
        return_annotation=return_annotation,
        is_static=is_static,
        is_lifecycle=func.name in _LIFECYCLE_METHODS,
        is_coroutine=is_coroutine,
        decorators=decorators,
    )


def _has_yield(func: ast.FunctionDef) -> bool:
    """Check if a function contains yield statements (making it a coroutine)."""
    for node in ast.walk(func):
        if isinstance(node, (ast.Yield, ast.YieldFrom)):
            return True
    return False


def parse_python(source: str) -> PyFile:
    """Parse Python source into a PyFile IR."""
    tree = ast.parse(source)
    source_lines = source.split("\n")

    imports = []
    classes = []
    module_constants = []
    module_functions = []

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(ast.unparse(node))
        elif isinstance(node, ast.ClassDef):
            classes.append(_parse_class_node(node, source_lines))
        elif isinstance(node, ast.FunctionDef):
            module_functions.append(_parse_method(node, source_lines))
        elif isinstance(node, ast.Assign):
            # Module-level constants (e.g., LAYER_LASER = 8, ROW_CONFIG = [...])
            for target in node.targets:
                if isinstance(target, ast.Name):
                    module_constants.append(PyField(
                        name=target.id,
                        type_annotation="",
                        default_value=_value_to_str(node.value),
                        is_class_level=True,
                    ))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            # Module-level annotated constants (e.g., CONFIGS: list[Type] = [...])
            ann = ast.unparse(node.annotation) if node.annotation else ""
            val = _value_to_str(node.value) if node.value else None
            module_constants.append(PyField(
                name=node.target.id,
                type_annotation=ann,
                default_value=val,
                is_class_level=True,
            ))

    return PyFile(imports=imports, classes=classes, module_constants=module_constants,
                  module_functions=module_functions)


def _parse_class_node(cls_node: ast.ClassDef, source_lines: list[str]) -> PyClass:
    """Parse a class definition into PyClass."""
    base_classes = []
    for base in cls_node.bases:
        base_classes.append(ast.unparse(base))

    is_mono = "MonoBehaviour" in base_classes
    is_enum = "Enum" in base_classes or "IntEnum" in base_classes
    is_scriptable = "ScriptableObject" in base_classes
    is_dataclass = any("dataclass" in ast.unparse(d) for d in cls_node.decorator_list)

    # Capture @create_asset_menu(...) decorator args, if present. The
    # translator emits a matching [CreateAssetMenu(...)] attribute.
    create_asset_menu = None
    for deco in cls_node.decorator_list:
        if isinstance(deco, ast.Call) and isinstance(deco.func, ast.Name) and deco.func.id == "create_asset_menu":
            meta: dict = {}
            for kw in deco.keywords:
                if kw.arg in ("file_name", "menu_name", "order") and isinstance(kw.value, ast.Constant):
                    meta[kw.arg] = kw.value.value
            create_asset_menu = meta

    # Class-level fields
    class_fields = _parse_class_fields(cls_node, source_lines)

    # Dataclass fields are instance fields, not class-level
    if is_dataclass:
        for f in class_fields:
            f.is_class_level = False

    # Instance fields from __init__
    instance_fields = []
    methods = []

    for item in cls_node.body:
        if isinstance(item, ast.FunctionDef):
            if item.name == "__init__":
                instance_fields = _parse_init_fields(item, source_lines)
            else:
                methods.append(_parse_method(item, source_lines))

    # Deduplicate fields: class-level annotations take priority for the type,
    # but fall back to a matching __init__ default when the class field has
    # no default.  Without this, `x: list[T]` at class level + `self.x = []`
    # in __init__ produced a C# field with no initializer — callers got a
    # NullReferenceException on the first `.Clear()` / `.Add()`.
    instance_by_name = {f.name: f for f in instance_fields}
    seen_field_names: set[str] = set()
    merged_fields: list[PyField] = []
    for f in class_fields:
        seen_field_names.add(f.name)
        if f.default_value is None and f.name in instance_by_name:
            init_field = instance_by_name[f.name]
            if init_field.default_value is not None:
                f.default_value = init_field.default_value
        merged_fields.append(f)
    for f in instance_fields:
        if f.name not in seen_field_names:
            seen_field_names.add(f.name)
            merged_fields.append(f)

    return PyClass(
        name=cls_node.name,
        base_classes=base_classes,
        is_monobehaviour=is_mono,
        is_enum=is_enum,
        is_scriptable_object=is_scriptable,
        create_asset_menu=create_asset_menu,
        fields=merged_fields,
        methods=methods,
    )


def parse_python_file(path: str | Path) -> PyFile:
    """Parse a Python file from disk."""
    source = Path(path).read_text(encoding="utf-8")
    return parse_python(source)
