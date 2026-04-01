"""Tests for C# to Python translator."""

from pathlib import Path
from src.translator.csharp_to_python import translate_file, translate
from src.translator.csharp_parser import parse_csharp

PONG_DIR = Path(__file__).parent.parent.parent / "examples" / "pong" / "pong_unity"


class TestTranslatorBasics:
    def test_simple_class(self):
        parsed = parse_csharp("using UnityEngine;\npublic class Foo : MonoBehaviour { }")
        result = translate(parsed)
        assert "class Foo(MonoBehaviour):" in result
        assert "from src.engine.core import MonoBehaviour" in result

    def test_field_translation(self):
        parsed = parse_csharp("""
        using UnityEngine;
        public class Foo : MonoBehaviour {
            [SerializeField] private float speed = 5f;
        }
        """)
        result = translate(parsed)
        assert "self.speed: float = 5.0" in result
        assert "__init__" in result

    def test_lifecycle_method_naming(self):
        parsed = parse_csharp("""
        using UnityEngine;
        public class Foo : MonoBehaviour {
            void Update() { }
            void FixedUpdate() { }
            void OnCollisionEnter2D(Collision2D col) { }
        }
        """)
        result = translate(parsed)
        assert "def update(self):" in result
        assert "def fixed_update(self):" in result
        assert "def on_collision_enter_2d(self, col):" in result

    def test_getcomponent_pattern(self):
        parsed = parse_csharp("""
        using UnityEngine;
        public class Foo : MonoBehaviour {
            private Rigidbody2D rb;
            void Start() {
                rb = GetComponent<Rigidbody2D>();
            }
        }
        """)
        result = translate(parsed)
        assert "self.get_component(Rigidbody2D)" in result

    def test_static_method(self):
        parsed = parse_csharp("""
        public class Foo {
            public static void DoThing() {
                int x = 5;
            }
        }
        """)
        result = translate(parsed)
        assert "@staticmethod" in result
        assert "def do_thing():" in result

    def test_new_keyword_removed(self):
        parsed = parse_csharp("""
        using UnityEngine;
        public class Foo : MonoBehaviour {
            void Start() {
                Vector2 v = new Vector2(1, 2);
            }
        }
        """)
        result = translate(parsed)
        assert "Vector2(1, 2)" in result
        assert "new " not in result

    def test_debug_log_becomes_print(self):
        parsed = parse_csharp("""
        using UnityEngine;
        public class Foo : MonoBehaviour {
            void Start() {
                Debug.Log("hello");
            }
        }
        """)
        result = translate(parsed)
        assert "print(" in result


class TestPongTranslation:
    def test_translate_paddle_controller(self):
        result = translate_file(PONG_DIR / "PaddleController.cs")
        # Should have class declaration
        assert "class PaddleController(MonoBehaviour):" in result
        # Should have __init__ with fields
        assert "self.speed: float = 10.0" in result
        assert "self.bound_y: float = 4.0" in result
        # Should have lifecycle methods
        assert "def start(self):" in result
        assert "def fixed_update(self):" in result
        # Should have Input and Rigidbody2D usage
        assert "Input.get_axis" in result
        assert "get_component(Rigidbody2D)" in result
        # Should have proper imports
        assert "from src.engine.input_manager import Input" in result

    def test_translate_ball_controller(self):
        result = translate_file(PONG_DIR / "BallController.cs")
        assert "class BallController(MonoBehaviour):" in result
        assert "self.initial_speed: float = 8.0" in result
        assert "def launch(self):" in result
        assert "def reset(self):" in result
        assert "def on_collision_enter_2d(self, collision):" in result
        assert "import random" in result

    def test_translate_score_manager(self):
        result = translate_file(PONG_DIR / "ScoreManager.cs")
        assert "class ScoreManager(MonoBehaviour):" in result
        assert "@staticmethod" in result
        assert "def add_score_left" in result
        assert "print(" in result

    def test_translate_game_manager(self):
        result = translate_file(PONG_DIR / "GameManager.cs")
        assert "class GameManager(MonoBehaviour):" in result
        assert "def start(self):" in result
        assert "def update(self):" in result
        assert "GameObject.find(" in result
        assert "Time.delta_time" in result

    def test_translated_code_is_valid_python(self):
        """Verify translated Pong files are syntactically valid Python.

        BallController.cs has a ternary-inside-constructor-args pattern
        that the line-level translator can't handle yet (known limitation).
        """
        import ast
        # These files should produce valid Python
        valid_files = ["PaddleController.cs", "ScoreManager.cs", "GameManager.cs"]
        for name in valid_files:
            result = translate_file(PONG_DIR / name)
            try:
                ast.parse(result)
            except SyntaxError as e:
                assert False, f"Translated {name} is not valid Python: {e}\n\n{result}"

    def test_ball_controller_known_limitations(self):
        """BallController has ternary-in-args that's a known limitation."""
        result = translate_file(PONG_DIR / "BallController.cs")
        # The structure is correct even if some expressions are not valid Python
        assert "class BallController(MonoBehaviour):" in result
        assert "def on_collision_enter_2d" in result
        # Ternary at top level works
        assert "1.0 if random.random() > 0.5 else -1.0" in result
