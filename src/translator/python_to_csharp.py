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
_reserved_method_renames: dict[str, str] = _translation_rules.get("reserved_method_renames", {})
_api_reverse: dict[str, str] = {v: k for k, v in _translation_rules["api_translations"].items()}

_type_mapper = TypeMapper()
_jinja_env = Environment(loader=FileSystemLoader(str(_TEMPLATE_DIR)), trim_blocks=True, lstrip_blocks=True)

# ── Reference-type detection for [SerializeField] emission ───
# Value types stay `public T field = default;`
# Reference types become `[SerializeField] private T field;`

_VALUE_TYPES = frozenset({
    "int", "float", "bool", "string", "double", "byte", "short", "long",
    "char", "void", "Color", "Color32", "Vector2", "Vector2Int",
    "Vector3", "Vector3Int", "Vector4", "Quaternion", "Rect", "Bounds",
    "LayerMask", "KeyCode",
})

_UNITY_REFERENCE_TYPES = frozenset({
    "GameObject", "Transform", "Rigidbody2D", "Rigidbody",
    "Collider2D", "Collider", "BoxCollider2D", "CircleCollider2D",
    "SpriteRenderer", "Camera", "AudioSource", "AudioClip",
    "Sprite", "Animator", "Canvas", "Text", "Image",
    "TilemapRenderer", "Tilemap", "ParticleSystem",
})


def _is_reference_type(csharp_type: str, parsed: PyFile) -> bool:
    """Determine if a C# type is a reference type that needs [SerializeField] private.

    Reference types: GameObject, MonoBehaviour subclasses, arrays of those, etc.
    Value types: int, float, bool, string, Vector2, Color, etc.
    """
    # Strip nullable suffix for checking
    base = csharp_type.rstrip("?")

    # Arrays: check the element type
    if base.endswith("[]"):
        element = base[:-2]
        return _is_reference_type(element, parsed)

    # List<T>: check element type
    list_match = re.match(r"List<(.+)>", base)
    if list_match:
        return _is_reference_type(list_match.group(1), parsed)

    # Known Unity reference types
    if base in _UNITY_REFERENCE_TYPES:
        return True

    # 'object' is a reference type in C# (System.Object)
    if base == "object":
        return True

    # Known value types — NOT reference
    if base in _VALUE_TYPES:
        return False

    # Check if it's a class name from the parsed file (MonoBehaviour subclass or other user class)
    class_names = {c.name for c in parsed.classes}
    if base in class_names:
        return True

    # Unknown PascalCase type that isn't a value type — assume reference
    # (covers types like GameManager, Ghost, Enemy from other files)
    if base and base[0].isupper() and base not in _VALUE_TYPES:
        return True

    return False


# ── Translation config (set per-call) ─────────────────────────

class _TranslationConfig:
    """Per-translation configuration, set by translate()/translate_file()."""
    unity_version: int = 6
    input_system: str = "new"  # "legacy" or "new"
    # Set of MonoBehaviour class names that are subclassed somewhere in the
    # same project. Base classes need their [SerializeField] reference fields
    # emitted as `protected` instead of `private` so C# subclasses can reach
    # them — see FU-3 SerializeField cross-component wiring.
    subclassed_classes: set[str] = set()
    # Map of ClassName → set of field names that are accessed as `x.field`
    # from some OTHER class's method body. Those fields must emit as `public`
    # instead of `[SerializeField] private` so cross-class reads/writes
    # compile — e.g. Ghost.chase accessed from GhostChase/GhostFrightened/
    # GhostScatter/GhostHome, or Pipes.top written from Spawner.Spawn.
    cross_accessed_fields: dict[str, set[str]] = {}

_config = _TranslationConfig()


def set_subclassed_classes(names: set[str]) -> None:
    """Called by project_translator before translating each file so that
    base-class reference fields emit as `[SerializeField] protected` instead
    of `[SerializeField] private`."""
    _config.subclassed_classes = set(names or ())


def set_cross_accessed_fields(mapping: dict[str, set[str]]) -> None:
    """Called by project_translator with fields that are read/written across
    class boundaries so those emit as `public` instead of `[SerializeField]
    private`. Without this, FU-3's private default breaks translation pairs
    like Ghost.chase ↔ GhostChase.OnEnable's `ghost.chase != null` check."""
    _config.cross_accessed_fields = {
        k: set(v) for k, v in (mapping or {}).items()
    }


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

    # S7-7: class name → ordered instance field names for positional-arg mapping
    # in constructor calls. Used by _py_value_to_csharp to emit object-initializer
    # syntax with positional args as named initializers.
    global _class_field_order
    _class_field_order = {}
    for cls in parsed.classes:
        if cls.is_enum:
            continue
        ordered = [f.name for f in cls.fields if not f.is_class_level]
        if ordered:
            _class_field_order[cls.name] = ordered

    # Pre-pass: collect bool, array, and dict fields from ALL classes for truthiness/length/membership checks
    global _bool_fields, _array_fields, _dict_fields, _cross_class_bool_fields
    _bool_fields = set()
    _array_fields = set()
    _dict_fields = set()
    _cross_class_bool_fields = set()
    for cls in parsed.classes:
        for f in cls.fields:
            ann = (f.type_annotation or "").strip()
            cs_name = f.name if f.name.isupper() else snake_to_camel(f.name)
            if ann == "bool" or f.default_value in ("True", "False"):
                _bool_fields.add(cs_name)
                # Also cache on the cross-class set so per-class translation
                # resets don't lose it — needed to classify `other.eaten`
                # in Ghost when `eaten: bool` lives on GhostFrightened.
                _cross_class_bool_fields.add(cs_name)
            if "list[" in ann or "[]" in ann:
                _array_fields.add(cs_name)
            if "dict[" in ann or ann.startswith("Dict[") or ann.startswith("Dictionary<"):
                _dict_fields.add(cs_name)
                # Also add expression-translator variant for _prefixed names
                if f.name.startswith("_"):
                    parts = f.name.lstrip("_").split("_")
                    expr_name = parts[0] + "".join(p.capitalize() for p in parts[1:])
                    _dict_fields.add(expr_name)

    # Also collect dict fields from module-level constants
    for mc in parsed.module_constants:
        ann = (mc.type_annotation or "").strip()
        if "dict[" in ann or ann.startswith("Dict[") or ann.startswith("Dictionary<"):
            # Add both naming variants: snake_to_camel and the expression translator's
            # _underscore_to_camel produce different results for _prefixed names.
            mc_name = mc.name if mc.name.isupper() else snake_to_camel(mc.name)
            _dict_fields.add(mc_name)
            # Also add the variant that _translate_py_expression produces
            if mc.name.startswith("_"):
                parts = mc.name.lstrip("_").split("_")
                expr_name = parts[0] + "".join(p.capitalize() for p in parts[1:])
                _dict_fields.add(expr_name)

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


# ── Package dependency detection ─────────────────────────

# Maps C# using directives to the Unity packages that provide them
_USING_TO_PACKAGE: dict[str, str] = {
    "UnityEngine.UI": "com.unity.ugui",
    "UnityEngine.InputSystem": "com.unity.inputsystem",
    "Unity.TextMeshPro": "com.unity.textmeshpro",
    "TMPro": "com.unity.textmeshpro",
}


def detect_required_packages(cs_source: str) -> list[dict[str, str]]:
    """Scan translated C# source for using directives that require Unity packages.

    Returns a list of dicts with 'package' and 'reason' keys.
    """
    packages = []
    seen = set()
    for line in cs_source.split("\n"):
        stripped = line.strip()
        if not stripped.startswith("using "):
            continue
        # Extract namespace: "using Foo.Bar;" -> "Foo.Bar"
        ns = stripped[6:].rstrip(";").strip()
        if ns in _USING_TO_PACKAGE and _USING_TO_PACKAGE[ns] not in seen:
            pkg = _USING_TO_PACKAGE[ns]
            seen.add(pkg)
            packages.append({"package": pkg, "reason": f"using {ns}"})
    return packages


def _translate_class(cls: PyClass, parsed: PyFile) -> str:
    """Translate a PyClass to C# source."""
    if cls.is_enum:
        return _translate_enum(cls)
    if cls.is_monobehaviour:
        return _translate_monobehaviour(cls, parsed)
    if cls.is_scriptable_object:
        return _translate_scriptable_object(cls, parsed)
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
        elif py_name in _reserved_method_renames:
            symbols[py_name] = _reserved_method_renames[py_name]
        else:
            symbols[py_name] = snake_to_pascal(py_name)
        # Also map _private variants
        if not py_name.startswith("_"):
            symbols[f"_{py_name}"] = symbols[py_name]
        else:
            symbols[py_name] = snake_to_pascal(py_name.lstrip("_"))

    return symbols


_UNITY_INHERITED_ATTRS = {
    # Attributes inherited from MonoBehaviour / Component / GameObject / Behaviour
    # in C#.  Assigning `self.X = Y` in Python to any of these is manipulating
    # the built-in — the translator must NOT emit a shadowing field, otherwise
    # CS0108 fires and user code ends up writing to the shadow instead of the
    # real property.
    "enabled", "tag", "name", "hideFlags",
}


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
            if field_name in _UNITY_INHERITED_ATTRS:
                continue
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

    # 1.5. For bare `list` annotations, pick up trailing `# T[]` or `# list[T]`
    # comment hints from the original source line.  This handles the Flappy Bird
    # Player.sprites pattern (`self.sprites: list = []  # Sprite[]`) where the
    # author documents the element type out of band because the assignment
    # target comes from scene serialization rather than code.  Without this,
    # the translator emits `List<object>` and the generated C# won't compile.
    _hint_re = re.compile(r"#\s*(?:list\[(\w+)\]|(\w+)\[\])")
    for field in cls.fields:
        t = (field.type_annotation or "").strip()
        if t.endswith("| None"):
            t = t[:-7].strip()
        if t == "list" and field.name not in type_map and field.source_line:
            m = _hint_re.search(field.source_line)
            if m:
                element = m.group(1) or m.group(2)
                if element and element != "list":
                    type_map[field.name] = f"list[{element}]"

    # 1.6. For bare `object` annotations, pick up trailing
    # `# TypeName component`/`# TypeName reference`/`# TypeName instance`
    # comment hints.  Handles Ghost.initial_behavior
    # (`self.initial_behavior: object = None  # GhostBehavior component`) where
    # the author could not narrow the annotation because the field holds any
    # GhostBehavior subclass.  Without this, the translator emits
    # `public object initialBehavior` and downstream `.Enable()` / method
    # calls fail with CS1061 (data/lessons/pacman_v2_deploy.md gap PV-6).
    _obj_hint_re = re.compile(r"#\s*(\w+)\s+(?:component|reference|instance|type)\b")
    for field in cls.fields:
        t = (field.type_annotation or "").strip()
        if t.endswith("| None"):
            t = t[:-7].strip()
        if t == "object" and field.name not in type_map and field.source_line:
            m = _obj_hint_re.search(field.source_line)
            if m:
                hinted = m.group(1)
                # Only accept PascalCase identifiers — avoids false positives
                # like "# raw bytes payload" being picked up.
                if hinted and hinted[0].isupper():
                    type_map[field.name] = hinted

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
_current_method_params: set[str] = set()
_current_method_locals: set[str] = set()  # C# camelCase names of locals declared in the current method body
_current_class_methods: set[str] = set()  # Python snake_case method names of the class being translated.
# Consulted by _self_dot_replace so `self._method_name` (no parens — method-as-value
# reference) emits PascalCase `MethodName` instead of falling through to field-style
# camelCase. Surfaced by Space Invaders' GameManager.on_player_killed:
#     self._invoke_callback = self._new_round
# previously emitted `... = newRound;` — a dangling identifier, not the method.
_in_trigger_callback: bool = False
_in_coroutine: bool = False  # True when translating an IEnumerator method — rewrites `return` → `yield break;`
_declared_vars: dict[str, int] = {}  # local_name -> indent level of first declaration
_current_indent: int = 0
_enumerate_inject: str | None = None
_bool_fields: set[str] = set()  # C# names of fields with bool type
_array_fields: set[str] = set()  # C# names of fields with array types (use .Length not .Count)
_dict_fields: set[str] = set()  # C# names of fields with dict types (use .ContainsKey not .Contains)
_prefab_fields: set[str] = set()  # Prefab fields discovered from Instantiate() calls
_enum_values: dict[str, str] = {}  # "EnumType.UPPER_SNAKE" -> "EnumType.PascalCase"
_cross_class_bool_fields: set[str] = set()  # Bool field names across ALL classes in the translation unit — survives the per-class _bool_fields reset so `other.bool_field` can be correctly translated.
_project_bool_fields: set[str] = set()  # Bool field names across ALL files in the project — seeded by project_translator before per-file translate() calls.


def set_project_bool_fields(names: set[str]) -> None:
    """Seed the project-wide bool field cache.  Called by project_translator
    after a cross-file pre-scan so that `other_class_ref.bool_field` in one
    file is correctly typed when `bool_field` was declared in another file.
    Cleared by passing an empty set."""
    global _project_bool_fields
    _project_bool_fields = set(names)


def _translate_monobehaviour(cls: PyClass, parsed: PyFile) -> str:
    """Translate a MonoBehaviour subclass using the Jinja2 template."""
    global _current_symbols, _bool_fields, _array_fields, _dict_fields, _prefab_fields, _current_class_methods
    _bool_fields = set()
    _array_fields = set()
    _dict_fields = set()
    _prefab_fields = set()
    _current_class_methods = {m.name for m in cls.methods}
    attributes = _infer_attributes(cls)

    # Discover dynamic fields (self.X = Y in methods, not in __init__) first,
    # so _infer_using_directives sees their types (e.g., Dictionary<>, List<>) and
    # emits the right `using` statements — S10-1.
    dynamic_fields = _discover_dynamic_fields(cls)
    cls.fields.extend(dynamic_fields)

    extra_using = _infer_using_directives(cls, parsed)

    # Build symbol table for consistent naming in method bodies
    _current_symbols = _build_symbol_table(cls)

    # Add module-level constants to symbol table (they stay UPPER_CASE)
    for mc in parsed.module_constants:
        _current_symbols[mc.name] = mc.name  # Keep UPPER_CASE as-is

    # Infer field types from annotations and get_component() calls
    inferred_types = _infer_field_types(cls)

    # G2: if inference produced any List<>/Dictionary<>/HashSet<> types, ensure
    # `using System.Collections.Generic;` is present.  _infer_using_directives
    # only saw the raw annotation text; by the time inference fires (e.g., from
    # .append() + get_component() chains), new generic usages appear that the
    # earlier pass missed.  Without this, the generated C# fails to compile.
    if any(
        t.startswith(("List<", "Dictionary<", "HashSet<"))
        for t in inferred_types.values()
    ) and "System.Collections.Generic" not in extra_using:
        extra_using = sorted(set(extra_using) | {"System.Collections.Generic"})

    # Detect fields accessed via ClassName.field (static access pattern)
    # e.g., GameManager.score, GameManager._instance — these must be `static`
    classname_accessed_fields: set[str] = set()
    for method in cls.methods:
        for m in re.finditer(rf"{re.escape(cls.name)}\.(\w+)", method.body_source):
            classname_accessed_fields.add(m.group(1))

    serialized_fields = []
    private_fields = []
    static_fields = []

    # Add module-level constants as static fields
    for mc in parsed.module_constants:
        # Use type annotation if available, otherwise infer from value
        if mc.type_annotation:
            mc_type = _py_type_to_csharp(mc.type_annotation, is_field=True)
        else:
            mc_type = _infer_constant_type(mc.default_value)
        if not mc_type:
            mc_type = "object"
        mc_default = _py_value_to_csharp(mc.default_value, mc_type) if mc.default_value else None
        # S12-3: Convert snake_case names to camelCase at the declaration site
        # so references translated by the expression pass line up. UPPER_SNAKE
        # constants stay as-is. Leading underscores are stripped first to match
        # how the expression translator rewrites `_recent_teleports` →
        # `recentTeleports` (not `RecentTeleports` as snake_to_camel would do).
        if mc.name.isupper():
            mc_decl_name = mc.name
        else:
            stripped = mc.name.lstrip("_")
            parts = stripped.split("_")
            mc_decl_name = parts[0] + "".join(p.capitalize() for p in parts[1:])
        static_fields.append({
            "csharp_type": mc_type,
            "csharp_name": mc_decl_name,
            "default": mc_default,
        })
        # Track dict-typed module constants for 'in' -> ContainsKey translation
        if mc_type.startswith("Dictionary<"):
            mc_cs_name = mc.name if mc.name.isupper() else snake_to_camel(mc.name)
            _dict_fields.add(mc_cs_name)
            # Also add expression-translator variant for _prefixed names
            if mc.name.startswith("_"):
                parts = mc.name.lstrip("_").split("_")
                expr_name = parts[0] + "".join(p.capitalize() for p in parts[1:])
                _dict_fields.add(expr_name)

    for field in cls.fields:
        # Use inferred type if available, otherwise fall back to annotation
        if field.name in inferred_types:
            csharp_type = _py_type_to_csharp(inferred_types[field.name], is_field=True)
        else:
            csharp_type = _py_type_to_csharp(field.type_annotation, is_field=True, default_value=field.default_value or "")
        # Preserve UPPER_CASE constants; strip leading `_` and camelCase others.
        # snake_to_camel("_body_sr") → "BodySr" (PascalCase) which doesn't match
        # the expression translator's lower-first-letter form. Matching both
        # requires stripping the leading underscore first.
        if field.name.isupper():
            csharp_name = field.name
        else:
            stripped = field.name.lstrip("_")
            parts = stripped.split("_")
            csharp_name = parts[0] + "".join(p.capitalize() for p in parts[1:])
        default = _py_value_to_csharp(field.default_value, csharp_type) if field.default_value else None

        # Track bool fields so condition translator can avoid != null
        if csharp_type == "bool":
            _bool_fields.add(csharp_name)
        # Track array fields so len() translator can use .Length not .Count
        if csharp_type.endswith("[]"):
            _array_fields.add(csharp_name)
        # Track dict fields so 'in' operator uses .ContainsKey() not .Contains()
        if csharp_type.startswith("Dictionary<"):
            _dict_fields.add(csharp_name)
            # Also add expression-translator variant for _prefixed names
            if field.name.startswith("_"):
                parts = field.name.lstrip("_").split("_")
                expr_name = parts[0] + "".join(p.capitalize() for p in parts[1:])
                _dict_fields.add(expr_name)

        # For reference types, strip nullable ? suffix (C# reference types are already nullable)
        is_ref = _is_reference_type(csharp_type, parsed)
        if is_ref and csharp_type.endswith("?"):
            csharp_type = csharp_type[:-1]

        # Reference fields always emit as `[SerializeField] private T field;`
        # so Unity's Inspector can wire them (prevents the Player.gameManager
        # NullRef class — FU-3). When the *owning* class is subclassed
        # somewhere in the project, upgrade to `protected` so C# subclasses
        # can still reach the base field (e.g. GhostBehavior.ghost is read
        # by GhostChase / GhostFrightened / GhostHome / GhostScatter).
        access = (
            "protected" if cls.name in _config.subclassed_classes else "private"
        )

        # Trailing-comment override: `self.x: T = None  # public T x` forces
        # `public T x;` (no [SerializeField]) so other translated classes in
        # the project can read/write it without CS0122.  Honours both
        # `# public T name` and `# public T` hints.  Discovered on FU-2
        # home-machine playtest — Spawner.cs wrote pipes_comp.top/.bottom
        # while Pipes.cs had them as [SerializeField] private after FU-3.
        force_public = False
        if is_ref and field.source_line:
            hint = re.search(r"#\s*public\s+\w+(?:\s+\w+)?\s*$",
                             field.source_line)
            if hint:
                force_public = True

        # Cross-class-access override: if this field is read/written as
        # `x.FIELD` from some OTHER class's method body in the same project,
        # FU-3's private default blocks the access (CS0122). project_translator
        # scans for this and calls set_cross_accessed_fields. Surfaced during
        # FU-2 pacman_v2 playtest — Ghost.chase/scatter/frightened/home/eyes
        # / movement/target are read from the ghost-state classes.
        if is_ref and field.name in _config.cross_accessed_fields.get(cls.name, set()):
            force_public = True

        entry = {
            "csharp_type": csharp_type,
            "csharp_name": csharp_name,
            "default": default,
            "serialize": is_ref and not force_public,
            "access": access,
            "force_public": force_public,
        }

        if field.is_class_level and field.name.isupper():
            # UPPER_CASE constants are truly static (e.g. PACMAN_LAYER = 7)
            static_fields.append(entry)
        elif field.is_class_level and field.name in classname_accessed_fields:
            # Fields accessed via ClassName.field in method bodies (e.g. GameManager.score)
            static_fields.append(entry)
        elif is_ref:
            # Reference types -> public T field  OR  [SerializeField] private T field
            private_fields.append(entry)
        elif default is not None and default != "null":
            serialized_fields.append(entry)
        else:
            private_fields.append(entry)

    methods = []
    for method in cls.methods:
        methods.append(_translate_method(method))

    # Add module-level functions as public static methods (on last MonoBehaviour class only)
    mono_classes = [c for c in parsed.classes if c.is_monobehaviour]
    if mono_classes and cls.name == mono_classes[-1].name:
        for func in parsed.module_functions:
            m = _translate_method(func)
            m['access'] = 'public static'
            methods.append(m)

    # Add discovered prefab fields (from Instantiate() calls in methods)
    existing_fields = {f['csharp_name'] for f in serialized_fields + private_fields + static_fields}
    for pf in _prefab_fields:
        if pf not in existing_fields:
            private_fields.append({
                "csharp_type": "GameObject",
                "csharp_name": pf,
                "default": None,
                "serialize": True,
            })

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


def _translate_scriptable_object(cls: PyClass, parsed: PyFile) -> str:
    """Translate a ScriptableObject subclass using the SO template.

    ScriptableObjects share most field/method translation with MonoBehaviours
    but emit ``public class X : ScriptableObject`` and an optional
    ``[CreateAssetMenu(...)]`` attribute derived from the ``@create_asset_menu``
    decorator on the Python source.
    """
    global _current_symbols, _bool_fields, _array_fields, _dict_fields, _prefab_fields, _current_class_methods
    _bool_fields = set()
    _array_fields = set()
    _dict_fields = set()
    _prefab_fields = set()
    _current_class_methods = {m.name for m in cls.methods}
    attributes = _infer_attributes(cls)

    extra_using = _infer_using_directives(cls, parsed)
    _current_symbols = _build_symbol_table(cls)
    for mc in parsed.module_constants:
        _current_symbols[mc.name] = mc.name

    inferred_types = _infer_field_types(cls)
    classname_accessed_fields: set[str] = set()
    for method in cls.methods:
        for m in re.finditer(rf"{re.escape(cls.name)}\.(\w+)", method.body_source):
            classname_accessed_fields.add(m.group(1))

    serialized_fields: list[dict] = []
    private_fields: list[dict] = []
    static_fields: list[dict] = []

    for field in cls.fields:
        if field.name in inferred_types:
            csharp_type = _py_type_to_csharp(inferred_types[field.name], is_field=True)
        else:
            csharp_type = _py_type_to_csharp(
                field.type_annotation, is_field=True,
                default_value=field.default_value or "",
            )
        csharp_name = field.name if field.name.isupper() else snake_to_camel(field.name)
        default = _py_value_to_csharp(field.default_value, csharp_type) if field.default_value else None

        if csharp_type == "bool":
            _bool_fields.add(csharp_name)
        if csharp_type.endswith("[]"):
            _array_fields.add(csharp_name)
        if csharp_type.startswith("Dictionary<"):
            _dict_fields.add(csharp_name)

        is_ref = _is_reference_type(csharp_type, parsed)
        if is_ref and csharp_type.endswith("?"):
            csharp_type = csharp_type[:-1]

        entry = {
            "csharp_type": csharp_type,
            "csharp_name": csharp_name,
            "default": default,
            "serialize": is_ref,
        }

        if field.is_class_level and field.name.isupper():
            static_fields.append(entry)
        elif field.is_class_level and field.name in classname_accessed_fields:
            static_fields.append(entry)
        elif is_ref:
            private_fields.append(entry)
        elif default is not None and default != "null":
            serialized_fields.append(entry)
        else:
            private_fields.append(entry)

    methods = [_translate_method(m) for m in cls.methods]

    # Build [CreateAssetMenu(...)] argument string from decorator metadata.
    # Only include keys the user actually supplied (skip empty strings / 0 order).
    create_asset_menu_str: str | None = None
    meta = cls.create_asset_menu
    if meta:
        parts: list[str] = []
        fn = meta.get("file_name")
        mn = meta.get("menu_name")
        order = meta.get("order")
        if fn:
            parts.append(f'fileName = "{fn}"')
        if mn:
            parts.append(f'menuName = "{mn}"')
        if order:
            parts.append(f"order = {order}")
        create_asset_menu_str = ", ".join(parts) if parts else ""

    template = _jinja_env.get_template("scriptable_object.cs.j2")
    return template.render(
        class_name=cls.name,
        extra_using=extra_using,
        attributes=attributes,
        create_asset_menu=create_asset_menu_str,
        serialized_fields=serialized_fields,
        private_fields=private_fields,
        static_fields=static_fields,
        methods=methods,
    )


def _translate_plain_class(cls: PyClass, parsed: PyFile) -> str:
    """Translate a non-MonoBehaviour class to C#.

    Non-MonoBehaviour covers user base classes that indirectly inherit from
    MonoBehaviour (e.g. GhostBehavior in pacman_v2). Those classes can still
    have coroutines and generic collections, so emit the same
    using-directive set we compute for MonoBehaviours.
    """
    global _current_class_methods
    _current_class_methods = {m.name for m in cls.methods}
    lines = ["using UnityEngine;"]
    for ns in _infer_using_directives(cls, parsed):
        lines.append(f"using {ns};")
    base = cls.base_classes[0] if cls.base_classes else ""
    base_str = f" : {base}" if base else ""
    lines.append(f"public class {cls.name}{base_str}")
    lines.append("{")

    for field in cls.fields:
        csharp_type = _py_type_to_csharp(field.type_annotation, is_field=True, default_value=field.default_value or "")
        # Preserve UPPER_CASE constants; strip leading `_` + camelCase others
        # to match the expression-translator's naming (e.g. `_body_sr` → `bodySr`).
        if field.name.isupper():
            csharp_name = field.name
        else:
            stripped = field.name.lstrip("_")
            parts = stripped.split("_")
            csharp_name = parts[0] + "".join(p.capitalize() for p in parts[1:])
        mod = "public static" if (field.is_class_level and field.name.isupper()) else "public"
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
    elif method.name in _reserved_method_renames:
        csharp_name = _reserved_method_renames[method.name]
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
    # Save _bool_fields so per-method bool param/local additions don't
    # poison sibling methods on the same class.
    saved_bool_fields = set(_bool_fields)
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
        # S10-3: emit default-value when the Python parameter has one, so
        # callers passing fewer args still compile (e.g. `SetDirection(dir)`
        # when signature is `SetDirection(Vector2, bool forced = false)`).
        if p.default_value is not None:
            cs_default = _py_value_to_csharp(p.default_value, csharp_type) or p.default_value
            params.append(f"{csharp_type} {csharp_param_name} = {cs_default}")
        else:
            params.append(f"{csharp_type} {csharp_param_name}")
        # Add param to symbol table
        _current_symbols[p.name] = csharp_param_name
        # Track bool params so `if forced:` translates to `if (forced)`
        # rather than `if (forced != null)`.  `_bool_fields` is consulted
        # by `_translate_py_condition` for the truthiness decision.
        if csharp_type == "bool":
            _bool_fields.add(csharp_param_name)
    params_str = ", ".join(params)

    # Track parameter names (camelCase) for this.X shadowing detection
    global _current_method_params, _current_method_locals, _in_trigger_callback, _in_coroutine
    _current_method_params = {snake_to_camel(p.name) for p in method.parameters}
    _current_method_locals = set()
    _in_trigger_callback = method.name in _trigger_methods
    _in_coroutine = method.is_coroutine

    # Extract local variable names and add to symbol table
    _add_locals_to_symbols(method.body_source)
    # Also detect local bool assignments so `if changing_axis:` doesn't
    # get `!= null` appended (CS0019 on value types).
    _detect_bool_locals(method.body_source)

    # Discover prefab fields from raw Python source: instantiate(self.xxx_prefab, ...)
    for prefab_match in re.finditer(r'instantiate\(self\.(\w*prefab\w*)', method.body_source, re.IGNORECASE):
        py_name = prefab_match.group(1)
        camel = snake_to_camel(py_name)
        _prefab_fields.add(camel)

    # Body
    body = _translate_body(method.body_source)

    # Match both the legacy FindObjectsOfType<T>() and the Unity 6
    # FindObjectsByType<T>(FindObjectsSortMode.None) rewrites — both return
    # T[] so .Count must be rewritten to .Length on the assigned local.
    array_locals = {m.group(1) for m in re.finditer(
        r"\bvar\s+(\w+)\s*=\s*[^;]*FindObjects(?:Of|By)Type<", body
    )}
    for name in array_locals:
        body = re.sub(rf"\b{re.escape(name)}\.Count\b", f"{name}.Length", body)

    body = re.sub(
        r"foreach\s*\(\s*var\s+(\w+)\s+in\s+([\w.]*transform)\.children\s*\)",
        r"foreach (Transform \1 in \2)",
        body,
    )
    body = re.sub(r"\btransform\.children\b", "transform", body)

    # Restore symbol table (remove method-scoped names)
    _current_symbols = saved_symbols
    _bool_fields.clear()
    _bool_fields.update(saved_bool_fields)
    _current_method_params = set()
    _current_method_locals = set()
    _in_trigger_callback = False
    _in_coroutine = False

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


_BOOL_EXPR_RE = re.compile(
    r"\b(and|or|not)\b|==|!=|<=|>=|<(?!=)|>(?!=)|\bTrue\b|\bFalse\b"
)


def _detect_bool_locals(body_source: str) -> None:
    """Scan the method body for assignments whose RHS is a boolean expression
    (uses `and`/`or`/`not`, comparison ops, or `True`/`False` literals) and
    add the local's C# name to `_bool_fields`.  The condition translator
    consults this set to avoid emitting `!= null` for bool locals — which
    would be CS0019 on value types.

    Handles the Movement.set_direction pattern (multi-line RHS):
        changing_axis = (
            (x != 0 and y != 0) or
            (x == 1 or y == 1)
        )
        if changing_axis:   # → `if (changingAxis)`, not `if (changingAxis != null)`

    Uses `_join_multiline` so RHS spanning multiple physical lines is
    analysed as a single logical expression.
    """
    global _bool_fields
    for _indent, line in _join_multiline(body_source.split("\n")):
        m = re.match(r"^([a-z_]\w*)\s*(?::\s*bool\s*)?=\s*(.+)$", line)
        if not m:
            continue
        name, rhs = m.group(1), m.group(2)
        if "." in name or name == "self":
            continue
        rhs_stripped = rhs.strip().rstrip(":")
        if _BOOL_EXPR_RE.search(rhs_stripped):
            _bool_fields.add(snake_to_camel(name))


def _add_locals_to_symbols(body_source: str) -> None:
    """Extract local variable assignments and add to symbol table.

    Also records each local's camelCase name in `_current_method_locals`
    so the self-dot replacer knows to emit `this.X` (not bare `X`) when a
    field and a local share a name — otherwise `self.X = X` collapses to
    a `X = X;` self-assignment on the local.
    """
    global _current_symbols, _current_method_locals
    def _record(py_name: str) -> None:
        if not py_name or py_name == "_":
            return
        cs_name = snake_to_camel(py_name)
        # Always mark as a method-scoped local, even if a class field
        # with the same name pre-registered it in `_current_symbols` —
        # the shadowing itself is the signal the self-dot replacer needs.
        _current_method_locals.add(cs_name)
        if py_name not in _current_symbols:
            _current_symbols[py_name] = cs_name
    for line in body_source.split("\n"):
        stripped = line.strip()
        # Match: var_name: Type = expression (typed assignment)
        m = re.match(r"^([a-z_]\w*)\s*:\s*\S+.*=\s*", stripped)
        if m and not stripped.startswith("self."):
            _record(m.group(1))
            continue
        # Match: var_name = expression (not self.var_name)
        m = re.match(r"^([a-z_]\w*)\s*=\s*", stripped)
        if m and not stripped.startswith("self."):
            _record(m.group(1))
        # Match for-loop variables: for var_name in ...
        m = re.match(r"^for\s+(\w+)\s+in\s+", stripped)
        if m:
            _record(m.group(1))
        # Match: for idx, var in enumerate(...)
        m = re.match(r"^for\s+(\w+),\s*(\w+)\s+in\s+", stripped)
        if m:
            _record(m.group(1))
            _record(m.group(2))


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


def _collect_hoist_candidates(
    logical_lines: list[tuple[int, str]],
) -> dict[str, str]:
    """Identify local variables whose usage indent is shallower than any of
    their assignments — they must be hoisted to the method-body base so C#
    block scoping doesn't lose them.  Returns ``{name: first_rhs}`` so the
    caller can infer a type.

    Example (from data/lessons/pacman_v2_deploy.md gap PV-7,
    Movement.SetDirection):

        if direction.x != 0:
            snapped = Vector2(...)     # assigned at indent 3
        else:
            snapped = Vector2(...)     # assigned at indent 3
        check_pos = Vector2(snapped.x, ...)   # read at indent 2 (shallower)

    Without hoisting, the per-branch ``Vector2 snapped = …`` declarations
    don't survive into the outer ``check_pos`` read (CS0103).
    """
    # Collect: name -> (all assignment indents, first RHS seen)
    assign_info: dict[str, tuple[list[int], str]] = {}
    for indent, line in logical_lines:
        m = re.match(r"^([a-z_]\w*)\s*:\s*\S+.*=\s*(.+)$", line)
        if m and "." not in m.group(1):
            name = m.group(1)
            if name in assign_info:
                assign_info[name][0].append(indent)
            else:
                assign_info[name] = ([indent], m.group(2))
            continue
        m = re.match(r"^([a-z_]\w*)\s*=\s*(.+)$", line)
        if m and "." not in m.group(1):
            name = m.group(1)
            if name in assign_info:
                assign_info[name][0].append(indent)
            else:
                assign_info[name] = ([indent], m.group(2))

    candidates: dict[str, str] = {}
    for name, (indents, first_rhs) in assign_info.items():
        min_assign = min(indents)
        # Skip top-level locals (nothing to hoist to).
        if min_assign == 0:
            continue
        # The lookbehind excludes member-access matches (`.x`, `.y`) — we
        # don't want `position.x` to count as a read of a local named `x`.
        # Without it, single-letter names collide with common Unity
        # properties (Vector2.x, Transform.position.x, etc.) and generate
        # spurious `var x = default;` hoists (CS0818 — `default` has no
        # inferrable type on its own).
        name_re = re.compile(rf"(?<![\.\w]){re.escape(name)}(?!\w)")
        assign_lhs_re = re.compile(rf"^{re.escape(name)}\s*[:=]")
        for use_indent, use_line in logical_lines:
            if use_indent >= min_assign:
                continue  # Not shallower — not an escaping use.
            if assign_lhs_re.match(use_line):
                continue  # This line IS an assignment to the name; not a read.
            if name_re.search(use_line):
                candidates[name] = first_rhs
                break
    return candidates


def _translate_body(body: str) -> str:
    """Translate Python method body to C#, adding braces for indented blocks."""
    if not body.strip():
        return ""

    raw_lines = body.split("\n")

    # First pass: join multi-line expressions into logical lines
    logical_lines = _join_multiline(raw_lines)

    # Track declared local variables to avoid redeclaration.  The dict maps
    # name -> indent level where it was first declared; before each
    # statement we prune entries whose stored indent is deeper than the
    # current line, because those declarations lived in sibling blocks
    # that have now ended.  Python's flat function scope lets
    # `if A: x = 1` and `if B: x = 2` share a name across sibling blocks
    # without C# block-scope conflict — the cleanest translation is to
    # let each sibling block re-declare its own `var x`.  Without the
    # prune, the second block emitted bare `x = 2` and Unity flagged
    # CS0103 (see data/lessons/pacman_v2_deploy.md gap PV-1 /
    # GhostHome.cs's ExitTransition coroutine).
    global _declared_vars, _enumerate_inject, _current_indent
    # Seed with parameter names at the method-body base indent (0).  In
    # C#, a local cannot shadow a method parameter (CS0136) — reassigning
    # a parameter inside the body must emit a bare `X = ...;`, not a
    # fresh `var X = ...;`.  Fixes data/lessons/pacman_v2_deploy.md gap
    # PV-4 (GhostBehavior.Enable reassigns the `duration` parameter
    # inside a sibling if-block).
    _declared_vars = {name: 0 for name in _current_method_params}

    # PV-7: variables assigned inside nested blocks and read at a
    # shallower indent must be hoisted to the method-body base — C#
    # block scoping would drop them after the inner block closes (CS0103).
    # Seed `_declared_vars` with them at indent 0 so all in-branch
    # assignments emit as bare reassignments, and emit the declarations
    # explicitly at the top of the method body below.
    hoist_candidates = _collect_hoist_candidates(logical_lines)
    for hname in hoist_candidates:
        _declared_vars[hname] = 0

    _enumerate_inject = None
    _current_indent = 0

    # Second pass: translate each logical line
    entries: list[tuple[int, str]] = []

    # Emit hoisted declarations at the method-body base (indent 0) for
    # variables whose usage indent is shallower than their assignment
    # indent (PV-7).  This way subsequent in-branch assignments — now
    # routed through the `cs_target in _declared_vars` path — emit as
    # bare reassignments, and the symbol is in scope at the outer-indent
    # usage.
    for hname, hfirst_rhs in list(hoist_candidates.items()):
        hcs_name = snake_to_camel(hname)
        # Params are already in scope and seeded by the PV-4 fix — skip
        # emitting a hoisted declaration for them (it would redeclare the
        # parameter).  The seed stays put so in-body assignments still
        # emit bare reassignments.
        if hcs_name in _current_method_params:
            continue
        hcs_type = _infer_expression_type(hfirst_rhs)
        # `var x = default;` is CS0818 — `default` on its own has no
        # inferrable type.  When we can't concretely type the RHS, skip
        # hoisting for that name (fall back to per-branch declarations —
        # PV-1 pattern).  Remove from the seed set too so in-branch
        # assignments still emit `var` declarations.
        if not hcs_type or hcs_type == "var":
            _declared_vars.pop(hcs_name, None)
            hoist_candidates.pop(hname, None)
            continue
        entries.append((0, f"{hcs_type} {hcs_name} = default;"))

    strip_block_indent: int | None = None  # When set, skip lines deeper than this
    in_docstring = False  # Track multi-line docstrings
    for indent_level, logical_line in logical_lines:
        # If we're stripping a block, skip until indent returns to block level
        if strip_block_indent is not None:
            if indent_level > strip_block_indent:
                continue  # Skip indented body of stripped block
            else:
                strip_block_indent = None  # Block ended, resume

        # Prune `_declared_vars` entries whose stored indent is deeper than
        # the current line — they were declared inside a block we've now
        # exited, so sibling blocks that reassign the same Python name
        # get their own `var X = …` declaration in C#.  Fixes the
        # GhostHome.cs coroutine pattern documented in
        # data/lessons/pacman_v2_deploy.md gap PV-1.
        _current_indent = indent_level
        stale = [n for n, d in _declared_vars.items() if d > indent_level]
        for n in stale:
            del _declared_vars[n]

        # Track multi-line docstrings
        if in_docstring:
            if '"""' in logical_line or "'''" in logical_line:
                in_docstring = False
            continue
        if logical_line.startswith('"""') or logical_line.startswith("'''"):
            # Single-line docstring (opens and closes on same line)
            if logical_line.count('"""') >= 2 or logical_line.count("'''") >= 2:
                continue  # Skip entire single-line docstring
            in_docstring = True
            continue

        if not logical_line or logical_line == "super().__init__()":
            continue
        if logical_line == "pass":
            # Emit empty statement so parent if/else/while blocks aren't stripped
            entries.append((indent_level, "/* pass */"))
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

    # Remove if/else-if/else entries with empty bodies (all children stripped)
    cleaned = []
    for i, (level, text) in enumerate(entries):
        if re.match(r"^(if \(|else if \(|else$|try$)", text):
            # Check if next entry is at a deeper indent (has a body)
            has_body = (i + 1 < len(entries) and entries[i + 1][0] > level)
            if not has_body:
                # Also skip the following catch/else that belongs to this empty block
                continue
        # Skip catch blocks that follow a stripped try
        if re.match(r"^catch\b", text):
            # Check if previous non-empty entry was a try (which would have been kept)
            prev_kept = cleaned[-1][1] if cleaned else ""
            if not prev_kept.startswith("try"):
                continue
        cleaned.append((level, text))
    entries = cleaned

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

    # pass statement — skip (produces empty method body in C#)
    if line == "pass":
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

    # Return — inside a coroutine (IEnumerator method), Python's early-exit
    # `return` or `return None` must become `yield break;`.  A plain
    # `return;` or `return null;` inside IEnumerator is CS1622.  Regression
    # for data/lessons/pacman_v2_deploy.md gap PV-3
    # (GhostHome.ExitTransition).
    if line.startswith("return "):
        value = line[7:].strip()
        if _in_coroutine and value in ("None", "null", ""):
            return "yield break;"
        value = _translate_py_expression(value)
        return f"return {value};"
    if line == "return":
        if _in_coroutine:
            return "yield break;"
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
            _declared_vars[cs_a] = _current_indent
            _declared_vars[cs_b] = _current_indent
            return f"var {cs_a} = {val_a}; var {cs_b} = {val_b};"
        else:
            # Single value — use C# tuple deconstruction
            val = _translate_py_expression(rhs)
            # If vars already declared, use assignment (no var)
            if cs_a in _declared_vars and cs_b in _declared_vars:
                return f"({cs_a}, {cs_b}) = {val}.Value;"
            _declared_vars[cs_a] = _current_indent
            _declared_vars[cs_b] = _current_indent
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
        # Always emit full declaration — Python typed assignments create new scope variables
        # This handles re-declarations in sibling if/elif blocks correctly
        _declared_vars[cs_target] = _current_indent
        if cs_type.endswith("[]"):
            _array_fields.add(cs_target)
            # Fix .ToList() → .ToArray() when target is array type
            if cs_value.endswith(".ToList()"):
                cs_value = cs_value[:-len(".ToList()")] + ".ToArray()"
        return f"{cs_type} {cs_target} = {cs_value};"

    # Typed declaration without assignment: var: Type (no =)
    typed_decl = re.match(r"^(\w+)\s*:\s*(.+)$", line)
    if typed_decl and "." not in typed_decl.group(1) and "=" not in typed_decl.group(2):
        var_name, py_type = typed_decl.groups()
        cs_target = _translate_py_expression(var_name)
        cs_type = _translate_type_annotation(py_type)
        if cs_target not in _declared_vars:
            _declared_vars[cs_target] = _current_indent
            return f"{cs_type} {cs_target};"
        return ""  # Already declared, skip

    # Assignment
    assign_match = re.match(r"^([\w.]+)\s*=\s*(.+)$", line)
    if assign_match:
        target, value = assign_match.groups()
        cs_target = _translate_py_expression(target)
        cs_value = _translate_py_expression(value)
        if cs_value == "__STRIP__" or cs_target == "__STRIP__":
            return ""

        # Immutable-struct-write fixups: Unity's Transform.position and
        # Transform.eulerAngles are value types, so
        # `transform.position.x = foo` / `transform.eulerAngles.z = bar`
        # don't compile. Splat through a fresh struct literal.
        pos_axis = re.match(r"^((?:[\w.]+\.)?transform)\.position\.([xyz])$", cs_target)
        if pos_axis:
            prefix, axis = pos_axis.group(1), pos_axis.group(2)
            pos = f"{prefix}.position"
            if axis == "x":
                return f"{pos} = new Vector3({cs_value}, {pos}.y, {pos}.z);"
            if axis == "y":
                return f"{pos} = new Vector3({pos}.x, {cs_value}, {pos}.z);"
            return f"{pos} = new Vector3({pos}.x, {pos}.y, {cs_value});"
        euler_axis = re.match(r"^((?:[\w.]+\.)?transform)\.eulerAngles\.z$", cs_target)
        if euler_axis:
            prefix = euler_axis.group(1)
            return f"{prefix}.rotation = Quaternion.Euler(0f, 0f, {cs_value});"
        rot_z = re.match(r"^((?:[\w.]+\.)?transform)\.rotation_?[Zz]$", cs_target)
        if rot_z:
            prefix = rot_z.group(1)
            return f"{prefix}.rotation = Quaternion.Euler(0f, 0f, {cs_value});"
        # Strip simulator-only property assignments
        if re.search(r"\.(clipRef|assetRef)\s*$", cs_target):
            return ""
        # Infer type for variable declarations (skip if already declared)
        if "." not in target and not target.startswith("self"):
            if cs_target in _declared_vars:
                # Already declared — just assign
                return f"{cs_target} = {cs_value};"
            _declared_vars[cs_target] = _current_indent
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
        # Python discard variable '_' -> C# '_i' (snake_to_camel("_") returns "")
        cs_var = "_i" if var == "_" else snake_to_camel(var)
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
        _declared_vars[idx_var] = _current_indent
        _declared_vars[val_var] = _current_indent
        # The body translator will add the val_var declaration as first line in the block
        # We store it for injection
        global _enumerate_inject
        _enumerate_inject = f"var {val_var} = {collection}[{idx_var}];"
        last_part = collection.rsplit(".", 1)[-1] if "." in collection else collection
        prop = ".Length" if (collection in _array_fields or last_part in _array_fields) else ".Count"
        return f"for (int {idx_var} = 0; {idx_var} < {collection}{prop}; {idx_var}++)"

    # Match: var in collection (foreach)
    foreach_match = re.match(r"(\w+)\s+in\s+(.+)$", body)
    if foreach_match:
        var = foreach_match.group(1)
        collection = foreach_match.group(2).strip()
        cs_var = snake_to_camel(var)
        cs_collection = _translate_py_expression(collection)
        return f"foreach (var {cs_var} in {cs_collection})"

    # S9-2: Tuple unpacking — `for a, b [, c...] in coll:` → C# deconstruction
    # Emit `foreach (var (a, b) in coll)` (C# 7.0+ tuple deconstruction syntax).
    # Parenthesized form `for (a, b) in coll:` is also accepted.
    tuple_match = re.match(
        r"\(?\s*(\w+(?:\s*,\s*\w+)+)\s*\)?\s+in\s+(.+)$",
        body,
    )
    if tuple_match:
        names = [n.strip() for n in tuple_match.group(1).split(",")]
        cs_names = [snake_to_camel(n) for n in names]
        collection = tuple_match.group(2).strip()
        cs_collection = _translate_py_expression(collection)
        for n in cs_names:
            _declared_vars[n] = _current_indent
        return f"foreach (var ({', '.join(cs_names)}) in {cs_collection})"

    # Fallback — unrecognized for-loop shape
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
            # Check both bare name and dotted form (e.g., ROW_CONFIG or Invaders.ROW_CONFIG)
            last_part = inner_translated.rsplit(".", 1)[-1] if "." in inner_translated else inner_translated
            prop = ".Length" if (inner_translated in _array_fields or last_part in _array_fields) else ".Count"
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
        cs_pred = _translate_py_condition(re.sub(rf"\b{re.escape(var)}\b", cs_var, pred) if var != "_" else pred)
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
        cs_pred = _translate_py_condition(re.sub(rf"\b{re.escape(var)}\b", cs_var, pred) if var != "_" else pred)
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
        cs_mapping = _translate_py_expression(re.sub(rf"\b{re.escape(var)}\b", cs_var, mapping) if var != "_" else mapping)
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
        cs_mapping = _translate_py_expression(re.sub(rf"\b{re.escape(var)}\b", cs_var, mapping) if var != "_" else mapping)
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
    """Translate Input.get_* calls to Unity New Input System (Mouse/Keyboard).

    Every emitted access is null-safe: `Keyboard.current` and
    `Mouse.current` return null when the corresponding device hasn't
    been registered (the default state during `-batchmode -runTests`,
    which has no real input device backend).  Bare unguarded reads
    threw NullReferenceException on every Update() tick under that
    environment — see translator-input-system-null-guard for the
    forensic trail (workflow runs 24971232854, 24971807340).

    The Boolean-coerced null-conditional pattern
        Keyboard.current?.spaceKey.wasPressedThisFrame == true
    collapses `bool?` back to `bool` so `if`, `||`, `&&`, and ternary
    chains continue to work.  Vector2 reads (`mouse_position`) coalesce
    against `Vector2.zero` so the result type stays Vector2.
    """
    # Input.get_mouse_button_down(0) -> Mouse.current?.leftButton.wasPressedThisFrame == true
    expr = re.sub(
        r"Input\.get_mouse_button_down\((\d)\)",
        lambda m: f"Mouse.current?.{_MOUSE_BUTTON_MAP.get(m.group(1), 'leftButton')}.wasPressedThisFrame == true",
        expr,
    )
    # Input.get_mouse_button_up(0) -> Mouse.current?.leftButton.wasReleasedThisFrame == true
    expr = re.sub(
        r"Input\.get_mouse_button_up\((\d)\)",
        lambda m: f"Mouse.current?.{_MOUSE_BUTTON_MAP.get(m.group(1), 'leftButton')}.wasReleasedThisFrame == true",
        expr,
    )
    # Input.get_mouse_button(0) -> Mouse.current?.leftButton.isPressed == true
    expr = re.sub(
        r"Input\.get_mouse_button\((\d)\)",
        lambda m: f"Mouse.current?.{_MOUSE_BUTTON_MAP.get(m.group(1), 'leftButton')}.isPressed == true",
        expr,
    )
    # Input.get_mouse_position() / Input.mouse_position -> Vector2-typed read with
    # a Vector2.zero fallback when the device is missing — keeps the result type
    # Vector2 (not Vector2?) so callers needing arithmetic don't break.
    expr = re.sub(
        r"Input\.get_mouse_position\(\)",
        "(Mouse.current?.position.ReadValue() ?? Vector2.zero)",
        expr,
    )
    expr = re.sub(
        r"Input\.mouse_position",
        "(Mouse.current?.position.ReadValue() ?? Vector2.zero)",
        expr,
    )

    # Input.get_key_down('space') -> Keyboard.current?.spaceKey.wasPressedThisFrame == true
    expr = re.sub(
        r"Input\.get_key_down\(['\"](\w+)['\"]\)",
        lambda m: f"Keyboard.current?.{_KEY_NAME_MAP.get(m.group(1), m.group(1) + 'Key')}.wasPressedThisFrame == true",
        expr,
    )
    # Input.get_key_up('space') -> Keyboard.current?.spaceKey.wasReleasedThisFrame == true
    expr = re.sub(
        r"Input\.get_key_up\(['\"](\w+)['\"]\)",
        lambda m: f"Keyboard.current?.{_KEY_NAME_MAP.get(m.group(1), m.group(1) + 'Key')}.wasReleasedThisFrame == true",
        expr,
    )
    # Input.get_key('space') -> Keyboard.current?.spaceKey.isPressed == true
    expr = re.sub(
        r"Input\.get_key\(['\"](\w+)['\"]\)",
        lambda m: f"Keyboard.current?.{_KEY_NAME_MAP.get(m.group(1), m.group(1) + 'Key')}.isPressed == true",
        expr,
    )

    # Input.get_axis('Horizontal') -> keyboard-based axis emulation for new input system
    def _replace_axis(m):
        axis = m.group(1)
        if axis == "Horizontal":
            return "((Keyboard.current?.dKey.isPressed == true ? 1f : 0f) - (Keyboard.current?.aKey.isPressed == true ? 1f : 0f))"
        elif axis == "Vertical":
            return "((Keyboard.current?.wKey.isPressed == true ? 1f : 0f) - (Keyboard.current?.sKey.isPressed == true ? 1f : 0f))"
        else:
            return f"0f /* unknown axis: {axis} */"
    expr = re.sub(
        r"Input\.get_axis\(['\"](\w+)['\"]\)",
        _replace_axis,
        expr,
    )

    return expr


def _translate_py_expression(expr: str) -> str:
    """Translate a Python expression to C#."""
    expr = expr.strip()

    # S8-1: Translate `x in collection` / `x not in collection` membership tests
    # before other transforms mangle the `not` / `in` keywords. This works in
    # ANY expression context (return, assignment, condition, arg, etc.) —
    # previously the rewrite only fired inside `_translate_py_condition`,
    # leaving `return x in self.items` to leak Python syntax into C#.
    if " in " in expr or " not in " in expr:
        expr = _translate_in_membership(expr)

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
    # Time.set_time_scale(value) → Time.timeScale = value (property assignment, handled at statement level)
    expr = re.sub(r"Time\.set_time_scale\((.+?)\)", r"Time.timeScale = \1", expr)
    expr = re.sub(r"Time\.SetTimeScale\((.+?)\)", r"Time.timeScale = \1", expr)

    # FindObjectsOfType → FindObjectsByType (Unity 6+; FindObjectsOfType is
    # deprecated → CS0618 warning). Preserve the legacy form on Unity 5
    # since FindObjectsByType + FindObjectsSortMode require 2022.2+/6.
    # FU-4 P2 cleanup.
    if _config.unity_version >= 6:
        _fot_replacement = r"FindObjectsByType<\1>(FindObjectsSortMode.None)"
    else:
        _fot_replacement = r"FindObjectsOfType<\1>()"
    expr = re.sub(r"(?:GameObject\.)?find_objects_of_type\((\w+)\)", _fot_replacement, expr)
    expr = re.sub(r"(?:GameObject\.)?FindObjectsOfType\((\w+)\)", _fot_replacement, expr)

    # Random.range → Random.Range
    expr = re.sub(r"Random\.range\(", "Random.Range(", expr)

    # DestroyImmediate
    expr = re.sub(r"(?:GameObject\.)?destroy_immediate\(", "DestroyImmediate(", expr)
    expr = re.sub(r"GameObject\.DestroyImmediate\(", "DestroyImmediate(", expr)

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
    expr = re.sub(r"\bmath\.degrees\(", "Mathf.Rad2Deg * (", expr)
    expr = re.sub(r"\bmath\.radians\(", "Mathf.Deg2Rad * (", expr)

    # List / string conversion
    expr = re.sub(r"\.index\(", ".IndexOf(", expr)   # Python .index(x) → C# .IndexOf(x)

    # Collision2D.layer → Collision2D.gameObject.layer (`layer` lives on GO).
    # Applies only to identifiers whose name hints at being a collision event
    # param (collision / other) to avoid clobbering legitimate `.layer` uses.
    expr = re.sub(r"\b(collision|other|col|coll)\.layer\b", r"\1.gameObject.layer", expr)

    # Transform.rotation_z/rotationZ — Unity has no such property. When the
    # expression is `<prefix>transform.rotation_z = X`, rewrite to
    # `<prefix>transform.rotation = Quaternion.Euler(0, 0, X)`; otherwise
    # treat as read-only and map to `transform.eulerAngles.z` — and then
    # fix the `transform.eulerAngles.z = X` immutable-struct-write case by
    # splatting through a new Quaternion.Euler.
    def _rotation_z_assign(m):
        prefix = m.group(1)
        value = m.group(2).strip()
        return f"{prefix}.rotation = Quaternion.Euler(0f, 0f, {value})"
    expr = re.sub(
        r"((?:[\w.]+\.)?transform)\.rotation_?[Zz]\s*=\s*(.+)",
        _rotation_z_assign, expr,
    )
    # After the read-only rewrite, catch the `eulerAngles.z = X` immutable
    # struct write case which is also invalid C#. Same Quaternion.Euler fix.
    expr = re.sub(
        r"((?:[\w.]+\.)?transform)\.eulerAngles\.z\s*=\s*(.+)",
        _rotation_z_assign, expr,
    )
    expr = re.sub(r"\btransform\.rotation_?[Zz]\b", "transform.eulerAngles.z", expr)

    # Transform.position.x = Y → Transform.position = new Vector3(Y, ...y, ...z)
    # Same for .y and .z. Unity's Transform.position is a Vector3 return-value,
    # so component assignment needs a fresh struct.
    def _position_axis_assign(m):
        prefix = m.group(1)
        axis = m.group(2)
        value = m.group(3).strip().rstrip(";").strip()
        pos = f"{prefix}.position"
        if axis == "x":
            return f"{pos} = new Vector3({value}, {pos}.y, {pos}.z)"
        if axis == "y":
            return f"{pos} = new Vector3({pos}.x, {value}, {pos}.z)"
        return f"{pos} = new Vector3({pos}.x, {pos}.y, {value})"
    expr = re.sub(
        r"((?:[\w.]+\.)?transform)\.position\.([xyz])\s*=\s*(.+)",
        _position_axis_assign, expr,
    )

    # random -> Random
    expr = re.sub(r"random\.random\(\)", "Random.value", expr)
    expr = re.sub(r"random\.uniform\(", "Random.Range(", expr)
    expr = re.sub(r"random\.randint\(", "Random.Range(", expr)
    # random.choice(collection) → collection[Random.Range(0, collection.Count)]
    def _replace_random_choice(m):
        arg = m.group(1).strip()
        return f"{arg}[Random.Range(0, {arg}.Count)]"
    expr = re.sub(r"random\.choice\((\w[\w.]*)\)", _replace_random_choice, expr)

    # print -> Debug.Log
    expr = re.sub(r"\bprint\(", "Debug.Log(", expr)

    # self.transform -> transform
    expr = expr.replace("self.transform", "transform")

    # super().method(args) -> base.Method(args) — bare super() gets swallowed
    def _super_call_replace(m):
        name = m.group(1)
        if name in _reserved_method_renames:
            return f"base.{_reserved_method_renames[name]}("
        return "base." + snake_to_pascal(name) + "("
    expr = re.sub(r"super\(\)\.(\w+)\(", _super_call_replace, expr)

    # self.method(...) call: strip `self.` AND convert method name to PascalCase,
    # since the post-pass snake_to_pascal regexes only catch names containing
    # underscores. Lifecycle/reserved renames win.
    def _self_method_call(m):
        name = m.group(1)
        if name in _reserved_method_renames:
            return _reserved_method_renames[name] + "("
        if name in _lifecycle_map_reverse:
            return _lifecycle_map_reverse[name] + "("
        return snake_to_pascal(name) + "("
    expr = re.sub(r"\bself\.(\w+)\(", _self_method_call, expr)

    # self.X -> this.X when X shadows a method parameter, else just X.
    # If X is a user method renamed to avoid Unity clash (reserved_method_renames),
    # emit the renamed form so call sites line up with the method definition.
    def _self_dot_replace(m):
        attr = m.group(1)
        if attr in _reserved_method_renames:
            return _reserved_method_renames[attr]
        # Method-as-value reference: `self._new_round` (no parens) on the RHS
        # of an assignment is a delegate-style method handle, not a field
        # access. The method-name path emits PascalCase (`NewRound`) — the
        # field-name path would camelCase to `newRound`, a dangling identifier.
        # Surfaced by Space Invaders' GameManager: `self._invoke_callback =
        # self._new_round` previously emitted `... = newRound;` and failed
        # Unity compile with CS0103.
        if attr in _current_class_methods or attr.lstrip("_") in _current_class_methods:
            method_name = attr if attr in _current_class_methods else attr.lstrip("_")
            if method_name in _lifecycle_map_reverse:
                return _lifecycle_map_reverse[method_name]
            return snake_to_pascal(method_name)
        # Match the field-declaration name-mangling: strip leading `_`, then
        # camelCase (e.g. `_body_sr` → `bodySr`, `blue_sprite` → `blueSprite`).
        # UPPER_SNAKE constants stay verbatim.
        if attr.isupper():
            cs_attr = attr
        else:
            stripped = attr.lstrip("_")
            parts = stripped.split("_")
            cs_attr = parts[0] + "".join(p.capitalize() for p in parts[1:])
        if cs_attr in _current_method_params:
            return f"this.{cs_attr}"
        # Field vs local shadowing: when a method has a local with the
        # same name as a class field, `self.X = X` must emit `this.X` so
        # the field is actually assigned — not a no-op `X = X;` on the
        # local.  Observed in Ghost.Start (`eyes` local vs `self.eyes`
        # field).
        if cs_attr in _current_method_locals:
            return f"this.{cs_attr}"
        return cs_attr
    expr = re.sub(r"\bself\.(\w+)", _self_dot_replace, expr)
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

    # Python ternary: x if cond else y -> cond ? x : y
    # Must run BEFORE hasattr replacement so condition is preserved
    ternary = re.match(r"^(.+?)\s+if\s+(.+?)\s+else\s+(.+)$", expr)
    if ternary:
        value_true = ternary.group(1).strip()
        cond = ternary.group(2).strip()
        value_false = ternary.group(3).strip()
        # Recursively translate each part so nested ternaries and
        # sub-expression transforms (get_component, hasattr, etc.) apply
        cs_true = _translate_py_expression(value_true)
        cs_cond = _translate_py_condition(cond)
        cs_false = _translate_py_expression(value_false)
        # Optimize: if condition is literal 'true' (e.g. from hasattr),
        # collapse to just the true branch
        if cs_cond == "true":
            expr = cs_true
        else:
            expr = f"{cs_cond} ? {cs_true} : {cs_false}"
        return expr

    # hasattr(x, "y") -> true (C# doesn't have hasattr; assume true for compiled code)
    expr = re.sub(r"hasattr\([^,]+,\s*['\"][^'\"]+['\"]\)", "true", expr)

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
    # `\bNone\b` eats the `None` in C# enum values like
    # `FindObjectsSortMode.None` (Unity 6 FU-4 replacement) — reverse it.
    expr = expr.replace("FindObjectsSortMode.null", "FindObjectsSortMode.None")

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
    # Don't match inside Vector2/Vector3/Quaternion constructors
    expr = re.sub(r"(?<!Vector2)(?<!Vector3)(?<!Quaternion)\((\d+),\s*(\d+),\s*(\d+)\)", _color_tuple_repl, expr)

    # Python builtins -> C# equivalents
    expr = re.sub(r"\bmax\(", "Mathf.Max(", expr)
    expr = re.sub(r"\bmin\(", "Mathf.Min(", expr)
    expr = re.sub(r"\babs\(", "Mathf.Abs(", expr)
    expr = re.sub(r"\bround\(", "Mathf.Round(", expr)

    # Python list operations:
    # row[:] -> row.Clone() (array copy)
    expr = re.sub(r"(\w+)\[:\]", r"(\1.Clone() as bool[])", expr)

    # [True] * N -> new bool[N] (filled with true via Enumerable)
    expr = re.sub(r"\[true\]\s*\*\s*([\w.]+)", r"Enumerable.Repeat(true, \1).ToArray()", expr)
    expr = re.sub(r"\[false\]\s*\*\s*([\w.]+)", r"Enumerable.Repeat(false, \1).ToArray()", expr)

    # range(N) standalone -> Enumerable.Range(0, N)
    expr = re.sub(r"\brange\(([\w.]+)\)", r"Enumerable.Range(0, \1)", expr)

    # Fix lambda with no param: .Select( => -> .Select(_ =>
    expr = re.sub(r"\.Select\(\s*=>", ".Select(_ =>", expr)

    # sum(1 for x in list) already handled by LINQ
    # Python casts: int(x) -> (int)(x), float(x) -> (float)(x), str(x) -> x.ToString()
    # Special-literal constructors (`float("inf")` etc.) MUST be rewritten
    # before the generic `float(x) -> (float)(x)` substitution — casting a
    # string literal to float is CS0030.  Regression for
    # data/lessons/pacman_v2_deploy.md gap PV-5 (GhostChase.min_dist sentinel).
    expr = re.sub(r"\bfloat\(\s*['\"]inf['\"]\s*\)", "float.PositiveInfinity", expr)
    expr = re.sub(r"\bfloat\(\s*['\"]-inf['\"]\s*\)", "float.NegativeInfinity", expr)
    expr = re.sub(r"\bfloat\(\s*['\"]nan['\"]\s*\)", "float.NaN", expr)
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
    # Catch remaining EnumType.UPPER_SNAKE patterns — but ONLY for known enum types
    # to avoid clobbering non-enum class constants like Layers.LASER
    _KNOWN_ENUM_TYPES = {"RigidbodyType2D", "ForceMode2D", "TextAnchor"}
    _KNOWN_ENUM_TYPES.update(k.split(".")[0] for k in _enum_values)
    def _enum_upper_to_pascal(m):
        enum_type = m.group(1)
        if enum_type not in _KNOWN_ENUM_TYPES:
            return m.group(0)  # Only convert known enums
        value = m.group(2)
        pascal = _upper_snake_to_pascal(value)
        return f"{enum_type}.{pascal}"
    expr = re.sub(r"(\b[A-Z]\w+)\.([A-Z][A-Z_]+)\b", _enum_upper_to_pascal, expr)

    # OnTriggerEnter2D: other → other.gameObject for property access and method args
    # Collider2D has no .layer, .tag, .name directly — need .gameObject accessor
    # Only apply inside trigger callbacks where 'other' is a Collider2D
    if _in_trigger_callback:
        expr = re.sub(r"\bother\.layer\b", "other.gameObject.layer", expr)
        expr = re.sub(r"\bother\.tag\b", "other.gameObject.tag", expr)
        expr = re.sub(r"\bother\.name\b", "other.gameObject.name", expr)
        # When 'other' is passed as a bare argument (Collider2D → GameObject)
        # In trigger callbacks, standalone 'other' in args should be other.gameObject
        expr = re.sub(r"(?<=\()other(?=[,)])", "other.gameObject", expr)
        expr = re.sub(r"(?<=, )other(?=[,)])", "other.gameObject", expr)

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
    # DisplayManager property access on stripped variables (dm._title, dm.xxx, etc.)
    if re.match(r"^dm\.", expr):
        return "__STRIP__"
    # hasattr() — Python-only runtime check, no C# equivalent
    if "hasattr(" in expr:
        return "__STRIP__"

    # S11-3 / S12-2: getattr(obj, "name", default)
    # - default==obj (idiomatic "use obj if no attr"): rewrite to just `obj`
    # - default==obj.name (same attr as fallback): rewrite to `obj.name`
    # - otherwise: rewrite to `obj.Name` (assume attr present — rare to rely on default)
    def _getattr_replace(m: re.Match) -> str:
        receiver = m.group(1).strip()
        attr = m.group(2)
        default = m.group(3).strip()
        cs_attr = snake_to_camel(attr)
        # If the trigger-callback pre-expansion already appended
        # `.gameObject` to the receiver (line ~2371 above), emitting
        # another `.gameObject` produces `other.gameObject.gameObject`
        # which compiles but chains an unnecessary hop.  Collapse it.
        if receiver.endswith("." + cs_attr):
            return receiver
        # Unity-core properties always exist on the types this idiom wraps
        # (Component/Collision2D/GameObject), so prefer the qualified form
        # over collapsing to bare `receiver`. S12-2 collapse still applies
        # for obscure attrs.
        if cs_attr in ("gameObject", "transform"):
            return f"{receiver}.{cs_attr}"
        if default == receiver:
            return receiver  # S12-2: don't chain .gameObject.gameObject
        return f"{receiver}.{cs_attr}"
    expr = re.sub(
        r'\bgetattr\(\s*([\w.]+)\s*,\s*["\']([\w_]+)["\']\s*,\s*([\w.]+)\s*\)',
        _getattr_replace,
        expr,
    )
    # 2-arg getattr used to look up a method by name and immediately invoke it:
    # `getattr(self, method_name)()` → `this.SendMessage(method_name)` (Unity's
    # dynamic dispatch for MonoBehaviours).
    expr = re.sub(
        r'\bgetattr\(\s*(\w[\w.]*)\s*,\s*(\w+)\s*\)\s*\(\s*\)',
        r'\1.SendMessage(\2)',
        expr,
    )
    # S11-3: id(x) → x.GetInstanceID()  (Unity's object-identity equivalent)
    expr = re.sub(r'\bid\(\s*(\w+)\s*\)', r'\1.GetInstanceID()', expr)
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
        _prefab_fields.add(prefab_field)
        expr = f"Instantiate({prefab_field}, {pos_var}, Quaternion.identity)"

    # Also discover prefab fields from Instantiate(self.xxx_prefab, ...) patterns
    # After self. stripping and camelCase, these become Instantiate(xxxPrefab, ...)
    inst_ref_match = re.match(r'^Instantiate\((\w*[Pp]refab)\b', expr)
    if inst_ref_match:
        prefab_field = inst_ref_match.group(1)
        _prefab_fields.add(prefab_field)

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
    # Generic remaining kwargs: key=value → just value (fallback).
    # S10-5: handle both mid-arg form ", key=v" AND first-arg form "(key=v".
    expr = re.sub(r",\s*\w+=([^,)]+)", r", \1", expr)
    expr = re.sub(r"\(\s*\w+=([^,)]+)", r"(\1", expr)

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
            # Also replace ClassName._field → ClassName.Field (static field access)
            if py_name.startswith("_"):
                expr = re.sub(rf"(?<=\.){re.escape(py_name)}(?!\w)", cs_name, expr)

    # Apply reserved method renames before generic snake_to_pascal conversion.
    # Names that CLASH with Unity static built-ins (e.g. UnityEngine.Object.Destroy(x))
    # must only be renamed on self/this-qualified calls — never on bare or
    # other-qualified calls, otherwise `Object.destroy(x)` / `destroy(x)` lose
    # their Unity semantics.
    _UNITY_STATIC_CLASH_RESERVED = {"destroy"}
    for py_name, cs_name in _reserved_method_renames.items():
        if py_name in _UNITY_STATIC_CLASH_RESERVED:
            # Only rewrite self.X( or this.X( — leave Object.X( and standalone X( alone.
            expr = re.sub(rf"\b(self|this)\.{re.escape(py_name)}\(",
                          rf"\1.{cs_name}(", expr)
        else:
            # Safe to rewrite any qualified or standalone call (e.g. reset → ResetState)
            expr = re.sub(rf"(?<=\.){re.escape(py_name)}\(", f"{cs_name}(", expr)
            expr = re.sub(rf"(?<![.\w]){re.escape(py_name)}\(", f"{cs_name}(", expr)

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

    # Match standalone snake_case_function( (no dot, no underscore prefix, must have _)
    def _bare_snake_to_pascal(m):
        name = m.group(1)
        parts = name.split('_')
        pascal = ''.join(p.capitalize() for p in parts if p)
        return pascal + '('
    expr = re.sub(r"(?<![.\w])([a-z]+_[a-z_]+)\(", _bare_snake_to_pascal, expr)

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


def _translate_in_membership(cond: str) -> str:
    """Translate Python 'in' / 'not in' membership operators to C# .Contains() / .ContainsKey().

    Must be called BEFORE _translate_py_expression so that 'not in' isn't
    mangled into '!in' by the general 'not' -> '!' rewrite.  Each side of
    the match is individually translated through _translate_py_expression so
    that self.field -> field and snake_case -> camelCase conversions happen.
    """

    def _replace_in(m):
        # Guard: skip matches inside a `for ... in ...` comprehension/loop.
        # Python's `re` doesn't support variable-length lookbehind, so we
        # manually scan the preceding slice for an unmatched `for ` keyword
        # within the same expression-term (stopping at `[`, `(`, or `,`).
        start = m.start()
        preceding = cond[:start]
        # Walk back until we hit a boundary, watching for ` for ` or `\bfor\b`
        # that belongs to a comprehension header.
        boundary_idx = max(
            preceding.rfind("["),
            preceding.rfind("("),
            preceding.rfind(","),
        )
        scan_from = boundary_idx + 1 if boundary_idx >= 0 else 0
        segment = preceding[scan_from:]
        if re.search(r"\bfor\b", segment):
            return m.group(0)  # leave untouched — this is `for X in Y`

        needle = _translate_py_expression(m.group(1).strip())
        negated = m.group(2) is not None  # "not" captured
        collection_raw = m.group(3).strip()
        collection = _translate_py_expression(collection_raw)

        # Determine if collection is dict-typed: check last dotted part against _dict_fields
        last_part = collection.rsplit(".", 1)[-1] if "." in collection else collection
        if last_part in _dict_fields or collection in _dict_fields:
            method = "ContainsKey"
        else:
            method = "Contains"

        call = f"{collection}.{method}({needle})"
        return f"!{call}" if negated else call

    # Handle 'X not in Y' first (greedy — must come before plain 'in')
    # Supports dotted names like self.items, _module_var, etc.
    cond = re.sub(
        r"([\w.]+(?:\[[\w.]+\])?)\s+(not\s+)?in\s+([\w.]+(?:\[[\w.]+\])?)",
        _replace_in,
        cond,
    )
    return cond


def _translate_py_condition(cond: str) -> str:
    """Translate a Python condition to C#."""
    # Handle 'is not None' / 'is None' before expression translation mangles them
    cond = cond.replace(" is not None", " != null").replace(" is None", " == null")

    # Handle 'not in' / 'in' membership operators BEFORE expression translation
    # (otherwise 'not' gets converted to '!' and 'in' leaks as raw keyword)
    cond = _translate_in_membership(cond)

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

    # Object truthiness: bare object/property names in && / || should get != null
    # But bool fields/properties stay as bare truthiness checks
    _BOOL_PROPERTIES = {"activeSelf", "activeInHierarchy", "enabled", "isActiveAndEnabled",
                        "isTrigger", "isKinematic", "loop",
                        "wasPressedThisFrame", "wasReleasedThisFrame", "isPressed"}
    parts = re.split(r"\s*(&&|\|\|)\s*", cond)
    fixed_parts = []
    for part in parts:
        if part in ("&&", "||"):
            fixed_parts.append(part)
        elif re.match(r"^[a-zA-Z_][\w.]*$", part.strip()) and part.strip() not in ("true", "false", "null"):
            ident = part.strip()
            # Check if it's a known bool field or ends with a bool property.
            # _cross_class_bool_fields and _project_bool_fields are consulted
            # only for dotted access (e.g. `other.eaten`) where the field is
            # declared in a different class/file.  Bare identifiers (e.g.
            # `isAlive`) must rely solely on _bool_fields so that the mutation
            # test can detect broken tracking by clearing _bool_fields.
            last_prop = ident.rsplit(".", 1)[-1] if "." in ident else ident
            is_dotted = "." in ident
            if (ident in _bool_fields
                    or last_prop in _BOOL_PROPERTIES
                    or last_prop in _bool_fields
                    or (is_dotted and last_prop in _cross_class_bool_fields)
                    or (is_dotted and last_prop in _project_bool_fields)):
                fixed_parts.append(ident)
            else:
                fixed_parts.append(f"{ident} != null")
        else:
            # Handle negated identifiers: !identifier -> identifier == null (for non-bool objects)
            neg_match = re.match(r"^!\s*([a-zA-Z_][\w.]*)$", part.strip())
            if neg_match:
                ident = neg_match.group(1)
                last_prop = ident.rsplit(".", 1)[-1] if "." in ident else ident
                is_dotted = "." in ident
                if (ident in _bool_fields
                        or last_prop in _BOOL_PROPERTIES
                        or last_prop in _bool_fields
                        or (is_dotted and last_prop in _cross_class_bool_fields)
                        or (is_dotted and last_prop in _project_bool_fields)):
                    fixed_parts.append(f"!{ident}")
                else:
                    fixed_parts.append(f"{ident} == null")
            else:
                fixed_parts.append(part)
    cond = " ".join(fixed_parts)

    return cond


_VALUE_TYPES = {"int", "float", "double", "bool", "byte", "short", "long", "char",
                "Vector2", "Vector3", "Quaternion", "Color", "Color32"}


def _translate_type_annotation(py_type: str) -> str:
    """Convert a Python type annotation string to C# type for local variables.

    Handles: int, float, str, bool, Vector2, Vector3, GameObject,
    list[T], tuple[T, ...], Type | None, etc.
    """
    py_type = py_type.strip()
    # Detect nullable before stripping
    is_nullable = bool(re.search(r"\|\s*None\s*$", py_type)) or py_type.startswith("None |")
    # Strip Optional/None union: Type | None -> Type, None | Type -> Type
    py_type = re.sub(r"\s*\|\s*None\s*$", "", py_type)
    py_type = re.sub(r"^None\s*\|\s*", "", py_type)
    # Also handle already-translated null: Type | null -> Type
    py_type = re.sub(r"\s*\|\s*null\s*$", "", py_type)
    py_type = py_type.strip()
    # Map through the existing type system
    result = _py_type_to_csharp(py_type)
    # Re-add nullable suffix for value types (tuples, int, float, etc.)
    if is_nullable and not result.endswith("?"):
        if result in _VALUE_TYPES or (result.startswith("(") and result.endswith(")")):
            result += "?"
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

    # Float: 5.0 -> 5f (always add f suffix for decimal literals)
    if re.match(r"^-?\d+\.\d+$", value) and csharp_type in ("float", ""):
        return value + "f"

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
            # Use the C# type to construct
            if csharp_type.startswith("List<"):
                return f"new {csharp_type}()"
            if csharp_type.endswith("[]"):
                return f"new {csharp_type[:-2]}[0]"
            return "new List<object>()"
        elif factory == "dict":
            return "new Dictionary<string, object>()"
        else:
            return f"new {factory}()"

    # Empty list: [] -> new List<T>() or empty array
    if value == "[]":
        if csharp_type.startswith("List<"):
            return f"new {csharp_type}()"
        return "null"

    # Empty dict: {} -> new Dictionary<K,V>() when typed, else null.
    # A static/class Dictionary field initialised to null NREs on the
    # first `.ContainsKey(...)` call; emit a fresh instance instead so
    # the field is usable from field init (e.g. Passage._recent_teleports).
    if value == "{}":
        if csharp_type.startswith("Dictionary<"):
            return f"new {csharp_type}()"
        return "null"

    # Dataclass/constructor calls with keyword args:
    # ClassName(field=value, ...) -> new ClassName { CamelField = value, ... }
    # S7-7: positional args are mapped to field names in declaration order
    # via _class_field_order registry, so enum-tagged entries keep their tags.
    ctor_call = re.match(r"^(\w+)\((.+)\)$", value, re.DOTALL)
    if ctor_call:
        cls_name = ctor_call.group(1)
        args_str = ctor_call.group(2)
        args = _split_args(args_str)
        has_kwargs = any(re.match(r"\w+\s*=", a.strip()) for a in args)
        if args and has_kwargs:
            # Look up ordered field names for positional-arg mapping (S7-7).
            ordered_fields = _class_field_order.get(cls_name, []) if "_class_field_order" in globals() else []
            initializers = []
            positional_index = 0
            for arg in args:
                arg = arg.strip()
                if "=" in arg and re.match(r"\w+\s*=", arg):
                    key, val = arg.split("=", 1)
                    key = key.strip()
                    val = val.strip()
                    cs_key = snake_to_camel(key)
                    cs_val = _py_value_to_csharp(val, "")
                    if cs_val is None:
                        cs_val = _translate_py_expression(val) if val else val
                    initializers.append(f"{cs_key} = {cs_val}")
                else:
                    # Positional arg — map to field[positional_index] if known (S7-7)
                    if positional_index < len(ordered_fields):
                        py_field_name = ordered_fields[positional_index]
                        cs_key = py_field_name if py_field_name.isupper() else snake_to_camel(py_field_name)
                        cs_val = _py_value_to_csharp(arg, "")
                        if cs_val is None:
                            cs_val = _translate_py_expression(arg) if arg else arg
                        initializers.append(f"{cs_key} = {cs_val}")
                    # else: unknown class, drop positional (existing fallback behavior)
                    positional_index += 1
            # All go in object initializer (C# data classes don't have parameterized constructors)
            return f"new {cls_name} {{ {', '.join(initializers)} }}"

    # List of constructor calls: [ClassName(...), ...] -> new ClassName[] { ... }
    list_match = re.match(r"^\[(.+)\]$", value, re.DOTALL)
    if list_match and csharp_type.endswith("[]"):
        inner = list_match.group(1)
        elements = _split_args(inner)
        if elements and all(re.match(r"\w+\(", e.strip()) for e in elements):
            converted = []
            elem_type = csharp_type[:-2]  # Remove []
            for elem in elements:
                cs_elem = _py_value_to_csharp(elem.strip(), elem_type)
                if cs_elem is None:
                    cs_elem = elem.strip()
                converted.append(cs_elem)
            return f"new {csharp_type[:-2]}[] {{ {', '.join(converted)} }}"

        # List of string literals: ["a", "b"] → new string[] { "a", "b" }
        # when the field is string[], OR null when it's a reference array
        # (the strings were asset-name tokens that get wired at runtime by
        # CoPlay / Resources.Load; emitting them verbatim produces invalid
        # C# like `Sprite[] s = ['a', 'b'];`).  FU-2 home-machine compile fix.
        def string_literal(e):
            return re.match(r"^\s*['\"][^'\"]*['\"]\s*$", e)
        if elements and all(string_literal(e) for e in elements):
            elem_type = csharp_type[:-2]
            if elem_type == "string":
                quoted = ', '.join(f'"{e.strip()[1:-1]}"' for e in elements)
                return f"new string[] {{ {quoted} }}"
            # Reference-array target with string-literal defaults: drop the
            # default so CoPlay / editor scripts wire the real assets.
            return "null"

    # Color tuples: (R, G, B) -> new Color32(R, G, B, 255)
    # Only apply when target type is Color32-related (avoid clobbering InvaderRowConfig etc.)
    if csharp_type in ("Color32", "Color", "object", ""):
        color_match = re.match(r"^\((\d+),\s*(\d+),\s*(\d+)\)$", value)
        if color_match:
            r, g, b = color_match.groups()
            return f"new Color32({r}, {g}, {b}, 255)"

    # List of color tuples: [(R,G,B), ...] -> new Color32[] { new Color32(...), ... }
    if csharp_type in ("Color32[]", "Color32", "object", ""):
        list_colors = re.match(r"^\[(.+)\]$", value)
        if list_colors:
            inner = list_colors.group(1)
            # Only match if the list contains ONLY tuples (not constructor calls)
            if not re.search(r"\w+\(", inner.split("(")[0] if "(" in inner else ""):
                tuples = re.findall(r"\((\d+),\s*(\d+),\s*(\d+)\)", inner)
                if tuples and len(tuples) == inner.count("("):
                    elements = ", ".join(f"new Color32({r}, {g}, {b}, 255)" for r, g, b in tuples)
                    return f"new Color32[] {{ {elements} }}"

    # Enum values: EnumType.UPPER_SNAKE -> EnumType.PascalCase
    for py_enum, cs_enum in _enum_values.items():
        value = value.replace(py_enum, cs_enum)

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
    # S10-1: also scan module-level constants — e.g. `_recent_teleports: dict[int, float]`
    # is declared at module scope in passage.py but gets hoisted into the class as a
    # static field. Without this, the inference misses the dict/list types.
    all_text += " " + " ".join(
        f"{mc.type_annotation} {mc.default_value or ''}"
        for mc in parsed.module_constants
    )

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

    # Add System if Math.Max/Min is used (from max()/min() translation)
    if "max(" in " ".join(m.body_source for m in cls.methods) or "min(" in " ".join(m.body_source for m in cls.methods):
        extra.add("System")

    # Add System if Exception is used (try/catch)
    if "except" in all_text or "Exception" in all_text:
        extra.add("System")

    # Add System.Collections.Generic if List<> or Dictionary<> is used (S10-1)
    # Check `all_text` so module-level `_x: dict[K,V]` constants (which get
    # hoisted into the class as static fields) are caught too.
    if ("list[" in all_text or "dict[" in all_text
            or "List<" in all_text
            or "Dictionary<" in all_text):
        extra.add("System.Collections.Generic")

    # Add UnityEngine.InputSystem when new input system is active and Input is used
    if _config.input_system == "new":
        import_text = " ".join(parsed.imports)
        if "Input" in all_text or "Input" in import_text:
            extra.add("UnityEngine.InputSystem")

    return sorted(extra)
