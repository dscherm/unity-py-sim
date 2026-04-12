"""Contract tests for Pacman V2 — verify Unity behavioral specs.

These tests validate that components behave according to the Unity/zigurous
Pacman tutorial specifications, independent of implementation details.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.core import GameObject, MonoBehaviour, _clear_registry
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
    GameManager.instance = None


def _make_ghost_with_behaviors():
    """Create a minimal Ghost with all behavior components for unit testing."""
    from examples.pacman_v2.pacman_v2_python.movement import Movement
    from examples.pacman_v2.pacman_v2_python.ghost import Ghost
    from examples.pacman_v2.pacman_v2_python.ghost_home import GhostHome
    from examples.pacman_v2.pacman_v2_python.ghost_scatter import GhostScatter
    from examples.pacman_v2.pacman_v2_python.ghost_chase import GhostChase
    from examples.pacman_v2.pacman_v2_python.ghost_frightened import GhostFrightened
    from src.engine.physics.rigidbody import Rigidbody2D

    go = GameObject("TestGhost")
    go.layer = 7

    rb = go.add_component(Rigidbody2D)
    movement = go.add_component(Movement)
    movement.speed = 7.0
    movement.initial_direction = Vector2(-1, 0)

    home = go.add_component(GhostHome)
    scatter = go.add_component(GhostScatter)
    scatter.duration = 7.0
    chase = go.add_component(GhostChase)
    chase.duration = 20.0
    frightened = go.add_component(GhostFrightened)

    ghost = go.add_component(Ghost)

    # Process awake queue so Ghost.awake() runs and wires references
    lm = LifecycleManager.instance()
    lm.process_awake_queue()
    lm.process_start_queue()

    return ghost


def _make_game_manager_with_ghost(ghost):
    """Create a GameManager and register a ghost."""
    from examples.pacman_v2.pacman_v2_python.game_manager import GameManager
    from examples.pacman_v2.pacman_v2_python.pacman import Pacman
    from examples.pacman_v2.pacman_v2_python.movement import Movement
    from src.engine.physics.rigidbody import Rigidbody2D

    # Create Pacman
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
    gm.register_ghost(ghost)

    lm.process_start_queue()

    return gm


class TestGhostBehaviorCycling:
    """Scatter and Chase cycle: scatter enables chase on disable, and vice versa."""

    def test_scatter_enables_chase_on_disable(self):
        """When GhostScatter is disabled, it should enable GhostChase."""
        ghost = _make_ghost_with_behaviors()

        # Start with scatter enabled
        ghost.scatter.enable(7.0)
        ghost.chase.disable()

        assert ghost.scatter.enabled is True
        assert ghost.chase.enabled is False

        # Disable scatter — should trigger chase
        ghost.scatter.disable()
        assert ghost.chase.enabled is True

    def test_chase_enables_scatter_on_disable(self):
        """When GhostChase is disabled, it should enable GhostScatter."""
        ghost = _make_ghost_with_behaviors()

        ghost.chase.enable(20.0)
        ghost.scatter.disable()

        assert ghost.chase.enabled is True
        assert ghost.scatter.enabled is False

        # Disable chase — should trigger scatter
        ghost.chase.disable()
        assert ghost.scatter.enabled is True

    def test_behavior_cycle_round_trip(self):
        """Scatter -> disable -> chase -> disable -> scatter (full cycle)."""
        ghost = _make_ghost_with_behaviors()

        ghost.scatter.enable(7.0)
        ghost.chase.disable()
        ghost.frightened.disable()

        # Scatter -> Chase
        ghost.scatter.disable()
        assert ghost.chase.enabled is True

        # Chase -> Scatter
        ghost.chase.disable()
        assert ghost.scatter.enabled is True


class TestGhostFrightenedSpeed:
    """GhostFrightened must halve speed on enable and restore on disable."""

    def test_frightened_sets_speed_multiplier_to_half(self):
        """on_enable should set movement.speed_multiplier to 0.5."""
        ghost = _make_ghost_with_behaviors()
        movement = ghost.movement

        assert movement.speed_multiplier == 1.0

        # Must disable first so enable() triggers on_enable callback
        ghost.frightened.disable()
        ghost.frightened.enable(8.0)
        assert movement.speed_multiplier == 0.5

    def test_frightened_restores_speed_on_disable(self):
        """on_disable should restore movement.speed_multiplier to 1.0."""
        ghost = _make_ghost_with_behaviors()
        movement = ghost.movement

        ghost.frightened.disable()
        ghost.frightened.enable(8.0)
        assert movement.speed_multiplier == 0.5

        ghost.frightened.disable()
        assert movement.speed_multiplier == 1.0


class TestMovementOccupied:
    """Movement.occupied() should detect walls via physics overlap."""

    def test_occupied_returns_false_in_open_space(self):
        """occupied() returns False when no wall is adjacent."""
        from examples.pacman_v2.pacman_v2_python.movement import Movement
        from src.engine.physics.rigidbody import Rigidbody2D

        go = GameObject("TestMover")
        go.add_component(Rigidbody2D)
        movement = go.add_component(Movement)

        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        # Place in open space — no walls anywhere
        go.transform.position = Vector2(100, 100)

        result = movement.occupied(Vector2(1, 0))
        assert result is False, "occupied() should be False in open space"

    def test_occupied_returns_true_when_wall_adjacent(self):
        """occupied() returns True when a wall collider is adjacent."""
        from examples.pacman_v2.pacman_v2_python.movement import Movement, OBSTACLE_LAYER
        from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
        from src.engine.physics.collider import BoxCollider2D

        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        # Create a wall to the right of the mover
        wall_go = GameObject("TestWall")
        wall_go.layer = OBSTACLE_LAYER
        wall_go.transform.position = Vector2(1, 0)
        wall_rb = wall_go.add_component(Rigidbody2D)
        wall_rb.body_type = RigidbodyType2D.STATIC
        wall_col = wall_go.add_component(BoxCollider2D)
        wall_col.size = Vector2(1.0, 1.0)

        # Create mover at origin
        mover_go = GameObject("TestMover")
        mover_go.add_component(Rigidbody2D)
        movement = mover_go.add_component(Movement)

        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        mover_go.transform.position = Vector2(0, 0)

        # Step physics so colliders are registered
        pm.step(1.0 / 60.0)

        result = movement.occupied(Vector2(1, 0))
        assert result is True, "occupied() should be True when wall is adjacent"


class TestPelletBehavior:
    """Pellet deactivates its GameObject when eaten."""

    def test_pellet_deactivates_on_eat(self):
        """Pellet.eat() should deactivate its game_object via GameManager."""
        from examples.pacman_v2.pacman_v2_python.pellet import Pellet
        from examples.pacman_v2.pacman_v2_python.game_manager import GameManager
        from examples.pacman_v2.pacman_v2_python.pacman import Pacman
        from examples.pacman_v2.pacman_v2_python.movement import Movement
        from src.engine.physics.rigidbody import Rigidbody2D

        # Set up GameManager
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

        # Create pellet
        pellet_go = GameObject("TestPellet")
        pellet = pellet_go.add_component(Pellet)
        gm.register_pellet(pellet)

        lm.process_awake_queue()
        lm.process_start_queue()

        assert pellet_go.active is True

        pellet.eat()
        assert pellet_go.active is False, "Pellet GO should be deactivated after eat()"


class TestGameManagerScoring:
    """GameManager scoring contracts."""

    def test_pellet_eaten_increments_score_by_pellet_points(self):
        """pellet_eaten should increase score by pellet.points."""
        from examples.pacman_v2.pacman_v2_python.pellet import Pellet
        from examples.pacman_v2.pacman_v2_python.game_manager import GameManager
        from examples.pacman_v2.pacman_v2_python.pacman import Pacman
        from examples.pacman_v2.pacman_v2_python.movement import Movement
        from src.engine.physics.rigidbody import Rigidbody2D

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

        pellet_go = GameObject("Pellet")
        pellet = pellet_go.add_component(Pellet)
        pellet.points = 10
        gm.register_pellet(pellet)

        # Add a second pellet so eating one doesn't trigger new_round
        pellet2_go = GameObject("Pellet2")
        pellet2 = pellet2_go.add_component(Pellet)
        gm.register_pellet(pellet2)

        lm.process_awake_queue()
        lm.process_start_queue()

        gm.score = 0
        gm.pellet_eaten(pellet)
        assert gm.score == 10, f"Expected score 10, got {gm.score}"

    def test_ghost_eaten_awards_200_times_multiplier(self):
        """ghost_eaten awards ghost.points * multiplier and increments multiplier."""
        ghost = _make_ghost_with_behaviors()
        gm = _make_game_manager_with_ghost(ghost)

        gm.score = 0
        gm.ghost_multiplier = 1

        # Need frightened enabled and not eaten for ghost_eaten to work
        ghost.frightened.enable(8.0)

        gm.ghost_eaten(ghost)
        assert gm.score == 200, f"First ghost: expected 200, got {gm.score}"
        assert gm.ghost_multiplier == 2

        # Second ghost at 2x
        ghost2 = _make_ghost_with_behaviors()
        ghost2.frightened.enable(8.0)
        gm.register_ghost(ghost2)

        gm.ghost_eaten(ghost2)
        assert gm.score == 200 + 400, f"Second ghost: expected 600, got {gm.score}"
        assert gm.ghost_multiplier == 3


class TestPowerPelletCallsCorrectMethod:
    """PowerPellet.eat must call GameManager.power_pellet_eaten, NOT pellet_eaten."""

    def test_power_pellet_eat_calls_power_pellet_eaten(self):
        """PowerPellet.eat() should invoke power_pellet_eaten."""
        from examples.pacman_v2.pacman_v2_python.power_pellet import PowerPellet
        from examples.pacman_v2.pacman_v2_python.game_manager import GameManager
        from examples.pacman_v2.pacman_v2_python.pacman import Pacman
        from examples.pacman_v2.pacman_v2_python.movement import Movement
        from src.engine.physics.rigidbody import Rigidbody2D

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

        pp_go = GameObject("TestPowerPellet")
        pp = pp_go.add_component(PowerPellet)
        pp.points = 50
        gm.register_pellet(pp)

        # Track which method gets called
        calls = {"pellet": 0, "power": 0}
        original_pe = gm.pellet_eaten
        original_ppe = gm.power_pellet_eaten

        def mock_pellet_eaten(pellet):
            calls["pellet"] += 1
            original_pe(pellet)

        def mock_power_pellet_eaten(pellet):
            calls["power"] += 1
            original_ppe(pellet)

        gm.pellet_eaten = mock_pellet_eaten
        gm.power_pellet_eaten = mock_power_pellet_eaten

        lm.process_awake_queue()
        lm.process_start_queue()

        pp.eat()

        assert calls["power"] == 1, "PowerPellet should call power_pellet_eaten"
        # power_pellet_eaten chains into pellet_eaten for deactivation + remaining check
        assert calls["pellet"] == 1, "power_pellet_eaten should chain into pellet_eaten"
