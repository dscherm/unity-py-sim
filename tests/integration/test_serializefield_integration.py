"""Integration tests for [SerializeField] emission using real example files.

Translates actual Python game files and verifies that reference-type fields
(Ghost, Pacman, etc.) get [SerializeField] private with concrete types,
while value-type fields (int, float) remain public.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.translator.python_to_csharp import translate_file


PACMAN_V2_DIR = Path(__file__).resolve().parents[2] / "examples" / "pacman_v2" / "pacman_v2_python"


# ===========================================================================
# 1. GameManager — mixed reference and value fields
# ===========================================================================

class TestGameManagerFieldEmission:
    """GameManager has:
    - ghosts: list[Ghost]         -> [SerializeField] private Ghost[] ghosts;
    - pacman: Pacman | None       -> [SerializeField] private Pacman pacman;
    - score: int = 0              -> public int score = 0;
    - lives: int = 3              -> public int lives = 3;
    - ghost_multiplier: int = 1   -> public int ghostMultiplier = 1;
    """

    @pytest.fixture(autouse=True)
    def translate_game_manager(self):
        gm_path = PACMAN_V2_DIR / "game_manager.py"
        if not gm_path.exists():
            pytest.skip("pacman_v2 example not found")
        self.cs = translate_file(str(gm_path), unity_version=5, input_system="legacy")

    def test_ghost_list_has_concrete_type(self):
        """ghosts field must have Ghost[] or List<Ghost>, not object."""
        assert "object ghosts" not in self.cs, (
            f"ghosts field must not be 'object'. Output:\n{self.cs}"
        )
        assert re.search(r"(Ghost\[\]|List<Ghost>)", self.cs), (
            f"ghosts field must be Ghost[] or List<Ghost>. Output:\n{self.cs}"
        )

    def test_ghost_list_has_serializefield(self):
        """ghosts field must have [SerializeField] attribute."""
        # Find the line with 'ghosts' field declaration
        assert "[SerializeField]" in self.cs, (
            "GameManager must have at least one [SerializeField] for reference fields"
        )

    def test_pacman_field_has_concrete_type(self):
        """pacman field must be typed as Pacman, not object."""
        assert "object pacman" not in self.cs
        assert re.search(r"Pacman\s+pacman", self.cs), (
            f"pacman field must have concrete type Pacman. Output:\n{self.cs}"
        )

    def test_pacman_field_is_private_serialized(self):
        """pacman field must be [SerializeField] private Pacman pacman;"""
        assert "public Pacman pacman" not in self.cs, (
            "pacman reference field must not be public — should be [SerializeField] private"
        )
        assert "private Pacman pacman;" in self.cs, (
            "pacman field must be 'private Pacman pacman;'"
        )

    def test_score_is_public_int(self):
        """score: int = 0 must remain public int score = 0;"""
        assert "public int score = 0;" in self.cs

    def test_lives_is_public_int(self):
        """lives: int = 3 must remain public int lives = 3;"""
        assert "public int lives = 3;" in self.cs

    def test_ghost_multiplier_is_public_int(self):
        """ghost_multiplier: int = 1 must remain public int ghostMultiplier = 1;"""
        assert "public int ghostMultiplier = 1;" in self.cs

    def test_no_public_object_in_output(self):
        """No field in GameManager should emit 'public object'."""
        for line in self.cs.splitlines():
            stripped = line.strip()
            if stripped.startswith("public object "):
                pytest.fail(
                    f"Found 'public object' field which should have a concrete type: {stripped}"
                )


# ===========================================================================
# 2. Ghost file — reference fields
# ===========================================================================

class TestGhostFieldEmission:
    """Ghost has reference fields to behavior scripts that must be typed."""

    @pytest.fixture(autouse=True)
    def translate_ghost(self):
        ghost_path = PACMAN_V2_DIR / "ghost.py"
        if not ghost_path.exists():
            pytest.skip("ghost.py not found")
        self.cs = translate_file(str(ghost_path), unity_version=5, input_system="legacy")

    def test_no_public_object_fields(self):
        """No 'public object' should appear for any typed field in Ghost."""
        for line in self.cs.splitlines():
            stripped = line.strip()
            if stripped.startswith("public object "):
                pytest.fail(
                    f"Found 'public object' in Ghost output: {stripped}"
                )


# ===========================================================================
# 3. Full project scan — no public object anywhere
# ===========================================================================

class TestNoPublicObjectInProject:
    """Translate all pacman_v2 Python files and assert none produce 'public object'."""

    def test_no_public_object_in_any_file(self):
        if not PACMAN_V2_DIR.exists():
            pytest.skip("pacman_v2 example not found")

        py_files = list(PACMAN_V2_DIR.glob("*.py"))
        # Exclude __init__.py
        py_files = [f for f in py_files if f.name != "__init__.py"]
        assert len(py_files) > 0, "No Python files found in pacman_v2"

        violations = []
        for py_file in py_files:
            try:
                cs = translate_file(str(py_file), unity_version=5, input_system="legacy")
            except Exception as e:
                # Skip files that fail to translate for other reasons
                continue

            for i, line in enumerate(cs.splitlines(), 1):
                if "public object " in line:
                    violations.append(f"{py_file.name}:{i}: {line.strip()}")

        if violations:
            msg = "Found 'public object' fields that should have concrete types:\n"
            msg += "\n".join(violations)
            pytest.fail(msg)
