"""Independent validation tests for Task 11 (corpus index / baseline metrics)
and Task 12 (compilation gate / syntax check).

These tests were written by a separate validation agent that did NOT read
any existing tests. They derive contracts from the source code in
src/gates/compilation_gate.py, tools/score_baseline.py, and tools/build_corpus.py.
"""

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.gates.compilation_gate import (
    CompilationResult,
    check_syntax,
    _PYTHON_ARTIFACTS,
)
from tools.score_baseline import score_pair

CORPUS_INDEX_PATH = ROOT / "data" / "corpus" / "corpus_index.json"
PAIRS_DIR = ROOT / "data" / "corpus" / "pairs"


# ────────────────────────────────────────────────────────────────────
# CONTRACT TESTS: corpus_index.json structure
# ────────────────────────────────────────────────────────────────────

class TestCorpusIndexContract:
    """Verify corpus_index.json structural integrity."""

    @pytest.fixture(scope="class")
    def corpus_index(self):
        assert CORPUS_INDEX_PATH.exists(), "corpus_index.json must exist"
        return json.loads(CORPUS_INDEX_PATH.read_text())

    def test_index_is_nonempty_list(self, corpus_index):
        assert isinstance(corpus_index, list)
        assert len(corpus_index) > 0

    def test_index_has_expected_count(self, corpus_index):
        """Task 11 spec says 37 entries."""
        assert len(corpus_index) == 37

    def test_each_entry_has_required_fields(self, corpus_index):
        for entry in corpus_index:
            assert "id" in entry, f"Entry missing 'id': {entry}"
            assert "game" in entry, f"Entry missing 'game': {entry}"
            assert "file" in entry, f"Entry missing 'file': {entry}"

    def test_all_ids_are_unique(self, corpus_index):
        ids = [e["id"] for e in corpus_index]
        assert len(ids) == len(set(ids)), f"Duplicate IDs found: {ids}"

    def test_all_pair_files_exist_on_disk(self, corpus_index):
        missing = []
        for entry in corpus_index:
            pair_path = ROOT / "data" / "corpus" / entry["file"]
            if not pair_path.exists():
                missing.append(entry["file"])
        assert not missing, f"Missing pair files: {missing}"

    def test_expected_games_present(self, corpus_index):
        games = set(e["game"] for e in corpus_index)
        assert "pong" in games
        assert "breakout" in games
        assert "angry_birds" in games
        assert "fsm_platformer" in games

    def test_game_counts(self, corpus_index):
        from collections import Counter
        counts = Counter(e["game"] for e in corpus_index)
        assert counts["pong"] == 4
        assert counts["breakout"] == 5
        assert counts["angry_birds"] == 8
        assert counts["fsm_platformer"] == 20


class TestPairFileContract:
    """Verify each pair file has required fields and references existing files."""

    @pytest.fixture(scope="class")
    def all_pairs(self):
        index = json.loads(CORPUS_INDEX_PATH.read_text())
        pairs = []
        for entry in index:
            pair_path = ROOT / "data" / "corpus" / entry["file"]
            pairs.append(json.loads(pair_path.read_text()))
        return pairs

    def test_each_pair_has_required_fields(self, all_pairs):
        for pair in all_pairs:
            assert "id" in pair, f"Pair missing 'id': {pair}"
            assert "python_file" in pair, f"Pair missing 'python_file': {pair}"
            assert "unity_file" in pair, f"Pair missing 'unity_file': {pair}"
            assert "game" in pair, f"Pair missing 'game': {pair}"

    def test_all_python_files_exist(self, all_pairs):
        missing = []
        for pair in all_pairs:
            py = ROOT / pair["python_file"]
            if not py.exists():
                missing.append(pair["python_file"])
        assert not missing, f"Missing Python files: {missing}"

    def test_all_csharp_files_exist(self, all_pairs):
        missing = []
        for pair in all_pairs:
            cs = ROOT / pair["unity_file"]
            if not cs.exists():
                missing.append(pair["unity_file"])
        assert not missing, f"Missing C# files: {missing}"

    def test_python_files_are_py(self, all_pairs):
        for pair in all_pairs:
            assert pair["python_file"].endswith(".py"), f"Not a .py file: {pair['python_file']}"

    def test_csharp_files_are_cs(self, all_pairs):
        for pair in all_pairs:
            assert pair["unity_file"].endswith(".cs"), f"Not a .cs file: {pair['unity_file']}"


# ────────────────────────────────────────────────────────────────────
# CONTRACT TESTS: check_syntax catches known Python artifacts
# ────────────────────────────────────────────────────────────────────

class TestCheckSyntaxCatchesPythonArtifacts:
    """check_syntax must detect Python-isms that leaked into generated C#."""

    def test_catches_self_dot(self):
        source = """using UnityEngine;
public class Foo : MonoBehaviour {
    void Start() { self.x = 5; }
}"""
        result = check_syntax(source, "test.cs")
        assert not result.syntax_passed
        assert any("self." in e for e in result.syntax_errors)

    def test_catches_from_import(self):
        source = """from UnityEngine import MonoBehaviour
public class Foo : MonoBehaviour { }"""
        result = check_syntax(source, "test.cs")
        assert not result.syntax_passed
        assert any("from" in e.lower() or "import" in e.lower() for e in result.syntax_errors)

    def test_catches_python_import(self):
        source = """import os
public class Foo { }"""
        result = check_syntax(source, "test.cs")
        assert not result.syntax_passed
        assert any("import" in e.lower() for e in result.syntax_errors)

    def test_catches_docstrings_triple_double(self):
        source = '''using UnityEngine;
public class Foo {
    """This is a docstring"""
}'''
        result = check_syntax(source, "test.cs")
        assert not result.syntax_passed
        assert any("docstring" in e.lower() for e in result.syntax_errors)

    def test_catches_docstrings_triple_single(self):
        source = """using UnityEngine;
public class Foo {
    '''Another docstring'''
}"""
        result = check_syntax(source, "test.cs")
        assert not result.syntax_passed
        assert any("docstring" in e.lower() for e in result.syntax_errors)

    def test_catches_python_true_without_semicolon(self):
        source = """using UnityEngine;
public class Foo {
    void Start() { if (True) {} }
}"""
        result = check_syntax(source, "test.cs")
        assert not result.syntax_passed
        assert any("True" in e for e in result.syntax_errors)

    def test_catches_python_true_with_semicolon(self):
        """True; is invalid C# (should be true;) — fixed: regex now catches it."""
        source = """using UnityEngine;
public class Foo {
    void Start() { bool x = True; }
}"""
        result = check_syntax(source, "test.cs")
        assert not result.syntax_passed

    def test_catches_python_false_without_semicolon(self):
        source = """using UnityEngine;
public class Foo {
    void Start() { if (False) {} }
}"""
        result = check_syntax(source, "test.cs")
        assert not result.syntax_passed
        assert any("False" in e for e in result.syntax_errors)

    def test_catches_python_false_with_semicolon(self):
        """False; is invalid C# (should be false;) — fixed: regex now catches it."""
        source = """using UnityEngine;
public class Foo {
    void Start() { bool x = False; }
}"""
        result = check_syntax(source, "test.cs")
        assert not result.syntax_passed

    def test_catches_python_none(self):
        source = """using UnityEngine;
public class Foo {
    void Start() { var x = None; }
}"""
        result = check_syntax(source, "test.cs")
        assert not result.syntax_passed
        assert any("None" in e for e in result.syntax_errors)

    def test_catches_def_keyword(self):
        source = """using UnityEngine;
public class Foo {
    def Start():
        pass
}"""
        result = check_syntax(source, "test.cs")
        assert not result.syntax_passed
        assert any("def" in e.lower() for e in result.syntax_errors)

    def test_catches_elif(self):
        source = """using UnityEngine;
public class Foo {
    void Update() {
        elif (x > 0) { }
    }
}"""
        result = check_syntax(source, "test.cs")
        assert not result.syntax_passed
        assert any("elif" in e for e in result.syntax_errors)

    def test_catches_pass_statement(self):
        source = """using UnityEngine;
public class Foo {
    void Start() {
        pass
    }
}"""
        result = check_syntax(source, "test.cs")
        assert not result.syntax_passed
        assert any("pass" in e.lower() for e in result.syntax_errors)

    def test_catches_colon_block_syntax(self):
        source = """using UnityEngine;
public class Foo {
    void Start():
        Debug.Log("hi");
}"""
        result = check_syntax(source, "test.cs")
        assert not result.syntax_passed
        assert any("Colon" in e or "block syntax" in e.lower() for e in result.syntax_errors)


class TestCheckSyntaxPassesCleanCSharp:
    """check_syntax must pass valid C# code."""

    def test_basic_monobehaviour(self):
        source = """using UnityEngine;

public class PlayerController : MonoBehaviour
{
    private float speed = 5.0f;

    void Start()
    {
        Debug.Log("Started");
    }

    void Update()
    {
        float h = Input.GetAxis("Horizontal");
        transform.Translate(new Vector3(h * speed * Time.deltaTime, 0, 0));
    }
}"""
        result = check_syntax(source, "PlayerController.cs")
        assert result.syntax_passed, f"Errors: {result.syntax_errors}"

    def test_enum_only_file(self):
        source = """namespace MyGame
{
    public enum GameState
    {
        Menu,
        Playing,
        Paused,
        GameOver
    }
}"""
        result = check_syntax(source, "GameState.cs")
        assert result.syntax_passed, f"Errors: {result.syntax_errors}"

    def test_class_with_csharp_true_false_null(self):
        source = """using UnityEngine;
public class Foo : MonoBehaviour {
    void Start() {
        bool a = true;
        bool b = false;
        object c = null;
    }
}"""
        result = check_syntax(source, "Foo.cs")
        assert result.syntax_passed, f"Errors: {result.syntax_errors}"

    def test_case_label_colon_not_flagged(self):
        """switch case labels end with colon -- should NOT be flagged."""
        source = """using UnityEngine;
public class Foo {
    void Update() {
        switch (state) {
            case 1:
                break;
            default:
                break;
        }
    }
}"""
        result = check_syntax(source, "Foo.cs")
        # case/default colons should be exempt
        colon_errors = [e for e in result.syntax_errors if "Colon" in e]
        assert len(colon_errors) == 0, f"False positive colon errors: {colon_errors}"


class TestCheckSyntaxBalancedBraces:
    """Verify brace-balance detection."""

    def test_unbalanced_braces_detected(self):
        source = """using UnityEngine;
public class Foo {
    void Start() {
        Debug.Log("hi");
    }
"""
        result = check_syntax(source, "Foo.cs")
        assert not result.syntax_passed
        assert any("Unbalanced" in e for e in result.syntax_errors)

    def test_balanced_braces_pass(self):
        source = """using UnityEngine;
public class Foo {
    void Start() { }
}"""
        result = check_syntax(source, "Foo.cs")
        brace_errors = [e for e in result.syntax_errors if "Unbalanced" in e]
        assert len(brace_errors) == 0


class TestCompilationResultContract:
    """Verify CompilationResult.passed property logic."""

    def test_passed_true_when_syntax_passed_and_no_build(self):
        r = CompilationResult(file_name="a.cs", syntax_passed=True)
        assert r.passed is True

    def test_passed_false_when_syntax_failed_and_no_build(self):
        r = CompilationResult(file_name="a.cs", syntax_passed=False)
        assert r.passed is False

    def test_passed_delegates_to_build_when_available(self):
        r = CompilationResult(file_name="a.cs", syntax_passed=True, build_passed=False)
        assert r.passed is False

    def test_passed_true_when_build_passed(self):
        r = CompilationResult(file_name="a.cs", syntax_passed=True, build_passed=True)
        assert r.passed is True


# ────────────────────────────────────────────────────────────────────
# EDGE CASE TESTS
# ────────────────────────────────────────────────────────────────────

class TestCheckSyntaxEdgeCases:

    def test_empty_source(self):
        result = check_syntax("", "empty.cs")
        # Empty file has no syntax errors per se (no python artifacts)
        # but should warn about missing class
        assert result.syntax_passed  # no errors, just warnings

    def test_comments_only(self):
        source = """// This is a C# file
// No actual code here
/* Block comment */"""
        result = check_syntax(source, "comments.cs")
        assert result.syntax_passed, f"Errors: {result.syntax_errors}"

    def test_enum_file_no_using(self):
        source = """public enum Direction { Up, Down, Left, Right }"""
        result = check_syntax(source, "Direction.cs")
        assert result.syntax_passed
        # Should warn about missing using directive
        assert any("using" in w.lower() for w in result.syntax_warnings)

    def test_no_class_warns(self):
        source = """using UnityEngine;
// Just using, no class
"""
        result = check_syntax(source, "noclass.cs")
        assert result.syntax_passed  # warnings, not errors
        assert any("class" in w.lower() or "enum" in w.lower() for w in result.syntax_warnings)


# ────────────────────────────────────────────────────────────────────
# INTEGRATION TESTS: score_pair on real corpus pairs
# ────────────────────────────────────────────────────────────────────

class TestScorePairIntegration:
    """Run score_pair on actual corpus entries and verify scores are sane."""

    @pytest.fixture(scope="class")
    def sample_pairs(self):
        """Load a few diverse pairs for testing."""
        index = json.loads(CORPUS_INDEX_PATH.read_text())
        # Pick one from each game
        games_seen = set()
        selected = []
        for entry in index:
            if entry["game"] not in games_seen:
                games_seen.add(entry["game"])
                pair_path = ROOT / "data" / "corpus" / entry["file"]
                selected.append(json.loads(pair_path.read_text()))
            if len(selected) >= 4:
                break
        return selected

    def test_scores_in_zero_one_range(self, sample_pairs):
        for pair_data in sample_pairs:
            result = score_pair(pair_data)
            assert 0.0 <= result.overall_score <= 1.0, (
                f"Score out of range for {result.pair_id}: {result.overall_score}"
            )
            assert 0.0 <= result.class_score <= 1.0
            assert 0.0 <= result.method_score <= 1.0
            assert 0.0 <= result.field_score <= 1.0
            assert 0.0 <= result.using_score <= 1.0

    def test_no_translation_errors(self, sample_pairs):
        for pair_data in sample_pairs:
            result = score_pair(pair_data)
            assert result.error is None, (
                f"Translation error for {result.pair_id}: {result.error}"
            )

    def test_pairscore_fields_populated(self, sample_pairs):
        for pair_data in sample_pairs:
            result = score_pair(pair_data)
            assert result.pair_id == pair_data["id"]
            assert result.game == pair_data["game"]
            assert result.python_file == pair_data["python_file"]
            assert result.csharp_file == pair_data["unity_file"]

    def test_overall_is_weighted_average(self, sample_pairs):
        """Verify the overall score formula matches the documented weights."""
        for pair_data in sample_pairs:
            r = score_pair(pair_data)
            expected = round(
                r.class_score * 0.3 +
                r.method_score * 0.35 +
                r.field_score * 0.25 +
                r.using_score * 0.1,
                3,
            )
            assert abs(r.overall_score - expected) < 0.001, (
                f"Overall {r.overall_score} != weighted avg {expected} for {r.pair_id}"
            )


class TestScorePairMissingFiles:
    """score_pair should handle missing files gracefully."""

    def test_missing_python_file(self):
        pair = {
            "id": "fake_missing_py",
            "game": "test",
            "python_file": "nonexistent/file.py",
            "unity_file": "examples/pong/pong_unity/PaddleController.cs",
        }
        result = score_pair(pair)
        assert result.error is not None
        assert "not found" in result.error.lower() or "Python" in result.error

    def test_missing_csharp_file(self):
        pair = {
            "id": "fake_missing_cs",
            "game": "test",
            "python_file": "examples/pong/pong_python/paddle_controller.py",
            "unity_file": "nonexistent/file.cs",
        }
        result = score_pair(pair)
        assert result.error is not None
        assert "not found" in result.error.lower() or "C#" in result.error


# ────────────────────────────────────────────────────────────────────
# INTEGRATION TESTS: check_syntax on translated output from real files
# ────────────────────────────────────────────────────────────────────

class TestCheckSyntaxOnTranslatedOutput:
    """Translate real Python files and run check_syntax on the output."""

    @pytest.fixture(scope="class")
    def translated_outputs(self):
        from src.translator.python_to_csharp import translate_file
        files = [
            ROOT / "examples" / "pong" / "pong_python" / "paddle_controller.py",
            ROOT / "examples" / "breakout" / "breakout_python" / "brick.py",
            ROOT / "examples" / "fsm_platformer" / "fsm_platformer_python" / "fsm.py",
        ]
        results = []
        for f in files:
            if f.exists():
                cs = translate_file(f, input_system="legacy", unity_version=5)
                results.append((f.name, cs))
        return results

    def test_at_least_one_file_translated(self, translated_outputs):
        assert len(translated_outputs) > 0

    def test_translated_output_is_nonempty(self, translated_outputs):
        for name, cs in translated_outputs:
            assert len(cs.strip()) > 0, f"Empty translation for {name}"

    def test_syntax_result_is_compilationresult(self, translated_outputs):
        for name, cs in translated_outputs:
            result = check_syntax(cs, name)
            assert isinstance(result, CompilationResult)

    def test_syntax_check_returns_meaningful_data(self, translated_outputs):
        """Even if some fail, the errors list must be populated if failed."""
        for name, cs in translated_outputs:
            result = check_syntax(cs, name)
            if not result.syntax_passed:
                assert len(result.syntax_errors) > 0, (
                    f"{name}: syntax_passed=False but no errors listed"
                )


# ────────────────────────────────────────────────────────────────────
# INTEGRATION TESTS: baseline.json structure
# ────────────────────────────────────────────────────────────────────

class TestBaselineJsonContract:
    """Verify data/metrics/baseline.json has expected structure."""

    @pytest.fixture(scope="class")
    def baseline(self):
        path = ROOT / "data" / "metrics" / "baseline.json"
        assert path.exists(), "baseline.json must exist"
        return json.loads(path.read_text())

    def test_has_total_pairs(self, baseline):
        assert "total_pairs" in baseline
        assert baseline["total_pairs"] == 37

    def test_has_avg_scores(self, baseline):
        for key in ["avg_overall", "avg_class", "avg_method", "avg_field", "avg_using"]:
            assert key in baseline, f"Missing key: {key}"
            assert 0.0 <= baseline[key] <= 1.0, f"{key} out of range: {baseline[key]}"

    def test_has_by_game(self, baseline):
        assert "by_game" in baseline
        for game in ["pong", "breakout", "angry_birds", "fsm_platformer"]:
            assert game in baseline["by_game"], f"Missing game: {game}"
            assert "count" in baseline["by_game"][game]
            assert "avg_overall" in baseline["by_game"][game]

    def test_has_pairs_list(self, baseline):
        assert "pairs" in baseline
        assert len(baseline["pairs"]) == 37

    def test_pairs_have_required_fields(self, baseline):
        for p in baseline["pairs"]:
            assert "id" in p
            assert "game" in p
            assert "overall" in p
            assert 0.0 <= p["overall"] <= 1.0


# ────────────────────────────────────────────────────────────────────
# MUTATION TESTS: monkeypatch _PYTHON_ARTIFACTS to verify detection
# ────────────────────────────────────────────────────────────────────

class TestMutationPythonArtifacts:
    """Prove that removing artifact patterns causes check_syntax to miss errors."""

    def test_removing_self_dot_pattern_breaks_detection(self):
        """If we remove the self. pattern, check_syntax should miss self. references."""
        source = """using UnityEngine;
public class Foo {
    void Start() { self.x = 5; }
}"""
        # First verify it catches it normally
        normal = check_syntax(source, "test.cs")
        assert not normal.syntax_passed

        # Now remove the self. pattern
        mutated = [p for p in _PYTHON_ARTIFACTS if "self." not in p[1]]
        with patch("src.gates.compilation_gate._PYTHON_ARTIFACTS", mutated):
            result = check_syntax(source, "test.cs")
            # Should now pass (the mutation breaks detection)
            self_errors = [e for e in result.syntax_errors if "self." in e]
            assert len(self_errors) == 0, "Mutation should have disabled self. detection"

    def test_removing_true_pattern_breaks_detection(self):
        # Use True without semicolon so the regex actually matches
        source = """using UnityEngine;
public class Foo {
    void Start() { if (True) {} }
}"""
        normal = check_syntax(source, "test.cs")
        assert not normal.syntax_passed

        mutated = [p for p in _PYTHON_ARTIFACTS if "True" not in p[1]]
        with patch("src.gates.compilation_gate._PYTHON_ARTIFACTS", mutated):
            result = check_syntax(source, "test.cs")
            true_errors = [e for e in result.syntax_errors if "True" in e]
            assert len(true_errors) == 0, "Mutation should have disabled True detection"

    def test_removing_none_pattern_breaks_detection(self):
        source = """using UnityEngine;
public class Foo {
    void Start() { var x = None; }
}"""
        normal = check_syntax(source, "test.cs")
        assert not normal.syntax_passed

        mutated = [p for p in _PYTHON_ARTIFACTS if "None" not in p[1]]
        with patch("src.gates.compilation_gate._PYTHON_ARTIFACTS", mutated):
            result = check_syntax(source, "test.cs")
            none_errors = [e for e in result.syntax_errors if "None" in e]
            assert len(none_errors) == 0, "Mutation should have disabled None detection"

    def test_removing_import_pattern_breaks_detection(self):
        source = """from os import path
public class Foo { }"""
        normal = check_syntax(source, "test.cs")
        assert not normal.syntax_passed

        mutated = [p for p in _PYTHON_ARTIFACTS if "import" not in p[1].lower()]
        with patch("src.gates.compilation_gate._PYTHON_ARTIFACTS", mutated):
            result = check_syntax(source, "test.cs")
            import_errors = [e for e in result.syntax_errors if "import" in e.lower()]
            assert len(import_errors) == 0

    def test_emptying_all_patterns_passes_everything(self):
        """If all patterns removed, even terrible code passes syntax check."""
        source = """from os import path
import sys
self.x = True
None
def foo():
    pass"""
        with patch("src.gates.compilation_gate._PYTHON_ARTIFACTS", []):
            with patch("src.gates.compilation_gate._SYNTAX_CHECKS", []):
                result = check_syntax(source, "test.cs")
                # Only brace check and structural warnings remain
                artifact_errors = [
                    e for e in result.syntax_errors if "Unbalanced" not in e
                ]
                assert len(artifact_errors) == 0, (
                    f"With empty patterns, should have no artifact errors: {artifact_errors}"
                )
