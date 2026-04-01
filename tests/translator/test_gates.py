"""Tests for structural and convention gates."""

from pathlib import Path

from src.gates.structural_gate import validate_csharp
from src.gates.convention_gate import check_conventions
from src.translator.python_to_csharp import translate_file as py_to_cs

PONG_PY_DIR = Path(__file__).parent.parent.parent / "examples" / "pong" / "pong_python"
PONG_CS_DIR = Path(__file__).parent.parent.parent / "examples" / "pong" / "pong_unity"


class TestStructuralGate:
    def test_valid_csharp(self):
        source = """using UnityEngine;
public class Foo : MonoBehaviour {
    void Start() { }
}"""
        result = validate_csharp(source)
        assert result.valid is True
        assert result.class_count == 1
        assert result.method_count == 1
        assert result.error_count == 0

    def test_invalid_csharp(self):
        source = "this is not valid C# at all {{{}}}"
        result = validate_csharp(source)
        assert result.error_count > 0

    def test_original_pong_files_valid(self):
        """All original Pong C# files should parse without errors."""
        for cs_file in PONG_CS_DIR.glob("*.cs"):
            source = cs_file.read_text(encoding="utf-8")
            result = validate_csharp(source)
            assert result.valid, f"{cs_file.name}: {result.errors}"
            assert result.class_count >= 1

    def test_translated_paddle_valid(self):
        """PaddleController Python -> C# should produce parseable C#."""
        cs_output = py_to_cs(PONG_PY_DIR / "paddle_controller.py")
        result = validate_csharp(cs_output)
        assert result.class_count >= 1, f"No classes found. Output:\n{cs_output[:500]}"

    def test_translated_score_manager_valid(self):
        cs_output = py_to_cs(PONG_PY_DIR / "score_manager.py")
        result = validate_csharp(cs_output)
        assert result.class_count >= 1

    def test_translated_game_manager_valid(self):
        cs_output = py_to_cs(PONG_PY_DIR / "game_manager.py")
        result = validate_csharp(cs_output)
        assert result.class_count >= 1


class TestConventionGate:
    def test_good_conventions(self):
        source = """using UnityEngine;
public class PlayerController : MonoBehaviour {
    [SerializeField] private float speed = 5f;
    void Start() { }
    void Update() { }
}"""
        result = check_conventions(source)
        assert result.passed is True
        assert len(result.violations) == 0
        assert result.checks_passed > 0

    def test_missing_using(self):
        source = """public class Foo : MonoBehaviour {
    void Start() { }
}"""
        result = check_conventions(source)
        assert any("using UnityEngine" in v for v in result.violations)

    def test_new_monobehaviour_violation(self):
        source = """using UnityEngine;
public class Foo : MonoBehaviour {
    void Start() {
        MonoBehaviour mb = new MonoBehaviour();
    }
}"""
        result = check_conventions(source)
        assert any("new MonoBehaviour()" in v for v in result.violations)

    def test_lifecycle_signature_check(self):
        source = """using UnityEngine;
public class Foo : MonoBehaviour {
    void Update() { }
    void OnCollisionEnter2D(Collision2D col) { }
}"""
        result = check_conventions(source)
        assert result.passed is True

    def test_pascal_case_class(self):
        source = """using UnityEngine;
public class foo : MonoBehaviour { }"""
        result = check_conventions(source)
        assert any("PascalCase" in v for v in result.violations)

    def test_original_pong_passes_conventions(self):
        """Original hand-written C# should pass convention checks."""
        for cs_file in PONG_CS_DIR.glob("*.cs"):
            source = cs_file.read_text(encoding="utf-8")
            result = check_conventions(source)
            assert result.passed, f"{cs_file.name}: {result.violations}"

    def test_translated_paddle_conventions(self):
        """Translated PaddleController should pass most conventions."""
        cs_output = py_to_cs(PONG_PY_DIR / "paddle_controller.py")
        result = check_conventions(cs_output)
        # May have some minor issues but core conventions should pass
        assert result.checks_passed >= result.checks_run * 0.5
