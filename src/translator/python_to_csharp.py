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

    results = []
    for cls in parsed.classes:
        results.append(_translate_class(cls, parsed))
    code = "\n".join(results).rstrip() + "\n"

    if namespace:
        # Indent all lines inside the namespace
        indented = "\n".join(
            ("    " + line if line.strip() else line)
            for line in code.split("\n")
        )
        code = f"namespace {namespace}\n{{\n{indented}}}\n"

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


def _translate_monobehaviour(cls: PyClass, parsed: PyFile) -> str:
    """Translate a MonoBehaviour subclass using the Jinja2 template."""
    extra_using = _infer_using_directives(cls, parsed)
    attributes = _infer_attributes(cls)

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
        attributes=attributes,
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
        if not translated:
            continue  # Skip stripped docstrings, inline imports, etc.
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
    # Docstrings — strip them entirely
    if line.startswith('"""') or line.startswith("'''"):
        return ""
    if line.endswith('"""') or line.endswith("'''"):
        return ""

    # Inline imports — strip (these are Python-only, C# uses using directives)
    if line.startswith("from ") and " import " in line:
        return ""
    if line.startswith("import ") and not line.startswith("import "):
        return ""

    # try/except → try/catch
    if line == "try:":
        return "try"
    if line.startswith("except") and line.endswith(":"):
        exc = line[6:].strip().rstrip(":")
        if exc:
            return f"catch ({exc.split(' as ')[0]})"
        return "catch"

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
            expr = expr[:start] + f"{inner_translated}.Count" + expr[pos:]
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
    # Handle 'is not None' / 'is None' before expression translation mangles them
    cond = cond.replace(" is not None", " != null").replace(" is None", " == null")
    cond = _translate_py_expression(cond)
    cond = cond.replace(" and ", " && ").replace(" or ", " || ")
    cond = re.sub(r"\bnot\s+", "!", cond)
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

    # Add UnityEngine.InputSystem when new input system is active and Input is used
    if _config.input_system == "new":
        import_text = " ".join(parsed.imports)
        if "Input" in all_text or "Input" in import_text:
            extra.add("UnityEngine.InputSystem")

    return sorted(extra)
