"""Integration tests for @serializable dataclass configs in Space Invaders and Breakout.

Validates that the dataclass-based config objects work correctly when used
through the actual game setup and game loop.
"""

import sys
import os
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


class TestInvaderRowConfigIntegration:
    """Verify InvaderRowConfig dataclass works in actual game setup."""

    def test_invader_row_config_instantiation(self):
        """InvaderRowConfig can be created with keyword args."""
        from examples.space_invaders.space_invaders_python.invaders import InvaderRowConfig

        cfg = InvaderRowConfig(
            animation_sprites=[(255, 0, 0), (200, 0, 0)],
            score=50,
        )
        assert cfg.animation_sprites == [(255, 0, 0), (200, 0, 0)]
        assert cfg.score == 50

    def test_invader_row_config_default_score(self):
        """InvaderRowConfig defaults score to 10."""
        from examples.space_invaders.space_invaders_python.invaders import InvaderRowConfig

        cfg = InvaderRowConfig(animation_sprites=[(1, 2, 3)])
        assert cfg.score == 10

    def test_row_config_list_has_correct_entries(self):
        """Invaders.ROW_CONFIG is a list of InvaderRowConfig with expected length and types."""
        from examples.space_invaders.space_invaders_python.invaders import (
            Invaders,
            InvaderRowConfig,
        )

        assert len(Invaders.ROW_CONFIG) == 5
        for cfg in Invaders.ROW_CONFIG:
            assert isinstance(cfg, InvaderRowConfig)
            assert isinstance(cfg.score, int)
            assert isinstance(cfg.animation_sprites, list)
            assert len(cfg.animation_sprites) >= 1

    def test_invader_gets_score_from_config(self):
        """When Invaders grid creates invaders, each gets score from InvaderRowConfig."""
        # Add example dir to sys.path so internal imports resolve
        example_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "examples", "space_invaders"
        )
        sys.path.insert(0, os.path.abspath(example_dir))
        try:
            from examples.space_invaders.space_invaders_python.invaders import (
                Invaders,
            )
            from src.engine.math.vector import Vector2

            grid_go = GameObject("InvadersGrid")
            grid_go.transform.position = Vector2(0, 3)
            inv_grid = grid_go.add_component(Invaders)
            # awake creates the grid
            LifecycleManager.instance().process_awake_queue()

            # Find all invader game objects
            invader_gos = [go for go in _game_objects.values() if go.name.startswith("Invader_")]
            assert len(invader_gos) > 0

            # Use the same import path that invaders.py uses internally
            from space_invaders_python.invader import Invader

            # Check that row 0 invaders have the score from ROW_CONFIG[0]
            row0_go = [go for go in invader_gos if go.name.startswith("Invader_0_")]
            for go in row0_go:
                inv_comp = go.get_component(Invader)
                assert inv_comp is not None
                assert inv_comp.score == Invaders.ROW_CONFIG[0].score
        finally:
            sys.path.remove(os.path.abspath(example_dir))

    def test_space_invaders_headless_runs(self):
        """Space Invaders runs headless for a few frames without crashing."""
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "--co", "-q"],
            capture_output=True, text=True, cwd=os.path.join(
                os.path.dirname(__file__), "..", "..",
            ),
        )
        # Use the playtest wrapper approach: run as subprocess
        result = subprocess.run(
            [
                sys.executable,
                os.path.join(
                    os.path.dirname(__file__), "..", "..",
                    "examples", "space_invaders", "run_space_invaders.py",
                ),
                "--headless", "--frames", "5",
            ],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"Space Invaders failed:\n{result.stderr}"


class TestPowerupConfigIntegration:
    """Verify PowerupConfig dataclass works in breakout."""

    def test_powerup_config_instantiation(self):
        """PowerupConfig can be created with all fields."""
        from examples.breakout.breakout_python.powerup import PowerupConfig, PowerupType

        cfg = PowerupConfig(
            powerup_type=PowerupType.EXTRA_LIFE,
            color=(255, 0, 0),
            weight=0.5,
        )
        assert cfg.powerup_type == PowerupType.EXTRA_LIFE
        assert cfg.color == (255, 0, 0)
        assert cfg.weight == 0.5

    def test_powerup_configs_list_structure(self):
        """POWERUP_CONFIGS is a list of PowerupConfig with correct types."""
        from examples.breakout.breakout_python.powerup import (
            POWERUP_CONFIGS,
            PowerupConfig,
            PowerupType,
        )

        assert len(POWERUP_CONFIGS) == 3
        for cfg in POWERUP_CONFIGS:
            assert isinstance(cfg, PowerupConfig)
            assert isinstance(cfg.powerup_type, PowerupType)
            assert isinstance(cfg.weight, float)
            assert isinstance(cfg.color, tuple)

    def test_powerup_configs_weights_sum_to_one(self):
        """Powerup weights should sum to 1.0 for correct probability distribution."""
        from examples.breakout.breakout_python.powerup import POWERUP_CONFIGS

        total = sum(cfg.weight for cfg in POWERUP_CONFIGS)
        assert abs(total - 1.0) < 0.001

    def test_breakout_headless_runs(self):
        """Breakout runs headless for a few frames without crashing."""
        import subprocess
        result = subprocess.run(
            [
                sys.executable,
                os.path.join(
                    os.path.dirname(__file__), "..", "..",
                    "examples", "breakout", "run_breakout.py",
                ),
                "--headless", "--frames", "5",
            ],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"Breakout failed:\n{result.stderr}"
