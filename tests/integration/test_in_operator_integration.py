"""Integration tests for 'in' operator translation in real Pacman V2 files.

Translates actual game files that use 'in' membership tests and validates:
1. The C# output parses correctly (structural gate)
2. No raw Python 'in' keyword leaks into if-conditions
"""

import re
from pathlib import Path

from src.translator.python_to_csharp import translate_file
from src.gates.structural_gate import validate_csharp

PACMAN_V2_DIR = Path(__file__).parent.parent.parent / "examples" / "pacman_v2" / "pacman_v2_python"


class TestPassageTranslation:
    """passage.py uses 'if obj_id in _recent_teleports' — dict membership test."""

    def test_passage_translates_without_in_leak(self):
        """Translate passage.py and verify no raw 'in' in if-conditions."""
        result = translate_file(PACMAN_V2_DIR / "passage.py")
        lines = result.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("if") and "foreach" not in stripped:
                # Should not contain raw Python 'in' as a membership operator
                if re.search(r"\b\w+\s+in\s+\w+", stripped) and "Contains" not in stripped:
                    assert False, (
                        f"Raw Python 'in' leaked in passage.py translation: {stripped}"
                    )

    def test_passage_structural_gate_passes(self):
        """Translated passage.py must parse as valid C#."""
        result = translate_file(PACMAN_V2_DIR / "passage.py")
        sr = validate_csharp(result)
        assert sr.valid, (
            f"passage.py translation has {sr.error_count} parse errors: {sr.errors}\n"
            f"Full output:\n{result}"
        )

    def test_passage_uses_containskey_for_dict(self):
        """passage.py has 'if obj_id in _recent_teleports' where _recent_teleports is a dict.
        Must translate to .ContainsKey() in C#."""
        result = translate_file(PACMAN_V2_DIR / "passage.py")
        # The dict membership test should produce ContainsKey
        assert "ContainsKey" in result, (
            f"Expected ContainsKey for dict membership in passage.py, got:\n{result}"
        )


class TestGameManagerTranslation:
    """game_manager.py uses 'if pellet not in self._all_pellets' and
    'if ghost not in self.ghosts' — list 'not in' tests."""

    def test_game_manager_translates_without_in_leak(self):
        """Translate game_manager.py and verify no raw 'in' in if-conditions."""
        result = translate_file(PACMAN_V2_DIR / "game_manager.py")
        lines = result.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("if") and "foreach" not in stripped:
                if re.search(r"\b\w+\s+in\s+\w+", stripped) and "Contains" not in stripped:
                    assert False, (
                        f"Raw Python 'in' leaked in game_manager.py translation: {stripped}"
                    )

    def test_game_manager_structural_gate_passes(self):
        """Translated game_manager.py must parse as valid C#."""
        result = translate_file(PACMAN_V2_DIR / "game_manager.py")
        sr = validate_csharp(result)
        assert sr.valid, (
            f"game_manager.py translation has {sr.error_count} parse errors: {sr.errors}\n"
            f"Full output:\n{result}"
        )

    def test_game_manager_uses_contains_for_not_in_list(self):
        """game_manager.py has 'if pellet not in self._all_pellets'.
        Must translate to '!allPellets.Contains(pellet)' in C#."""
        result = translate_file(PACMAN_V2_DIR / "game_manager.py")
        # Should have negated Contains for 'not in' list test
        assert "Contains" in result, (
            f"Expected .Contains() for list 'not in' test in game_manager.py, got:\n{result}"
        )
        # The negation must be present
        has_negated = "!allPellets.Contains" in result or "!_allPellets.Contains" in result
        # Also accept other camelCase variants
        if not has_negated:
            has_negated = any(
                "!" in line and "Contains" in line
                for line in result.split("\n")
                if line.strip().startswith("if")
            )
        assert has_negated, (
            f"Expected negated .Contains() for 'not in' pattern in game_manager.py, got:\n{result}"
        )
