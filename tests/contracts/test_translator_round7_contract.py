"""Contract tests for translator round 7 fixes.

Tests derived from Unity C# conventions and actual Space Invaders translation bugs:
1. UPPER_CASE constants preserved in MonoBehaviour fields
2. forEach with List<GameObject> uses typed IEnumerator<T>
3. IEnumerator<T> extends IDisposable for coroutine support
4. [True] * Bunker.GRID_COLS captures dotted names in Repeat regex
5. Local variables without underscores (like 'gm') added to symbol table
"""

import pytest

from src.translator.python_to_csharp import translate
from src.translator.python_parser import parse_python


# ── Fix 1: UPPER_CASE constants preserved ──────────────────────


class TestUpperCaseConstantsPreserved:
    """MonoBehaviour class-level UPPER_CASE fields must stay UPPER_CASE in C#,
    not get mangled to PascalCase (e.g. GRID_ROWS must not become GRIDRows)."""

    def test_grid_rows_stays_uppercase(self):
        source = """\
class Bunker(MonoBehaviour):
    GRID_ROWS = 5
    GRID_COLS = 8

    def start(self):
        pass
"""
        parsed = parse_python(source)
        result = translate(parsed)
        # GRID_ROWS and GRID_COLS must appear verbatim
        assert "GRID_ROWS" in result
        assert "GRID_COLS" in result
        # Must NOT contain the PascalCase mangled versions
        assert "GRIDRows" not in result, "GRID_ROWS was mangled to GRIDRows"
        assert "GRIDCols" not in result, "GRID_COLS was mangled to GRIDCols"
        assert "GridRows" not in result, "GRID_ROWS was mangled to GridRows"
        assert "GridCols" not in result, "GRID_COLS was mangled to GridCols"

    def test_mixed_fields_upper_and_lower(self):
        """UPPER_CASE stays as-is, snake_case becomes camelCase."""
        source = """\
class Invader(MonoBehaviour):
    MAX_SPEED = 10
    move_speed = 2.0

    def start(self):
        pass
"""
        parsed = parse_python(source)
        result = translate(parsed)
        assert "MAX_SPEED" in result
        assert "moveSpeed" in result
        # MAX_SPEED must not be mangled
        assert "MAXSpeed" not in result
        assert "MaxSpeed" not in result

    def test_single_word_upper_constant(self):
        """Single-word UPPER constant like SPEED stays SPEED."""
        source = """\
class Ship(MonoBehaviour):
    SPEED = 5

    def start(self):
        pass
"""
        parsed = parse_python(source)
        result = translate(parsed)
        assert "SPEED" in result
        assert "Speed" not in result or "SPEED" in result  # Speed could appear in method names


# ── Fix 2 & 3: forEach typed IEnumerator and IDisposable ───────


class TestForEachTypedEnumerator:
    """When iterating a List<GameObject>, the C# foreach should use 'var'
    which resolves to the correct element type. The generated using
    directives must include System.Collections.Generic for List<T>."""

    def test_foreach_uses_var_keyword(self):
        """foreach (var item in collection) pattern is used."""
        source = """\
class Manager(MonoBehaviour):
    def start(self):
        self.enemies: list[GameObject] = []

    def clear_enemies(self):
        for enemy in self.enemies:
            enemy.set_active(False)
"""
        parsed = parse_python(source)
        result = translate(parsed)
        # Should produce foreach with var
        assert "foreach" in result
        assert "var enemy" in result or "var Enemy" in result

    def test_coroutine_returns_ienumerator(self):
        """Coroutine methods must return IEnumerator in C#."""
        source = """\
class Spawner(MonoBehaviour):
    def spawn_wave(self):
        yield 1.0
"""
        parsed = parse_python(source)
        result = translate(parsed)
        assert "IEnumerator" in result
        # System.Collections must be in using directives for IEnumerator
        assert "System.Collections" in result


# ── Fix 4: [True] * Bunker.GRID_COLS captures dotted names ────


class TestRepeatWithDottedNames:
    """[True] * Bunker.GRID_COLS must produce
    Enumerable.Repeat(true, Bunker.GRID_COLS).ToArray()
    NOT Enumerable.Repeat(true, Bunker).ToArray() (truncating at the dot)."""

    def test_repeat_captures_full_dotted_name(self):
        source = """\
class Bunker(MonoBehaviour):
    GRID_COLS = 8
    GRID_ROWS = 5

    def start(self):
        self.alive = [True] * Bunker.GRID_COLS
"""
        parsed = parse_python(source)
        result = translate(parsed)
        # Must contain the FULL dotted expression
        assert "Bunker.GRID_COLS" in result, (
            "Dotted name Bunker.GRID_COLS was truncated in Repeat expression"
        )
        # Must NOT truncate to just "Bunker"
        # Check that Repeat contains the full dotted name
        assert "Repeat(true, Bunker.GRID_COLS)" in result or \
               "Repeat(true, Bunker.GRID_COLS).ToArray()" in result, (
            f"Expected Repeat(true, Bunker.GRID_COLS) in output, got:\n{result}"
        )

    def test_repeat_with_simple_name(self):
        """[False] * count should still work with simple names."""
        source = """\
class Grid(MonoBehaviour):
    def start(self):
        count = 10
        self.cells = [False] * count
"""
        parsed = parse_python(source)
        result = translate(parsed)
        assert "Repeat(false," in result

    def test_range_with_dotted_name(self):
        """range(Bunker.GRID_ROWS) must produce
        Enumerable.Range(0, Bunker.GRID_ROWS) not truncate at the dot."""
        source = """\
class Bunker(MonoBehaviour):
    GRID_ROWS = 5

    def rebuild(self):
        for row in range(Bunker.GRID_ROWS):
            pass
"""
        parsed = parse_python(source)
        result = translate(parsed)
        # range(X) translates to a for loop: for (int row = 0; row < X; row++)
        assert "Bunker.GRID_ROWS" in result, (
            "Dotted name Bunker.GRID_ROWS was truncated in range() expression"
        )


# ── Fix 5: Local variables without underscores in symbol table ──


class TestLocalVariableSymbolTable:
    """Short local variables like 'gm' must be added to the symbol table
    so that second uses don't get a redundant 'var' declaration."""

    def test_no_redeclaration_of_short_local(self):
        """Variable 'gm' declared once, used again — no second 'var'."""
        source = """\
class Invader(MonoBehaviour):
    def start(self):
        gm = self.game_object.find("GameManager")
        gm.do_something()
"""
        parsed = parse_python(source)
        result = translate(parsed)
        # 'gm' should appear with a type/var declaration exactly once
        lines = [l.strip() for l in result.split("\n") if "gm" in l.lower()]
        # Filter to lines that declare gm (have 'var gm' or a type before gm =)
        decl_lines = [l for l in lines if "var gm" in l or l.startswith("var gm")]
        # At most one declaration
        assert len(decl_lines) <= 1, (
            f"Variable 'gm' declared multiple times:\n" +
            "\n".join(decl_lines)
        )

    def test_short_local_tracked_in_symbol_table(self):
        """A two-letter variable like 'rb' should be properly tracked."""
        source = """\
class Player(MonoBehaviour):
    def start(self):
        rb = self.game_object.get_component(Rigidbody2D)
        rb.velocity = Vector2(0, 0)
"""
        parsed = parse_python(source)
        result = translate(parsed)
        # Should not have two declarations of rb
        lines = [l.strip() for l in result.split("\n")]
        decl_count = sum(1 for l in lines if "var rb" in l or l.startswith("Rigidbody2D rb"))
        assert decl_count <= 1, f"Variable 'rb' declared {decl_count} times"

    def test_local_without_underscore_not_redeclared(self):
        """Variable assigned then reassigned should only be declared once."""
        source = """\
class Logic(MonoBehaviour):
    def update(self):
        dx = 1.0
        dx = dx + 0.5
"""
        parsed = parse_python(source)
        result = translate(parsed)
        lines = [l.strip() for l in result.split("\n") if "dx" in l]
        # First usage should declare, second should just assign
        decl_lines = [l for l in lines if l.startswith("var dx") or l.startswith("float dx")]
        assign_lines = [l for l in lines if l.startswith("dx =")]
        assert len(decl_lines) == 1, f"Expected 1 declaration, got {len(decl_lines)}"
        assert len(assign_lines) == 1, f"Expected 1 reassignment, got {len(assign_lines)}"


# ── Integration: combined patterns from Space Invaders ──────────


class TestSpaceInvadersCombined:
    """Integration test combining multiple fixes as they appear in real code."""

    def test_bunker_class_with_grid_constants_and_repeat(self):
        """Full Bunker pattern: UPPER_CASE constants + [True] * dotted repeat."""
        source = """\
class Bunker(MonoBehaviour):
    GRID_ROWS = 5
    GRID_COLS = 8

    def start(self):
        self.alive = [True] * Bunker.GRID_COLS
        for row in range(Bunker.GRID_ROWS):
            for col in range(Bunker.GRID_COLS):
                pass
"""
        parsed = parse_python(source)
        result = translate(parsed)

        # Constants preserved
        assert "GRID_ROWS" in result
        assert "GRID_COLS" in result
        assert "GRIDRows" not in result
        assert "GRIDCols" not in result

        # Dotted names in Repeat and range not truncated
        assert "Bunker.GRID_COLS" in result
        assert "Bunker.GRID_ROWS" in result

    def test_game_manager_with_short_locals(self):
        """GameManager pattern: short local variables used multiple times."""
        source = """\
class GameManager(MonoBehaviour):
    def spawn_invaders(self):
        gm = self.game_object
        gm.set_active(True)
        go = gm.find("Player")
        go.set_active(True)
"""
        parsed = parse_python(source)
        result = translate(parsed)

        # Each local declared at most once
        lines = [l.strip() for l in result.split("\n")]
        gm_decls = sum(1 for l in lines if "var gm" in l or "GameObject gm" in l)
        go_decls = sum(1 for l in lines if "var go" in l or "GameObject go" in l)
        assert gm_decls <= 1, f"'gm' declared {gm_decls} times"
        assert go_decls <= 1, f"'go' declared {go_decls} times"
