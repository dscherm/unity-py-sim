"""C# to Python translator — converts parsed C# IR to Python source code."""

from __future__ import annotations

import json
import re
from pathlib import Path

from src.translator.csharp_parser import CSharpFile, CSharpClass, CSharpField, CSharpMethod, parse_csharp_file
from src.translator.type_mapper import (
    TypeMapper, pascal_to_snake, camel_to_snake, convert_float_literal,
)

_RULES_DIR = Path(__file__).parent / "rules"
_translation_rules = json.loads((_RULES_DIR / "translation_rules.json").read_text())
_lifecycle_map: dict[str, str] = _translation_rules["lifecycle_method_mapping"]
_api_translations: dict[str, str] = _translation_rules["api_translations"]
_literal_transforms: dict[str, str] = _translation_rules["literal_transforms"]

_type_mapper = TypeMapper()


def translate_file(path: str | Path) -> str:
    """Translate a C# file to Python source code."""
    parsed = parse_csharp_file(path)
    return translate(parsed)


def translate(parsed: CSharpFile) -> str:
    """Translate a CSharpFile IR to Python source code."""
    lines: list[str] = []
    lines.append(_generate_docstring(parsed))
    lines.append("")
    lines.extend(_generate_imports(parsed))
    lines.append("")
    lines.append("")

    for cls in parsed.classes:
        lines.extend(_translate_class(cls))
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _generate_docstring(parsed: CSharpFile) -> str:
    if parsed.classes:
        name = parsed.classes[0].name
        return f'"""Translated from {name}.cs"""'
    return '"""Translated from C#"""'


def _generate_imports(parsed: CSharpFile) -> list[str]:
    """Generate Python imports based on types used."""
    imports = set()
    needs_random = False

    for cls in parsed.classes:
        if cls.is_monobehaviour:
            imports.add("from src.engine.core import MonoBehaviour, GameObject")

        for field in cls.fields:
            _add_type_imports(field.type, imports)

        for method in cls.methods:
            _add_type_imports(method.return_type, imports)
            for param in method.parameters:
                _add_type_imports(param.type, imports)

            # Scan body for API usage
            body = method.body
            if "Input." in body:
                imports.add("from src.engine.input_manager import Input")
            if "Time." in body:
                imports.add("from src.engine.time_manager import Time")
            if "Random." in body:
                needs_random = True
            if "Mathf." in body:
                imports.add("from src.engine.math.mathf import Mathf")
            if "Vector2" in body:
                imports.add("from src.engine.math.vector import Vector2")
            if "Vector3" in body:
                imports.add("from src.engine.math.vector import Vector3")

        for field in cls.fields:
            if "Rigidbody2D" in field.type:
                imports.add("from src.engine.physics.rigidbody import Rigidbody2D")
            _add_type_imports(field.type, imports)

    if needs_random:
        imports.add("import random")

    return sorted(imports)


def _add_type_imports(type_str: str, imports: set[str]) -> None:
    """Add import statements based on type references."""
    if "Vector2" in type_str:
        imports.add("from src.engine.math.vector import Vector2")
    if "Vector3" in type_str:
        imports.add("from src.engine.math.vector import Vector3")
    if "Quaternion" in type_str:
        imports.add("from src.engine.math.quaternion import Quaternion")
    if "Rigidbody2D" in type_str:
        imports.add("from src.engine.physics.rigidbody import Rigidbody2D")
    if "Collision2D" in type_str:
        imports.add("from src.engine.physics.physics_manager import Collision2D")
    if "GameObject" in type_str and "MonoBehaviour" not in type_str:
        imports.add("from src.engine.core import MonoBehaviour, GameObject")


def _translate_class(cls: CSharpClass) -> list[str]:
    """Translate a CSharpClass to Python lines."""
    lines: list[str] = []

    # Class declaration
    base = "MonoBehaviour" if cls.is_monobehaviour else ""
    if cls.base_classes and not cls.is_monobehaviour:
        base = cls.base_classes[0]
    base_str = f"({base})" if base else ""
    lines.append(f"class {cls.name}{base_str}:")

    # Collect serialized fields and instance fields for __init__
    init_fields = []
    class_fields = []

    for field in cls.fields:
        if "static" in field.modifiers:
            class_fields.append(field)
        else:
            init_fields.append(field)

    # Class-level static fields
    if class_fields:
        for field in class_fields:
            py_name = camel_to_snake(field.name)
            value = _translate_literal(field.initializer) if field.initializer else "None"
            py_type = _type_mapper.csharp_to_python(field.type)
            lines.append(f"    {py_name}: {py_type} = {value}")
        lines.append("")

    # __init__ with instance fields
    if init_fields:
        lines.append("    def __init__(self):")
        lines.append("        super().__init__()")
        for field in init_fields:
            py_name = camel_to_snake(field.name)
            py_type = _type_mapper.csharp_to_python(field.type)
            value = _translate_literal(field.initializer) if field.initializer else "None"
            lines.append(f"        self.{py_name}: {py_type} = {value}")
        lines.append("")

    # Methods
    for method in cls.methods:
        lines.extend(_translate_method(method, cls))
        lines.append("")

    # Ensure class body is not empty
    if len(lines) == 1:
        lines.append("    pass")

    return lines


def _translate_method(method: CSharpMethod, cls: CSharpClass) -> list[str]:
    """Translate a CSharpMethod to Python lines."""
    lines: list[str] = []

    # Method name
    if method.name in _lifecycle_map:
        py_name = _lifecycle_map[method.name]
    else:
        py_name = camel_to_snake(method.name)

    # Parameters
    is_static = "static" in method.modifiers
    params = ["self"] if not is_static else []
    for p in method.parameters:
        py_param_name = camel_to_snake(p.name)
        params.append(py_param_name)

    param_str = ", ".join(params)

    # Decorators
    if is_static:
        lines.append("    @staticmethod")

    lines.append(f"    def {py_name}({param_str}):")

    # Body
    body_lines = _translate_body(method.body, cls)
    if body_lines:
        for line in body_lines:
            if line.strip():
                lines.append(f"        {line}")
            else:
                lines.append("")
    else:
        lines.append("        pass")

    return lines


def _translate_body(body: str, cls: CSharpClass) -> list[str]:
    """Translate a C# method body to Python lines."""
    if not body or body.strip() in ("{}", "{ }"):
        return []

    # Strip outer braces
    body = body.strip()
    if body.startswith("{"):
        body = body[1:]
    if body.endswith("}"):
        body = body[:-1]
    body = body.strip()

    if not body:
        return []

    lines = []
    indent_level = 0
    for raw_line in body.split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        # Track brace depth for indentation
        if line == "{":
            indent_level += 1
            continue
        if line == "}":
            indent_level = max(0, indent_level - 1)
            continue

        # Handle lines ending with {
        opens_block = line.endswith("{")
        if opens_block:
            line = line[:-1].rstrip()

        if not line:
            if opens_block:
                indent_level += 1
            continue

        if line.startswith("//"):
            prefix = "    " * indent_level
            lines.append(f"{prefix}# {line[2:].strip()}")
            if opens_block:
                indent_level += 1
            continue

        translated = _translate_statement(line, cls)
        prefix = "    " * indent_level
        for t in translated:
            lines.append(f"{prefix}{t}")

        if opens_block:
            indent_level += 1

    return lines


def _translate_statement(line: str, cls: CSharpClass) -> list[str]:
    """Translate a single C# statement to Python."""
    # Extract comment first, then strip semicolons from the code part
    comment = ""
    comment_idx = line.find("//")
    if comment_idx >= 0:
        comment = f"  # {line[comment_idx+2:].strip()}"
        line = line[:comment_idx].rstrip()

    # Strip trailing semicolons
    line = line.rstrip("; ")

    # Apply API translations
    result = _apply_translations(line, cls)

    # Handle control flow
    if result.startswith("if (") or result.startswith("if("):
        cond = _extract_condition(result)
        return [f"if {cond}:{comment}"]
    if result.startswith("else if (") or result.startswith("else if("):
        cond = _extract_condition(result.replace("else if", "elif", 1) if False else result)
        # Extract condition after "else if"
        inner = result[len("else if"):].strip()
        cond = _extract_condition("if" + inner)
        return [f"elif {cond}:{comment}"]
    if result == "else":
        return [f"else:{comment}"]
    if result.startswith("while (") or result.startswith("while("):
        cond = _extract_condition(result)
        return [f"while {cond}:{comment}"]
    if result.startswith("for (") or result.startswith("for("):
        return [f"# TODO: translate for loop: {result}{comment}"]
    if result.startswith("foreach (") or result.startswith("foreach("):
        return [f"# TODO: translate foreach: {result}{comment}"]
    if result.startswith("return "):
        value = result[7:].strip()
        value = _translate_expression(value, cls)
        return [f"return {value}{comment}"]
    if result == "return":
        return [f"return{comment}"]

    # Variable declaration: Type name = value
    decl_match = re.match(r"^(\w+)\s+(\w+)\s*=\s*(.+)$", result)
    if decl_match:
        var_type, var_name, value = decl_match.groups()
        if var_type in ("int", "float", "double", "bool", "string", "var",
                         "Vector2", "Vector3", "GameObject", "Rigidbody2D",
                         "BallController", "Collision2D"):
            py_name = camel_to_snake(var_name)
            py_value = _translate_expression(value, cls)
            return [f"{py_name} = {py_value}{comment}"]

    # Assignment: name = value
    assign_match = re.match(r"^([\w.]+)\s*=\s*(.+)$", result)
    if assign_match:
        target, value = assign_match.groups()
        py_target = _translate_expression(target, cls)
        py_value = _translate_expression(value, cls)
        return [f"{py_target} = {py_value}{comment}"]

    # Compound assignment: name += value, name -= value
    compound_match = re.match(r"^([\w.]+)\s*([+\-*/])=\s*(.+)$", result)
    if compound_match:
        target, op, value = compound_match.groups()
        py_target = _translate_expression(target, cls)
        py_value = _translate_expression(value, cls)
        return [f"{py_target} {op}= {py_value}{comment}"]

    # Increment/decrement: name++, name--
    inc_match = re.match(r"^([\w.]+)\+\+$", result)
    if inc_match:
        py_target = _translate_expression(inc_match.group(1), cls)
        return [f"{py_target} += 1{comment}"]
    dec_match = re.match(r"^([\w.]+)--$", result)
    if dec_match:
        py_target = _translate_expression(dec_match.group(1), cls)
        return [f"{py_target} -= 1{comment}"]

    # Method call
    result = _translate_expression(result, cls)
    return [f"{result}{comment}"]


def _translate_expression(expr: str, cls: CSharpClass) -> str:
    """Translate a C# expression to Python."""
    expr = expr.strip()

    # new Constructor() -> Constructor()
    expr = re.sub(r"\bnew\s+", "", expr)

    # Float literals: 5f -> 5.0, 0.5f -> 0.5 (order matters — decimal first)
    expr = re.sub(r"(\d+\.\d+)f\b", r"\1", expr)
    expr = re.sub(r"\b(\d+)f\b", lambda m: m.group(1) + ".0", expr)

    # Ternary: a ? b : c -> b if a else c
    # Only match simple ternaries (no nested parens in condition)
    # Uses a conservative pattern to avoid mangling complex expressions
    ternary_match = re.match(r"^([^?,(]+)\s*\?\s*([^:,]+)\s*:\s*([^,)]+)$", expr)
    if ternary_match:
        cond, true_val, false_val = ternary_match.groups()
        expr = f"{true_val.strip()} if {cond.strip()} else {false_val.strip()}"

    # Bool/null literals
    expr = expr.replace("true", "True").replace("false", "False")
    expr = re.sub(r"\bnull\b", "None", expr)

    # Apply API translations
    for cs_api, py_api in _api_translations.items():
        expr = expr.replace(cs_api, py_api)

    # GetComponent<T>() -> self.get_component(T)
    expr = re.sub(r"get_component<(\w+)>\(\)", r"self.get_component(\1)", expr)
    expr = re.sub(r"GetComponent<(\w+)>\(\)", r"self.get_component(\1)", expr)

    # transform.X -> self.transform.X
    if re.match(r"^transform\.", expr):
        expr = "self." + expr

    # Property access translations
    expr = expr.replace(".gameObject", ".game_object")
    expr = expr.replace(".transform", ".transform")

    # Tag comparison: .tag == "X" (already works in Python)
    # .position (already Vector3, works)

    # String quotes: "..." -> '...'
    expr = re.sub(r'"([^"]*)"', r"'\1'", expr)

    # Vector2.zero -> Vector2(0, 0), etc.
    for cs_lit, py_lit in _literal_transforms.items():
        if cs_lit.startswith("Vector"):
            expr = expr.replace(cs_lit, py_lit)

    return expr


def _apply_translations(line: str, cls: CSharpClass) -> str:
    """Apply broad API translations to a line."""
    # Already handled by _translate_expression in most cases
    return line


def _extract_condition(text: str) -> str:
    """Extract condition from 'if (condition) {' pattern."""
    # Find the parenthesized condition
    match = re.search(r"\((.+)\)\s*\{?\s*$", text)
    if match:
        cond = match.group(1)
        # Translate the condition
        cond = cond.replace("==", "==").replace("!=", "!=")
        cond = cond.replace("&&", " and ").replace("||", " or ")
        cond = cond.replace("!", "not ")
        # Fix double negation cleanup
        cond = cond.replace("not =", "!=").replace("not  =", "!=")
        # Float literals (decimal first to avoid partial matches)
        cond = re.sub(r"(\d+\.\d+)f\b", r"\1", cond)
        cond = re.sub(r"\b(\d+)f\b", lambda m: m.group(1) + ".0", cond)
        # String quotes
        cond = re.sub(r'"([^"]*)"', r"'\1'", cond)
        # API translations
        for cs_api, py_api in _api_translations.items():
            cond = cond.replace(cs_api, py_api)
        # Property access
        cond = cond.replace(".gameObject", ".game_object")
        cond = cond.replace("true", "True").replace("false", "False")
        cond = re.sub(r"\bnull\b", "None", cond)
        return cond
    return text


def _translate_literal(value: str | None) -> str:
    """Translate a C# literal value to Python."""
    if value is None:
        return "None"
    value = value.strip()
    value = convert_float_literal(value)
    value = value.replace("true", "True").replace("false", "False")
    value = re.sub(r"\bnull\b", "None", value)
    value = re.sub(r'"([^"]*)"', r"'\1'", value)
    return value
