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
        assert "[SerializeField] private float speed = 5f;" in result

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
        result = translate(parsed)
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
        assert "public static int count = 0;" in result

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
    def test_translate_paddle_controller(self):
        result = translate_file(PONG_DIR / "paddle_controller.py")
        assert "public class PaddleController : MonoBehaviour" in result
        assert "[SerializeField] private float speed = 10f;" in result
        assert "Start()" in result
        assert "Update()" in result
        assert "Input.GetAxis(" in result

    def test_translate_ball_controller(self):
        result = translate_file(PONG_DIR / "ball_controller.py")
        assert "public class BallController : MonoBehaviour" in result
        assert "[SerializeField] private float initialSpeed = 6f;" in result
        assert "Start()" in result
        assert "Launch()" in result
        assert "Reset()" in result
        assert "OnCollisionEnter2D(Collision2D collision)" in result

    def test_translate_score_manager(self):
        result = translate_file(PONG_DIR / "score_manager.py")
        assert "public class ScoreManager : MonoBehaviour" in result
        assert "public static int scoreLeft = 0;" in result
        assert "public static" in result
        assert "Debug.Log(" in result

    def test_translate_game_manager(self):
        result = translate_file(PONG_DIR / "game_manager.py")
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
            result = translate_file(py_file)
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
