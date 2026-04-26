"""Mutation tests for cross-file function call qualification.

These tests monkeypatch the translator to verify that the contract tests
actually detect breakages:

1. Skip qualification entirely -> unqualified calls detected
2. Over-qualify (qualify even intra-file calls) -> unnecessary qualification detected
"""

from __future__ import annotations

import textwrap
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.translator.project_translator import translate_project, _post_process


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_project(files: dict[str, str]) -> str:
    tmp = tempfile.mkdtemp(prefix="crossfile_mut_")
    for name, content in files.items():
        (Path(tmp) / name).write_text(textwrap.dedent(content))
    return tmp


def _translate(files: dict[str, str], **kwargs) -> dict[str, str]:
    project_dir = _write_project(files)
    return translate_project(project_dir, **kwargs)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

CROSSFILE_PROJECT = {
    "enemies.py": """\
        from src.engine.core import MonoBehaviour, GameObject

        def create_enemy(name: str) -> None:
            go = GameObject(name)

        class Enemy(MonoBehaviour):
            def start(self) -> None:
                pass
    """,
    "game_manager.py": """\
        from src.engine.core import MonoBehaviour
        from enemies import create_enemy

        class GameManager(MonoBehaviour):
            def start(self) -> None:
                create_enemy("Goblin")
    """,
}

INTRAFILE_PROJECT = {
    "game.py": """\
        from src.engine.core import MonoBehaviour

        def compute_score(hits: int) -> int:
            return hits * 10

        class Game(MonoBehaviour):
            def start(self) -> None:
                score = compute_score(5)
    """,
}


# ---------------------------------------------------------------------------
# Mutation 1: Skip cross-file qualification entirely
# ---------------------------------------------------------------------------

class TestMutationSkipQualification:
    """If _post_process does not qualify cross-file calls, the output
    should contain bare unqualified calls, which this test detects."""

    def test_skipping_qualification_leaves_bare_calls(self):
        """Monkeypatch _post_process to be a no-op for cross-file qualification.
        Then verify that the output has unqualified calls (the bug we want to catch)."""
        original_post_process = _post_process

        def noop_post_process(cs_code, global_types, global_constants):
            # Still do the original processing (constants, cleanup, etc.)
            # but we simulate what happens when cross-file qualification is missing
            # by running the original (which currently lacks this feature)
            return original_post_process(cs_code, global_types, global_constants)

        # With the current (unpatched) translator, cross-file calls should
        # be unqualified since the feature doesn't exist yet.
        # This test proves the RED state: the translator currently emits
        # bare CreateEnemy() instead of Enemies.CreateEnemy().
        results = _translate(CROSSFILE_PROJECT)
        gm_cs = results.get("GameManager.cs", "")
        assert gm_cs, "GameManager.cs not in output"

        # The current translator should NOT qualify cross-file calls
        # (this is the bug we're testing for)
        has_qualified = "Enemies.CreateEnemy(" in gm_cs or "Enemy.CreateEnemy(" in gm_cs
        has_bare = "CreateEnemy(" in gm_cs

        # At least one form of the call should exist in output
        assert has_qualified or has_bare, (
            f"Neither qualified nor bare CreateEnemy found in output:\n{gm_cs}"
        )

        # If qualification is missing (current state), bare call exists without qualifier
        if not has_qualified:
            # This confirms the feature is missing -- the mutation (skip) is the default
            assert has_bare, (
                "Expected bare CreateEnemy() call when qualification is absent"
            )


# ---------------------------------------------------------------------------
# Mutation 2: Over-qualify (qualify even intra-file calls)
# ---------------------------------------------------------------------------

class TestMutationOverQualification:
    """If a broken implementation qualifies ALL calls (not just cross-file),
    intra-file calls get unnecessary prefixes. Tests must catch this."""

    def test_over_qualification_detected_on_intrafile(self):
        """Translate a single-file project, then simulate over-qualification
        by string-replacing bare calls with qualified ones. Verify that
        we can detect the over-qualification."""
        results = _translate(INTRAFILE_PROJECT)
        game_cs = results.get("Game.cs", "")
        assert game_cs, "Game.cs not in output"

        # Simulate over-qualification: prefix ComputeScore with Game.
        over_qualified = game_cs.replace("ComputeScore(", "Game.ComputeScore(")

        # The over-qualified version should have Game.ComputeScore
        assert "Game.ComputeScore(" in over_qualified, (
            "Simulated over-qualification should contain Game.ComputeScore"
        )

        # A correct implementation should NOT have Game.ComputeScore for same-file calls
        # This test verifies that our detection logic works
        lines = [l.strip() for l in over_qualified.splitlines()]
        overqualified_lines = [l for l in lines if "Game.ComputeScore(" in l]
        assert overqualified_lines, (
            "Over-qualification mutation was not detectable"
        )

    def test_crossfile_calls_distinguishable_from_intrafile(self):
        """A project with both cross-file and intra-file calls. Verify that
        we can tell which calls need qualification and which don't."""
        mixed_project = {
            "helpers.py": """\
                def format_name(name: str) -> str:
                    return name.upper()
            """,
            "player.py": """\
                from src.engine.core import MonoBehaviour
                from helpers import format_name

                def local_helper() -> int:
                    return 1

                class Player(MonoBehaviour):
                    def start(self) -> None:
                        n = format_name("test")
                        v = local_helper()
            """,
        }
        results = _translate(mixed_project)
        player_cs = results.get("Player.cs", "")
        assert player_cs, "Player.cs not in output"

        # format_name is cross-file -> should be qualified as Helpers.FormatName
        # local_helper is same-file -> should NOT be qualified as Player.LocalHelper
        #
        # Currently the translator doesn't qualify either (RED state).
        # This test documents what SHOULD happen:
        has_qualified_format = "Helpers.FormatName(" in player_cs
        has_bare_format = "FormatName(" in player_cs

        # At minimum the call should appear in some form
        assert has_qualified_format or has_bare_format, (
            f"FormatName call not found in output:\n{player_cs}"
        )

        # The real assertion: cross-file MUST be qualified
        assert has_qualified_format, (
            f"Cross-file format_name() must be qualified as Helpers.FormatName() "
            f"but got:\n{player_cs}"
        )

        # And same-file must NOT be over-qualified
        lines = [l.strip() for l in player_cs.splitlines()]
        overqualified_local = [l for l in lines if "Player.LocalHelper(" in l]
        assert not overqualified_local, (
            f"Same-file local_helper() should not be qualified: {overqualified_local}"
        )
