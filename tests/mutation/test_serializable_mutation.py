"""Mutation tests for @serializable dataclass configs.

Monkeypatch config values to verify the game logic actually reads from
the dataclass fields rather than using hardcoded values.
"""

import sys
import os
import random
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.core import GameObject, _clear_registry, _game_objects
from src.engine.lifecycle import LifecycleManager


@pytest.fixture(autouse=True)
def clean_engine():
    """Reset engine state before each test."""
    LifecycleManager.reset()
    _clear_registry()
    yield
    LifecycleManager.reset()
    _clear_registry()


@pytest.fixture
def space_invaders_path():
    """Add space_invaders example dir to sys.path for internal imports."""
    example_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "examples", "space_invaders")
    )
    sys.path.insert(0, example_dir)
    yield
    sys.path.remove(example_dir)


class TestInvaderScoreMutation:
    """Monkeypatch InvaderRowConfig.score and verify invaders pick it up."""

    def test_mutated_score_propagates_to_invaders(self, space_invaders_path):
        """If Invaders.ROW_CONFIG[0].score is changed, new invaders in row 0 get the mutated value."""
        from examples.space_invaders.space_invaders_python.invaders import (
            Invaders,
            InvaderRowConfig,
        )
        # Use same import path as invaders.py uses internally
        from space_invaders_python.invader import Invader
        from src.engine.math.vector import Vector2

        original_score = Invaders.ROW_CONFIG[0].score
        try:
            # Mutate
            Invaders.ROW_CONFIG[0].score = 999

            grid_go = GameObject("InvadersGrid")
            grid_go.transform.position = Vector2(0, 3)
            inv_grid = grid_go.add_component(Invaders)
            LifecycleManager.instance().process_awake_queue()

            # Row 0 invaders should have score 999
            row0_gos = [go for go in _game_objects.values() if go.name.startswith("Invader_0_")]
            assert len(row0_gos) > 0
            for go in row0_gos:
                inv = go.get_component(Invader)
                assert inv is not None, "Invader component not found on game object"
                assert inv.score == 999, (
                    f"Expected mutated score 999, got {inv.score} — "
                    "invader score is not read from ROW_CONFIG"
                )
        finally:
            Invaders.ROW_CONFIG[0].score = original_score

    def test_different_rows_have_different_scores(self, space_invaders_path):
        """Rows with different ROW_CONFIG entries must produce different scores."""
        from examples.space_invaders.space_invaders_python.invaders import (
            Invaders,
            InvaderRowConfig,
        )
        # Use same import path as invaders.py uses internally
        from space_invaders_python.invader import Invader
        from src.engine.math.vector import Vector2

        # ROW_CONFIG has rows with score 10, 10, 20, 20, 30
        grid_go = GameObject("InvadersGrid")
        grid_go.transform.position = Vector2(0, 3)
        inv_grid = grid_go.add_component(Invaders)
        LifecycleManager.instance().process_awake_queue()

        scores_by_row = {}
        for go in _game_objects.values():
            if go.name.startswith("Invader_"):
                parts = go.name.split("_")
                row = int(parts[1])
                inv = go.get_component(Invader)
                if inv:
                    scores_by_row.setdefault(row, set()).add(inv.score)

        # Row 0 and row 4 should have different scores (10 vs 30)
        assert scores_by_row[0] != scores_by_row[4], (
            "Row 0 and Row 4 should have different scores from ROW_CONFIG"
        )


class TestPowerupWeightMutation:
    """Monkeypatch PowerupConfig.weight and verify spawn selection is affected."""

    def test_zero_weight_prevents_selection(self):
        """If all configs except one have weight=0, only that one should be chosen."""
        from examples.breakout.breakout_python.powerup import (
            POWERUP_CONFIGS,
            PowerupType,
            maybe_spawn_powerup,
        )
        from src.engine.math.vector import Vector2

        original_weights = [(cfg.weight, cfg.powerup_type) for cfg in POWERUP_CONFIGS]
        try:
            # Set all weights to 0 except EXTRA_LIFE
            for cfg in POWERUP_CONFIGS:
                if cfg.powerup_type == PowerupType.EXTRA_LIFE:
                    cfg.weight = 1.0
                else:
                    cfg.weight = 0.0

            # Force spawns by fixing random
            spawned_types = []
            old_random = random.random

            call_count = [0]
            def fake_random():
                call_count[0] += 1
                # First call in maybe_spawn_powerup checks 20% threshold — always spawn
                # Second call picks the weighted type — pick 0.5 (middle)
                if call_count[0] % 2 == 1:
                    return 0.0  # Always below 0.20 threshold
                else:
                    return 0.5  # In the middle of the weight range

            random.random = fake_random

            for _ in range(5):
                call_count[0] = 0
                maybe_spawn_powerup(Vector2(0, 0))

            random.random = old_random

            # Check spawned powerups — they should all be EXTRA_LIFE
            powerup_gos = [go for go in _game_objects.values() if go.name.startswith("Powerup_")]
            assert len(powerup_gos) > 0, "No powerups were spawned"

            from examples.breakout.breakout_python.powerup import Powerup
            for go in powerup_gos:
                pu = go.get_component(Powerup)
                assert pu.powerup_type == PowerupType.EXTRA_LIFE, (
                    f"Expected EXTRA_LIFE but got {pu.powerup_type} — "
                    "weight mutation not respected"
                )

        finally:
            # Restore original weights
            for cfg, (orig_w, orig_t) in zip(POWERUP_CONFIGS, original_weights):
                cfg.weight = orig_w

    def test_color_lookup_uses_config(self):
        """_get_color reads from POWERUP_CONFIGS, not hardcoded values."""
        from examples.breakout.breakout_python.powerup import (
            POWERUP_CONFIGS,
            PowerupType,
            _get_color,
        )

        # Find the WIDE_PADDLE config and mutate its color
        for cfg in POWERUP_CONFIGS:
            if cfg.powerup_type == PowerupType.WIDE_PADDLE:
                original_color = cfg.color
                try:
                    cfg.color = (1, 2, 3)
                    result = _get_color(PowerupType.WIDE_PADDLE)
                    assert result == (1, 2, 3), (
                        f"Expected mutated color (1,2,3) but got {result} — "
                        "_get_color doesn't read from config"
                    )
                finally:
                    cfg.color = original_color
                break
