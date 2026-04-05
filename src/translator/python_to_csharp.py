"""Python to C# translator — converts Python simulator code to idiomatic Unity C#."""

from __future__ import annotations

import json
import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from src.translator.python_parser import PyFile, PyClass, PyField, PyMethod, parse_python_file
from src.translator.type_mapper import (
    TypeMapper, snake_to_pascal, snake_to_camel,
)

_RULES_DIR = Path(__file__).parent / "rules"
_TEMPLATE_DIR = Path(__file__).parent / "templates"
_translation_rules = json.loads((_RULES_DIR / "translation_rules.json").read_text())
_lifecycle_map_reverse: dict[str, str] = {v: k for k, v in _translation_rules["lifecycle_method_mapping"].items()}
_api_reverse: dict[str, str] = {v: k for k, v in _translation_rules["api_translations"].items()}

_type_mapper = TypeMapper()
_jinja_env = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), trim_blocks=True, lstrip_blocks=True)


# ── Translation config (set per-call) ─────────────────────────

class _TranslationConfig:
    """Per-translation configuration, set by translate()/translate_file()."""
    unity_version: int = 6
    input_system: str = "new"  # "legacy" or "new"

_config = _TranslationConfig()


def translate_file(
    path: str | Path,
    *,
    namespace: str | None = None,
    unity_version: int = 6,
    input_system: str = "new",
) -> str:
    """Translate a Python file to C# source code."""
    parsed = parse_python_file(path)
    return translate(parsed, namespace=namespace, unity_version=unity_version, input_system=input_system)


def translate(
    parsed: PyFile,
    namespace: str | None = None,
    *,
    unity_version: int = 6,
    input_system: str = "new",
) -> str:
    """Translate a PyFile IR to C# source code.

    Args:
        parsed: The parsed Python IR.
        namespace: Optional C# namespace to wrap the output in.
        unity_version: Target Unity version (default 6). Affects API mappings.
        input_system: "legacy" or "new" (default "new"). Controls Input API translation.
    """
    _config.unity_version = unity_version
    _config.input_system = input_system

    # Build enum value mapping for UPPER_SNAKE -> PascalCase conversion in expressions
    global _enum_values
    _enum_values = {}
    for cls in parsed.classes:
        if cls.is_enum:
            for f in cls.fields:
                if f.is_class_level and f.name.isupper():
                    pascal = _upper_snake_to_pascal(f.name)
                    _enum_values[f"{cls.name}.{f.name}"] = f"{cls.name}.{pascal}"

    results = []
    for cls in parsed.classes:
        results.append(_translate_class(cls, parsed))

    # Hoist all 'using' directives to the top of the file so multi-class
    # files don't have using statements scattered between class definitions
    all_using: list[str] = []
    class_bodies: list[str] = []
    for block in results:
        lines = block.split("\n")
        usings = []
        body_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("using ") and stripped.endswith(";"):
                usings.append(stripped)
            elif stripped:
                body_lines.append(line)
        all_using.extend(usings)
        class_bodies.append("\n".join(body_lines))

    # Deduplicate and sort using directives
    unique_using = sorted(set(all_using))
    using_block = "\n".join(unique_using)
    code = using_block + "\n" + "\n".join(class_bodies).rstrip() + "\n"

    if namespace:
        # Indent class bodies inside the namespace, using stays outside
        body_only = "\n".join(class_bodies).rstrip() + "\n"
        indented = "\n".join(
            ("    " + line if line.strip() else line)
            for line in body_only.split("\n")
        )
        code = using_block + "\n" + f"namespace {namespace}\n{{\n{indented}}}\n"

    return code


def _translate_class(cls: PyClass, parsed: PyFile) -> str:
    """Translate a PyClass to C# source."""
    if cls.is_enum:
        return _translate_enum(cls)
    if cls.is_monobehaviour:
        return _translate_monobehaviour(cls, parsed)
    return _translate_plain_class(cls, parsed)


def _upper_snake_to_pascal(name: str) -> str:
    """Convert UPPER_SNAKE_CASE to PascalCase (e.g. BEFORE_THROWN -> BeforeThrown)."""
    return "".join(word.capitalize() for word in name.lower().split("_"))


def _translate_enum(cls: PyClass) -> str:
    """Translate a Python Enum class to a C# enum."""
    lines = ["public enum " + cls.name, "{"]
    members = []
    for f in cls.fields:
        if f.is_class_level and f.name.isupper():
            pascal_name = _upper_snake_to_pascal(f.name)
            members.append(f"    {pascal_name}")
        elif f.is_class_level:
            members.append(f"    {snake_to_pascal(f.name)}")
    lines.append(",\n".join(members))
    lines.append("}")
    return "\n".join(lines)


def _infer_attributes(cls: PyClass) -> list[str]:
    """Infer C# class-level attributes from usage patterns."""
    attrs = []
    # Detect RequireComponent from get_component() calls in start/awake
    required_components: set[str] = set()
    for method in cls.methods:
        if method.name in ("start", "awake"):
            for match in re.finditer(r"get_component\((\w+)\)", method.body_source):
                comp_type = match.group(1)
                required_components.add(comp_type)
    for comp in sorted(required_components):
        attrs.append(f"[RequireComponent(typeof({comp}))]")
    return attrs


def _build_symbol_table(cls: PyClass) -> dict[str, str]:
    """Build a mapping of Python names → C# names for fields, methods, and params."""
    symbols: dict[str, str] = {}

    # Map field names: snake_case → camelCase, UPPER_CASE stays as-is
    for field in cls.fields:
        py_name = field.name
        if py_name.isupper():
            cs_name = py_name  # Preserve UPPER_CASE constants
        else:
            cs_name = snake_to_camel(py_name)
        symbols[py_name] = cs_name
        # Also map _private variants
        if not py_name.startswith("_"):
            symbols[f"_{py_name}"] = cs_name

    # Map method names: snake_case → PascalCase (or lifecycle mapping)
    for method in cls.methods:
        py_name = method.name
        if py_name in _lifecycle_map_reverse:
            symbols[py_name] = _lifecycle_map_reverse[py_name]
        else:
            symbols[py_name] = snake_to_pascal(py_name)
        # Also map _private variants
        if not py_name.startswith("_"):
            symbols[f"_{py_name}"] = symbols[py_name]
        else:
            symbols[py_name] = snake_to_pascal(py_name.lstrip("_"))

    return symbols


def _discover_dynamic_fields(cls: PyClass) -> list[PyField]:
    """Find self.X = Y assignments in ALL methods that aren't in __init__."""
    known_fields = {f.name for f in cls.fields}
    dynamic: dict[str, str] = {}

    for method in cls.methods:
        # Match both self.field = value AND self.field: Type = value (single line only)
        for line in method.body_source.split("\n"):
            m = re.match(r".*self\.(\w+)(?:\s*:\s*([^=\n]+?))?\s*=\s*(.+)", line)
            if not m:
                continue
            field_name = m.group(1)
            type_annotation = (m.group(2) or "").strip()
            value = m.group(3).strip()
            if field_name not in known_fields and field_name not in dynamic:
                # Use explicit type annotation if present, otherwise infer from value
                if type_annotation:
                    # Strip | None suffix for the field type
                    clean_type = re.sub(r"\s*\|\s*None\s*$", "", type_annotation).strip()
                    dynamic[field_name] = clean_type
                else:
                    inferred = _infer_type_from_value(value)
                    dynamic[field_name] = inferred

    return [PyField(name=name, type_annotation=ann, default_value=None, is_class_level=False)
            for name, ann in dynamic.items()]


def _infer_type_from_value(value: str) -> str:
    """Infer type annotation from an assignment value."""
    v = value.strip()
    # X.add_component(T) or X.AddComponent<T>
    m = re.match(r"\w+\.add_component\((\w+)\)", v)
    if m:
        return m.group(1)
    # X.get_component(T)
    m = re.match(r"\w+\.get_component\((\w+)\)", v)
    if m:
        return m.group(1)
    # GameObject("name")
    if v.startswith("GameObject("):
        return "GameObject"
    # Numeric
    if re.match(r"^-?\d+$", v):
        return "int"
    if re.match(r"^-?\d+\.\d+$", v):
        return "float"
    if v in ("True", "False"):
        return "bool"
    if v.startswith("'") or v.startswith('"'):
        return "string"
    if v.startswith("Vector2("):
        return "Vector2"
    if v.startswith("Vector3("):
        return "Vector3"
    if v == "None" or v == "null":
        return ""  # Can't infer
    # Color tuple: (R, G, B)
    if re.match(r"^\(\d+,\s*\d+,\s*\d+\)$", v):
        return "Color32"
    # List of color tuples: [(R,G,B), ...]
    if re.match(r"^\[.*\(\d+,\s*\d+,\s*\d+\).*\]$", v):
        return "Color32[]"
    # Method reference: self._method_name → Action delegate
    if re.match(r"self\.\w+", v) and "(" not in v:
        return "System.Action"
    return ""


def _infer_field_types(cls: PyClass) -> dict[str, str]:
    """Infer field types from get_component() calls in start/awake and type annotations."""
    type_map: dict[str, str] = {}

    # 1. From type annotations (strip | None suffix)
    for field in cls.fields:
        if field.type_annotation:
            t = field.type_annotation.strip()
            # Strip "| None" suffix
            if t.endswith("| None"):
                t = t[:-7].strip()
            if t and t not in ("", "list", "dict", "object"):
                type_map[field.name] = t

    # 2. From get_component(T) calls in start/awake
    for method in cls.methods:
        if method.name in ("start", "awake"):
            for m in re.finditer(r"self\.(\w+)\s*=\s*\w+\.get_component\((\w+)\)", method.body_source):
                field_name = m.group(1)
                comp_type = m.group(2)
                type_map[field_name] = comp_type

    # 3. From GameObject.find patterns
    for method in cls.methods:
        if method.name in ("start", "awake"):
            for m in re.finditer(r"self\.(\w+)\s*=\s*GameObject\.find\(", method.body_source):
                field_name = m.group(1)
                if field_name not in type_map:
                    type_map[field_name] = "GameObject"

    # 4. Fix array→List when .append() is used, and infer element type
    all_body = " ".join(m.body_source for m in cls.methods)
    for field in cls.fields:
        field_name = field.name
        if f"self.{field_name}.append(" in all_body:
            # Find what's being appended
            append_match = re.search(rf"self\.{re.escape(field_name)}\.append\((\w+)\)", all_body)
            appended_var = append_match.group(1) if append_match else None

            # Infer element type from the appended variable
            element_type = None
            if appended_var:
                # Check if appended var comes from get_component(T)
                comp_match = re.search(rf"{re.escape(appended_var)}\s*=\s*\w+\.get_component\((\w+)\)", all_body)
                if comp_match:
                    element_type = comp_match.group(1)

            t = type_map.get(field_name, field.type_annotation or "")
            if element_type:
                type_map[field_name] = f"List<{element_type}>"
            elif "list[" in t:
                list_match = re.match(r"list\[(.+)\]", t)
                if list_match:
                    inner = list_match.group(1)
                    type_map[field_name] = f"List<{inner}>"
            elif t.endswith("[]"):
                inner = t[:-2]
                type_map[field_name] = f"List<{inner}>"
            elif t in ("list", "List<object>", ""):
                if element_type:
                    type_map[field_name] = f"List<{element_type}>"

    # 5. Detect callable fields (self.field = self.method — no parens → Action)
    for method in cls.methods:
        for m in re.finditer(r"self\.(\w+)\s*=\s*self\.(\w+)\s*$", method.body_source, re.MULTILINE):
            field_name = m.group(1)
            target_name = m.group(2)
            # If target is a method name (no parens = method reference)
            method_names = {meth.name for meth in cls.methods}
            if target_name in method_names or target_name.lstrip("_") in method_names:
                type_map[field_name] = "System.Action"

    return type_map


# Thread-local symbol table for the current class being translated
_current_symbols: dict[str, str] = {}
_declared_vars: set[str] = set()
_enumerate_inject: str | None = None
_bool_fields: set[str] = set()  # C# names of fields with bool type
_array_fields: set[str] = set()  # C# names of fields with array types (use .Length not .Count)
_enum_values: dict[str, str] = {}  # "EnumType.UPPER_SNAKE" -> "EnumType.PascalCase"


def _translate_monobehaviour(cls: PyClass, parsed: PyFile) -> str:
    """Translate a MonoBehaviour subclass using the Jinja2 template."""
    global _current_symbols, _bool_fields, _array_fields
    _bool_fields = set()
    _array_fields = set()
    extra_using = _infer_using_directives(cls, parsed)
    attributes = _infer_attributes(cls)

    # Discover dynamic fields (self.X = Y in methods, not in __init__)
    dynamic_fields = _discover_dynamic_fields(cls)
    cls.fields.extend(dynamic_fields)

    # Build symbol table for consistent naming in method bodies
    _current_symbols = _build_symbol_table(cls)

    # Add module-level constants to symbol table (they stay UPPER_CASE)
    for mc in parsed.module_constants:
        _current_symbols[mc.name] = mc.name  # Keep UPPER_CASE as-is

    # Infer field types from annotations and get_component() calls
    inferred_types = _infer_field_types(cls)

    serialized_fields = []
    private_fields = []
    static_fields = []

    # Add module-level constants as static fields (only simple types)
    for mc in parsed.module_constants:
        mc_type = _infer_constant_type(mc.default_value)
        if not mc_type:
            continue
        mc_default = _py_value_to_csharp(mc.default_value, mc_type)
        if mc_default:
            static_fields.append({
                "csharp_type": mc_type,
                "csharp_name": mc.name,
                "default": mc_default,
            })

    for field in cls.fields:
        # Use inferred type if available, otherwise fall back to annotation
        if field.name in inferred_types:
            csharp_type = _py_type_to_csharp(inferred_types[field.name], is_field=True)
        else:
            csharp_type = _py_type_to_csharp(field.type_annotation, is_field=True, default_value=field.default_value or "")
        csharp_name = snake_to_camel(field.name)
        default = _py_value_to_csharp(field.default_value, csharp_type) if field.default_value else None

        # Track bool fields so condition translator can avoid != null
        if csharp_type == "bool":
            _bool_fields.add(csharp_name)
        # Track array fields so len() translator can use .Length not .Count
        if csharp_type.endswith("[]"):
            _array_fields.add(csharp_name)

        entry = {
            "csharp_type": csharp_type,
            "csharp_name": csharp_name,
            "default": default,
        }

        if field.is_class_level:
            static_fields.append(entry)
        elif default is not None and default != "null":
            serialized_fields.append(entry)
        else:
            private_fields.append(entry)

    methods = []
    for method in cls.methods:
        methods.append(_translate_method(method))

    template = _jinja_env.get_template("monobehaviour.cs.j2")
    return template.render(
        class_name=cls.name,
        extra_using=extra_using,
        attributes=attributes,
        serialized_fields=serialized_fields,
        private_fields=private_fields,
        static_fields=static_fields,
        methods=methods,
    )


def _translate_plain_class(cls: PyClass, parsed: PyFile) -> str:
    """Translate a non-MonoBehaviour class to C#."""
    # using directives are hoisted by translate() — just emit the class body
    lines = ["using UnityEngine;"]
    base = cls.base_classes[0] if cls.base_classes else ""
    base_str = f" : {base}" if base else ""
    lines.append(f"public class {cls.name}{base_str}")
    lines.append("{")

    for field in cls.fields:
        csharp_type = _py_type_to_csharp(field.type_annotation, is_field=True, default_value=field.default_value or "")
        csharp_name = snake_to_camel(field.name)
        mod = "public static" if field.is_class_level else "private"
        default = _py_value_to_csharp(field.default_value, csharp_type) if field.default_value else None
        init = f" = {default}" if default else ""
        lines.append(f"    {mod} {csharp_type} {csharp_name}{init};")

    for method in cls.methods:
        m = _translate_method(method)
        lines.append("")
        lines.append(f"    {m['access']} {m['return_type']} {m['csharp_name']}({m['params']})")
        lines.append("    {")
        lines.append(m['body'])
        lines.append("    }")

    lines.append("}")
    return "\n".join(lines)


def _translate_method(method: PyMethod) -> dict:
    """Translate a PyMethod to a C# method dict for the template."""
    global _current_symbols

    # Name
    if method.name in _lifecycle_map_reverse:
        csharp_name = _lifecycle_map_reverse[method.name]
    else:
        csharp_name = snake_to_pascal(method.name)

    # Access modifier
    if method.is_static:
        access = "public static"
    elif method.is_lifecycle:
        access = "void"
        return_type = ""
    else:
        access = "public"

    # Return type — prefer annotation, then infer from body
    if method.is_coroutine:
        return_type = "IEnumerator"
    elif method.return_annotation:
        return_type = _py_type_to_csharp(method.return_annotation)
        if return_type == "var":
            return_type = "object"  # var not valid for return types
    else:
        return_type = _infer_return_type(method)

    # Parameters — add to symbol table for this method's scope
    saved_symbols = dict(_current_symbols)
    # Trigger callbacks: Unity receives Collider2D, not GameObject
    # In the Python simulator, triggers receive GameObject directly — override the annotation
    _trigger_methods = {"on_trigger_enter_2d", "on_trigger_exit_2d", "on_trigger_stay_2d"}
    params = []
    for p in method.parameters:
        if method.name in _trigger_methods and p.name in ("other", "collider"):
            csharp_type = "Collider2D"
        elif p.type_annotation:
            csharp_type = _py_type_to_csharp(p.type_annotation)
        else:
            csharp_type = _infer_param_type(p.name, method)
        csharp_param_name = snake_to_camel(p.name)
        params.append(f"{csharp_type} {csharp_param_name}")
        # Add param to symbol table
        _current_symbols[p.name] = csharp_param_name
    params_str = ", ".join(params)

    # Extract local variable names and add to symbol table
    _add_locals_to_symbols(method.body_source)

    # Body
    body = _translate_body(method.body_source)

    # Restore symbol table (remove method-scoped names)
    _current_symbols = saved_symbols

    # Fix access for lifecycle methods
    if method.is_lifecycle:
        access = ""

    return {
        "access": access,
        "return_type": return_type,
        "csharp_name": csharp_name,
        "params": params_str,
        "body": body,
    }


def _add_locals_to_symbols(body_source: str) -> None:
    """Extract local variable assignments and add to symbol table."""
    global _current_symbols
    for line in body_source.split("\n"):
        stripped = line.strip()
        # Match: var_name: Type = expression (typed assignment)
        m = re.match(r"^([a-z_]\w*)\s*:\s*\S+.*=\s*", stripped)
        if m and not stripped.startswith("self."):
            py_name = m.group(1)
            if py_name not in _current_symbols and "_" in py_name:
                _current_symbols[py_name] = snake_to_camel(py_name)
            continue
        # Match: var_name = expression (not self.var_name)
        m = re.match(r"^([a-z_]\w*)\s*=\s*", stripped)
        if m and not stripped.startswith("self."):
            py_name = m.group(1)
            if py_name not in _current_symbols and "_" in py_name:
                _current_symbols[py_name] = snake_to_camel(py_name)
        # Match for-loop variables: for var_name in ...
        m = re.match(r"^for\s+(\w+)\s+in\s+", stripped)
        if m:
            py_name = m.group(1)
            if py_name not in _current_symbols and "_" in py_name:
                _current_symbols[py_name] = snake_to_camel(py_name)
        # Match: for idx, var in enumerate(...)
        m = re.match(r"^for\s+(\w+),\s*(\w+)\s+in\s+", stripped)
        if m:
            for py_name in [m.group(1), m.group(2)]:
                if py_name not in _current_symbols and "_" in py_name:
                    _current_symbols[py_name] = snake_to_camel(py_name)


def _infer_constant_type(value: str | None) -> str:
    """Infer C# type from a constant value."""
    if value is None:
        return "object"
    v = value.strip()
    if re.match(r"^-?\d+$", v):
        return "int"
    if re.match(r"^-?\d+\.\d+$", v):
        return "float"
    if v in ("True", "False"):
        return "bool"
    if v.startswith("'") or v.startswith('"'):
        return "string"
    # Color tuple: (R, G, B)
    if re.match(r"^\(\d+,\s*\d+,\s*\d+\)$", v):
        return "Color32"
    # List of color tuples
    if re.match(r"^\[.*\(\d+,\s*\d+,\s*\d+\).*\]$", v):
        return "Color32[]"
    # Constructor types: Vector2(...), Vector3(...), etc.
    for ctor in ("Vector2", "Vector3", "Quaternion", "Color"):
        if v.startswith(f"{ctor}("):
            return ctor
    # Complex types (lists, dicts) — skip, they can't be simple constants
    return ""


def _infer_return_type(method: PyMethod) -> str:
    """Infer C# return type from method body."""
    body = method.body_source
    # Check for return statements with values
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped.startswith("return ") and stripped != "return":
            value = stripped[7:].strip()
            if value == "True" or value == "False":
                return "bool"
            if re.match(r"^\d+$", value):
                return "int"
            if re.match(r"^\d+\.\d+$", value):
                return "float"
            if value.startswith("(") and value.endswith(")"):
                return "object"  # tuple
            # Default for non-void returns — use object as fallback
            return "object"
    return "void"


def _infer_param_type(param_name: str, method: PyMethod) -> str:
    """Infer C# type from parameter name and usage when no annotation exists."""
    # Known Unity callback params
    if param_name in ("collision",):
        return "Collision2D"
    if param_name in ("other",):
        return "Collider2D"

    # Common param names → types
    _PARAM_TYPE_MAP = {
        "position": "Vector3",
        "hit_point": "Vector3",
        "point": "Vector2",
        "direction": "Vector3",
        "force": "Vector2",
        "velocity": "Vector2",
        "target": "Transform",
        "other_collider": "BoxCollider2D",
        "collider": "Collider2D",
        "side": "string",
        "name": "string",
        "tag": "string",
        "score": "int",
        "speed": "float",
        "duration": "float",
        "delay": "float",
        "count": "int",
        "index": "int",
        "player": "Player",
        "invader": "Invader",
        "mystery_ship": "MysteryShip",
    }

    if param_name in _PARAM_TYPE_MAP:
        return _PARAM_TYPE_MAP[param_name]

    # Infer from usage in method body
    body = method.body_source
    if f"{param_name}.x" in body or f"{param_name}.y" in body:
        return "Vector2"
    if f"{param_name}.game_object" in body or f"{param_name}.transform" in body:
        return "Component"
    if f"{param_name}.size" in body:
        return "BoxCollider2D"

    return "object"


def _join_multiline(raw_lines: list[str]) -> list[tuple[int, str]]:
    """Join Python multi-line expressions into single logical lines.

    Handles:
    - Open parentheses/brackets spanning lines
    - Backslash line continuations
    - Preserves indent of the FIRST line in a group
    """
    result: list[tuple[int, str]] = []
    current = ""
    current_indent = 0
    paren_depth = 0

    for raw_line in raw_lines:
        stripped = raw_line.strip()
        if not stripped:
            continue

        if current == "":
            # Start of a new logical line — record indent
            indent = len(raw_line) - len(raw_line.lstrip())
            current_indent = indent // 4

        # Handle backslash continuation
        if stripped.endswith("\\"):
            current += stripped[:-1].strip() + " "
            continue

        current += stripped

        # Count parens/brackets to detect multi-line expressions
        for ch in stripped:
            if ch in "([":
                paren_depth += 1
            elif ch in ")]":
                paren_depth -= 1

        if paren_depth <= 0:
            paren_depth = 0
            result.append((current_indent, current.strip()))
            current = ""
        else:
            current += " "

    # Flush any remaining
    if current.strip():
        result.append((current_indent, current.strip()))

    return result


def _translate_body(body: str) -> str:
    """Translate Python method body to C#, adding braces for indented blocks."""
    if not body.strip():
        return ""

    raw_lines = body.split("\n")

    # First pass: join multi-line expressions into logical lines
    logical_lines = _join_multiline(raw_lines)

    # Track declared local variables to avoid redeclaration
    global _declared_vars, _enumerate_inject
    _declared_vars = set()
    _enumerate_inject = None

    # Second pass: translate each logical line
    entries: list[tuple[int, str]] = []
    strip_block_indent: int | None = None  # When set, skip lines deeper than this
    for indent_level, logical_line in logical_lines:
        # If we're stripping a block, skip until indent returns to block level
        if strip_block_indent is not None:
            if indent_level > strip_block_indent:
                continue  # Skip indented body of stripped block
            else:
                strip_block_indent = None  # Block ended, resume

        if not logical_line or logical_line == "pass" or logical_line == "super().__init__()":
            continue
        translated = _translate_py_statement(logical_line)
        if not translated:
            continue
        if translated == "__STRIP_BLOCK__":
            strip_block_indent = indent_level
            continue
        entries.append((indent_level, translated))
        # Inject enumerate variable declaration after the for-loop line
        if _enumerate_inject and translated.startswith("for ("):
            # Will be injected as first line inside the block (higher indent)
            entries.append((indent_level + 1, _enumerate_inject))
            _enumerate_inject = None

    if not entries:
        return ""

    # Third pass: emit with braces on indentation changes
    lines = []
    base_indent = "        "
    prev_indent = entries[0][0]
    indent_stack: list[int] = []

    for i, (level, text) in enumerate(entries):
        if level > prev_indent:
            lines.append(f"{base_indent}{'    ' * prev_indent}{{")
            indent_stack.append(prev_indent)
        elif level < prev_indent:
            while indent_stack and indent_stack[-1] >= level:
                close_level = indent_stack.pop()
                lines.append(f"{base_indent}{'    ' * close_level}}}")

        cs_indent = base_indent + "    " * level
        lines.append(f"{cs_indent}{text}")
        prev_indent = level

    while indent_stack:
        close_level = indent_stack.pop()
        lines.append(f"{base_indent}{'    ' * close_level}}}")

    return "\n".join(lines)


def _translate_py_statement(line: str) -> str:
    """Translate a single Python statement to C#."""
    # Strip inline comments: code  # comment -> code
    if "  #" in line:
        line = line[:line.index("  #")].rstrip()
    if not line:
        return ""

    # Docstrings — strip them entirely
    if line.startswith('"""') or line.startswith("'''"):
        return ""
    if line.endswith('"""') or line.endswith("'''"):
        return ""
    if '"""' in line:
        return ""

    # Inline imports — strip (these are Python-only, C# uses using directives)
    if line.startswith("from ") and " import " in line:
        return ""
    if re.match(r"^import\s+\w+", line):
        return ""

    # try/except → try/catch
    if line == "try:":
        return "try"
    if line.startswith("except") and line.endswith(":"):
        exc = line[6:].strip().rstrip(":").strip()
        if exc:
            return f"catch ({exc.split(' as ')[0]}) {{ }}"
        return "catch { }"

    # Comments
    if line.startswith("#"):
        return f"// {line[1:].strip()}"

    # If/elif/else
    if line.startswith("if ") and line.endswith(":"):
        cond = line[3:-1].strip()
        cond = _translate_py_condition(cond)
        # If condition contains stripped simulator code, skip entire block
        if "__STRIP__" in cond:
            return "__STRIP_BLOCK__"
        return f"if ({cond})"
    if line.startswith("elif ") and line.endswith(":"):
        cond = line[5:-1].strip()
        cond = _translate_py_condition(cond)
        return f"else if ({cond})"
    if line == "else:":
        return "else"
    if line.startswith("while ") and line.endswith(":"):
        cond = line[6:-1].strip()
        cond = _translate_py_condition(cond)
        return f"while ({cond})"
    if line.startswith("for ") and line.endswith(":"):
        return _translate_for_loop(line)

    # Yield (coroutine)
    if line.startswith("yield "):
        value = line[6:].strip()
        if value == "None" or value == "":
            return "yield return null;"
        value = _translate_py_expression(value)
        return f"yield return new {value};"
    if line == "yield":
        return "yield return null;"

    # Return
    if line.startswith("return "):
        value = line[7:].strip()
        value = _translate_py_expression(value)
        return f"return {value};"
    if line == "return":
        return "return;"

    # Compound assignment
    compound_match = re.match(r"^([\w.]+)\s*([+\-*/])=\s*(.+)$", line)
    if compound_match:
        target, op, value = compound_match.groups()
        cs_target = _translate_py_expression(target)
        cs_value = _translate_py_expression(value)
        return f"{cs_target} {op}= {cs_value};"

    # gameObject.active = X -> gameObject.SetActive(X)
    # ANY .active = X assignment → .SetActive(X) (Unity pattern)
    active_match = re.match(r"^([\w.]+)\.active\s*=\s*(.+)$", line)
    if active_match:
        target = _translate_py_expression(active_match.group(1))
        value = _translate_py_expression(active_match.group(2))
        return f"{target}.SetActive({value});"

    # Tuple unpacking: a, b = expr1, expr2 -> int a = expr1; int b = expr2;
    tuple_match = re.match(r"^(\w+),\s*(\w+)\s*=\s*(.+)$", line)
    if tuple_match:
        a = tuple_match.group(1)
        b = tuple_match.group(2)
        rhs = tuple_match.group(3)
        # Split RHS by comma (respecting parens)
        parts = _split_args(rhs)
        cs_a = _translate_py_expression(a)
        cs_b = _translate_py_expression(b)
        if len(parts) == 2:
            val_a = _translate_py_expression(parts[0].strip())
            val_b = _translate_py_expression(parts[1].strip())
            _declared_vars.add(cs_a)
            _declared_vars.add(cs_b)
            return f"var {cs_a} = {val_a}; var {cs_b} = {val_b};"
        else:
            # Single value — use C# tuple deconstruction
            val = _translate_py_expression(rhs)
            _declared_vars.add(cs_a)
            _declared_vars.add(cs_b)
            # Handle nullable tuples: result.Value for (T1,T2)? types
            return f"var ({cs_a}, {cs_b}) = {val}.Value;"

    # Typed self.field assignment: self.field: Type = value (strip annotation, emit field = value)
    self_typed = re.match(r"^self\.(\w+)\s*:\s*.+?\s*=\s*(.+)$", line)
    if self_typed:
        field_name, value = self_typed.groups()
        cs_field = _translate_py_expression(f"self.{field_name}")
        cs_value = _translate_py_expression(value)
        return f"{cs_field} = {cs_value};"

    # Typed assignment: var: Type = value (Python type annotation on local variable)
    typed_assign = re.match(r"^(\w+)\s*:\s*(.+?)\s*=\s*(.+)$", line)
    if typed_assign and "." not in typed_assign.group(1):
        var_name, py_type, value = typed_assign.groups()
        cs_target = _translate_py_expression(var_name)
        cs_value = _translate_py_expression(value)
        if cs_value == "__STRIP__":
            return ""
        # Convert Python type to C# type
        cs_type = _translate_type_annotation(py_type)
        if cs_target in _declared_vars:
            return f"{cs_target} = {cs_value};"
        _declared_vars.add(cs_target)
        return f"{cs_type} {cs_target} = {cs_value};"

    # Typed declaration without assignment: var: Type (no =)
    typed_decl = re.match(r"^(\w+)\s*:\s*(.+)$", line)
    if typed_decl and "." not in typed_decl.group(1) and "=" not in typed_decl.group(2):
        var_name, py_type = typed_decl.groups()
        cs_target = _translate_py_expression(var_name)
        cs_type = _translate_type_annotation(py_type)
        if cs_target not in _declared_vars:
            _declared_vars.add(cs_target)
            return f"{cs_type} {cs_target};"
        return ""  # Already declared, skip

    # Assignment
    assign_match = re.match(r"^([\w.]+)\s*=\s*(.+)$", line)
    if assign_match:
        target, value = assign_match.groups()
        cs_target = _translate_py_expression(target)
        cs_value = _translate_py_expression(value)
        if cs_value == "__STRIP__":
            return ""
        # Strip simulator-only property assignments
        if re.search(r"\.(clipRef|assetRef)\s*$", cs_target):
            return ""
        # Infer type for variable declarations (skip if already declared)
        if "." not in target and not target.startswith("self"):
            if cs_target in _declared_vars:
                # Already declared — just assign
                return f"{cs_target} = {cs_value};"
            _declared_vars.add(cs_target)
            cs_type = _infer_expression_type(value)
            return f"{cs_type} {cs_target} = {cs_value};"
        return f"{cs_target} = {cs_value};"

    # Expression (method call, etc.)
    expr = _translate_py_expression(line)
    if expr == "__STRIP__":
        return ""
    return f"{expr};"


def _translate_for_loop(line: str) -> str:
    """Translate a Python for-loop to C# for/foreach."""
    # Strip 'for ' prefix and ':' suffix
    body = line[4:-1].strip()

    # Match: var in range(...)
    range_match = re.match(r"(\w+)\s+in\s+range\((.+)\)$", body)
    if range_match:
        var = range_match.group(1)
        args_str = range_match.group(2)
        args = _split_args(args_str)
        cs_var = snake_to_camel(var)
        if len(args) == 1:
            # range(n) -> for (int var = 0; var < n; var++)
            limit = _translate_py_expression(args[0])
            return f"for (int {cs_var} = 0; {cs_var} < {limit}; {cs_var}++)"
        elif len(args) == 2:
            # range(start, end) -> for (int var = start; var < end; var++)
            start = _translate_py_expression(args[0])
            end = _translate_py_expression(args[1])
            return f"for (int {cs_var} = {start}; {cs_var} < {end}; {cs_var}++)"
        elif len(args) == 3:
            # range(start, end, step) -> for (int var = start; var < end; var += step)
            start = _translate_py_expression(args[0])
            end = _translate_py_expression(args[1])
            step = _translate_py_expression(args[2])
            return f"for (int {cs_var} = {start}; {cs_var} < {end}; {cs_var} += {step})"

    # Match: idx, var in enumerate(collection)
    enum_match = re.match(r"(\w+),\s*(\w+)\s+in\s+enumerate\((.+)\)$", body)
    if enum_match:
        idx_var = snake_to_camel(enum_match.group(1))
        val_var = snake_to_camel(enum_match.group(2))
        collection = _translate_py_expression(enum_match.group(3).strip())
        _declared_vars.add(idx_var)
        _declared_vars.add(val_var)
        # The body translator will add the val_var declaration as first line in the block
        # We store it for injection
        global _enumerate_inject
        _enumerate_inject = f"var {val_var} = {collection}[{idx_var}];"
        prop = ".Length" if collection in _array_fields else ".Count"
        return f"for (int {idx_var} = 0; {idx_var} < {collection}{prop}; {idx_var}++)"

    # Match: var in collection (foreach)
    foreach_match = re.match(r"(\w+)\s+in\s+(.+)$", body)
    if foreach_match:
        var = foreach_match.group(1)
        collection = foreach_match.group(2).strip()
        cs_var = snake_to_camel(var)
        cs_collection = _translate_py_expression(collection)
        return f"foreach (var {cs_var} in {cs_collection})"

    # Tuple unpacking: var1, var2 in collection — emit TODO
    return f"// TODO: translate for loop: {line}"


def _split_args(args_str: str) -> list[str]:
    """Split comma-separated arguments respecting parentheses."""
    result = []
    depth = 0
    current = ""
    for ch in args_str:
        if ch in "([{":
            depth += 1
            current += ch
        elif ch in ")]}":
            depth -= 1
            current += ch
        elif ch == "," and depth == 0:
            result.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        result.append(current.strip())
    return result


def _translate_len_calls(expr: str) -> str:
    """Translate len(x) to x.Count."""
    # Find len( and match balanced parens
    while True:
        match = re.search(r"\blen\(", expr)
        if not match:
            break
        start = match.start()
        paren_start = match.end() - 1  # position of '('
        depth = 1
        pos = paren_start + 1
        while pos < len(expr) and depth > 0:
            if expr[pos] == "(":
                depth += 1
            elif expr[pos] == ")":
                depth -= 1
            pos += 1
        if depth == 0:
            inner = expr[paren_start + 1:pos - 1]
            inner_translated = _translate_py_expression(inner)
            # Use .Length for arrays, .Count for Lists
            prop = ".Length" if inner_translated in _array_fields else ".Count"
            expr = expr[:start] + f"{inner_translated}{prop}" + expr[pos:]
        else:
            break
    return expr


def _translate_all_call(expr: str) -> str:
    """Translate all(pred for x in coll) to coll.All(x => pred)."""
    match = re.match(r"^all\((.+)\s+for\s+(\w+)\s+in\s+(.+)\)$", expr)
    if match:
        pred = match.group(1).strip()
        var = match.group(2)
        coll = match.group(3).strip()
        cs_var = snake_to_camel(var)
        cs_coll = _translate_py_expression(coll)
        cs_pred = _translate_py_condition(pred.replace(var, cs_var))
        return f"{cs_coll}.All({cs_var} => {cs_pred})"
    return expr


def _translate_any_call(expr: str) -> str:
    """Translate any(pred for x in coll) to coll.Any(x => pred)."""
    match = re.match(r"^any\((.+)\s+for\s+(\w+)\s+in\s+(.+)\)$", expr)
    if match:
        pred = match.group(1).strip()
        var = match.group(2)
        coll = match.group(3).strip()
        cs_var = snake_to_camel(var)
        cs_coll = _translate_py_expression(coll)
        cs_pred = _translate_py_condition(pred.replace(var, cs_var))
        return f"{cs_coll}.Any({cs_var} => {cs_pred})"
    return expr


def _translate_sum_count_call(expr: str) -> str:
    """Translate sum(1 for x in coll if cond) to coll.Count(x => cond)."""
    match = re.match(r"^sum\(1\s+for\s+(\w+)\s+in\s+(.+?)\s+if\s+(.+)\)$", expr)
    if match:
        var = match.group(1)
        coll = match.group(2).strip()
        cond = match.group(3).strip()
        cs_var = snake_to_camel(var)
        cs_coll = _translate_py_expression(coll)
        cs_cond = _translate_py_condition(cond.replace(var, cs_var))
        return f"{cs_coll}.Count({cs_var} => {cs_cond})"
    return expr


def _translate_list_comprehension(expr: str) -> str:
    """Translate [expr for x in coll if cond] to LINQ."""
    # Match [mapping for var in collection if condition]
    match = re.match(r"^\[(.+?)\s+for\s+(\w+)\s+in\s+(.+?)\s+if\s+(.+)\]$", expr)
    if match:
        mapping = match.group(1).strip()
        var = match.group(2)
        coll = match.group(3).strip()
        cond = match.group(4).strip()
        cs_var = snake_to_camel(var)
        cs_coll = _translate_py_expression(coll)
        cs_cond = _translate_py_condition(cond.replace(var, cs_var))
        cs_mapping = _translate_py_expression(mapping.replace(var, cs_var))
        # If mapping is just the variable, skip Select
        if cs_mapping == cs_var:
            return f"{cs_coll}.Where({cs_var} => {cs_cond}).ToList()"
        return f"{cs_coll}.Where({cs_var} => {cs_cond}).Select({cs_var} => {cs_mapping}).ToList()"

    # Match [mapping for var in collection] (no filter)
    match = re.match(r"^\[(.+?)\s+for\s+(\w+)\s+in\s+(.+)\]$", expr)
    if match:
        mapping = match.group(1).strip()
        var = match.group(2)
        coll = match.group(3).strip()
        cs_var = snake_to_camel(var)
        cs_coll = _translate_py_expression(coll)
        cs_mapping = _translate_py_expression(mapping.replace(var, cs_var))
        if cs_mapping == cs_var:
            return f"{cs_coll}.ToList()"
        return f"{cs_coll}.Select({cs_var} => {cs_mapping}).ToList()"

    return expr


# ── New Input System key name mapping ──────────────────────────

_KEY_NAME_MAP = {
    "space": "spaceKey",
    "escape": "escapeKey",
    "left": "leftArrowKey",
    "right": "rightArrowKey",
    "up": "upArrowKey",
    "down": "downArrowKey",
    "return": "enterKey",
    "tab": "tabKey",
    "left_shift": "leftShiftKey",
    "right_shift": "rightShiftKey",
    "left_control": "leftCtrlKey",
    "right_control": "rightCtrlKey",
    "a": "aKey", "b": "bKey", "c": "cKey", "d": "dKey",
    "e": "eKey", "f": "fKey", "g": "gKey", "h": "hKey",
    "i": "iKey", "j": "jKey", "k": "kKey", "l": "lKey",
    "m": "mKey", "n": "nKey", "o": "oKey", "p": "pKey",
    "q": "qKey", "r": "rKey", "s": "sKey", "t": "tKey",
    "u": "uKey", "v": "vKey", "w": "wKey", "x": "xKey",
    "y": "yKey", "z": "zKey",
}

_MOUSE_BUTTON_MAP = {
    "0": "leftButton",
    "1": "rightButton",
    "2": "middleButton",
}


def _translate_new_input_system(expr: str) -> str:
    """Translate Input.get_* calls to Unity New Input System (Mouse/Keyboard)."""
    # Input.get_mouse_button_down(0) -> Mouse.current.leftButton.wasPressedThisFrame
    expr = re.sub(
        r"Input\.get_mouse_button_down\((\d)\)",
        lambda m: f"Mouse.current.{_MOUSE_BUTTON_MAP.get(m.group(1), 'leftButton')}.wasPressedThisFrame",
        expr,
    )
    # Input.get_mouse_button_up(0) -> Mouse.current.leftButton.wasReleasedThisFrame
    expr = re.sub(
        r"Input\.get_mouse_button_up\((\d)\)",
        lambda m: f"Mouse.current.{_MOUSE_BUTTON_MAP.get(m.group(1), 'leftButton')}.wasReleasedThisFrame",
        expr,
    )
    # Input.get_mouse_button(0) -> Mouse.current.leftButton.isPressed
    expr = re.sub(
        r"Input\.get_mouse_button\((\d)\)",
        lambda m: f"Mouse.current.{_MOUSE_BUTTON_MAP.get(m.group(1), 'leftButton')}.isPressed",
        expr,
    )
    # Input.get_mouse_position() / Input.mouse_position -> Mouse.current.position.ReadValue()
    expr = re.sub(r"Input\.get_mouse_position\(\)", "Mouse.current.position.ReadValue()", expr)
    expr = re.sub(r"Input\.mouse_position", "Mouse.current.position.ReadValue()", expr)

    # Input.get_key_down('space') -> Keyboard.current.spaceKey.wasPressedThisFrame
    expr = re.sub(
        r"Input\.get_key_down\(['\"](\w+)['\"]\)",
        lambda m: f"Keyboard.current.{_KEY_NAME_MAP.get(m.group(1), m.group(1) + 'Key')}.wasPressedThisFrame",
        expr,
    )
    # Input.get_key_up('space') -> Keyboard.current.spaceKey.wasReleasedThisFrame
    expr = re.sub(
        r"Input\.get_key_up\(['\"](\w+)['\"]\)",
        lambda m: f"Keyboard.current.{_KEY_NAME_MAP.get(m.group(1), m.group(1) + 'Key')}.wasReleasedThisFrame",
        expr,
    )
    # Input.get_key('space') -> Keyboard.current.spaceKey.isPressed
    expr = re.sub(
        r"Input\.get_key\(['\"](\w+)['\"]\)",
        lambda m: f"Keyboard.current.{_KEY_NAME_MAP.get(m.group(1), m.group(1) + 'Key')}.isPressed",
        expr,
    )

    # Input.get_axis('Horizontal') -> keep as comment/TODO since new input system uses Actions
    expr = re.sub(
        r"Input\.get_axis\(['\"](\w+)['\"]\)",
        r'/* TODO: use InputAction for \1 axis */ 0f',
        expr,
    )

    return expr


def _translate_py_expression(expr: str) -> str:
    """Translate a Python expression to C#."""
    expr = expr.strip()

    # self.start_coroutine(method(args)) -> StartCoroutine(method(args))
    expr = re.sub(r"self\.start_coroutine\(", "StartCoroutine(", expr)

    # self.get_component(T) -> GetComponent<T>()
    expr = re.sub(r"self\.get_component\((\w+)\)", r"GetComponent<\1>()", expr)

    # GameObject.find('X') -> GameObject.Find("X")
    expr = re.sub(r"GameObject\.find\(", "GameObject.Find(", expr)
    expr = re.sub(r"GameObject\.find_with_tag\(", "GameObject.FindWithTag(", expr)
    expr = re.sub(r"GameObject\.find_game_objects_with_tag\(", "GameObject.FindGameObjectsWithTag(", expr)
    expr = re.sub(r"GameObject\.destroy\(", "Destroy(", expr)

    # Input API — version-dependent
    if _config.input_system == "new":
        expr = _translate_new_input_system(expr)
    else:
        expr = re.sub(r"Input\.get_axis\(", "Input.GetAxis(", expr)
        expr = re.sub(r"Input\.get_key\(", "Input.GetKey(", expr)
        expr = re.sub(r"Input\.get_key_down\(", "Input.GetKeyDown(", expr)
        expr = re.sub(r"Input\.get_key_up\(", "Input.GetKeyUp(", expr)
        expr = re.sub(r"Input\.get_mouse_button\(", "Input.GetMouseButton(", expr)
        expr = re.sub(r"Input\.get_mouse_button_down\(", "Input.GetMouseButtonDown(", expr)
        expr = re.sub(r"Input\.get_mouse_button_up\(", "Input.GetMouseButtonUp(", expr)
        expr = re.sub(r"Input\.get_mouse_position\(\)", "Input.mousePosition", expr)
        expr = re.sub(r"Input\.mouse_position", "Input.mousePosition", expr)

    # Time API
    expr = expr.replace("Time.delta_time", "Time.deltaTime")
    expr = expr.replace("Time.fixed_delta_time", "Time.fixedDeltaTime")

    # Python math module -> Unity Mathf
    expr = re.sub(r"\bmath\.pi\b", "Mathf.PI", expr)
    expr = re.sub(r"\bmath\.inf\b", "Mathf.Infinity", expr)
    expr = re.sub(r"\bmath\.cos\(", "Mathf.Cos(", expr)
    expr = re.sub(r"\bmath\.sin\(", "Mathf.Sin(", expr)
    expr = re.sub(r"\bmath\.tan\(", "Mathf.Tan(", expr)
    expr = re.sub(r"\bmath\.acos\(", "Mathf.Acos(", expr)
    expr = re.sub(r"\bmath\.asin\(", "Mathf.Asin(", expr)
    expr = re.sub(r"\bmath\.atan2\(", "Mathf.Atan2(", expr)
    expr = re.sub(r"\bmath\.atan\(", "Mathf.Atan(", expr)
    expr = re.sub(r"\bmath\.sqrt\(", "Mathf.Sqrt(", expr)
    expr = re.sub(r"\bmath\.floor\(", "Mathf.Floor(", expr)
    expr = re.sub(r"\bmath\.ceil\(", "Mathf.Ceil(", expr)
    expr = re.sub(r"\bmath\.log\(", "Mathf.Log(", expr)
    expr = re.sub(r"\bmath\.pow\(", "Mathf.Pow(", expr)

    # random -> Random
    expr = re.sub(r"random\.random\(\)", "Random.value", expr)
    expr = re.sub(r"random\.uniform\(", "Random.Range(", expr)

    # print -> Debug.Log
    expr = re.sub(r"\bprint\(", "Debug.Log(", expr)

    # self.transform -> transform
    expr = expr.replace("self.transform", "transform")
    # self.X -> just X (instance field access)
    expr = re.sub(r"\bself\.", "", expr)
    # Standalone 'self' -> 'this'
    expr = re.sub(r"\bself\b", "this", expr)

    # f-strings: f"text {var}" -> $"text {var}"
    expr = re.sub(r'\bf"', '$"', expr)
    expr = re.sub(r"\bf'", "$'", expr)

    # 'or' / 'and' in expressions (outside conditions — conditions handle these separately)
    expr = re.sub(r"\bor\b", "||", expr)
    expr = re.sub(r"\band\b", "&&", expr)

    # 'is not None' -> '!= null', 'is None' -> '== null', 'is X' -> '== X'
    expr = expr.replace(" is not None", " != null")
    expr = expr.replace(" is None", " == null")
    expr = re.sub(r"\bis not\b", "!=", expr)
    expr = re.sub(r"\bis\b(?!\s*null)", "==", expr)

    # game_object -> gameObject (with or without dot prefix)
    expr = re.sub(r"\bgame_object\b", "gameObject", expr)
    # gameObject.active = X -> gameObject.SetActive(X)
    # Handle in statement translator instead — here just fix reads
    expr = re.sub(r"\.active\b(?!\s*=)(?!Self)", ".activeSelf", expr)

    # .add_component(T) -> .AddComponent<T>()
    expr = re.sub(r"\.add_component\((\w+)\)", r".AddComponent<\1>()", expr)

    # .get_component(T) (not self — already stripped) -> .GetComponent<T>()
    expr = re.sub(r"\.get_component\((\w+)\)", r".GetComponent<\1>()", expr)

    # hasattr(x, "y") -> true (C# doesn't have hasattr; assume true for compiled code)
    expr = re.sub(r"hasattr\([^,]+,\s*['\"][^'\"]+['\"]\)", "true", expr)

    # Python ternary: x if cond else y -> cond ? x : y
    ternary = re.match(r"^(.+?)\s+if\s+(.+?)\s+else\s+(.+)$", expr)
    if ternary:
        value_true = ternary.group(1).strip()
        cond = ternary.group(2).strip()
        value_false = ternary.group(3).strip()
        cond = _translate_py_condition(cond)
        expr = f"{cond} ? {value_true} : {value_false}"

    # List operations: .append(x) -> .Add(x), .remove(x) -> .Remove(x)
    expr = re.sub(r"\.append\(", ".Add(", expr)
    expr = re.sub(r"\.remove\(", ".Remove(", expr)
    expr = re.sub(r"\.extend\(", ".AddRange(", expr)
    expr = re.sub(r"\.insert\(", ".Insert(", expr)

    # len(x) -> x.Count (for lists) — handle nested parens
    expr = _translate_len_calls(expr)

    # all(pred for x in collection) -> collection.All(x => pred)
    expr = _translate_all_call(expr)

    # any(pred for x in collection) -> collection.Any(x => pred)
    expr = _translate_any_call(expr)

    # sum(1 for x in collection if cond) -> collection.Count(x => cond)
    expr = _translate_sum_count_call(expr)

    # List comprehensions: [expr for x in coll] -> coll.Select(x => expr).ToList()
    # [expr for x in coll if cond] -> coll.Where(x => cond).Select(x => expr).ToList()
    expr = _translate_list_comprehension(expr)

    # list(...) wrapper -> .ToList()
    expr = re.sub(r"\blist\((.+)\)$", r"\1.ToList()", expr)

    # Property names: snake_case -> camelCase for known Unity properties
    _prop_map = [
        ("gravity_scale", "gravityScale"),
        ("body_type", "bodyType"),
        ("sorting_order", "sortingOrder"),
        ("orthographic_size", "orthographicSize"),
        ("background_color", "backgroundColor"),
        ("sqr_magnitude", "sqrMagnitude"),
        ("mouse_position", "mousePosition"),
    ]

    # Unity 6+: velocity -> linearVelocity, angularVelocity -> angularVelocity (same)
    if _config.unity_version >= 6:
        _prop_map.append(("velocity", "linearVelocity"))
        _prop_map.append(("angular_velocity", "angularVelocity"))
    else:
        _prop_map.append(("angular_velocity", "angularVelocity"))
        # velocity stays as velocity for Unity 5

    for py_prop, cs_prop in _prop_map:
        expr = expr.replace(f".{py_prop}", f".{cs_prop}")

    # String quotes: '...' -> "..."
    expr = re.sub(r"'([^']*)'", r'"\1"', expr)

    # Float literals: add f suffix to all decimal number literals
    # 5.0 -> 5f, 0.5 -> 0.5f, -6.5 -> -6.5f
    expr = re.sub(r"(?<![a-zA-Z_])(\d+\.\d+)(?!f)\b", r"\1f", expr)

    # True/False/None -> true/false/null
    expr = expr.replace("True", "true").replace("False", "false")
    expr = re.sub(r"\bNone\b", "null", expr)

    # Vector2(0, 0) -> Vector2.zero
    expr = re.sub(r"Vector2\(0,\s*0\)", "Vector2.zero", expr)
    expr = re.sub(r"Vector3\(0,\s*0,\s*0\)", "Vector3.zero", expr)

    # Add 'new' keyword for constructors
    for ctor in ("Vector2", "Vector3", "Quaternion", "GameObject"):
        # Match Ctor( but not .Ctor( or already preceded by 'new '
        expr = re.sub(rf"(?<!\.)\b{ctor}\((?!\.)", f"new {ctor}(", expr)
    # Clean up double 'new new'
    expr = expr.replace("new new ", "new ")
    # Don't add new to Vector2.zero etc.
    expr = expr.replace("new Vector2.zero", "Vector2.zero")
    expr = expr.replace("new Vector3.zero", "Vector3.zero")

    # Color tuple literals: (R, G, B) -> new Color32(R, G, B, 255)
    # Handle standalone and inline (inside arrays, arguments, etc.)
    def _color_tuple_repl(m):
        r, g, b = m.group(1), m.group(2), m.group(3)
        return f"new Color32({r}, {g}, {b}, 255)"
    expr = re.sub(r"\((\d+),\s*(\d+),\s*(\d+)\)", _color_tuple_repl, expr)

    # Python builtins -> C# equivalents
    expr = re.sub(r"\bmax\(", "Mathf.Max(", expr)
    expr = re.sub(r"\bmin\(", "Mathf.Min(", expr)
    expr = re.sub(r"\babs\(", "Mathf.Abs(", expr)

    # Python list operations:
    # row[:] -> row.Clone() (array copy)
    expr = re.sub(r"(\w+)\[:\]", r"(\1.Clone() as bool[])", expr)

    # [True] * N -> new bool[N] (filled with true via Enumerable)
    expr = re.sub(r"\[true\]\s*\*\s*(\w+)", r"Enumerable.Repeat(true, \1).ToArray()", expr)
    expr = re.sub(r"\[false\]\s*\*\s*(\w+)", r"Enumerable.Repeat(false, \1).ToArray()", expr)

    # range(N) standalone -> Enumerable.Range(0, N)
    expr = re.sub(r"\brange\((\w+)\)", r"Enumerable.Range(0, \1)", expr)

    # Fix lambda with no param: .Select( => -> .Select(_ =>
    expr = re.sub(r"\.Select\(\s*=>", ".Select(_ =>", expr)

    # sum(1 for x in list) already handled by LINQ
    # Python casts: int(x) -> (int)(x), float(x) -> (float)(x), str(x) -> x.ToString()
    expr = re.sub(r"\bint\(([^)]+)\)", r"(int)(\1)", expr)
    expr = re.sub(r"\bfloat\(([^)]+)\)", r"(float)(\1)", expr)
    expr = re.sub(r"\bstr\(([^)]+)\)", r"\1.ToString()", expr)

    # Python string methods
    expr = re.sub(r"\.zfill\((\d+)\)", r'.PadLeft(\1, "0"[0])', expr)

    # Python floor division: // -> /
    expr = expr.replace("//", "/")

    # Enum casing: UPPER_CASE enum values -> PascalCase
    # Built-in Unity enums (hardcoded)
    for py_enum, cs_enum in [
        ("RigidbodyType2D.KINEMATIC", "RigidbodyType2D.Kinematic"),
        ("RigidbodyType2D.STATIC", "RigidbodyType2D.Static"),
        ("RigidbodyType2D.DYNAMIC", "RigidbodyType2D.Dynamic"),
        ("ForceMode2D.FORCE", "ForceMode2D.Force"),
        ("ForceMode2D.IMPULSE", "ForceMode2D.Impulse"),
        ("TextAnchor.UPPER_LEFT", "TextAnchor.UpperLeft"),
        ("TextAnchor.UPPER_CENTER", "TextAnchor.UpperCenter"),
        ("TextAnchor.UPPER_RIGHT", "TextAnchor.UpperRight"),
        ("TextAnchor.MIDDLE_LEFT", "TextAnchor.MiddleLeft"),
        ("TextAnchor.MIDDLE_CENTER", "TextAnchor.MiddleCenter"),
        ("TextAnchor.MIDDLE_RIGHT", "TextAnchor.MiddleRight"),
    ]:
        expr = expr.replace(py_enum, cs_enum)
    # User-defined enums from the same file (dynamic)
    for py_enum, cs_enum in _enum_values.items():
        expr = expr.replace(py_enum, cs_enum)
    # Catch remaining EnumType.UPPER_SNAKE patterns not in the map
    # Exclude known Unity types (Mathf, Vector2, etc.) whose constants are already correct
    _NON_ENUM_TYPES = {"Mathf", "Vector2", "Vector3", "Quaternion", "Color", "Color32",
                       "Physics2D", "KeyCode", "Input", "Time", "Random", "Debug", "Screen"}
    def _enum_upper_to_pascal(m):
        enum_type = m.group(1)
        if enum_type in _NON_ENUM_TYPES:
            return m.group(0)  # Don't touch Unity constants
        value = m.group(2)
        pascal = _upper_snake_to_pascal(value)
        return f"{enum_type}.{pascal}"
    expr = re.sub(r"(\b[A-Z]\w+)\.([A-Z][A-Z_]+)\b", _enum_upper_to_pascal, expr)

    # OnTriggerEnter2D: other.layer -> other.gameObject.layer (Collider2D has no .layer)
    expr = re.sub(r"\bother\.layer\b", "other.gameObject.layer", expr)

    # Simulator-only calls — strip entirely
    # .build() is simulator physics setup
    if re.match(r"^[\w.]+\.build\(\)$", expr):
        return "__STRIP__"
    expr = re.sub(r"\.build\(\)", "", expr)
    # _sync_from_transform() — simulator-only physics sync (catch before and after naming)
    if "_sync_from_transform" in expr or "SyncFromTransform()" in expr or "syncFromTransform()" in expr:
        return "__STRIP__"
    # LifecycleManager.instance().register_component(...) — simulator only
    if "LifecycleManager" in expr:
        return "__STRIP__"
    # PhysicsManager — simulator-internal (Unity handles physics automatically)
    if "PhysicsManager" in expr:
        return "__STRIP__"
    # DisplayManager — simulator-internal (Unity handles display)
    if "DisplayManager" in expr:
        return "__STRIP__"
    # hasattr() — Python-only runtime check, no C# equivalent
    if "hasattr(" in expr:
        return "__STRIP__"
    # pymunk internals: _space, _shape, _body (simulator physics implementation details)
    if "_space." in expr or "_shape" in expr:
        return "__STRIP__"
    # Simulator-only property assignments: clip_ref, asset_ref (become clipRef, assetRef)
    # In Unity, audio clips are assigned via inspector, not by string reference
    if re.match(r"^[\w.]+\.clipRef\s*=", expr):
        return "__STRIP__"
    if re.match(r"^[\w.]+\.assetRef\s*=", expr):
        return "__STRIP__"

    # Instantiate() — convert Python prefab pattern to Unity pattern
    # Instantiate("Name", position=pos, tag="Tag") → Instantiate(namePrefab, pos, Quaternion.identity)
    inst_match = re.match(r'^Instantiate\("(\w+)"(?:,\s*position=(\w+))?(?:,\s*tag="(\w+)")?\)', expr)
    if inst_match:
        prefab_name = inst_match.group(1)
        pos_var = inst_match.group(2) or "transform.position"
        # In Unity, prefab is a serialized field reference: camelCase + Prefab
        prefab_field = prefab_name[0].lower() + prefab_name[1:] + "Prefab"
        expr = f"Instantiate({prefab_field}, {pos_var}, Quaternion.identity)"

    # Trailing commas in constructor args: (x, y, ) -> (x, y)
    expr = re.sub(r",\s*\)", ")", expr)

    # Strip all Python keyword arguments from function calls
    # color=(R,G,B) → new Color32(R,G,B,255) first, then strip remaining kwargs
    def _translate_color_kwarg(m):
        r, g, b = m.group(1), m.group(2), m.group(3)
        return f", new Color32({r}, {g}, {b}, 255)"
    expr = re.sub(r",\s*color=\((\d+),\s*(\d+),\s*(\d+)\)", _translate_color_kwarg, expr)
    # duration=N → just N (positional)
    expr = re.sub(r",\s*duration=(\w+)", r", \1f", expr)
    # tag="X" → strip (handled at GameObject level)
    expr = re.sub(r",\s*tag=\"[^\"]+\"", "", expr)
    expr = re.sub(r",\s*tag='[^']+'", "", expr)
    # Generic remaining kwargs: key=value → just value (fallback)
    expr = re.sub(r",\s*\w+=([^,)]+)", r", \1", expr)

    # Input.GetKey("a") -> Input.GetKey(KeyCode.A)
    def _key_string_to_keycode(m):
        key = m.group(1)
        keycode_map = {
            'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D', 'e': 'E', 'f': 'F',
            'g': 'G', 'h': 'H', 'i': 'I', 'j': 'J', 'k': 'K', 'l': 'L',
            'm': 'M', 'n': 'N', 'o': 'O', 'p': 'P', 'q': 'Q', 'r': 'R',
            's': 'S', 't': 'T', 'u': 'U', 'v': 'V', 'w': 'W', 'x': 'X',
            'y': 'Y', 'z': 'Z', 'space': 'Space', 'escape': 'Escape',
            'return': 'Return', 'left': 'LeftArrow', 'right': 'RightArrow',
            'up': 'UpArrow', 'down': 'DownArrow', 'tab': 'Tab',
        }
        kc = keycode_map.get(key, key.capitalize())
        return f"KeyCode.{kc}"
    expr = re.sub(r'Input\.GetKey\("(\w+)"\)', lambda m: f"Input.GetKey({_key_string_to_keycode(m)})", expr)
    expr = re.sub(r'Input\.GetKeyDown\("(\w+)"\)', lambda m: f"Input.GetKeyDown({_key_string_to_keycode(m)})", expr)
    expr = re.sub(r'Input\.GetKeyUp\("(\w+)"\)', lambda m: f"Input.GetKeyUp({_key_string_to_keycode(m)})", expr)

    # Apply symbol table: replace known Python names with C# equivalents
    # This ensures field/method references in bodies match declarations
    if _current_symbols:
        # Sort by length descending to match longer names first (avoid partial matches)
        for py_name, cs_name in sorted(_current_symbols.items(), key=lambda x: -len(x[0])):
            if py_name == cs_name:
                continue
            # Replace as whole word: \b doesn't work with _ prefix, use lookaround
            expr = re.sub(rf"(?<![.\w]){re.escape(py_name)}(?!\w)", cs_name, expr)

    # Convert ALL remaining snake_case method calls to PascalCase (cross-class calls)
    def _snake_method_to_pascal(m):
        prefix = m.group(1) or ""
        name = m.group(2)
        parts = name.lstrip('_').split('_')
        pascal = ''.join(p.capitalize() for p in parts if p)
        return prefix + pascal + '('
    # Match: .method_name( with underscores → .PascalCase(
    expr = re.sub(r"(\.)([a-z_][a-z_]*[a-z])\(", _snake_method_to_pascal, expr)

    # Match standalone _method_name( → PascalCase(
    def _standalone_snake_method(m):
        name = m.group(1)
        parts = name.lstrip('_').split('_')
        pascal = ''.join(p.capitalize() for p in parts if p)
        return pascal + '('
    expr = re.sub(r"(?<![.\w])(_[a-z][a-z_]*)\(", _standalone_snake_method, expr)

    # Convert .snake_case field access to .camelCase (for external objects not in symbol table)
    def _snake_field_to_camel(m):
        dot = m.group(1)
        name = m.group(2)
        parts = name.split('_')
        camel = parts[0] + ''.join(p.capitalize() for p in parts[1:])
        return dot + camel
    expr = re.sub(r"(\.)([a-z]+_[a-z_]+)(?!\()", _snake_field_to_camel, expr)

    # Convert standalone _underscore_names to camelCase (fields not in symbol table)
    def _underscore_to_camel(m):
        name = m.group(0)
        parts = name.lstrip('_').split('_')
        return parts[0] + ''.join(p.capitalize() for p in parts[1:])
    expr = re.sub(r"(?<![.\w])_[a-z][a-z_]*[a-z]\b(?!\()", _underscore_to_camel, expr)

    return expr


def _translate_py_condition(cond: str) -> str:
    """Translate a Python condition to C#."""
    # Handle 'is not None' / 'is None' before expression translation mangles them
    cond = cond.replace(" is not None", " != null").replace(" is None", " == null")
    cond = _translate_py_expression(cond)
    cond = cond.replace(" and ", " && ").replace(" or ", " || ")
    cond = re.sub(r"\bnot\s+", "!", cond)

    # Python chained comparisons: 0 <= x < N -> x >= 0 && x < N
    chain_match = re.match(r"^(\d+)\s*<=\s*(\w+)\s*<\s*(.+)$", cond)
    if chain_match:
        low = chain_match.group(1)
        var = chain_match.group(2)
        high = chain_match.group(3)
        cond = f"{var} >= {low} && {var} < {high}"

    # Fix chained comparisons with && (multiple chained)
    cond = re.sub(r"(\d+)\s*<=\s*(\w+)\s*<\s*(\w+)", r"\2 >= \1 && \2 < \3", cond)

    # Object truthiness: bare object names in && / || should get != null
    # e.g., "spriteRenderer && animationSprites" → "spriteRenderer != null && animationSprites != null"
    # But bool fields should stay as bare identifiers (no != null)
    parts = re.split(r"\s*(&&|\|\|)\s*", cond)
    fixed_parts = []
    for part in parts:
        if part in ("&&", "||"):
            fixed_parts.append(part)
        elif re.match(r"^[a-zA-Z_]\w*$", part.strip()) and part.strip() not in ("true", "false", "null"):
            ident = part.strip()
            # Bool fields stay as bare truthiness checks (no != null)
            if ident in _bool_fields:
                fixed_parts.append(ident)
            else:
                fixed_parts.append(f"{ident} != null")
        else:
            fixed_parts.append(part)
    cond = " ".join(fixed_parts)

    return cond


def _translate_type_annotation(py_type: str) -> str:
    """Convert a Python type annotation string to C# type for local variables.

    Handles: int, float, str, bool, Vector2, Vector3, GameObject,
    list[T], tuple[T, ...], Type | None, etc.
    """
    py_type = py_type.strip()
    # Strip Optional/None union: Type | None -> Type, None | Type -> Type
    py_type = re.sub(r"\s*\|\s*None\s*$", "", py_type)
    py_type = re.sub(r"^None\s*\|\s*", "", py_type)
    # Also handle already-translated null: Type | null -> Type
    py_type = re.sub(r"\s*\|\s*null\s*$", "", py_type)
    py_type = py_type.strip()
    # Map through the existing type system
    result = _py_type_to_csharp(py_type)
    return result


def _py_type_to_csharp(type_str: str, is_field: bool = False, default_value: str = "") -> str:
    """Convert a Python type annotation to C# type."""
    if not type_str:
        # Try to infer from default value
        if default_value:
            inferred = _infer_constant_type(default_value)
            if inferred:
                return inferred
        return "object" if is_field else "var"
    return _type_mapper.python_to_csharp(type_str)


def _py_value_to_csharp(value: str | None, csharp_type: str) -> str | None:
    """Convert a Python default value to C# literal."""
    if value is None:
        return None
    value = value.strip()

    if value == "None":
        return "null"
    if value == "True":
        return "true"
    if value == "False":
        return "false"

    # String: 'text' -> "text"
    if value.startswith("'") and value.endswith("'"):
        return f'"{value[1:-1]}"'

    # Float: 5.0 -> 5f
    if "." in value and csharp_type == "float":
        return value.rstrip("0").rstrip(".") + "f" if "." in value else value + "f"

    # Int with float type: 5 -> 5f
    if csharp_type == "float" and value.isdigit():
        return value + "f"

    # Constructor calls: Vector2(...) -> new Vector2(...) with float suffixes
    for ctor in ("Vector2", "Vector3", "Quaternion", "Color"):
        if value.startswith(f"{ctor}("):
            # Add f suffix to decimal literals inside constructor args
            fixed = re.sub(r"(?<![a-zA-Z_])(\d+\.\d+)(?!f)\b", r"\1f", value)
            return f"new {fixed}"

    # dataclass field(default_factory=...) -> new Type()
    field_match = re.match(r"field\(default_factory=(\w+)\)", value)
    if field_match:
        factory = field_match.group(1)
        if factory == "list":
            # Use the C# type to construct: List<T> -> new List<T>()
            if csharp_type.startswith("List<"):
                return f"new {csharp_type}()"
            return f"new List<object>()"
        elif factory == "dict":
            return f"new Dictionary<string, object>()"
        else:
            return f"new {factory}()"

    # Empty list: [] -> new List<T>() or empty array
    if value == "[]":
        if csharp_type.startswith("List<"):
            return f"new {csharp_type}()"
        return "null"

    # Empty dict: {} -> null
    if value == "{}":
        return "null"

    # Color tuples: (R, G, B) -> new Color32(R, G, B, 255)
    color_match = re.match(r"^\((\d+),\s*(\d+),\s*(\d+)\)$", value)
    if color_match:
        r, g, b = color_match.groups()
        return f"new Color32({r}, {g}, {b}, 255)"

    # List of color tuples: [(R,G,B), ...] -> new Color32[] { new Color32(...), ... }
    list_colors = re.match(r"^\[(.+)\]$", value)
    if list_colors:
        inner = list_colors.group(1)
        tuples = re.findall(r"\((\d+),\s*(\d+),\s*(\d+)\)", inner)
        if tuples:
            elements = ", ".join(f"new Color32({r}, {g}, {b}, 255)" for r, g, b in tuples)
            return f"new Color32[] {{ {elements} }}"

    return value


def _infer_expression_type(expr: str) -> str:
    """Infer C# type from a Python expression."""
    expr = expr.strip()
    if expr.startswith("self.get_component("):
        match = re.search(r"get_component\((\w+)\)", expr)
        if match:
            return match.group(1)
    if expr.startswith("GameObject.find("):
        return "GameObject"
    if expr.startswith("Vector2("):
        return "Vector2"
    if expr.startswith("Vector3("):
        return "Vector3"
    if expr.startswith("Input.get_axis("):
        return "float"
    return "var"


def _infer_using_directives(cls: PyClass, parsed: PyFile) -> list[str]:
    """Infer extra using directives needed based on types used."""
    extra = set()
    all_text = " ".join(f.type_annotation for f in cls.fields) + " "
    all_text += " ".join(m.body_source for m in cls.methods)

    if "System.Collections" in all_text or "IEnumerator" in all_text:
        extra.add("System.Collections")

    # Add System.Collections if any method is a coroutine
    if any(m.is_coroutine for m in cls.methods):
        extra.add("System.Collections")

    # Add System.Linq if LINQ operations are used (all(), any(), sum() with generators,
    # list comprehensions, or .Where/.Select/.Count with lambdas)
    _linq_indicators = ["all(", "any(", "sum(1 for", " for ", " if "]
    if any(indicator in all_text for indicator in _linq_indicators):
        # Check more specifically — look for generator expressions
        if (re.search(r"\ball\(.+for\s+\w+\s+in\s+", all_text) or
            re.search(r"\bany\(.+for\s+\w+\s+in\s+", all_text) or
            re.search(r"\bsum\(1\s+for\s+", all_text) or
            re.search(r"\[.+for\s+\w+\s+in\s+", all_text)):
            extra.add("System.Linq")

    if "random" in " ".join(parsed.imports):
        # No extra using needed — Random is in UnityEngine
        pass

    # Add UnityEngine.UI if UI types are used
    import_text = " ".join(parsed.imports)
    if "Text" in all_text or "Canvas" in all_text or "Button" in all_text or "Image" in all_text:
        if "ui" in import_text.lower() or "Text" in " ".join(f.type_annotation for f in cls.fields):
            extra.add("UnityEngine.UI")

    # Add System.Linq if Enumerable is used (from list comprehension translation)
    if "Enumerable" in all_text or "[:]" in all_text:
        extra.add("System.Linq")

    # Add System if Exception is used (try/catch)
    if "except" in all_text or "Exception" in all_text:
        extra.add("System")

    # Add System.Collections.Generic if List<> is used
    field_types = " ".join(f.type_annotation for f in cls.fields)
    if "list" in field_types or "dict" in field_types or "List<" in all_text or "List<" in field_types:
        extra.add("System.Collections.Generic")

    # Add UnityEngine.InputSystem when new input system is active and Input is used
    if _config.input_system == "new":
        import_text = " ".join(parsed.imports)
        if "Input" in all_text or "Input" in import_text:
            extra.add("UnityEngine.InputSystem")

    return sorted(extra)
