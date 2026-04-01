"""C# parser using tree-sitter — produces intermediate representation dataclasses."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import tree_sitter_c_sharp as ts_cs
import tree_sitter as ts


# ── IR Dataclasses ───────────────────────────────────────────

@dataclass
class CSharpParameter:
    name: str
    type: str
    default: str | None = None

@dataclass
class CSharpField:
    name: str
    type: str
    modifiers: list[str] = field(default_factory=list)
    attributes: list[str] = field(default_factory=list)
    initializer: str | None = None

@dataclass
class CSharpProperty:
    name: str
    type: str
    modifiers: list[str] = field(default_factory=list)
    has_getter: bool = True
    has_setter: bool = True

@dataclass
class CSharpMethod:
    name: str
    return_type: str
    parameters: list[CSharpParameter] = field(default_factory=list)
    modifiers: list[str] = field(default_factory=list)
    body: str = ""
    is_lifecycle: bool = False

@dataclass
class CSharpClass:
    name: str
    base_classes: list[str] = field(default_factory=list)
    attributes: list[str] = field(default_factory=list)
    fields: list[CSharpField] = field(default_factory=list)
    properties: list[CSharpProperty] = field(default_factory=list)
    methods: list[CSharpMethod] = field(default_factory=list)
    is_monobehaviour: bool = False
    using_directives: list[str] = field(default_factory=list)

@dataclass
class CSharpFile:
    using_directives: list[str] = field(default_factory=list)
    classes: list[CSharpClass] = field(default_factory=list)


# ── Known lifecycle methods ──────────────────────────────────

_LIFECYCLE_METHODS = {
    "Awake", "Start", "Update", "FixedUpdate", "LateUpdate",
    "OnDestroy", "OnEnable", "OnDisable",
    "OnCollisionEnter2D", "OnCollisionExit2D", "OnCollisionStay2D",
    "OnTriggerEnter2D", "OnTriggerExit2D", "OnTriggerStay2D",
}

# ── Parser ───────────────────────────────────────────────────

_lang = ts.Language(ts_cs.language())
_parser = ts.Parser(_lang)


def _text(node) -> str:
    """Get the text content of a node."""
    return node.text.decode("utf-8") if node.text else ""


def _find_children(node, type_name: str) -> list:
    """Find all direct children of a given type."""
    return [c for c in node.children if c.type == type_name]


def _find_child(node, type_name: str):
    """Find first direct child of a given type."""
    for c in node.children:
        if c.type == type_name:
            return c
    return None


def _get_modifiers(node) -> list[str]:
    """Extract modifiers (public, private, static, etc.) from a declaration."""
    mods = []
    for child in node.children:
        if child.type == "modifier":
            mods.append(_text(child))
    return mods


def _get_attributes(node) -> list[str]:
    """Extract attribute names from attribute_list nodes."""
    attrs = []
    for child in node.children:
        if child.type == "attribute_list":
            for attr in _find_children(child, "attribute"):
                name_node = _find_child(attr, "identifier") or _find_child(attr, "qualified_name")
                if name_node:
                    attrs.append(_text(name_node))
    return attrs


def _parse_field(node) -> CSharpField:
    """Parse a field_declaration node into CSharpField."""
    modifiers = _get_modifiers(node)
    attributes = _get_attributes(node)

    # Find the variable_declaration
    var_decl = _find_child(node, "variable_declaration")
    field_type = ""
    field_name = ""
    initializer = None

    if var_decl:
        # First child is the type
        type_node = var_decl.children[0] if var_decl.children else None
        if type_node and type_node.type != "variable_declarator":
            field_type = _text(type_node)

        # Find variable_declarator
        declarator = _find_child(var_decl, "variable_declarator")
        if declarator:
            id_node = _find_child(declarator, "identifier")
            if id_node:
                field_name = _text(id_node)

            # Find initializer — could be equals_value_clause or direct = + value children
            eq_clause = _find_child(declarator, "equals_value_clause")
            if eq_clause and len(eq_clause.children) >= 2:
                initializer = _text(eq_clause.children[1])
            else:
                # tree-sitter-c-sharp may put = and value as direct children
                children = declarator.children
                for i, c in enumerate(children):
                    if c.type == "=" and i + 1 < len(children):
                        initializer = _text(children[i + 1])
                        break

    return CSharpField(
        name=field_name,
        type=field_type,
        modifiers=modifiers,
        attributes=attributes,
        initializer=initializer,
    )


def _parse_property(node) -> CSharpProperty:
    """Parse a property_declaration node into CSharpProperty."""
    modifiers = _get_modifiers(node)

    # Type
    type_node = None
    for child in node.children:
        if child.type not in ("modifier", "attribute_list", "identifier", "accessor_list",
                               "{", "}", ";"):
            type_node = child
            break
    prop_type = _text(type_node) if type_node else ""

    # Name
    id_node = _find_child(node, "identifier")
    prop_name = _text(id_node) if id_node else ""

    # Accessors
    has_getter = False
    has_setter = False
    accessor_list = _find_child(node, "accessor_list")
    if accessor_list:
        for accessor in _find_children(accessor_list, "accessor_declaration"):
            accessor_text = _text(accessor)
            if "get" in accessor_text:
                has_getter = True
            if "set" in accessor_text:
                has_setter = True

    return CSharpProperty(
        name=prop_name,
        type=prop_type,
        modifiers=modifiers,
        has_getter=has_getter,
        has_setter=has_setter,
    )


def _parse_parameter(node) -> CSharpParameter:
    """Parse a parameter node."""
    param_type = ""
    param_name = ""
    default = None

    # Collect identifiers and type nodes in order
    # Pattern: [type_node] [identifier] or [identifier] [identifier] (type, name)
    type_candidates = []
    for child in node.children:
        if child.type in ("identifier", "predefined_type", "qualified_name",
                           "generic_name", "array_type", "nullable_type"):
            type_candidates.append(_text(child))
        elif child.type == "equals_value_clause":
            if len(child.children) >= 2:
                default = _text(child.children[1])
        elif child.type == "=" and not default:
            # Direct = value pattern
            idx = list(node.children).index(child)
            if idx + 1 < len(node.children):
                default = _text(node.children[idx + 1])

    # Last identifier-like thing is the name, everything before is the type
    if len(type_candidates) >= 2:
        param_type = " ".join(type_candidates[:-1])
        param_name = type_candidates[-1]
    elif len(type_candidates) == 1:
        param_name = type_candidates[0]

    return CSharpParameter(name=param_name, type=param_type, default=default)


def _parse_method(node) -> CSharpMethod:
    """Parse a method_declaration node into CSharpMethod."""
    modifiers = _get_modifiers(node)

    # Return type — find the type node (not modifier, not identifier, not parameter_list, not block)
    return_type = "void"
    name = ""

    children_types = [(c.type, c) for c in node.children]

    for i, (ctype, child) in enumerate(children_types):
        if ctype == "identifier":
            name = _text(child)
            # The node before identifier (that isn't a modifier) is the return type
            for j in range(i - 1, -1, -1):
                if children_types[j][0] not in ("modifier", "attribute_list"):
                    return_type = _text(children_types[j][1])
                    break
            break

    # Parameters
    params = []
    param_list = _find_child(node, "parameter_list")
    if param_list:
        for param_node in _find_children(param_list, "parameter"):
            params.append(_parse_parameter(param_node))

    # Body
    block = _find_child(node, "block")
    body = _text(block) if block else ""

    return CSharpMethod(
        name=name,
        return_type=return_type,
        parameters=params,
        modifiers=modifiers,
        body=body,
        is_lifecycle=name in _LIFECYCLE_METHODS,
    )


def _parse_class(node, using_directives: list[str]) -> CSharpClass:
    """Parse a class_declaration node into CSharpClass."""
    name = ""
    base_classes = []
    attributes = _get_attributes(node)

    id_node = _find_child(node, "identifier")
    if id_node:
        name = _text(id_node)

    base_list = _find_child(node, "base_list")
    if base_list:
        for child in base_list.children:
            if child.type == "identifier" or child.type == "qualified_name":
                base_classes.append(_text(child))

    # Parse members
    fields = []
    properties = []
    methods = []

    decl_list = _find_child(node, "declaration_list")
    if decl_list:
        for member in decl_list.children:
            if member.type == "field_declaration":
                fields.append(_parse_field(member))
            elif member.type == "property_declaration":
                properties.append(_parse_property(member))
            elif member.type == "method_declaration":
                methods.append(_parse_method(member))

    is_mono = "MonoBehaviour" in base_classes

    return CSharpClass(
        name=name,
        base_classes=base_classes,
        attributes=attributes,
        fields=fields,
        properties=properties,
        methods=methods,
        is_monobehaviour=is_mono,
        using_directives=using_directives,
    )


def parse_csharp(source: str) -> CSharpFile:
    """Parse C# source code into a CSharpFile IR."""
    tree = _parser.parse(source.encode("utf-8"))
    root = tree.root_node

    using_directives = []
    classes = []

    for child in root.children:
        if child.type == "using_directive":
            # Extract the namespace name
            id_node = _find_child(child, "identifier") or _find_child(child, "qualified_name")
            if id_node:
                using_directives.append(_text(id_node))
        elif child.type == "class_declaration":
            classes.append(_parse_class(child, using_directives))

    return CSharpFile(using_directives=using_directives, classes=classes)


def parse_csharp_file(path: str | Path) -> CSharpFile:
    """Parse a C# file from disk."""
    source = Path(path).read_text(encoding="utf-8")
    return parse_csharp(source)
