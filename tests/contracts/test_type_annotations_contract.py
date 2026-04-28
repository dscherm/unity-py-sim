"""Contract tests — verify type annotations exist on all Space Invaders and Breakout example files.

Task 6 added full type annotations to all 13 example files. These tests verify
annotations are present using Python's inspect and typing modules, NOT by reading
the implementation — purely checking that the annotation contract holds.
"""
from __future__ import annotations

import sys
import os
import typing

import pytest

# Ensure examples are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "examples", "space_invaders"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "examples", "breakout"))


# ---------------------------------------------------------------------------
# Space Invaders
# ---------------------------------------------------------------------------

class TestSpaceInvadersInitAnnotations:
    """All MonoBehaviour subclasses in space_invaders/ must have __init__ -> None."""

    @pytest.fixture(autouse=True)
    def _import_modules(self):
        from space_invaders_python.player import Player
        from space_invaders_python.invaders import Invaders
        from space_invaders_python.invader import Invader
        from space_invaders_python.projectile import Projectile
        from space_invaders_python.bunker import Bunker
        from space_invaders_python.mystery_ship import MysteryShip
        from space_invaders_python.game_manager import GameManager

        self.classes = [Player, Invaders, Invader, Projectile, Bunker, MysteryShip, GameManager]

    def test_all_init_return_none(self):
        """Every MonoBehaviour subclass __init__ must annotate -> None."""
        for cls in self.classes:
            hints = typing.get_type_hints(cls.__init__)
            assert "return" in hints, f"{cls.__name__}.__init__ missing return annotation"
            assert hints["return"] is type(None), (
                f"{cls.__name__}.__init__ return annotation should be None, got {hints['return']}"
            )


class TestPlayerAnnotations:
    """Player method annotations."""

    @pytest.fixture(autouse=True)
    def _import(self):
        from space_invaders_python.player import Player
        self.Player = Player

    def test_update_returns_none(self):
        hints = typing.get_type_hints(self.Player.update)
        assert hints.get("return") is type(None)

    def test_instantiate_laser_returns_game_object(self):
        from src.engine.core import GameObject
        hints = typing.get_type_hints(self.Player._instantiate_laser)
        assert hints.get("return") is GameObject, (
            f"Expected GameObject, got {hints.get('return')}"
        )

    def test_on_trigger_enter_2d_other_annotated(self):
        from src.engine.core import GameObject
        hints = typing.get_type_hints(self.Player.on_trigger_enter_2d)
        assert "other" in hints, "on_trigger_enter_2d missing 'other' param annotation"
        assert hints["other"] is GameObject


class TestInvadersAnnotations:
    """Invaders method annotations."""

    @pytest.fixture(autouse=True)
    def _import(self):
        from space_invaders_python.invaders import Invaders
        self.Invaders = Invaders

    def test_create_invader_grid_returns_none(self):
        hints = typing.get_type_hints(self.Invaders._create_invader_grid)
        assert hints.get("return") is type(None)

    def test_get_alive_count_returns_int(self):
        hints = typing.get_type_hints(self.Invaders.get_alive_count)
        assert hints.get("return") is int

    def test_instantiate_missile_position_annotated(self):
        from src.engine.math.vector import Vector2
        hints = typing.get_type_hints(self.Invaders._instantiate_missile)
        assert "position" in hints
        assert hints["position"] is Vector2


class TestBrickAnnotations:
    """Breakout Brick — on_collision_enter_2d collision param annotated."""

    def test_collision_param_annotated(self):
        from breakout_python.brick import Brick
        from src.engine.physics.physics_manager import Collision2D
        hints = typing.get_type_hints(Brick.on_collision_enter_2d)
        assert "collision" in hints, "Brick.on_collision_enter_2d missing 'collision' annotation"
        assert hints["collision"] is Collision2D


class TestBreakoutGameManagerAnnotations:
    """All public static methods in Breakout GameManager have return annotations."""

    @pytest.fixture(autouse=True)
    def _import(self):
        from breakout_python.game_manager import GameManager
        self.GM = GameManager

    def test_public_methods_have_return_annotations(self):
        public_methods = [
            "start", "reset", "add_score", "on_ball_lost", "on_brick_destroyed",
        ]
        for name in public_methods:
            method = getattr(self.GM, name)
            hints = typing.get_type_hints(method)
            assert "return" in hints, (
                f"Breakout GameManager.{name} missing return annotation"
            )


class TestSpotCheckParamAnnotations:
    """Spot-check 5+ methods across files for parameter annotations."""

    def test_projectile_check_collision_other_annotated(self):
        from space_invaders_python.projectile import Projectile
        from src.engine.core import GameObject
        hints = typing.get_type_hints(Projectile._check_collision)
        assert "other" in hints
        assert hints["other"] is GameObject

    def test_bunker_check_collision_params(self):
        from space_invaders_python.bunker import Bunker
        try:
            hints = typing.get_type_hints(Bunker.check_collision)
        except TypeError:
            # Python 3.9 can't evaluate X | None in get_type_hints even with
            # from __future__ import annotations. Fall back to raw annotations.
            hints = typing.get_type_hints(Bunker.check_collision, include_extras=False) if sys.version_info >= (3, 10) else Bunker.check_collision.__annotations__
        assert "hit_point" in hints, "Bunker.check_collision missing hit_point annotation"

    def test_mystery_ship_init_returns_none(self):
        from space_invaders_python.mystery_ship import MysteryShip
        hints = typing.get_type_hints(MysteryShip.__init__)
        assert hints.get("return") is type(None)

    def test_powerup_apply_paddle_annotated(self):
        from breakout_python.powerup import Powerup
        from src.engine.core import GameObject
        hints = typing.get_type_hints(Powerup._apply)
        assert "paddle" in hints
        assert hints["paddle"] is GameObject

    def test_ball_controller_launch_returns_none(self):
        from breakout_python.ball_controller import BallController
        hints = typing.get_type_hints(BallController.launch)
        assert hints.get("return") is type(None)

    def test_paddle_controller_update_returns_none(self):
        from breakout_python.paddle_controller import PaddleController
        hints = typing.get_type_hints(PaddleController.update)
        assert hints.get("return") is type(None)

    def test_prefabs_register_returns_none(self):
        from space_invaders_python.prefabs import register_prefabs
        hints = typing.get_type_hints(register_prefabs)
        assert hints.get("return") is type(None)

    def test_prefabs_setup_laser_go_annotated(self):
        from space_invaders_python.prefabs import _setup_laser
        from src.engine.core import GameObject
        hints = typing.get_type_hints(_setup_laser)
        assert "go" in hints
        assert hints["go"] is GameObject
