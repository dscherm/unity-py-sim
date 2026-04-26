"""Integration tests for coroutine translation on real Angry Birds example files.

Validates end-to-end translation of bird.py and game_manager.py, checking that
coroutine-related C# constructs appear correctly in the full translator output.

Written by independent validation agent — no existing test files were consulted.
"""

import pytest
from pathlib import Path

from src.translator.python_to_csharp import translate_file


ANGRY_BIRDS_DIR = Path(__file__).resolve().parents[2] / "examples" / "angry_birds" / "angry_birds_python"


class TestBirdTranslation:
    """Integration: translate bird.py and verify coroutine constructs."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.output = translate_file(ANGRY_BIRDS_DIR / "bird.py")

    def test_bird_has_ienumerator(self):
        """Bird._destroy_after is a coroutine and must produce IEnumerator."""
        assert "IEnumerator" in self.output

    def test_bird_has_yield_return_new_wait_for_seconds(self):
        """yield WaitForSeconds(seconds) must translate to yield return new WaitForSeconds(...)."""
        assert "yield return new WaitForSeconds(" in self.output

    def test_bird_has_start_coroutine(self):
        """self.start_coroutine(...) must translate to StartCoroutine(...)."""
        assert "StartCoroutine(" in self.output

    def test_bird_has_using_system_collections(self):
        """Bird has a coroutine so using System.Collections; must be present."""
        assert "using System.Collections;" in self.output


class TestGameManagerTranslation:
    """Integration: translate game_manager.py and verify coroutine constructs."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.output = translate_file(ANGRY_BIRDS_DIR / "game_manager.py")

    def test_game_manager_has_ienumerator(self):
        """GameManager._next_turn is a coroutine and must produce IEnumerator."""
        assert "IEnumerator" in self.output

    def test_game_manager_has_yield_return(self):
        """_next_turn yields WaitForSeconds(1.0), must translate to yield return."""
        assert "yield return new WaitForSeconds(" in self.output

    def test_game_manager_has_start_coroutine(self):
        """self.start_coroutine(self._next_turn()) must translate to StartCoroutine(...)."""
        assert "StartCoroutine(" in self.output

    def test_game_manager_has_using_system_collections(self):
        """GameManager has a coroutine so using System.Collections; must be present."""
        assert "using System.Collections;" in self.output
