"""Mutation tests for Pacman V2 — monkeypatch breakage to prove test coverage.

Each test introduces a specific mutation and verifies the game behavior
changes as expected, proving the code under test is actually exercised.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.math.vector import Vector2


@pytest.fixture(autouse=True)
def clean_engine():
    """Reset engine state before each test."""
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager._instance = None
    from examples.pacman_v2.pacman_v2_python.game_manager import GameManager
    GameManager.instance = None
    yield
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager._instance = None
    from examples.pacman_v2.pacman_v2_python.game_manager import GameManager
    GameManager.instance = None


class TestMutationGhostFrightened:
    """Remove ghost.frightened -> Ghost always triggers pacman_eaten."""

    def test_removing_frightened_makes_ghost_always_eat_pacman(self, monkeypatch):
        """If ghost.frightened is None, on_collision_enter_2d always calls pacman_eaten."""
        from examples.pacman_v2.pacman_v2_python.ghost import Ghost
        from examples.pacman_v2.pacman_v2_python.ghost_home import GhostHome
        from examples.pacman_v2.pacman_v2_python.ghost_scatter import GhostScatter
        from examples.pacman_v2.pacman_v2_python.ghost_chase import GhostChase
        from examples.pacman_v2.pacman_v2_python.ghost_frightened import GhostFrightened
        from examples.pacman_v2.pacman_v2_python.movement import Movement
        from examples.pacman_v2.pacman_v2_python.game_manager import GameManager
        from examples.pacman_v2.pacman_v2_python.pacman import Pacman
        from src.engine.physics.rigidbody import Rigidbody2D

        # Set up GameManager
        pacman_go = GameObject("Pacman")
        pacman_go.layer = 3
        pacman_go.add_component(Rigidbody2D)
        pacman_go.add_component(Movement)
        pacman_comp = pacman_go.add_component(Pacman)

        gm_go = GameObject("GameManager")
        gm = gm_go.add_component(GameManager)

        # Ghost setup
        ghost_go = GameObject("TestGhost")
        ghost_go.layer = 7
        ghost_go.add_component(Rigidbody2D)
        movement = ghost_go.add_component(Movement)
        movement.speed = 7.0
        ghost_go.add_component(GhostHome)
        ghost_go.add_component(GhostScatter)
        ghost_go.add_component(GhostChase)
        frightened = ghost_go.add_component(GhostFrightened)
        ghost = ghost_go.add_component(Ghost)

        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        gm.pacman = pacman_comp
        gm.register_ghost(ghost)
        lm.process_start_queue()

        # Track calls
        calls = {"pacman_eaten": 0, "ghost_eaten": 0}

        def mock_pacman_eaten():
            calls["pacman_eaten"] += 1

        def mock_ghost_eaten(g):
            calls["ghost_eaten"] += 1

        gm.pacman_eaten = mock_pacman_eaten
        gm.ghost_eaten = mock_ghost_eaten

        # MUTATION: remove frightened reference
        ghost.frightened = None

        # Enable frightened on the actual component (it still exists, but ghost can't see it)
        frightened.ghost = ghost
        frightened.enable(8.0)

        # Collide with Pacman — should always eat pacman since frightened is None
        ghost.on_collision_enter_2d(pacman_go)

        assert calls["pacman_eaten"] == 1, (
            "With frightened=None, ghost should always eat pacman"
        )
        assert calls["ghost_eaten"] == 0, (
            "With frightened=None, ghost should never be eaten"
        )


class TestMutationMovementSpeedZero:
    """Setting Movement.speed to 0 should prevent all movement."""

    def test_speed_zero_prevents_movement(self, monkeypatch):
        """Pacman should not move if Movement.speed is set to 0."""
        from examples.pacman_v2.pacman_v2_python.movement import Movement
        from src.engine.physics.rigidbody import Rigidbody2D
        from src.engine.time_manager import Time

        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        go = GameObject("TestMover")
        rb = go.add_component(Rigidbody2D)
        movement = go.add_component(Movement)

        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        start_x = go.transform.position.x
        start_y = go.transform.position.y

        # Set direction but speed to 0
        movement.direction = Vector2(1, 0)
        monkeypatch.setattr(movement, "speed", 0)

        # Run several fixed_update frames
        Time._fixed_delta_time = 1.0 / 60.0
        for _ in range(60):
            movement.fixed_update()

        end_x = go.transform.position.x
        end_y = go.transform.position.y

        assert end_x == start_x, f"X should not change with speed=0, moved from {start_x} to {end_x}"
        assert end_y == start_y, "Y should not change with speed=0"


class TestMutationPelletPointsZero:
    """Setting pellet.points to 0 should keep score at 0 after eating."""

    def test_zero_points_pellets_give_no_score(self, monkeypatch):
        """Score stays 0 when all pellets have points=0."""
        from examples.pacman_v2.pacman_v2_python.pellet import Pellet
        from examples.pacman_v2.pacman_v2_python.game_manager import GameManager
        from examples.pacman_v2.pacman_v2_python.pacman import Pacman
        from examples.pacman_v2.pacman_v2_python.movement import Movement
        from src.engine.physics.rigidbody import Rigidbody2D

        # GameManager
        pacman_go = GameObject("Pacman")
        pacman_go.layer = 3
        pacman_go.add_component(Rigidbody2D)
        pacman_go.add_component(Movement)
        pacman_comp = pacman_go.add_component(Pacman)

        gm_go = GameObject("GameManager")
        gm = gm_go.add_component(GameManager)

        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        gm.pacman = pacman_comp

        # Create pellets with points monkeypatched to 0
        pellets = []
        for i in range(5):
            p_go = GameObject(f"Pellet_{i}")
            pellet = p_go.add_component(Pellet)
            monkeypatch.setattr(pellet, "points", 0)
            gm.register_pellet(pellet)
            pellets.append(pellet)

        lm.process_awake_queue()
        lm.process_start_queue()

        gm.score = 0

        # Eat all but one (to avoid triggering new_round)
        for pellet in pellets[:-1]:
            gm.pellet_eaten(pellet)

        assert gm.score == 0, (
            f"Score should be 0 with zero-point pellets, got {gm.score}"
        )
