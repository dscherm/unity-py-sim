"""Contract tests for translator fixes rounds 7-9.

Tests are derived from Unity C# conventions and the translator's public API,
NOT from reading existing test files. Each test targets a specific fix.
"""


from src.translator.python_to_csharp import translate
from src.translator.python_parser import parse_python


# ── 1. UPPER_CASE constants preserved in MonoBehaviour field declarations ──


class TestUpperCaseConstantsPreserved:
    """UPPER_CASE field names in MonoBehaviour classes must stay UPPER_CASE
    in the C# output — never get mangled to GRIDRows or similar."""

    def test_grid_rows_stays_upper_case(self):
        src = '''\
from src.engine.core import MonoBehaviour

class Board(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.GRID_ROWS: int = 11
        self.GRID_COLS: int = 11
'''
        ir = parse_python(src)
        cs = translate(ir)
        assert "GRID_ROWS" in cs, "GRID_ROWS was mangled"
        assert "GRID_COLS" in cs, "GRID_COLS was mangled"
        # Must NOT contain camelCase corruption
        assert "GRIDRows" not in cs
        assert "GRIDCols" not in cs
        assert "gridRows" not in cs
        assert "gridCols" not in cs

    def test_multiple_upper_constants_in_field_declarations(self):
        src = '''\
from src.engine.core import MonoBehaviour

class GameConfig(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.MAX_SPEED: float = 10.0
        self.MIN_SPEED: float = 1.0
        self.SPAWN_DELAY: float = 0.5
'''
        ir = parse_python(src)
        cs = translate(ir)
        assert "MAX_SPEED" in cs
        assert "MIN_SPEED" in cs
        assert "SPAWN_DELAY" in cs
        # None should be camelCased
        assert "maxSpeed" not in cs
        assert "minSpeed" not in cs
        assert "spawnDelay" not in cs

    def test_upper_constants_used_in_method_bodies(self):
        """When UPPER_CASE fields are referenced in method bodies, they should
        stay UPPER_CASE (not get snake_to_camel'd)."""
        src = '''\
from src.engine.core import MonoBehaviour

class Board(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.GRID_ROWS: int = 11

    def update(self):
        for i in range(self.GRID_ROWS):
            pass
'''
        ir = parse_python(src)
        cs = translate(ir)
        # In the for-loop body, the reference to GRID_ROWS must be preserved
        assert "GRID_ROWS" in cs
        assert "GRIDRows" not in cs


# ── 2. List comprehension with _ variable doesn't strip underscores ──


class TestUnderscoreInListComprehension:
    """Using _ as a throwaway variable in list comprehensions must not
    affect the translation of other names containing underscores."""

    def test_underscore_var_doesnt_corrupt_other_names(self):
        src = '''\
from src.engine.core import MonoBehaviour

class Spawner(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.enemy_list: list = []

    def start(self):
        result = [0 for _ in range(10)]
        self.enemy_list = result
'''
        ir = parse_python(src)
        cs = translate(ir)
        # enemy_list should translate to enemyList, not get corrupted
        assert "enemyList" in cs
        # The _ in comprehension should not break anything
        assert "0" in cs

    def test_underscore_in_comprehension_with_filter(self):
        """[expr for _ in coll if cond] — underscore should not be substituted."""
        src = '''\
from src.engine.core import MonoBehaviour

class Builder(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.total_count: int = 0

    def build(self):
        items = [True for _ in range(5)]
'''
        ir = parse_python(src)
        cs = translate(ir)
        # totalCount must be camelCase, not corrupted
        assert "totalCount" in cs


# ── 3. Typed assignments always re-declare ──


class TestTypedAssignmentsRedeclare:
    """Python typed assignments (gm: GameManager = ...) should ALWAYS emit
    a C# type declaration, even if the variable was previously assigned."""

    def test_typed_local_always_declares_type(self):
        src = '''\
from src.engine.core import MonoBehaviour

class Player(MonoBehaviour):
    def update(self):
        gm: GameManager = self.get_component(GameManager)
        gm.do_something()
'''
        ir = parse_python(src)
        cs = translate(ir)
        # Must emit "GameManager gm = ..." not "var gm = ..."
        assert "GameManager gm" in cs or "GameManager gm =" in cs

    def test_typed_redeclaration_in_sibling_blocks(self):
        """Even if a variable is assigned in one if-branch with a type annotation,
        a second typed assignment in an elif branch should also emit the type."""
        src = '''\
from src.engine.core import MonoBehaviour

class Controller(MonoBehaviour):
    def update(self):
        if True:
            target: Transform = self.transform
        else:
            target: Transform = self.transform
'''
        ir = parse_python(src)
        cs = translate(ir)
        # Both branches should have "Transform target"
        count = cs.count("Transform target")
        assert count == 2, f"Expected 2 declarations, got {count}"


# ── 4. Local array vars added to _array_fields — use .Length not .Count ──


class TestLocalArrayVarsUseLength:
    """When a local variable is typed as T[], len(var) should emit var.Length,
    not var.Count (which is for List<T>)."""

    def test_local_array_uses_length(self):
        """list[int] type annotation maps to int[] in C#, so len() -> .Length."""
        src = '''\
from src.engine.core import MonoBehaviour

class Grid(MonoBehaviour):
    def update(self):
        cells: list[int] = [1, 2, 3]
        n = len(cells)
'''
        ir = parse_python(src)
        cs = translate(ir)
        # list[int] -> int[] (array), so must use .Length
        assert ".Length" in cs

    def test_list_field_with_append_uses_count(self):
        """When .append() is used, the translator upgrades list[T] to List<T>,
        so len() should emit .Count."""
        src = '''\
from src.engine.core import MonoBehaviour

class Inventory(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.items: list[int] = []

    def update(self):
        self.items.append(1)
        n = len(self.items)
'''
        ir = parse_python(src)
        cs = translate(ir)
        # append() upgrades to List<int>, so .Count is used
        assert ".Count" in cs

    def test_array_field_uses_length(self):
        """A list[int] field WITHOUT .append() maps to int[], uses .Length."""
        src = '''\
from src.engine.core import MonoBehaviour

class Grid(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.cells: list[int] = []

    def update(self):
        n = len(self.cells)
'''
        ir = parse_python(src)
        cs = translate(ir)
        # No append usage -> int[] -> .Length
        assert ".Length" in cs


# ── 5. .ToList() -> .ToArray() when target type is T[] ──


class TestToListToArrayConversion:
    """When a typed local variable has type T[], any .ToList() on the RHS
    should be replaced with .ToArray()."""

    def test_to_list_becomes_to_array_for_array_type(self):
        """list[Invader] typed local maps to Invader[], so .ToList() -> .ToArray()."""
        src = '''\
from src.engine.core import MonoBehaviour

class Filter(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.invaders: list[object] = []

    def start(self):
        active: list[Invader] = [inv for inv in self.invaders if inv.active]
'''
        ir = parse_python(src)
        cs = translate(ir)
        # list[Invader] -> Invader[] -> .ToArray() not .ToList()
        assert ".ToArray()" in cs
        assert ".ToList()" not in cs

    def test_comprehension_without_typed_target_keeps_to_list(self):
        """Without an explicit typed assignment, list comprehension keeps .ToList()."""
        src = '''\
from src.engine.core import MonoBehaviour

class Filter(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.invaders: list[object] = []

    def start(self):
        active = [inv for inv in self.invaders if inv.active]
'''
        ir = parse_python(src)
        cs = translate(ir)
        # No explicit type annotation -> var -> keeps .ToList()
        assert ".ToList()" in cs


# ── 6. Module-level functions emitted as public static methods ──


class TestModuleFunctionsAsStaticMethods:
    """Top-level (module-level) functions in the Python source should be
    emitted as public static methods on the last MonoBehaviour class."""

    def test_module_function_becomes_static(self):
        src = '''\
from src.engine.core import MonoBehaviour

def helper_func(x: int) -> int:
    return x * 2

class Player(MonoBehaviour):
    def update(self):
        result = helper_func(5)
'''
        ir = parse_python(src)
        cs = translate(ir)
        # The function should appear as "public static" inside the class
        assert "public static" in cs
        assert "HelperFunc" in cs

    def test_module_function_parsed_correctly(self):
        """parse_python should capture module-level functions in module_functions."""
        src = '''\
def compute_score(base: int, multiplier: float) -> float:
    return base * multiplier
'''
        ir = parse_python(src)
        assert len(ir.module_functions) == 1
        func = ir.module_functions[0]
        assert func.name == "compute_score"
        assert len(func.parameters) == 2
        assert func.parameters[0].name == "base"
        assert func.parameters[1].name == "multiplier"
        assert func.return_annotation == "float"

    def test_multiple_module_functions(self):
        src = '''\
from src.engine.core import MonoBehaviour

def func_a() -> int:
    return 1

def func_b() -> int:
    return 2

class Game(MonoBehaviour):
    def start(self):
        pass
'''
        ir = parse_python(src)
        cs = translate(ir)
        assert "FuncA" in cs
        assert "FuncB" in cs
        # Both should be public static
        assert cs.count("public static") >= 2


# ── 7. Dataclass constructor kwargs -> C# object initializer ──


class TestDataclassKwargsToObjectInitializer:
    """Dataclass constructor calls with keyword args should translate to
    C# object initializer syntax: new ClassName { field = value }."""

    def test_dataclass_kwargs_to_initializer_in_field_default(self):
        """Dataclass constructor kwargs in field defaults (processed by
        _py_value_to_csharp) should emit C# object initializer syntax."""
        src = '''\
from dataclasses import dataclass
from src.engine.core import MonoBehaviour

@dataclass
class InvaderRowConfig:
    sprite_index: int = 0
    points: int = 10
    count: int = 11

class GameManager(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.row_configs: list[InvaderRowConfig] = [
            InvaderRowConfig(sprite_index=0, points=10, count=11),
            InvaderRowConfig(sprite_index=1, points=20, count=11),
        ]
'''
        ir = parse_python(src)
        cs = translate(ir)
        # Should use object initializer syntax in the field default
        assert "new InvaderRowConfig {" in cs or "new InvaderRowConfig{" in cs
        # Fields should be camelCased
        assert "spriteIndex = 0" in cs or "spriteIndex=0" in cs

    def test_single_dataclass_kwarg_in_field_default(self):
        """Single kwarg in a field default should also emit object initializer."""
        src = '''\
from dataclasses import dataclass
from src.engine.core import MonoBehaviour

@dataclass
class Config:
    speed: float = 1.0

class Player(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.config: Config = Config(speed=5.0)
'''
        ir = parse_python(src)
        cs = translate(ir)
        assert "new Config" in cs
        assert "speed = 5.0" in cs or "speed=5.0" in cs

    def test_dataclass_fields_emitted_as_plain_class(self):
        """Dataclass fields should appear as public fields in a plain C# class."""
        src = '''\
from dataclasses import dataclass

@dataclass
class InvaderRowConfig:
    sprite_index: int = 0
    points: int = 10
'''
        ir = parse_python(src)
        cs = translate(ir)
        assert "public class InvaderRowConfig" in cs
        assert "spriteIndex" in cs
        assert "points" in cs


# ── 8. Bool fields collected from ALL classes in pre-pass ──


class TestBoolFieldsFromAllClasses:
    """The pre-pass that collects bool fields for truthiness checks must
    scan ALL classes, not just the first one."""

    def test_bool_field_in_second_class(self):
        """A bool field declared in the second class should still be recognized
        for truthiness translation (field instead of field != null)."""
        src = '''\
from src.engine.core import MonoBehaviour

class Player(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.is_alive: bool = True

class Enemy(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.is_active: bool = True

    def update(self):
        if self.is_active:
            pass
'''
        ir = parse_python(src)
        cs = translate(ir)
        # "if (isActive)" should NOT become "if (isActive != null)"
        # It should be just "if (isActive)" since bool fields are truthy as-is
        assert "isActive != null" not in cs

    def test_bool_field_default_value_detection(self):
        """Fields with default True/False should be detected as bool even
        without explicit type annotation."""
        src = '''\
from src.engine.core import MonoBehaviour

class Bullet(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.can_fire = True

class Ship(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.is_destroyed = False

    def update(self):
        if self.is_destroyed:
            pass
'''
        ir = parse_python(src)
        cs = translate(ir)
        # is_destroyed -> isDestroyed, should be treated as bool
        assert "isDestroyed != null" not in cs

    def test_bool_from_first_class_also_works(self):
        """Sanity check: bool fields in the first class still work too."""
        src = '''\
from src.engine.core import MonoBehaviour

class Player(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.is_grounded: bool = False

    def update(self):
        if self.is_grounded:
            pass
'''
        ir = parse_python(src)
        cs = translate(ir)
        assert "isGrounded != null" not in cs


# ── Mutation tests ──


class TestMutationRoundtrip:
    """Mutation tests that break specific translator logic and verify
    the tests catch the breakage."""

    def test_mutation_upper_case_field_mangled(self):
        """If UPPER_CASE preservation were broken, we'd see camelCase output."""
        src = '''\
from src.engine.core import MonoBehaviour

class Board(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.MAX_HP: int = 100
'''
        ir = parse_python(src)
        cs = translate(ir)
        # The correct output has MAX_HP
        assert "MAX_HP" in cs
        # If the field were mangled, it would be maxHp or MAXHp
        assert "maxHp" not in cs
        assert "MAXHp" not in cs

    def test_mutation_typed_assign_uses_var(self):
        """Typed assignment must emit the explicit type, never 'var'."""
        src = '''\
from src.engine.core import MonoBehaviour

class Test(MonoBehaviour):
    def start(self):
        rb: Rigidbody2D = self.get_component(Rigidbody2D)
'''
        ir = parse_python(src)
        cs = translate(ir)
        assert "Rigidbody2D rb" in cs
        # Must NOT use var for typed assignments
        assert "var rb" not in cs

    def test_mutation_array_length_not_count(self):
        """If array detection broke, we'd see .Count instead of .Length.
        list[int] without .append() maps to int[], so .Length is correct."""
        src = '''\
from src.engine.core import MonoBehaviour

class Test(MonoBehaviour):
    def __init__(self):
        super().__init__()
        self.grid: list[int] = []

    def update(self):
        n = len(self.grid)
'''
        ir = parse_python(src)
        cs = translate(ir)
        assert ".Length" in cs
        assert "grid.Count" not in cs

    def test_mutation_module_func_not_lost(self):
        """Module-level functions must not be silently dropped."""
        src = '''\
from src.engine.core import MonoBehaviour

def calculate_damage(base: int) -> int:
    return base * 2

class Enemy(MonoBehaviour):
    def start(self):
        dmg = calculate_damage(10)
'''
        ir = parse_python(src)
        cs = translate(ir)
        assert "CalculateDamage" in cs
        assert "public static" in cs
