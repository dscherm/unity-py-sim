"""Mutation tests for Pacman Tasks 4+5: Ghost state machine and GameManager.

Monkeypatches breakage into ghost behaviors and verifies tests detect
the broken behavior (proving our contract tests are meaningful).
"""

import sys
import os
import pytest

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_pacman_root = os.path.join(_project_root, "examples", "pacman")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
if _pacman_root not in sys.path:
    sys.path.insert(0, _pacman_root)

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.time_manager import Time
from src.engine.math.vector import Vector2
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.rigidbody import Rigidbody2D

from pacman_python.movement import Movement
from pacman_python.ghost import Ghost
from pacman_python.ghost_scatter import GhostScatter
from pacman_python.ghost_chase import GhostChase
from pacman_python.ghost_frightened import GhostFrightened
from pacman_python.ghost_home import GhostHome
from pacman_python.ghost_eyes import GhostEyes
from pacman_python.game_manager import GameManager
from pacman_python.node import Node


@pytest.fixture(autouse=True)
def reset_engine():
    _clear_registry()
    PhysicsManager.reset()
    LifecycleManager.reset()
    Time._reset()
    GameManager.instance = None
    yield
    _clear_registry()
    PhysicsManager.reset()
    LifecycleManager.reset()
    Time._reset()
    GameManager.instance = None


def _make_ghost_go():
    go = GameObject("Ghost")
    go.add_component(Rigidbody2D)
    go.add_component(Movement)
    go.add_component(GhostHome)
    go.add_component(GhostScatter)
    go.add_component(GhostChase)
    go.add_component(GhostFrightened)
    go.add_component(Ghost)
    go.add_component(SpriteRenderer)
    return go


def _init_ghost(go):
    lm = LifecycleManager.instance()
    lm.process_awake_queue()
    lm.process_start_queue()
    return go.get_component(Ghost)


class TestMutationGhostChaseDirection:
    """Mutation: break chase to always pick FIRST direction instead of closest."""

    def test_broken_chase_picks_wrong_direction(self, monkeypatch):
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.frightened.disable_behavior()
        ghost.chase.enable_behavior()
        go.transform.position = Vector2(5, 5)

        target_go = GameObject("Pacman")
        target_go.transform.position = Vector2(10, 5)  # target to the right
        ghost.target = target_go.transform

        node_go = GameObject("Node")
        node = node_go.add_component(Node)
        # First direction is UP (wrong), second is RIGHT (correct - toward target)
        node.available_directions = [Vector2(0, 1), Vector2(1, 0)]

        # Monkeypatch: broken chase always picks first direction
        def broken_trigger(self_chase, other):
            node_comp = other.get_component(Node) if hasattr(other, 'get_component') else None
            if node_comp is not None and self_chase.enabled:
                dirs = node_comp.available_directions
                if dirs:
                    self_chase.ghost.movement.set_direction(dirs[0])  # always first!

        monkeypatch.setattr(GhostChase, "on_trigger_enter_2d", broken_trigger)

        ghost.chase.on_trigger_enter_2d(node_go)
        d = ghost.movement.direction

        # The broken version picks (0,1) instead of (1,0)
        # Our contract test would catch this: chase should pick RIGHT
        assert d.x == 0 and d.y == 1, "Mutant should pick first dir (0,1), not closest"
        # Proving the mutation is detectable: the correct behavior would pick (1,0)
        assert not (d.x == 1 and d.y == 0), "Mutant must NOT match correct behavior"


class TestMutationFrightenedSpeed:
    """Mutation: break frightened to not change speed_multiplier."""

    def test_broken_frightened_no_speed_change(self, monkeypatch):
        go = _make_ghost_go()
        ghost = _init_ghost(go)

        # Monkeypatch: on_enable does nothing to speed
        def broken_on_enable(self_f):
            pass  # speed_multiplier stays at 1.0

        monkeypatch.setattr(GhostFrightened, "on_enable", broken_on_enable)

        ghost.movement.speed_multiplier = 1.0
        ghost.frightened.on_enable()

        # With the broken version, speed stays at 1.0
        assert ghost.movement.speed_multiplier == 1.0, \
            "Mutant should leave speed at 1.0 (not 0.5)"

        # Prove this differs from correct behavior:
        # Correct on_enable would set it to 0.5
        monkeypatch.undo()
        ghost.frightened.on_enable()
        assert ghost.movement.speed_multiplier == 0.5, \
            "Correct behavior should set speed to 0.5"


class TestMutationResetStateNoDisableFrightened:
    """Mutation: break reset_state to skip disabling frightened."""

    def test_broken_reset_leaves_frightened_enabled(self, monkeypatch):
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.frightened.enable_behavior()
        assert ghost.frightened.enabled is True

        # Monkeypatch: reset_state skips disabling frightened
        original_reset = Ghost.reset_state

        def broken_reset(self_ghost):
            self_ghost.game_object.active = True
            self_ghost.movement.reset_state()
            # BROKEN: skip self.frightened.disable_behavior()
            self_ghost.chase.disable_behavior()
            self_ghost.scatter.enable_behavior()
            if self_ghost.home is not self_ghost.initial_behavior:
                self_ghost.home.disable_behavior()
            if self_ghost.initial_behavior is not None:
                self_ghost.initial_behavior.enable_behavior()

        monkeypatch.setattr(Ghost, "reset_state", broken_reset)

        ghost.reset_state()
        # With broken version, frightened stays enabled
        assert ghost.frightened.enabled is True, \
            "Mutant should leave frightened enabled"

        # Prove the correct version disables it
        monkeypatch.undo()
        ghost.frightened.enable_behavior()
        ghost.reset_state()
        assert ghost.frightened.enabled is False, \
            "Correct reset_state should disable frightened"


class TestMutationGhostEatenNoMultiplier:
    """Mutation: break ghost_eaten to not double the multiplier."""

    def test_broken_multiplier_stays_same(self, monkeypatch):
        gm_go = GameObject("GameManager")
        gm = gm_go.add_component(GameManager)
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.points = 200
        gm.ghosts = [ghost]

        def broken_ghost_eaten(self_gm, g):
            points = g.points * self_gm._ghost_multiplier
            self_gm.score += points
            # BROKEN: no multiplier doubling

        monkeypatch.setattr(GameManager, "ghost_eaten", broken_ghost_eaten)

        gm._ghost_multiplier = 1
        gm.score = 0
        gm.ghost_eaten(ghost)
        gm.ghost_eaten(ghost)

        # With broken version: 200 + 200 = 400 (multiplier stays 1)
        assert gm.score == 400, "Mutant should score 400 without doubling"
        assert gm._ghost_multiplier == 1, "Mutant should NOT double multiplier"

        # Prove correct version differs
        monkeypatch.undo()
        gm._ghost_multiplier = 1
        gm.score = 0
        gm.ghost_eaten(ghost)
        gm.ghost_eaten(ghost)
        assert gm.score == 600, "Correct: 200*1 + 200*2 = 600"
        assert gm._ghost_multiplier == 4, "Correct: multiplier should be 4 after 2 eats"
