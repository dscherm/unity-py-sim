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
