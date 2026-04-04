"""Bidirectional type mapper and naming convention converter."""

from __future__ import annotations

import json
import re
from pathlib import Path


_RULES_DIR = Path(__file__).parent / "rules"


def _load_json(filename: str) -> dict:
    with open(_RULES_DIR / filename) as f:
        return json.load(f)


class TypeMapper:
    """Maps C# types to Python types and vice versa."""

    def __init__(self) -> None:
        data = _load_json("type_mappings.json")
        self._primitives: dict[str, str] = data["primitive_types"]
        self._unity_types: dict[str, str] = data["unity_types"]
        self._generics: dict[str, str] = data["generic_types"]
        # Build reverse maps with preferred C# types (first match wins)
        self._reverse_primitives: dict[str, str] = {}
        # Preferred order: primary types first, then aliases
        _primary_order = ["int", "float", "bool", "string", "void", "double", "byte", "short", "long", "char", "object"]
        for k in _primary_order:
            if k in self._primitives:
                v = self._primitives[k]
                if v not in self._reverse_primitives:
                    self._reverse_primitives[v] = k
        self._reverse_unity = {v: k for k, v in self._unity_types.items()}

    def csharp_to_python(self, csharp_type: str) -> str:
        """Convert a C# type to its Python equivalent."""
        t = csharp_type.strip()

        # Nullable: int? -> int | None
        if t.endswith("?"):
            base = self.csharp_to_python(t[:-1])
            return f"{base} | None"

        # Array: float[] -> list[float]
        if t.endswith("[]"):
            base = self.csharp_to_python(t[:-2])
            return f"list[{base}]"

        # Generic: List<T>, Dictionary<K,V>
        generic_match = re.match(r"(\w+)<(.+)>", t)
        if generic_match:
            container = generic_match.group(1)
            args = self._split_generic_args(generic_match.group(2))
            py_container = self._generics.get(container, container.lower())
            py_args = ", ".join(self.csharp_to_python(a) for a in args)
            return f"{py_container}[{py_args}]"

        # Primitives
        if t in self._primitives:
            return self._primitives[t]

        # Unity types
        if t in self._unity_types:
            return self._unity_types[t]

        # Unknown — preserve
        return t

    def python_to_csharp(self, python_type: str) -> str:
        """Convert a Python type to its C# equivalent."""
        t = python_type.strip()

        # Optional: int | None -> int?
        if t.endswith("| None"):
            base = self.python_to_csharp(t[:-7].strip())
            return f"{base}?"

        # list[list[T]] -> List<T[]> (nested lists use List for mutability)
        nested_match = re.match(r"list\[list\[(.+)\]\]", t)
        if nested_match:
            inner = self.python_to_csharp(nested_match.group(1))
            return f"List<{inner}[]>"

        # list[T] -> T[]
        list_match = re.match(r"list\[(.+)\]", t)
        if list_match:
            inner = self.python_to_csharp(list_match.group(1))
            return f"{inner}[]"

        # bare 'list' without type param -> List<object>
        if t == "list":
            return "List<object>"

        # tuple[T1, T2] -> (T1, T2) C# value tuple
        tuple_match = re.match(r"tuple\[(.+)\]", t)
        if tuple_match:
            args = self._split_generic_args(tuple_match.group(1))
            cs_args = ", ".join(self.python_to_csharp(a) for a in args)
            return f"({cs_args})"

        # bare tuple -> Color32 when used as color, otherwise object
        # In Unity game context, bare tuples are almost always RGB colors
        if t == "tuple":
            return "Color32"

        # dict[K, V] -> Dictionary<K, V>
        dict_match = re.match(r"dict\[(.+),\s*(.+)\]", t)
        if dict_match:
            k = self.python_to_csharp(dict_match.group(1))
            v = self.python_to_csharp(dict_match.group(2))
            return f"Dictionary<{k}, {v}>"

        # Reverse primitives
        if t in self._reverse_primitives:
            return self._reverse_primitives[t]

        # Reverse Unity types
        if t in self._reverse_unity:
            return self._reverse_unity[t]

        # None -> void
        if t == "None":
            return "void"

        return t

    def _split_generic_args(self, args_str: str) -> list[str]:
        """Split generic arguments respecting nested angle brackets."""
        result = []
        depth = 0
        current = ""
        for ch in args_str:
            if ch == "<":
                depth += 1
                current += ch
            elif ch == ">":
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


# ── Naming conventions ───────────────────────────────────────

def pascal_to_snake(name: str) -> str:
    """Convert PascalCase or camelCase to snake_case."""
    # Handle consecutive capitals (e.g. "OnCollisionEnter2D" -> "on_collision_enter_2d")
    s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
    s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
    s = re.sub(r'([a-zA-Z])(\d)', r'\1_\2', s)
    return s.lower()


def snake_to_pascal(name: str) -> str:
    """Convert snake_case to PascalCase."""
    return "".join(word.capitalize() for word in name.split("_"))


def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    parts = name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case (same as pascal_to_snake)."""
    return pascal_to_snake(name)


def convert_float_literal(value: str) -> str:
    """Convert C# float literal to Python: '5f' -> '5.0', '0.5f' -> '0.5'."""
    if value.endswith("f") or value.endswith("F"):
        num = value[:-1]
        if "." not in num:
            return num + ".0"
        return num
    return value
