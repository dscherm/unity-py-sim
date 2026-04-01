"""Tests for Python parser — verify IR extracted from Pong Python files."""

from pathlib import Path
from src.translator.python_parser import parse_python, parse_python_file

PONG_DIR = Path(__file__).parent.parent.parent / "examples" / "pong" / "pong_python"


class TestPythonParserBasic:
    def test_simple_class(self):
        result = parse_python("class Foo:\n    pass")
        assert len(result.classes) == 1
        assert result.classes[0].name == "Foo"

    def test_monobehaviour_detection(self):
        result = parse_python(
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n    pass"
        )
        assert result.classes[0].is_monobehaviour is True

    def test_class_level_field(self):
        result = parse_python("class Foo:\n    count: int = 0")
        cls = result.classes[0]
        assert len(cls.fields) == 1
        assert cls.fields[0].name == "count"
        assert cls.fields[0].type_annotation == "int"
        assert cls.fields[0].default_value == "0"
        assert cls.fields[0].is_class_level is True

    def test_init_fields(self):
        result = parse_python(
            "class Foo:\n"
            "    def __init__(self):\n"
            "        self.speed: float = 5.0\n"
            "        self.name: str = 'test'\n"
        )
        cls = result.classes[0]
        assert len(cls.fields) == 2
        assert cls.fields[0].name == "speed"
        assert cls.fields[0].type_annotation == "float"
        assert cls.fields[0].default_value == "5.0"
        assert cls.fields[0].is_class_level is False

    def test_method_extraction(self):
        result = parse_python(
            "class Foo:\n"
            "    def update(self):\n"
            "        x = 1\n"
        )
        cls = result.classes[0]
        assert len(cls.methods) == 1
        assert cls.methods[0].name == "update"
        assert cls.methods[0].is_lifecycle is True

    def test_static_method(self):
        result = parse_python(
            "class Foo:\n"
            "    @staticmethod\n"
            "    def do_thing():\n"
            "        pass\n"
        )
        m = result.classes[0].methods[0]
        assert m.is_static is True
        assert m.name == "do_thing"

    def test_method_parameters(self):
        result = parse_python(
            "class Foo:\n"
            "    def on_collision_enter_2d(self, collision):\n"
            "        pass\n"
        )
        m = result.classes[0].methods[0]
        assert len(m.parameters) == 1
        assert m.parameters[0].name == "collision"
        assert m.is_lifecycle is True

    def test_imports(self):
        result = parse_python(
            "import random\n"
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n    pass"
        )
        assert len(result.imports) == 2
        assert any("random" in i for i in result.imports)
        assert any("MonoBehaviour" in i for i in result.imports)


class TestPongParsing:
    def test_parse_paddle_controller(self):
        result = parse_python_file(PONG_DIR / "paddle_controller.py")
        assert len(result.classes) == 1
        cls = result.classes[0]
        assert cls.name == "PaddleController"
        assert cls.is_monobehaviour is True

        field_names = [f.name for f in cls.fields]
        assert "speed" in field_names
        assert "bound_y" in field_names
        assert "input_axis" in field_names

        method_names = [m.name for m in cls.methods]
        assert "start" in method_names
        assert "update" in method_names

    def test_parse_ball_controller(self):
        result = parse_python_file(PONG_DIR / "ball_controller.py")
        cls = result.classes[0]
        assert cls.name == "BallController"
        assert cls.is_monobehaviour is True

        field_names = [f.name for f in cls.fields]
        assert "initial_speed" in field_names
        assert "speed_increase" in field_names

        method_names = [m.name for m in cls.methods]
        assert "start" in method_names
        assert "launch" in method_names
        assert "reset" in method_names
        assert "on_collision_enter_2d" in method_names

    def test_parse_score_manager(self):
        result = parse_python_file(PONG_DIR / "score_manager.py")
        cls = result.classes[0]
        assert cls.name == "ScoreManager"

        # Class-level fields
        class_fields = [f for f in cls.fields if f.is_class_level]
        field_names = [f.name for f in class_fields]
        assert "score_left" in field_names
        assert "score_right" in field_names
        assert "win_score" in field_names

        # Static methods
        method_names = [m.name for m in cls.methods]
        assert "add_score_left" in method_names
        static_methods = [m for m in cls.methods if m.is_static]
        assert len(static_methods) >= 3

    def test_parse_game_manager(self):
        result = parse_python_file(PONG_DIR / "game_manager.py")
        cls = result.classes[0]
        assert cls.name == "GameManager"

        field_names = [f.name for f in cls.fields]
        assert "reset_delay" in field_names
        assert "ball" in field_names

        method_names = [m.name for m in cls.methods]
        assert "start" in method_names
        assert "update" in method_names
        assert "on_goal_scored" in method_names
