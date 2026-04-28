"""Contract tests: for _ in range(N) must not break UPPER_CASE constants.

Bug: snake_to_camel("_") returns "" which:
  1. Produces invalid C# loop variable: `for (int  = 0; ...)`
  2. Can corrupt identifiers containing underscores via symbol replacement
"""


from src.translator.python_parser import parse_python
from src.translator.python_to_csharp import translate


def _translate_snippet(code: str) -> str:
    """Translate a Python MonoBehaviour class to C#."""
    parsed = parse_python(code)
    return translate(parsed)


class TestUnderscoreLoopVariable:
    """for _ in range(...) must produce valid C# with a real loop variable."""

    def test_underscore_range_with_upper_snake_constant(self):
        """GRID_COLS must be preserved (not GRIDCOLS or broken)."""
        code = '''
import engine

class Grid(engine.MonoBehaviour):
    GRID_COLS: int = 10

    def start(self):
        for _ in range(self.GRID_COLS):
            pass
'''
        cs = _translate_snippet(code)
        # The constant must appear intact
        assert "GRID_COLS" in cs, f"GRID_COLS was corrupted in output:\n{cs}"
        # The loop variable must be a real identifier (not empty)
        assert "int  =" not in cs, f"Empty loop variable in output:\n{cs}"
        # Must have a valid for-loop structure
        assert "for (int " in cs, f"Missing valid for-loop:\n{cs}"

    def test_underscore_range_with_member_field(self):
        """self.num_rows must translate to numRows."""
        code = '''
import engine

class Grid(engine.MonoBehaviour):
    num_rows: int = 5

    def start(self):
        for _ in range(self.num_rows):
            pass
'''
        cs = _translate_snippet(code)
        assert "int  =" not in cs, f"Empty loop variable:\n{cs}"
        # numRows should appear in the loop limit
        assert "numRows" in cs, f"num_rows not converted to numRows:\n{cs}"

    def test_underscore_range_simple_literal(self):
        """for _ in range(3) must produce a valid loop."""
        code = '''
import engine

class Simple(engine.MonoBehaviour):
    def start(self):
        for _ in range(3):
            pass
'''
        cs = _translate_snippet(code)
        assert "int  =" not in cs, f"Empty loop variable:\n{cs}"
        assert "< 3" in cs, f"Missing limit:\n{cs}"

    def test_regular_loop_variable_unaffected(self):
        """for i in range(n) must still work normally."""
        code = '''
import engine

class Normal(engine.MonoBehaviour):
    def start(self):
        for i in range(10):
            pass
'''
        cs = _translate_snippet(code)
        assert "int i = 0" in cs, f"Normal loop variable broken:\n{cs}"
        assert "i < 10" in cs

    def test_upper_snake_constant_in_loop_body(self):
        """UPPER_SNAKE_CASE constants in the loop body must keep underscores."""
        code = '''
import engine

class Config(engine.MonoBehaviour):
    MAX_HEALTH: int = 100
    TILE_SIZE: int = 32

    def start(self):
        for _ in range(3):
            x = self.MAX_HEALTH + self.TILE_SIZE
'''
        cs = _translate_snippet(code)
        assert "MAX_HEALTH" in cs, f"MAX_HEALTH corrupted:\n{cs}"
        assert "TILE_SIZE" in cs, f"TILE_SIZE corrupted:\n{cs}"

    def test_two_underscore_loops_in_sequence(self):
        """Two consecutive for _ loops must both be valid."""
        code = '''
import engine

class Multi(engine.MonoBehaviour):
    ROWS: int = 3
    COLS: int = 5

    def start(self):
        for _ in range(self.ROWS):
            pass
        for _ in range(self.COLS):
            pass
'''
        cs = _translate_snippet(code)
        count = cs.count("int  =")
        assert count == 0, f"Found {count} empty loop variables:\n{cs}"
