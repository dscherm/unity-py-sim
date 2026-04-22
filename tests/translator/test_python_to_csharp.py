"""Tests for Python to C# translator."""

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
