"""Contract tests for Python 'in' operator translation to C#.

Derived from C# language spec:
- List<T>.Contains(x) for list membership
- Dictionary<K,V>.ContainsKey(k) for dict key membership
- string.Contains(s) for string containment
- 'not in' must negate: !collection.Contains(x) / !dict.ContainsKey(k)
- 'for x in collection' must still produce 'foreach (var x in collection)' (regression guard)
"""

from src.translator.python_to_csharp import translate
from src.translator.python_parser import parse_python


class TestInOperatorListContains:
    """'x in my_list' must translate to 'my_list.Contains(x)' in C#."""

    def test_if_x_in_list(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.items: list[int] = []\n"
            "    def update(self):\n"
            "        x: int = 5\n"
            "        if x in self.items:\n"
            "            pass\n"
        )
        result = translate(parsed)
        # Must NOT contain raw Python 'in' keyword in an if-condition context
        # Must produce .Contains() call
        assert "items.Contains(x)" in result or "items.Contains(x)" in result.replace(" ", ""), (
            f"Expected 'items.Contains(x)' in output, got:\n{result}"
        )
        # Must NOT have 'x in items' as a C# condition (that's invalid C#)
        lines = result.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("if") and "in" in stripped and "Contains" not in stripped:
                # Allow 'foreach ... in ...' but not 'if (x in items)'
                if "foreach" not in stripped:
                    assert False, f"Leaked Python 'in' operator in condition: {stripped}"


class TestInOperatorDictContainsKey:
    """'key in my_dict' must translate to 'my_dict.ContainsKey(key)' for dict-typed vars."""

    def test_if_key_in_dict(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.lookup: dict[str, int] = {}\n"
            "    def update(self):\n"
            "        key: str = 'hello'\n"
            "        if key in self.lookup:\n"
            "            pass\n"
        )
        result = translate(parsed)
        assert "ContainsKey" in result, (
            f"Expected 'ContainsKey' for dict membership test, got:\n{result}"
        )
        # Specifically check for the correct form
        assert "lookup.ContainsKey(key)" in result or "lookup.ContainsKey(key)" in result.replace(" ", ""), (
            f"Expected 'lookup.ContainsKey(key)' in output, got:\n{result}"
        )


class TestNotInOperator:
    """'x not in items' must translate to '!items.Contains(x)' in C#."""

    def test_if_x_not_in_list(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.items: list[int] = []\n"
            "    def update(self):\n"
            "        x: int = 5\n"
            "        if x not in self.items:\n"
            "            pass\n"
        )
        result = translate(parsed)
        # Must negate: !items.Contains(x)
        assert "!items.Contains(x)" in result or "!items.Contains(x)" in result.replace(" ", ""), (
            f"Expected '!items.Contains(x)' for 'not in' list test, got:\n{result}"
        )

    def test_if_key_not_in_dict(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.lookup: dict[str, int] = {}\n"
            "    def update(self):\n"
            "        key: str = 'hello'\n"
            "        if key not in self.lookup:\n"
            "            pass\n"
        )
        result = translate(parsed)
        assert "!lookup.ContainsKey(key)" in result or "!lookup.ContainsKey(key)" in result.replace(" ", ""), (
            f"Expected '!lookup.ContainsKey(key)' for 'not in' dict test, got:\n{result}"
        )


class TestForInRegressionGuard:
    """'for x in collection' must STILL produce 'foreach (var x in collection)' — not broken by in-operator fix."""

    def test_for_in_still_produces_foreach(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.items: list[int] = []\n"
            "    def update(self):\n"
            "        for item in self.items:\n"
            "            pass\n"
        )
        result = translate(parsed)
        assert "foreach" in result, f"Expected 'foreach' in output, got:\n{result}"
        assert "foreach (var" in result, f"Expected 'foreach (var ...' pattern, got:\n{result}"

    def test_for_in_range_still_works(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        for i in range(10):\n"
            "            pass\n"
        )
        result = translate(parsed)
        assert "for (int" in result, f"Expected 'for (int ...' for range loop, got:\n{result}"


class TestStringContains:
    """'if char in my_string' must translate to 'my_string.Contains(char)' in C#."""

    def test_if_char_in_string(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.name: str = 'hello'\n"
            "    def update(self):\n"
            "        ch: str = 'a'\n"
            "        if ch in self.name:\n"
            "            pass\n"
        )
        result = translate(parsed)
        # Must produce .Contains() for string membership
        assert "Contains" in result, (
            f"Expected '.Contains()' for string membership test, got:\n{result}"
        )
        # Must NOT have raw 'ch in name' as C# condition
        lines = result.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("if") and "ch in" in stripped.lower() and "Contains" not in stripped:
                if "foreach" not in stripped:
                    assert False, f"Leaked Python 'in' operator in string condition: {stripped}"
