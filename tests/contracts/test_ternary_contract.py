"""Contract tests: ternary operator translation must preserve conditions.

Bug: Python ternary `x if condition else y` was translated with condition
replaced by `true` because hasattr() replacement ran before ternary parsing.
"""

from src.translator.python_to_csharp import _translate_py_expression


class TestTernaryConditionPreserved:
    """The condition in a ternary must be translated, not replaced with 'true'."""

    def test_hasattr_condition_not_replaced_with_true(self):
        """The original bug: hasattr condition became literal 'true'."""
        py = "other.get_component(Bunker) if hasattr(other, 'get_component') else None"
        cs = _translate_py_expression(py)
        assert "true ?" not in cs, f"Condition replaced with 'true': {cs}"
        # hasattr should become true, but the ternary should collapse or
        # at minimum not emit `true ?` — the real fix is condition preservation
        # For hasattr specifically, `true ? X : Y` should simplify to just X,
        # but the core contract is: non-hasattr conditions MUST be preserved.

    def test_tag_comparison_condition_preserved(self):
        """Tag comparison must appear in the C# ternary condition."""
        py = 'other.get_component(Bunker) if other.tag == "Bunker" else None'
        cs = _translate_py_expression(py)
        assert "?" in cs, f"No ternary operator in output: {cs}"
        # The condition must reference the tag check, not be 'true'
        assert "true ?" not in cs, f"Condition replaced with 'true': {cs}"
        assert 'tag' in cs.lower() or 'Tag' in cs, f"Tag check missing from condition: {cs}"

    def test_self_field_condition_preserved(self):
        """self.is_active condition must translate to isActive."""
        py = "a if self.is_active else b"
        cs = _translate_py_expression(py)
        assert "?" in cs, f"No ternary operator in output: {cs}"
        assert "true ?" not in cs, f"Condition replaced with 'true': {cs}"
        assert "isActive" in cs or "is_active" in cs, f"Condition not preserved: {cs}"

    def test_comparison_condition_preserved(self):
        """x > 0 condition must be preserved."""
        py = "x if x > 0 else -x"
        cs = _translate_py_expression(py)
        assert "?" in cs, f"No ternary operator in output: {cs}"
        assert "x > 0" in cs, f"Comparison condition not preserved: {cs}"

    def test_nested_ternary(self):
        """Nested ternary must preserve both conditions."""
        py = "a if x else (b if y else c)"
        cs = _translate_py_expression(py)
        assert "?" in cs, f"No ternary operator in output: {cs}"
        # Should have two ? operators for nested ternary
        assert cs.count("?") == 2, f"Expected 2 ternary operators, got {cs.count('?')}: {cs}"

    def test_none_translates_to_null(self):
        """None in ternary false branch must become null."""
        py = "x if cond else None"
        cs = _translate_py_expression(py)
        assert "null" in cs, f"None not translated to null: {cs}"
