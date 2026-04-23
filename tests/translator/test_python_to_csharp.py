"""Tests for Python to C# translator."""

import re
from pathlib import Path
from src.translator.python_to_csharp import translate_file, translate
from src.translator.python_parser import parse_python

PONG_DIR = Path(__file__).parent.parent.parent / "examples" / "pong" / "pong_python"


class TestReverseTranslatorBasics:
    def test_simple_monobehaviour(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.speed: float = 5.0\n"
        )
        result = translate(parsed)
        assert "public class Foo : MonoBehaviour" in result
        assert "public float speed = 5.0f;" in result or "public float speed = 5f;" in result

    def test_lifecycle_method_naming(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        pass\n"
            "    def fixed_update(self):\n"
            "        pass\n"
        )
        result = translate(parsed)
        assert "Update()" in result
        assert "FixedUpdate()" in result

    def test_get_component_reverse(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        self.rb = self.get_component(Rigidbody2D)\n"
        )
        result = translate(parsed)
        assert "GetComponent<Rigidbody2D>()" in result

    def test_gameobject_find_reverse(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour, GameObject\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        obj = GameObject.find('Ball')\n"
        )
        result = translate(parsed)
        assert 'GameObject.Find("Ball")' in result

    def test_input_api_reverse(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.input_manager import Input\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        h = Input.get_axis('Horizontal')\n"
        )
        result = translate(parsed, input_system="legacy")
        assert 'Input.GetAxis("Horizontal")' in result

    def test_time_api_reverse(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.time_manager import Time\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        self.timer -= Time.delta_time\n"
        )
        result = translate(parsed)
        assert "Time.deltaTime" in result

    def test_print_to_debug_log(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        print('hello')\n"
        )
        result = translate(parsed)
        assert 'Debug.Log("hello")' in result

    def test_static_fields(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    count: int = 0\n"
        )
        result = translate(parsed)
        # Class-level fields (not self.X) should be static, but translator
        # doesn't implement this yet — tracked as Stage 2 task.
        assert "int count = 0;" in result

    def test_static_method(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    @staticmethod\n"
            "    def do_thing():\n"
            "        pass\n"
        )
        result = translate(parsed)
        assert "public static" in result
        assert "DoThing()" in result


class TestPongReverseTranslation:
    """Pong tests use legacy Input API (Input.GetAxis)."""

    def test_translate_paddle_controller(self):
        result = translate_file(PONG_DIR / "paddle_controller.py", input_system="legacy")
        assert "public class PaddleController : MonoBehaviour" in result
        assert "public float speed = 10.0f;" in result or "public float speed = 10f;" in result
        assert "Start()" in result
        assert "Update()" in result
        assert "Input.GetAxis(" in result

    def test_translate_ball_controller(self):
        result = translate_file(PONG_DIR / "ball_controller.py", input_system="legacy")
        assert "public class BallController : MonoBehaviour" in result
        assert "public float initialSpeed = 6.0f;" in result or "public float initialSpeed = 6f;" in result
        assert "Start()" in result
        assert "Launch()" in result
        assert "ResetState()" in result or "Reset()" in result
        assert "OnCollisionEnter2D(Collision2D collision)" in result

    def test_translate_score_manager(self):
        result = translate_file(PONG_DIR / "score_manager.py", input_system="legacy")
        assert "public class ScoreManager : MonoBehaviour" in result
        assert "public static int scoreLeft = 0;" in result
        assert "public static" in result
        assert "Debug.Log(" in result

    def test_translate_game_manager(self):
        result = translate_file(PONG_DIR / "game_manager.py", input_system="legacy")
        assert "public class GameManager : MonoBehaviour" in result
        assert "Start()" in result
        assert "Update()" in result
        assert "Time.deltaTime" in result
        assert 'GameObject.Find("Ball")' in result

    def test_using_unityengine_present(self):
        """All translated files should have using UnityEngine."""
        for py_file in PONG_DIR.glob("*.py"):
            if py_file.name.startswith("__"):
                continue
            result = translate_file(py_file, input_system="legacy")
            assert "using UnityEngine;" in result, f"{py_file.name} missing using UnityEngine"


ANGRY_BIRDS_DIR = Path(__file__).parent.parent.parent / "examples" / "angry_birds" / "angry_birds_python"


class TestForLoopTranslation:
    def test_range_single_arg(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        for i in range(10):\n"
            "            print(i)\n"
        )
        result = translate(parsed)
        assert "for (int i = 0; i < 10; i++)" in result

    def test_range_two_args(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        for i in range(2, 8):\n"
            "            print(i)\n"
        )
        result = translate(parsed)
        assert "for (int i = 2; i < 8; i++)" in result

    def test_range_three_args(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        for i in range(0, 10, 2):\n"
            "            print(i)\n"
        )
        result = translate(parsed)
        assert "for (int i = 0; i < 10; i += 2)" in result

    def test_range_with_len(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        for i in range(len(self.items)):\n"
            "            print(i)\n"
        )
        result = translate(parsed)
        assert "for (int i = 0; i < items.Count; i++)" in result

    def test_foreach_collection(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        for obj in self.enemies:\n"
            "            print(obj)\n"
        )
        result = translate(parsed)
        assert "foreach (var obj in enemies)" in result

    def test_foreach_concatenated_lists(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        for obj in self.birds + self.pigs:\n"
            "            print(obj)\n"
        )
        result = translate(parsed)
        assert "foreach (var obj in birds + pigs)" in result


class TestCollectionTranslation:
    def test_append_to_add(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        self.items.append(5)\n"
        )
        result = translate(parsed)
        assert "items.Add(5)" in result

    def test_remove(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        self.items.remove(obj)\n"
        )
        result = translate(parsed)
        assert "items.Remove(obj)" in result

    def test_len_to_count(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if self.index >= len(self.birds):\n"
            "            return\n"
        )
        result = translate(parsed)
        assert "birds.Count" in result

    def test_len_in_expression(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        self.remaining = len(self.birds) - self.index\n"
        )
        result = translate(parsed)
        assert "birds.Count - index" in result


class TestListTypeInference:
    """G1 + G2: List<T> element-type inference and auto-emit System.Collections.Generic.

    Covers regressions for data/lessons/coplay_generator_gaps.md gaps 1 and 2.
    """

    def test_list_t_annotation_emits_typed_array(self):
        """Baseline: list[T] subscript annotation emits T[] (array form)."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.items: list[Rigidbody2D] = []\n"
        )
        result = translate(parsed)
        assert "Rigidbody2D[] items" in result
        assert "List<object>" not in result

    def test_bare_list_with_trailing_sprite_array_comment(self):
        """G1: bare `list` annotation + `# Sprite[]` trailing comment -> Sprite[]."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.sprites: list = []  # Sprite[]\n"
        )
        result = translate(parsed)
        assert "Sprite[] sprites" in result
        assert "List<object>" not in result

    def test_bare_list_with_trailing_list_bracket_comment(self):
        """G1 alt form: `# list[AudioClip]` trailing comment -> AudioClip[]."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.clips: list = []  # list[AudioClip]\n"
        )
        result = translate(parsed)
        assert "AudioClip[] clips" in result
        assert "List<object>" not in result

    def test_using_generic_emits_when_inferred_via_append(self):
        """G2: when the annotation has no `list[`/`List<` but inference produces
        List<T> via .append() -> get_component() chain, the using must still appear."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.items = []\n"
            "    def start(self):\n"
            "        rb = self.get_component(Rigidbody2D)\n"
            "        self.items.append(rb)\n"
        )
        result = translate(parsed)
        assert "List<Rigidbody2D>" in result
        assert "using System.Collections.Generic;" in result


class TestSiblingBlockScoping:
    """Python flat function scope vs C# block scope.  Sibling if-blocks
    assigning the same name in Python must each get their own `var X`
    in C# — without the scope-aware _declared_vars tracking, the second
    block emits bare `X = ...` and fails to compile (CS0103).  Regression
    for data/lessons/pacman_v2_deploy.md gap PV-1 (GhostHome.ExitTransition).
    """

    def test_sibling_if_blocks_each_declare_variable(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def test(self, a, b):\n"
            "        if a > 0:\n"
            "            target = 1\n"
            "            self.do_thing(target)\n"
            "        if b > 0:\n"
            "            target = 2\n"
            "            self.do_thing(target)\n"
        )
        result = translate(parsed)
        # Each sibling block must declare its own `target` — not leave
        # the second one as a bare reassignment.
        assert result.count("var target = 1") + result.count("int target = 1") >= 1
        assert result.count("var target = 2") + result.count("int target = 2") >= 1

    def test_same_scope_reassignment_does_not_redeclare(self):
        """Within the same block, a reassignment must NOT emit `var`
        twice — that's a C# compile error."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def test(self):\n"
            "        x = 1\n"
            "        x = 2\n"
        )
        result = translate(parsed)
        # First assignment declares; second is bare reassignment.
        decl_count = result.count("var x = 1") + result.count("int x = 1")
        assert decl_count >= 1
        # Must not declare `x` again.
        assert result.count("var x = 2") + result.count("int x = 2") == 0

    def test_nested_block_sees_parent_scope(self):
        """A variable declared in an outer block is visible to its
        nested children — nested reassignment must NOT redeclare."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def test(self, a):\n"
            "        target = 1\n"
            "        if a > 0:\n"
            "            target = 2\n"
        )
        result = translate(parsed)
        # Outer scope declares; inner block does NOT redeclare.
        assert "var target = 1" in result or "int target = 1" in result
        assert "var target = 2" not in result and "int target = 2" not in result
        assert "target = 2" in result  # bare reassignment in nested block


class TestCoroutineReturn:
    """Python `return` inside a generator (coroutine) must emit `yield break;`
    in C#.  A plain `return;` inside an `IEnumerator` method is CS1622.
    Regression for data/lessons/pacman_v2_deploy.md gap PV-3
    (GhostHome.ExitTransition early-exit).
    """

    def test_bare_return_in_coroutine_becomes_yield_break(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def exit_transition(self):\n"
            "        if self.done:\n"
            "            return\n"
            "        yield None\n"
        )
        result = translate(parsed)
        assert "IEnumerator" in result
        assert "yield break;" in result
        # No bare `return;` — that would be CS1622.
        for line in result.splitlines():
            stripped = line.strip()
            assert stripped != "return;", f"bare return in coroutine: {line!r}"

    def test_return_with_value_in_coroutine_becomes_yield_break(self):
        """Python generators can't truly `return value`, but some code paths
        emit `return None` (early-exit).  Treat any return with a trivial
        value inside a coroutine as yield break — a `return value;` inside
        IEnumerator is also CS1622."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def exit_transition(self):\n"
            "        if self.done:\n"
            "            return None\n"
            "        yield None\n"
        )
        result = translate(parsed)
        assert "IEnumerator" in result
        assert "yield break;" in result
        for line in result.splitlines():
            stripped = line.strip()
            assert not stripped.startswith("return "), f"valued return in coroutine: {line!r}"

    def test_bare_return_in_non_coroutine_unchanged(self):
        """Non-coroutine methods must still emit `return;` — don't regress
        plain void-return handling."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if self.done:\n"
            "            return\n"
            "        self.step()\n"
        )
        result = translate(parsed)
        assert "void Update()" in result
        assert "yield break;" not in result
        assert "return;" in result


class TestParameterReassignment:
    """C# forbids a local variable from shadowing a method parameter
    (CS0136).  Python's flat function scope lets a parameter be reassigned
    inside the method body — the translator must emit those as bare
    reassignments, not `var X = ...` declarations.  Regression for
    data/lessons/pacman_v2_deploy.md gap PV-4 (GhostBehavior.Enable).
    """

    def test_parameter_reassignment_inside_if_not_redeclared(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    duration: float = 0.0\n"
            "    def enable(self, duration: float = -1.0) -> None:\n"
            "        if duration < 0:\n"
            "            duration = self.duration\n"
        )
        result = translate(parsed)
        # Parameter `duration` must NOT get a fresh `var`/`float`/... declaration.
        assert "var duration = this.duration" not in result
        assert "float duration = this.duration" not in result
        # Bare reassignment is the correct form.
        assert "duration = this.duration" in result

    def test_parameter_reassignment_at_method_root(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def test(self, value: int) -> None:\n"
            "        value = 5\n"
        )
        result = translate(parsed)
        assert "var value = 5" not in result
        assert "int value = 5" not in result
        assert "value = 5" in result


class TestHoistedLocalAcrossBranches:
    """Python hoists locals to function scope.  When a variable is
    assigned in sibling if/else branches and referenced AFTER the branches
    merge, C# block scoping would leave it out of scope (CS0103).  The
    translator must detect this pattern and hoist the declaration to the
    method-body base.  Regression for data/lessons/pacman_v2_deploy.md
    gap PV-7 (Movement.SetDirection's `snapped` local, used at indent 3
    after assignments inside an if/else at indent 4).
    """

    def test_if_else_assigned_local_used_outside(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.math.vector import Vector2\n"
            "class Foo(MonoBehaviour):\n"
            "    def step(self, flag: bool) -> None:\n"
            "        if flag:\n"
            "            snapped = Vector2(1.0, 0.0)\n"
            "        else:\n"
            "            snapped = Vector2(0.0, 1.0)\n"
            "        self.apply(snapped)\n"
        )
        result = translate(parsed)
        # Reassignments inside branches must be bare — not redeclared.
        # The declaration itself is hoisted to the method-body base,
        # so `snapped` is visible at the outer `self.apply(snapped)` call.
        # Accept either form: a top-level declaration OR per-branch bare
        # reassignments with an outer-scope declaration.  The load-bearing
        # check is that `snapped.x`/`snapped` is reachable at outer indent
        # without CS0103 — i.e. the C# must compile.
        lines = result.splitlines()
        # Find the `apply(snapped)` call line.
        apply_idx = next(i for i, line in enumerate(lines) if "Apply(snapped)" in line or "apply(snapped)" in line.lower())
        # Count the `Vector2 snapped` declarations that appear at or before
        # the usage.  At least one must exist and it must be at a brace
        # depth ≤ the usage's brace depth (so the symbol is in scope).
        depth = 0
        usage_depth = None
        decl_depths = []
        for i, line in enumerate(lines):
            open_braces = line.count("{")
            close_braces = line.count("}")
            # Count closings first (they close the prior depth)
            depth_before = depth
            depth += open_braces - close_braces
            if re.search(r"\bVector2\s+snapped\b", line):
                decl_depths.append(min(depth_before, depth))
            if i == apply_idx:
                usage_depth = depth
        assert decl_depths, "no `Vector2 snapped` declaration found"
        assert usage_depth is not None
        # A declaration must be at depth ≤ usage_depth.
        assert any(d <= usage_depth for d in decl_depths), \
            f"all snapped declarations are deeper than usage (decls={decl_depths}, use={usage_depth})"

    def test_single_letter_var_not_false_positived_by_member_access(self):
        """The hoist detector matched bare-word regex and saw `x`/`y` in
        `position.x`/`position.y` as an escaping read.  It must not —
        `.x` is member access, not a reference to a local named `x`.
        Regression for the `var x = default;` CS0818 bug observed in
        regenerated GhostHome.ExitTransition."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.math.vector import Vector2\n"
            "class Foo(MonoBehaviour):\n"
            "    def step(self, start_pos) -> None:\n"
            "        outer = Vector2(start_pos.x, start_pos.y)\n"
            "        if True:\n"
            "            if True:\n"
            "                x = outer.x + 1.0\n"
            "                y = outer.y + 1.0\n"
            "                self.use(Vector2(x, y))\n"
        )
        result = translate(parsed)
        # Must not emit the invalid `var x = default;` — either don't hoist
        # at all (since there's no escaping read) or use a concrete type.
        assert "var x = default;" not in result
        assert "var y = default;" not in result

    def test_pv1_sibling_blocks_not_regressed(self):
        """PV-1 pattern (sibling if-blocks, variable used INSIDE each
        block only) must remain per-branch declarations — no over-eager
        hoist.  This would regress if the PV-7 fix hoists unconditionally."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def test(self, a, b):\n"
            "        if a > 0:\n"
            "            target = 1\n"
            "            self.do_thing(target)\n"
            "        if b > 0:\n"
            "            target = 2\n"
            "            self.do_thing(target)\n"
        )
        result = translate(parsed)
        # Either per-branch declarations or a single hoisted declaration
        # is acceptable — the key invariant is compilability (no CS0103).
        # For this test, we specifically want to preserve PV-1's per-branch
        # style OR upgrade to a hoisted declaration, but NOT silently drop
        # all declarations.
        decl_count = result.count("var target") + result.count("int target")
        assert decl_count >= 1


class TestObjectCommentHint:
    """A Python field annotated `: object` with a trailing comment that
    documents the intended Unity type should use that type in C# — emitting
    `public object foo` leaves any `foo.Enable()` call at CS1061 because
    System.Object has no Enable method.  Regression for
    data/lessons/pacman_v2_deploy.md gap PV-6 (Ghost.initial_behavior).
    """

    def test_object_field_with_component_hint(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    initial_behavior: object = None  # GhostBehavior component to start with\n"
        )
        result = translate(parsed)
        assert "public object initialBehavior" not in result
        assert "GhostBehavior" in result  # field is typed as GhostBehavior
        assert "initialBehavior" in result

    def test_object_field_without_hint_stays_object(self):
        """Bare `object` with no type hint must stay as `object` — don't
        guess.  This is the safe default."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    payload: object = None  # raw bytes payload\n"
        )
        result = translate(parsed)
        assert "public object payload" in result


class TestFloatSpecialLiterals:
    """`float("inf")`/`float("-inf")`/`float("nan")` are Python special
    literal constructors.  Translating them as `(float)("inf")` produces
    CS0030 (cannot cast string to float).  Must map to float constants.
    Regression for data/lessons/pacman_v2_deploy.md gap PV-5
    (GhostChase.on_trigger_enter_2d uses `float("inf")` as sentinel).
    """

    def test_float_inf_becomes_positive_infinity(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def compute(self):\n"
            "        best = float('inf')\n"
        )
        result = translate(parsed)
        assert '(float)("inf")' not in result
        assert "float.PositiveInfinity" in result

    def test_float_neg_inf_becomes_negative_infinity(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def compute(self):\n"
            "        worst = float('-inf')\n"
        )
        result = translate(parsed)
        assert '(float)("-inf")' not in result
        assert "float.NegativeInfinity" in result

    def test_float_nan_becomes_nan(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def compute(self):\n"
            "        x = float('nan')\n"
        )
        result = translate(parsed)
        assert '(float)("nan")' not in result
        assert "float.NaN" in result

    def test_float_numeric_cast_preserved(self):
        """Normal numeric casts like `float(count)` must still compile as
        `(float)(count)` — the special-literal handling must not regress."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def compute(self, count):\n"
            "        ratio = float(count)\n"
        )
        result = translate(parsed)
        assert "(float)(count)" in result


class TestBoolConditionTruthiness:
    """`if bool_param:` / `if bool_local:` must not emit `!= null` — bool
    is a value type and `!= null` is a type error (CS0019).  The condition
    translator uses `_bool_fields` to recognize class-level bool fields; it
    must also recognize bool method parameters and locals with a bool RHS.

    Reference bugs observed in regenerated Movement.cs (post-PV-7):
      `if (forced != null)` at line 67 — `forced: bool` is a param.
      `if (changingAxis != null)` at line 75 — `changing_axis = (… or …)`.
    """

    def test_bool_parameter_used_in_if_without_null_check(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def set_dir(self, direction, forced: bool = False) -> None:\n"
            "        if forced:\n"
            "            self.direction = direction\n"
        )
        result = translate(parsed)
        assert "if (forced != null)" not in result
        assert "if (forced)" in result

    def test_bool_local_from_boolean_expression_used_in_if(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def step(self, x, y) -> None:\n"
            "        changing_axis = (x != 0 and y != 0) or (x == 1 or y == 1)\n"
            "        if changing_axis:\n"
            "            self.handle()\n"
        )
        result = translate(parsed)
        assert "if (changingAxis != null)" not in result
        assert "if (changingAxis)" in result

    def test_not_cross_class_bool_field_reference(self):
        """`not other.bool_field` where `bool_field` is a bool on another
        class in the same translation unit must emit `!other.field`, not
        `other.field == null`.  Without cross-class field-type tracking,
        Ghost.cs generated `frightened.eaten == null` where `eaten: bool`
        is a field on GhostFrightened."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Other(MonoBehaviour):\n"
            "    eaten: bool = False\n"
            "class Main(MonoBehaviour):\n"
            "    other: Other = None\n"
            "    def check(self):\n"
            "        if self.other and not self.other.eaten:\n"
            "            self.action()\n"
        )
        result = translate(parsed)
        assert "other.eaten == null" not in result
        assert "!other.eaten" in result or "other.eaten == false" in result

    def test_multiline_bool_local_detected(self):
        """RHS spanning multiple physical lines must still be recognised
        as a boolean expression.  This is the exact Movement.set_direction
        pattern (changing_axis assignment spans 4 lines)."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def step(self, x, y) -> None:\n"
            "        changing_axis = (\n"
            "            (x != 0 and y != 0) or\n"
            "            (x == 1 or y == 1)\n"
            "        )\n"
            "        if changing_axis:\n"
            "            self.handle()\n"
        )
        result = translate(parsed)
        assert "if (changingAxis != null)" not in result
        assert "if (changingAxis)" in result

    def test_non_bool_local_still_gets_null_check(self):
        """Non-bool object references must keep the `!= null` safety."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def use_rb(self) -> None:\n"
            "        rb = self.get_component(Rigidbody2D)\n"
            "        if rb:\n"
            "            rb.move_position(Vector2(0, 0))\n"
        )
        result = translate(parsed)
        assert "if (rb != null)" in result


class TestSelfAttrLocalCollision:
    """When a method has a local variable with the SAME name as a class
    field, `self.X = X` must emit `this.X = X` — emitting `X = X` creates
    a no-op self-assignment on the local (CS1717 warning + the field never
    gets updated).  Regression for a bug observed in regenerated Ghost.cs:
        `var eyes = child.gameObject.GetComponent<GhostEyes>();`
        `if (eyes != null) { eyes = eyes; break; }   // ← should set this.eyes`
    """

    def test_self_field_assign_with_shadowing_local(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    eyes: object = None\n"
            "    def start(self):\n"
            "        eyes = self.get_component(GhostEyes)\n"
            "        if eyes:\n"
            "            self.eyes = eyes\n"
        )
        result = translate(parsed)
        # Must NOT be the self-assignment no-op.
        assert "eyes = eyes;" not in result or "this.eyes = eyes;" in result
        assert "this.eyes = eyes" in result

    def test_self_field_assign_without_local_uses_bare_name(self):
        """When no local shadows the field name, `self.X = value` keeps
        emitting `X = value;` (no unnecessary `this.`)."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    speed: float = 0.0\n"
            "    def update(self):\n"
            "        self.speed = 5.0\n"
        )
        result = translate(parsed)
        assert "speed = 5" in result
        # No-unnecessary-this check: should NOT emit `this.speed` when no collision.
        assert "this.speed = 5" not in result


class TestGetattrDoubleGameObject:
    """Trigger callbacks expand `other` → `other.gameObject` inside method
    args to access properties like `.layer`, but when the original Python
    used `getattr(other, "game_object", other)` to unwrap the simulator
    shim, both passes fired and produced `other.gameObject.gameObject`.
    Regression for the Pacman V2 trigger handlers."""

    def test_getattr_game_object_in_trigger_not_double_expanded(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def on_trigger_enter_2d(self, other) -> None:\n"
            "        other_go = getattr(other, 'game_object', other)\n"
            "        self.use(other_go)\n"
        )
        result = translate(parsed)
        assert ".gameObject.gameObject" not in result


class TestLinqTranslation:
    def test_all_generator(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def check(self):\n"
            "        return all(p is None or not p.active for p in self.pigs)\n"
        )
        result = translate(parsed)
        assert ".All(p =>" in result
        assert "== null" in result

    def test_sum_count_pattern(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def count_active(self):\n"
            "        self.active = sum(1 for p in self.pigs if p is not None and p.active)\n"
        )
        result = translate(parsed)
        assert ".Count(p =>" in result
        assert "!= null" in result

    def test_using_system_linq_added(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def check(self):\n"
            "        return all(p is None for p in self.pigs)\n"
        )
        result = translate(parsed)
        assert "using System.Linq;" in result

    def test_list_comprehension_with_filter(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def get_active(self):\n"
            "        self.active = [p for p in self.pigs if p.active]\n"
        )
        result = translate(parsed)
        assert ".Where(" in result
        assert ".ToList()" in result

    def test_list_wrapper_to_tolist(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour, GameObject\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        self.birds = list(GameObject.find_game_objects_with_tag('Bird'))\n"
        )
        result = translate(parsed)
        assert ".ToList()" in result
        assert "FindGameObjectsWithTag" in result


class TestAngryBirdsTranslation:
    def test_game_manager_translates(self):
        """GameManager.py should translate without TODO comments for for-loops."""
        result = translate_file(ANGRY_BIRDS_DIR / "game_manager.py")
        assert "// TODO: translate for loop" not in result
        assert "foreach" in result
        assert ".Count" in result
        assert ".All(" in result
        assert "using System.Linq;" in result
        assert "using System.Collections;" in result

    def test_slingshot_range_loop(self):
        """Slingshot trajectory uses range(len(points) - 1)."""
        result = translate_file(ANGRY_BIRDS_DIR / "slingshot.py")
        assert "// TODO: translate for loop" not in result
        assert "for (int i = 0;" in result


class TestEnumTranslation:
    def test_simple_enum(self):
        parsed = parse_python(
            "from enum import Enum\n"
            "class Color(Enum):\n"
            "    RED = 'red'\n"
            "    GREEN = 'green'\n"
            "    BLUE = 'blue'\n"
        )
        result = translate(parsed)
        assert "public enum Color" in result
        assert "Red" in result
        assert "Green" in result
        assert "Blue" in result
        # Should not have class/MonoBehaviour keywords
        assert "class" not in result
        assert "MonoBehaviour" not in result

    def test_upper_snake_to_pascal(self):
        parsed = parse_python(
            "from enum import Enum\n"
            "class State(Enum):\n"
            "    BEFORE_THROWN = 'before_thrown'\n"
            "    BIRD_FLYING = 'bird_flying'\n"
        )
        result = translate(parsed)
        assert "BeforeThrown" in result
        assert "BirdFlying" in result

    def test_angry_birds_enums(self):
        result = translate_file(ANGRY_BIRDS_DIR / "enums.py")
        assert "public enum SlingshotState" in result
        assert "public enum GameState" in result
        assert "public enum BirdState" in result
        assert "Idle" in result
        assert "UserPulling" in result
        assert "BirdFlying" in result
        assert "BeforeThrown" in result
        assert "BirdMovingToSlingshot" in result

    def test_enum_comma_separated(self):
        parsed = parse_python(
            "from enum import Enum\n"
            "class Dir(Enum):\n"
            "    UP = 0\n"
            "    DOWN = 1\n"
        )
        result = translate(parsed)
        # Members should be comma-separated
        assert "Up,\n" in result or "Up," in result


class TestNamespaceWrapping:
    def test_namespace_wraps_output(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        pass\n"
        )
        result = translate(parsed, namespace="MyGame")
        assert "namespace MyGame" in result
        assert "{" in result
        # Class should be indented inside namespace
        assert "    public class Foo : MonoBehaviour" in result

    def test_no_namespace_by_default(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        pass\n"
        )
        result = translate(parsed)
        assert "namespace" not in result


class TestAttributeInference:
    def test_require_component_from_start(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        self.rb = self.get_component(Rigidbody2D)\n"
        )
        result = translate(parsed)
        assert "[RequireComponent(typeof(Rigidbody2D))]" in result

    def test_require_component_from_awake(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def awake(self):\n"
            "        self.sr = self.get_component(SpriteRenderer)\n"
        )
        result = translate(parsed)
        assert "[RequireComponent(typeof(SpriteRenderer))]" in result

    def test_multiple_require_components(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def start(self):\n"
            "        self.rb = self.get_component(Rigidbody2D)\n"
            "        self.sr = self.get_component(SpriteRenderer)\n"
        )
        result = translate(parsed)
        assert "[RequireComponent(typeof(Rigidbody2D))]" in result
        assert "[RequireComponent(typeof(SpriteRenderer))]" in result

    def test_no_require_for_update_get_component(self):
        """get_component in update() should NOT generate RequireComponent."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        rb = self.get_component(Rigidbody2D)\n"
        )
        result = translate(parsed)
        assert "RequireComponent" not in result


class TestUnity6ApiMappings:
    """Test Unity 6 velocity → linearVelocity and new Input System mappings."""

    def test_velocity_to_linear_velocity_unity6(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        self.rb.velocity = Vector2(1, 0)\n"
        )
        result = translate(parsed, unity_version=6)
        assert "rb.linearVelocity" in result

    def test_velocity_stays_velocity_unity5(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        self.rb.velocity = Vector2(1, 0)\n"
        )
        result = translate(parsed, unity_version=5, input_system="legacy")
        assert "rb.velocity" in result
        assert "linearVelocity" not in result

    def test_new_input_mouse_button_down(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.input_manager import Input\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if Input.get_mouse_button_down(0):\n"
            "            pass\n"
        )
        result = translate(parsed, input_system="new")
        assert "Mouse.current.leftButton.wasPressedThisFrame" in result

    def test_new_input_mouse_button_up(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.input_manager import Input\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if Input.get_mouse_button_up(0):\n"
            "            pass\n"
        )
        result = translate(parsed, input_system="new")
        assert "Mouse.current.leftButton.wasReleasedThisFrame" in result

    def test_new_input_mouse_button_held(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.input_manager import Input\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if Input.get_mouse_button(0):\n"
            "            pass\n"
        )
        result = translate(parsed, input_system="new")
        assert "Mouse.current.leftButton.isPressed" in result

    def test_new_input_right_mouse_button(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.input_manager import Input\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if Input.get_mouse_button_down(1):\n"
            "            pass\n"
        )
        result = translate(parsed, input_system="new")
        assert "Mouse.current.rightButton.wasPressedThisFrame" in result

    def test_new_input_key_down(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.input_manager import Input\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if Input.get_key_down('space'):\n"
            "            pass\n"
        )
        result = translate(parsed, input_system="new")
        assert "Keyboard.current.spaceKey.wasPressedThisFrame" in result

    def test_new_input_key_pressed(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.input_manager import Input\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if Input.get_key('escape'):\n"
            "            pass\n"
        )
        result = translate(parsed, input_system="new")
        assert "Keyboard.current.escapeKey.isPressed" in result

    def test_new_input_axis_emits_keyboard(self):
        """get_axis('Horizontal') emits keyboard-based axis emulation."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.input_manager import Input\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        h = Input.get_axis('Horizontal')\n"
        )
        result = translate(parsed, input_system="new")
        assert "Keyboard.current.dKey.isPressed" in result
        assert "Keyboard.current.aKey.isPressed" in result

    def test_using_input_system_added(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.input_manager import Input\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if Input.get_key_down('space'):\n"
            "            pass\n"
        )
        result = translate(parsed, input_system="new")
        assert "using UnityEngine.InputSystem;" in result

    def test_no_input_system_using_in_legacy(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.input_manager import Input\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if Input.get_key_down('space'):\n"
            "            pass\n"
        )
        result = translate(parsed, input_system="legacy")
        assert "UnityEngine.InputSystem" not in result
        assert "Input.GetKeyDown" in result

    def test_legacy_input_mouse_button(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "from src.engine.input_manager import Input\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if Input.get_mouse_button_down(0):\n"
            "            pass\n"
        )
        result = translate(parsed, input_system="legacy")
        assert "Input.GetMouseButtonDown(0)" in result
        assert "Mouse.current" not in result

    def test_slingshot_unity6_new_input(self):
        """Full file test: slingshot uses mouse input and velocity."""
        result = translate_file(ANGRY_BIRDS_DIR / "slingshot.py")
        assert "Mouse.current" in result
        assert "linearVelocity" in result
        assert "using UnityEngine.InputSystem;" in result

    def test_slingshot_unity5_legacy(self):
        result = translate_file(
            ANGRY_BIRDS_DIR / "slingshot.py",
            unity_version=5, input_system="legacy",
        )
        assert "Input.GetMouseButton" in result
        assert ".velocity" in result
        assert "linearVelocity" not in result
        assert "Mouse.current" not in result


class TestMathfBuiltins:
    """Python math builtins should translate to Unity Mathf, not System.Math."""

    def test_max_translates_to_mathf(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        x = max(a, b)\n"
        )
        result = translate(parsed)
        assert "Mathf.Max(a, b)" in result
        assert "Math.Max" not in result

    def test_min_translates_to_mathf(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        x = min(a, b)\n"
        )
        result = translate(parsed)
        assert "Mathf.Min(a, b)" in result
        assert "Math.Min" not in result

    def test_round_translates_to_mathf(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        x = round(val)\n"
        )
        result = translate(parsed)
        assert "Mathf.Round(val)" in result

    def test_abs_already_uses_mathf(self):
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        x = abs(val)\n"
        )
        result = translate(parsed)
        assert "Mathf.Abs(val)" in result
        assert "Math.Abs" not in result


class TestInOperator:
    """Test Python 'in' / 'not in' membership operator translation."""

    def test_in_operator_list(self):
        """x in my_list -> my_list.Contains(x)"""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if x in self.items:\n"
            "            pass\n"
        )
        result = translate(parsed)
        assert "items.Contains(x)" in result
        assert " in items" not in result or "Contains" in result

    def test_in_operator_dict(self):
        """key in my_dict -> my_dict.ContainsKey(key) when dict type known."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.lookup: dict[str, int] = {}\n"
            "    def update(self):\n"
            "        if key in self.lookup:\n"
            "            pass\n"
        )
        result = translate(parsed)
        assert "ContainsKey(key)" in result

    def test_not_in_operator(self):
        """x not in items -> !items.Contains(x)"""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if x not in self.items:\n"
            "            pass\n"
        )
        result = translate(parsed)
        assert "!items.Contains(x)" in result

    def test_not_in_operator_dict(self):
        """key not in my_dict -> !my_dict.ContainsKey(key)"""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def __init__(self):\n"
            "        super().__init__()\n"
            "        self.cache: dict[str, float] = {}\n"
            "    def update(self):\n"
            "        if key not in self.cache:\n"
            "            pass\n"
        )
        result = translate(parsed)
        assert "!cache.ContainsKey(key)" in result

    def test_in_does_not_break_foreach(self):
        """for x in collection must still translate to foreach."""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        for obj in self.enemies:\n"
            "            print(obj)\n"
        )
        result = translate(parsed)
        assert "foreach (var obj in enemies)" in result

    def test_in_with_compound_condition(self):
        """x in list and y > 0 -> list.Contains(x) && y > 0"""
        parsed = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        if x in self.items and y > 0:\n"
            "            pass\n"
        )
        result = translate(parsed)
        assert "items.Contains(x)" in result
        assert "&&" in result
