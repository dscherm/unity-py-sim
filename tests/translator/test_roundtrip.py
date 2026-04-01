"""Tests for roundtrip translation: C# -> Python -> C# equivalence."""

from pathlib import Path

from src.gates.roundtrip_gate import score_roundtrip, score_roundtrip_file
from src.gates.accuracy_tracker import AccuracyScore, record_accuracy, record_roundtrip, load_scores

PONG_DIR = Path(__file__).parent.parent.parent / "examples" / "pong" / "pong_unity"
METRICS_DIR = Path(__file__).parent.parent.parent / "data" / "metrics"


class TestRoundtripScoring:
    def test_simple_roundtrip(self):
        source = """using UnityEngine;
public class Foo : MonoBehaviour {
    [SerializeField] private float speed = 5f;
    void Start() { }
    void Update() { }
}"""
        result = score_roundtrip(source, "Foo.cs")
        assert result.overall_score > 0.5
        assert result.original_class_count == 1
        assert result.roundtrip_class_count == 1

    def test_structural_score_class_preserved(self):
        source = """using UnityEngine;
public class Bar : MonoBehaviour {
    void Start() { }
    void Update() { }
    void FixedUpdate() { }
}"""
        result = score_roundtrip(source, "Bar.cs")
        assert result.structural_score >= 0.8
        # Class name and all lifecycle methods should survive
        assert "MISSING class" not in " ".join(result.details)

    def test_naming_score_lifecycle_methods(self):
        source = """using UnityEngine;
public class Baz : MonoBehaviour {
    void Awake() { }
    void Start() { }
    void Update() { }
    void OnDestroy() { }
}"""
        result = score_roundtrip(source, "Baz.cs")
        assert result.naming_score >= 0.8

    def test_type_score_fields(self):
        source = """using UnityEngine;
public class TypeTest : MonoBehaviour {
    [SerializeField] private float speed = 5f;
    [SerializeField] private int count = 0;
    [SerializeField] private bool active = true;
    [SerializeField] private string label = "test";
}"""
        result = score_roundtrip(source, "TypeTest.cs")
        assert result.type_score >= 0.5


class TestPongRoundtrip:
    def test_paddle_controller_roundtrip(self):
        result = score_roundtrip_file(PONG_DIR / "PaddleController.cs")
        assert result.overall_score >= 0.5
        assert result.structural_score >= 0.7
        assert "MISSING class" not in " ".join(result.details)

    def test_score_manager_roundtrip(self):
        result = score_roundtrip_file(PONG_DIR / "ScoreManager.cs")
        assert result.overall_score >= 0.4
        assert result.structural_score >= 0.5

    def test_game_manager_roundtrip(self):
        result = score_roundtrip_file(PONG_DIR / "GameManager.cs")
        assert result.overall_score >= 0.4
        assert result.structural_score >= 0.5

    def test_all_pong_files_produce_scores(self):
        """Every Pong C# file should produce a valid roundtrip score."""
        for cs_file in PONG_DIR.glob("*.cs"):
            result = score_roundtrip_file(cs_file)
            assert 0.0 <= result.overall_score <= 1.0, f"{cs_file.name}: invalid score"
            assert result.original_class_count >= 1


class TestAccuracyTracker:
    def test_record_and_load(self, tmp_path):
        import src.gates.accuracy_tracker as tracker
        original_dir = tracker._METRICS_DIR
        tracker._METRICS_DIR = tmp_path

        try:
            score = AccuracyScore(
                file_name="test.cs",
                timestamp="2026-04-01T00:00:00",
                structural_score=0.9,
                type_score=0.8,
                naming_score=0.85,
                overall_score=0.85,
            )
            record_accuracy(score)

            scores = load_scores()
            assert len(scores) == 1
            assert scores[0]["file_name"] == "test.cs"
            assert scores[0]["overall_score"] == 0.85
        finally:
            tracker._METRICS_DIR = original_dir

    def test_record_roundtrip_fidelity(self, tmp_path):
        import src.gates.accuracy_tracker as tracker
        original_dir = tracker._METRICS_DIR
        tracker._METRICS_DIR = tmp_path

        try:
            record_roundtrip("Paddle.cs", 0.75, "good structure")
            scores = load_scores("roundtrip_fidelity.jsonl")
            assert len(scores) == 1
            assert scores[0]["fidelity"] == 0.75
        finally:
            tracker._METRICS_DIR = original_dir
