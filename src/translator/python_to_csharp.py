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


def translate_file(path: str | Path) -> str:
    """Translate a Python file to C# source code."""
    parsed = parse_python_file(path)
    return translate(parsed)


def translate(parsed: PyFile) -> str:
    """Translate a PyFile IR to C# source code."""
    results = []
    for cls in parsed.classes:
        results.append(_translate_class(cls, parsed))
    return "\n".join(results).rstrip() + "\n"


def _translate_class(cls: PyClass, parsed: PyFile) -> str:
    """Translate a PyClass to C# source."""
    if cls.is_monobehaviour:
        return _translate_monobehaviour(cls, parsed)
    return _translate_plain_class(cls, parsed)


def _translate_monobehaviour(cls: PyClass, parsed: PyFile) -> str:
    """Translate a MonoBehaviour subclass using the Jinja2 template."""
    extra_using = _infer_using_directives(cls, parsed)

    serialized_fields = []
    private_fields = []
    static_fields = []

    for field in cls.fields:
        csharp_type = _py_type_to_csharp(field.type_annotation)
        csharp_name = snake_to_camel(field.name)
        default = _py_value_to_csharp(field.default_value, csharp_type) if field.default_value else None

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
        serialized_fields=serialized_fields,
        private_fields=private_fields,
        static_fields=static_fields,
        methods=methods,
    )


def _translate_plain_class(cls: PyClass, parsed: PyFile) -> str:
    """Translate a non-MonoBehaviour class to C#."""
    # Reuse the same logic but without MonoBehaviour base
    lines = ["using UnityEngine;", ""]
    base = cls.base_classes[0] if cls.base_classes else ""
    base_str = f" : {base}" if base else ""
    lines.append(f"public class {cls.name}{base_str}")
    lines.append("{")

    for field in cls.fields:
        csharp_type = _py_type_to_csharp(field.type_annotation)
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
    # Name
    if method.name in _lifecycle_map_reverse:
        csharp_name = _lifecycle_map_reverse[method.name]
    else:
        csharp_name = snake_to_pascal(method.name)

    # Access modifier
    if method.is_static:
        access = "public static"
    elif method.is_lifecycle:
        access = "void"  # Lifecycle methods don't need access modifier prefix
        # Actually Unity lifecycle methods use just "void"
        return_type = ""
    else:
        access = "public"

    # Return type
    return_type = "IEnumerator" if method.is_coroutine else "void"

    # Parameters
    params = []
    for p in method.parameters:
        csharp_type = _py_type_to_csharp(p.type_annotation) if p.type_annotation else _infer_param_type(p.name, method)
        csharp_param_name = snake_to_camel(p.name)
        params.append(f"{csharp_type} {csharp_param_name}")
    params_str = ", ".join(params)

    # Body
    body = _translate_body(method.body_source)

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


def _infer_param_type(param_name: str, method: PyMethod) -> str:
    """Infer C# type from parameter name when no annotation exists."""
    if param_name in ("collision",):
        return "Collision2D"
    if param_name in ("other",):
        return "Collider2D"
    if param_name in ("side", "name", "tag"):
        return "string"
    return "object"


def _translate_body(body: str) -> str:
    """Translate Python method body to C#, adding braces for indented blocks."""
    if not body.strip():
        return ""

    raw_lines = body.split("\n")
    # First pass: collect (indent_level, translated_line) pairs
    entries: list[tuple[int, str]] = []
    for raw_line in raw_lines:
        stripped = raw_line.strip()
        if not stripped or stripped == "pass" or stripped == "super().__init__()":
            continue
        indent = len(raw_line) - len(raw_line.lstrip())
        indent_level = indent // 4
        translated = _translate_py_statement(stripped)
        entries.append((indent_level, translated))

    if not entries:
        return ""

    # Second pass: emit with braces on indentation changes
    lines = []
    base_indent = "        "
    prev_indent = entries[0][0]
    indent_stack: list[int] = []

    for i, (level, text) in enumerate(entries):
        # Check if previous line opened a block (if/else/while)
        if level > prev_indent:
            lines.append(f"{base_indent}{'    ' * prev_indent}{{")
            indent_stack.append(prev_indent)
        elif level < prev_indent:
            # Close blocks
            while indent_stack and indent_stack[-1] >= level:
                close_level = indent_stack.pop()
                lines.append(f"{base_indent}{'    ' * close_level}}}")

        cs_indent = base_indent + "    " * level
        lines.append(f"{cs_indent}{text}")
        prev_indent = level

    # Close any remaining open blocks
    while indent_stack:
        close_level = indent_stack.pop()
        lines.append(f"{base_indent}{'    ' * close_level}}}")

    return "\n".join(lines)


def _translate_py_statement(line: str) -> str:
    """Translate a single Python statement to C#."""
    # Comments
    if line.startswith("#"):
        return f"// {line[1:].strip()}"

    # If/elif/else
    if line.startswith("if ") and line.endswith(":"):
        cond = line[3:-1].strip()
        cond = _translate_py_condition(cond)
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
        return f"// TODO: translate for loop: {line}"

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

    # Assignment
    assign_match = re.match(r"^([\w.]+)\s*=\s*(.+)$", line)
    if assign_match:
        target, value = assign_match.groups()
        cs_target = _translate_py_expression(target)
        cs_value = _translate_py_expression(value)
        # Infer type for variable declarations
        if "." not in target and not target.startswith("self"):
            cs_type = _infer_expression_type(value)
            return f"{cs_type} {cs_target} = {cs_value};"
        return f"{cs_target} = {cs_value};"

    # Expression (method call, etc.)
    expr = _translate_py_expression(line)
    return f"{expr};"


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

    # Input/Time API
    expr = re.sub(r"Input\.get_axis\(", "Input.GetAxis(", expr)
    expr = re.sub(r"Input\.get_key\(", "Input.GetKey(", expr)
    expr = re.sub(r"Input\.get_key_down\(", "Input.GetKeyDown(", expr)
    expr = expr.replace("Time.delta_time", "Time.deltaTime")
    expr = expr.replace("Time.fixed_delta_time", "Time.fixedDeltaTime")

    # random -> Random
    expr = re.sub(r"random\.random\(\)", "Random.value", expr)
    expr = re.sub(r"random\.uniform\(", "Random.Range(", expr)

    # print -> Debug.Log
    expr = re.sub(r"\bprint\(", "Debug.Log(", expr)

    # self.transform -> transform
    expr = expr.replace("self.transform", "transform")
    # self.X -> just X (instance field access)
    expr = re.sub(r"\bself\.", "", expr)

    # .game_object -> .gameObject
    expr = expr.replace(".game_object", ".gameObject")

    # Property names: snake_case -> camelCase for known Unity properties
    for py_prop, cs_prop in [
        ("angular_velocity", "angularVelocity"),
        ("gravity_scale", "gravityScale"),
        ("body_type", "bodyType"),
        ("sorting_order", "sortingOrder"),
        ("orthographic_size", "orthographicSize"),
        ("background_color", "backgroundColor"),
    ]:
        expr = expr.replace(f".{py_prop}", f".{cs_prop}")

    # String quotes: '...' -> "..."
    expr = re.sub(r"'([^']*)'", r'"\1"', expr)

    # Float literals: ensure f suffix where needed
    # 5.0 -> 5f (only bare floats, not in method calls)
    expr = re.sub(r"\b(\d+\.0)\b", lambda m: m.group(1)[:-2] + "f", expr)

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

    return expr


def _translate_py_condition(cond: str) -> str:
    """Translate a Python condition to C#."""
    cond = _translate_py_expression(cond)
    cond = cond.replace(" and ", " && ").replace(" or ", " || ")
    cond = re.sub(r"\bnot\s+", "!", cond)
    cond = cond.replace(" is null", " == null").replace(" is not null", " != null")
    return cond


def _py_type_to_csharp(type_str: str) -> str:
    """Convert a Python type annotation to C# type."""
    if not type_str:
        return "var"
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
    if "random" in " ".join(parsed.imports):
        # No extra using needed — Random is in UnityEngine
        pass

    return sorted(extra)
