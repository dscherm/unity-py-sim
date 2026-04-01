"""Tests for C# parser — verify IR extracted from Pong C# files."""

from pathlib import Path
from src.translator.csharp_parser import parse_csharp, parse_csharp_file, CSharpFile

PONG_DIR = Path(__file__).parent.parent.parent / "examples" / "pong" / "pong_unity"


class TestCSharpParserBasic:
    def test_parse_simple_class(self):
        result = parse_csharp("public class Foo { }")
        assert len(result.classes) == 1
        assert result.classes[0].name == "Foo"

    def test_parse_using_directives(self):
        result = parse_csharp("using UnityEngine;\nusing System;\npublic class Foo { }")
        assert "UnityEngine" in result.using_directives
        assert "System" in result.using_directives

    def test_parse_base_class(self):
        result = parse_csharp("public class Foo : MonoBehaviour { }")
        cls = result.classes[0]
        assert "MonoBehaviour" in cls.base_classes
        assert cls.is_monobehaviour is True

    def test_parse_field(self):
        result = parse_csharp("public class Foo { private float speed = 5f; }")
        cls = result.classes[0]
        assert len(cls.fields) == 1
        assert cls.fields[0].name == "speed"
        assert cls.fields[0].type == "float"
        assert cls.fields[0].initializer == "5f"

    def test_parse_field_with_attribute(self):
        result = parse_csharp("public class Foo { [SerializeField] private float speed = 5f; }")
        f = result.classes[0].fields[0]
        assert "SerializeField" in f.attributes
        assert "private" in f.modifiers

    def test_parse_method(self):
        result = parse_csharp("public class Foo { void Update() { } }")
        cls = result.classes[0]
        assert len(cls.methods) == 1
        assert cls.methods[0].name == "Update"
        assert cls.methods[0].return_type == "void"
        assert cls.methods[0].is_lifecycle is True

    def test_parse_method_with_params(self):
        result = parse_csharp("public class Foo { void OnCollisionEnter2D(Collision2D col) { } }")
        m = result.classes[0].methods[0]
        assert m.name == "OnCollisionEnter2D"
        assert len(m.parameters) == 1
        assert m.parameters[0].type == "Collision2D"
        assert m.parameters[0].name == "col"

    def test_parse_static_method(self):
        result = parse_csharp("public class Foo { public static void DoThing() { } }")
        m = result.classes[0].methods[0]
        assert "static" in m.modifiers
        assert "public" in m.modifiers

    def test_method_body_captured(self):
        result = parse_csharp("public class Foo { void Start() { int x = 5; } }")
        m = result.classes[0].methods[0]
        assert "int x = 5" in m.body


class TestPongParsing:
    def test_parse_paddle_controller(self):
        result = parse_csharp_file(PONG_DIR / "PaddleController.cs")
        assert len(result.classes) == 1
        cls = result.classes[0]
        assert cls.name == "PaddleController"
        assert cls.is_monobehaviour is True
        assert "UnityEngine" in result.using_directives

        # Fields
        field_names = [f.name for f in cls.fields]
        assert "speed" in field_names
        assert "boundY" in field_names
        assert "inputAxis" in field_names
        assert "rb" in field_names

        # Methods
        method_names = [m.name for m in cls.methods]
        assert "Start" in method_names
        assert "FixedUpdate" in method_names

        # SerializeField attributes
        speed_field = next(f for f in cls.fields if f.name == "speed")
        assert "SerializeField" in speed_field.attributes

    def test_parse_ball_controller(self):
        result = parse_csharp_file(PONG_DIR / "BallController.cs")
        cls = result.classes[0]
        assert cls.name == "BallController"
        assert cls.is_monobehaviour is True

        field_names = [f.name for f in cls.fields]
        assert "initialSpeed" in field_names
        assert "speedIncrease" in field_names

        method_names = [m.name for m in cls.methods]
        assert "Start" in method_names
        assert "Launch" in method_names
        assert "Reset" in method_names
        assert "OnCollisionEnter2D" in method_names

        # OnCollisionEnter2D has a parameter
        ocol = next(m for m in cls.methods if m.name == "OnCollisionEnter2D")
        assert len(ocol.parameters) == 1
        assert ocol.parameters[0].type == "Collision2D"

    def test_parse_score_manager(self):
        result = parse_csharp_file(PONG_DIR / "ScoreManager.cs")
        cls = result.classes[0]
        assert cls.name == "ScoreManager"

        method_names = [m.name for m in cls.methods]
        assert "AddScoreLeft" in method_names
        assert "AddScoreRight" in method_names
        assert "ResetScores" in method_names

        # Static methods
        add_left = next(m for m in cls.methods if m.name == "AddScoreLeft")
        assert "static" in add_left.modifiers

    def test_parse_game_manager(self):
        result = parse_csharp_file(PONG_DIR / "GameManager.cs")
        cls = result.classes[0]
        assert cls.name == "GameManager"

        field_names = [f.name for f in cls.fields]
        assert "resetDelay" in field_names

        method_names = [m.name for m in cls.methods]
        assert "Start" in method_names
        assert "Update" in method_names
        assert "OnGoalScored" in method_names
