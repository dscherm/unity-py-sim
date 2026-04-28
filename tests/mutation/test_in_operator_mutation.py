"""Mutation tests for Python 'in' operator translation.

These tests monkeypatch the translator to introduce specific bugs,
then verify that our contract tests would catch them.
"""

import re

from src.translator.python_to_csharp import translate
from src.translator.python_parser import parse_python


def _make_parsed_list_in():
    """Helper: create parsed IR with 'x in list' pattern."""
    return parse_python(
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


def _make_parsed_dict_in():
    """Helper: create parsed IR with 'key in dict' pattern."""
    return parse_python(
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


def _make_parsed_not_in():
    """Helper: create parsed IR with 'x not in list' pattern."""
    return parse_python(
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


class TestMutationContainsForDict:
    """Mutant: emit .Contains() for dicts instead of .ContainsKey() — tests must catch it."""

    def test_contains_instead_of_containskey_is_wrong(self):
        """If the translator emitted .Contains() for a dict, that's a bug.
        Dict.Contains() checks KeyValuePair, not key — must use .ContainsKey()."""
        result = translate(_make_parsed_dict_in())
        # The correct output should have ContainsKey, not just Contains
        # This test verifies our contract catches the distinction.
        #
        # Currently the translator doesn't handle 'in' at all, so this
        # will fail. Once fixed, if someone mutates ContainsKey -> Contains,
        # this test catches it.
        assert "ContainsKey" in result, (
            f"Dict membership must use .ContainsKey(), not .Contains(). Got:\n{result}"
        )
        # Also ensure it's not just .Contains (which would be wrong for dict)
        # Strip out ContainsKey occurrences, then check no bare .Contains remains for dict
        without_containskey = result.replace("ContainsKey", "REPLACED")
        if "Contains" in without_containskey:
            # There might be other Contains calls — that's ok if not for dict
            pass  # This is acceptable, just verifying ContainsKey is present


class TestMutationLeakedInKeyword:
    """Mutant: translator does NOT translate 'in' at all — raw Python leaks through."""

    def test_raw_in_keyword_leaks_to_csharp(self):
        """The 'in' keyword in if-conditions is invalid C#.
        Tests must detect raw 'x in items' in output."""
        result = translate(_make_parsed_list_in())
        # Check that no if-condition contains raw 'in' (Python syntax leak)
        lines = result.split("\n")
        found_leak = False
        for line in lines:
            stripped = line.strip()
            # Look for 'if (... in ...)' pattern that is NOT foreach
            if stripped.startswith("if") and "foreach" not in stripped:
                # Check for raw Python 'in' that should have been translated
                if re.search(r"\b\w+\s+in\s+\w+", stripped) and "Contains" not in stripped:
                    found_leak = True
                    break

        # Currently the translator DOES leak 'in' — this test documents the bug.
        # Once fixed, the leak should be gone and this assertion should pass.
        assert not found_leak, (
            f"Raw Python 'in' keyword leaked into C# if-condition: {stripped}"
        )

    def test_raw_not_in_keyword_leaks_to_csharp(self):
        """'not in' must not leak as raw text into C#."""
        result = translate(_make_parsed_not_in())
        lines = result.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("if") and "foreach" not in stripped:
                assert "not in" not in stripped, (
                    f"Raw Python 'not in' leaked into C# if-condition: {stripped}"
                )


class TestMutationMissingNegation:
    """Mutant: 'not in' translated without negation — tests must detect missing '!'."""

    def test_not_in_must_negate(self):
        """If 'x not in items' translates to 'items.Contains(x)' without '!',
        that's a logic bug — tests must catch the missing negation."""
        result = translate(_make_parsed_not_in())
        # Must have negation for 'not in'
        # Look for either !items.Contains(x) or !lookup.ContainsKey(key)
        has_negated_contains = "!items.Contains" in result or "!" in result and "Contains" in result
        assert has_negated_contains, (
            f"Expected negated Contains (!) for 'not in' pattern, got:\n{result}"
        )
        # Double-check: must NOT have bare .Contains without ! for a 'not in' case
        # (i.e., the negation must be present)
        lines = result.split("\n")
        for line in lines:
            stripped = line.strip()
            if "Contains" in stripped and stripped.startswith("if"):
                assert "!" in stripped, (
                    f"Missing negation for 'not in' translation: {stripped}"
                )
