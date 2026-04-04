"""Validation: Task 5 — module-level constants moved into classes.

Verifies that class-level constants are correctly defined and accessible,
and that backwards-compat aliases still work.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ---------------------------------------------------------------------------
# Contract tests: Layers class constants (player.py)
# ---------------------------------------------------------------------------

class TestLayersClassConstants:
    def test_layers_laser_value(self):
        from examples.space_invaders.space_invaders_python.player import Layers
        assert Layers.LASER == 8

    def test_layers_missile_value(self):
        from examples.space_invaders.space_invaders_python.player import Layers
        assert Layers.MISSILE == 9

    def test_layers_invader_value(self):
        from examples.space_invaders.space_invaders_python.player import Layers
        assert Layers.INVADER == 10

    def test_layers_boundary_value(self):
        from examples.space_invaders.space_invaders_python.player import Layers
        assert Layers.BOUNDARY == 11

    def test_backwards_compat_aliases(self):
        """Module-level aliases must still work for existing code."""
        from examples.space_invaders.space_invaders_python.player import (
            LAYER_LASER, LAYER_MISSILE, LAYER_INVADER, LAYER_BOUNDARY, Layers,
        )
        assert LAYER_LASER == Layers.LASER
        assert LAYER_MISSILE == Layers.MISSILE
        assert LAYER_INVADER == Layers.INVADER
        assert LAYER_BOUNDARY == Layers.BOUNDARY


# ---------------------------------------------------------------------------
# Contract tests: Bunker class constants (bunker.py)
# ---------------------------------------------------------------------------

class TestBunkerClassConstants:
    def test_grid_cols(self):
        from examples.space_invaders.space_invaders_python.bunker import Bunker
        assert Bunker.GRID_COLS == 16

    def test_grid_rows(self):
        from examples.space_invaders.space_invaders_python.bunker import Bunker
        assert Bunker.GRID_ROWS == 12

    def test_cell_size(self):
        from examples.space_invaders.space_invaders_python.bunker import Bunker
        assert Bunker.CELL_SIZE == 0.125


# ---------------------------------------------------------------------------
# Contract tests: Invaders.ROW_CONFIG (invaders.py)
# ---------------------------------------------------------------------------

class TestInvadersRowConfig:
    def test_row_config_has_5_entries(self):
        from examples.space_invaders.space_invaders_python.invaders import Invaders
        assert len(Invaders.ROW_CONFIG) == 5

    def test_row_config_scores(self):
        """Scores should be 10, 10, 20, 20, 30 (matching Unity C# reference)."""
        from examples.space_invaders.space_invaders_python.invaders import Invaders
        scores = [cfg.score for cfg in Invaders.ROW_CONFIG]
        assert scores == [10, 10, 20, 20, 30]


# ---------------------------------------------------------------------------
# Contract tests: LevelConfig.ROWS (run_breakout.py)
# ---------------------------------------------------------------------------

class TestLevelConfigRows:
    """LevelConfig and BrickRowConfig live in run_breakout.py which uses
    relative imports (breakout_python.*) that only resolve when the breakout
    directory is on sys.path.  We add it before importing."""

    @staticmethod
    def _import_level_config():
        _examples_breakout = os.path.join(
            os.path.dirname(__file__), "..", "..", "examples", "breakout"
        )
        if _examples_breakout not in sys.path:
            sys.path.insert(0, _examples_breakout)
        from run_breakout import LevelConfig
        return LevelConfig

    def test_rows_has_8_entries(self):
        LevelConfig = self._import_level_config()
        assert len(LevelConfig.ROWS) == 8

    def test_rows_points(self):
        """Points: 30, 30, 20, 20, 10, 10, 10, 10."""
        LevelConfig = self._import_level_config()
        points = [r.points for r in LevelConfig.ROWS]
        assert points == [30, 30, 20, 20, 10, 10, 10, 10]

    def test_rows_colors_are_tuples(self):
        LevelConfig = self._import_level_config()
        for row in LevelConfig.ROWS:
            assert isinstance(row.color, tuple) and len(row.color) == 3


# ---------------------------------------------------------------------------
# Integration: headless space_invaders uses Layers in collision setup
# ---------------------------------------------------------------------------

class TestSpaceInvadersLayerUsage:
    def test_boundary_uses_layers_constant(self):
        """Boundaries must be stamped with Layers.BOUNDARY layer value."""
        from examples.space_invaders.space_invaders_python.player import Layers
        from src.engine.core import GameObject

        boundary = GameObject("BoundaryTopTest", tag="Boundary")
        boundary.layer = Layers.BOUNDARY
        assert boundary.layer == 11

    def test_invader_grid_uses_layers_constant(self):
        """Invader GameObjects created by Invaders._create_invader_grid must have Layers.INVADER."""
        # invaders.py uses bare `from space_invaders_python.invader import ...`
        _si_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "examples", "space_invaders"
        )
        if _si_dir not in sys.path:
            sys.path.insert(0, _si_dir)

        from src.engine.core import GameObject
        from examples.space_invaders.space_invaders_python.player import Layers
        from examples.space_invaders.space_invaders_python.invaders import Invaders
        from src.engine.math.vector import Vector2

        grid_go = GameObject("InvadersGridTest")
        grid_go.transform.position = Vector2(0, 3)
        inv = grid_go.add_component(Invaders)
        # awake creates the grid
        inv.awake()

        # All children should have INVADER layer
        assert len(inv._invader_children) > 0
        for child in inv._invader_children:
            assert child.layer == Layers.INVADER, (
                f"{child.name} has layer {child.layer}, expected {Layers.INVADER}"
            )
