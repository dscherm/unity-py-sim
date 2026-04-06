"""Contract tests for Pacman Tasks 4+5: Ghost state machine and GameManager.

Validates behavior contracts derived from Unity reference (zigurous/unity-pacman-tutorial).
"""

import sys
import os
import pytest

# Project root on sys.path (for src.engine imports); examples/pacman for pacman_python imports
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_pacman_root = os.path.join(_project_root, "examples", "pacman")
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
if _pacman_root not in sys.path:
    sys.path.insert(0, _pacman_root)

from src.engine.core import GameObject, _clear_registry, MonoBehaviour
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.time_manager import Time
from src.engine.math.vector import Vector2
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.rigidbody import Rigidbody2D

from pacman_python.movement import Movement
from pacman_python.ghost import Ghost, PACMAN_LAYER
from pacman_python.ghost_behavior import GhostBehavior
from pacman_python.ghost_scatter import GhostScatter
from pacman_python.ghost_chase import GhostChase
from pacman_python.ghost_frightened import GhostFrightened
from pacman_python.ghost_home import GhostHome
from pacman_python.ghost_eyes import GhostEyes
from pacman_python.game_manager import GameManager
from pacman_python.node import Node


@pytest.fixture(autouse=True)
def reset_engine():
    """Reset all engine singletons between tests."""
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


def _make_ghost_go(name="Blinky"):
    """Create a fully-wired ghost GameObject with all behavior components."""
    go = GameObject(name)
    go.add_component(Rigidbody2D)
    go.add_component(Movement)
    go.add_component(GhostHome)
    go.add_component(GhostScatter)
    go.add_component(GhostChase)
    go.add_component(GhostFrightened)
    go.add_component(Ghost)
    go.add_component(GhostEyes)
    go.add_component(SpriteRenderer)
    return go


def _init_ghost(go):
    """Run awake+start lifecycle on all components of a ghost GO."""
    lm = LifecycleManager.instance()
    lm.process_awake_queue()
    lm.process_start_queue()
    return go.get_component(Ghost)


def _make_pacman_target():
    """Create a simple target Transform for chase behavior."""
    target_go = GameObject("Pacman")
    target_go.transform.position = Vector2(10, 10)
    return target_go.transform


# ---------------------------------------------------------------------------
# GhostBehavior base
# ---------------------------------------------------------------------------

class TestGhostBehaviorContract:
    def test_enable_behavior_sets_enabled_true(self):
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.scatter.disable_behavior()
        assert ghost.scatter.enabled is False
        ghost.scatter.enable_behavior()
        assert ghost.scatter.enabled is True

    def test_disable_behavior_sets_enabled_false(self):
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.scatter.enable_behavior()
        assert ghost.scatter.enabled is True
        ghost.scatter.disable_behavior()
        assert ghost.scatter.enabled is False

    def test_enable_with_zero_duration_no_auto_disable(self):
        """duration=0 should NOT auto-disable (no timer started)."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.scatter.enable_behavior(0.0)
        assert ghost.scatter.enabled is True


# ---------------------------------------------------------------------------
# GhostScatter
# ---------------------------------------------------------------------------

class TestGhostScatterContract:
    def test_on_disable_enables_chase(self):
        """Unity ref: GhostScatter.OnDisable enables chase behavior."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.chase.disable_behavior()
        assert ghost.chase.enabled is False

        ghost.scatter.on_disable()
        assert ghost.chase.enabled is True

    def test_picks_direction_from_available(self):
        """Scatter should pick a direction from the node's available list."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.frightened.disable_behavior()
        ghost.scatter.enable_behavior()
        ghost.movement.direction = Vector2(1, 0)

        # Create a node with known available directions
        node_go = GameObject("Node")
        node = node_go.add_component(Node)
        node.available_directions = [Vector2(0, 1), Vector2(1, 0)]

        ghost.scatter.on_trigger_enter_2d(node_go)

        d = ghost.movement.direction
        valid = any(
            d.x == v.x and d.y == v.y
            for v in [Vector2(0, 1), Vector2(1, 0)]
        )
        assert valid, f"Direction {d} not in available list"

    def test_avoids_reverse_direction(self):
        """Scatter should avoid picking the reverse of current direction."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.frightened.disable_behavior()
        ghost.scatter.enable_behavior()

        node_go = GameObject("Node")
        node = node_go.add_component(Node)
        # Only two choices: reverse (-1,0) and forward (0,1)
        node.available_directions = [Vector2(-1, 0), Vector2(0, 1)]

        # Run many times to verify it never picks the reverse
        for _ in range(20):
            # Reset direction each iteration so reverse is always (-1,0)
            ghost.movement.direction = Vector2(1, 0)
            ghost.scatter.on_trigger_enter_2d(node_go)
            d = ghost.movement.direction
            assert not (d.x == -1 and d.y == 0), "Scatter should avoid reverse direction"


# ---------------------------------------------------------------------------
# GhostChase
# ---------------------------------------------------------------------------

class TestGhostChaseContract:
    def test_on_disable_enables_scatter(self):
        """Unity ref: GhostChase.OnDisable enables scatter behavior."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.scatter.disable_behavior()
        assert ghost.scatter.enabled is False

        ghost.chase.on_disable()
        assert ghost.scatter.enabled is True

    def test_picks_direction_minimizing_distance_to_target(self):
        """Chase picks the direction that minimizes sqrMagnitude to target."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.frightened.disable_behavior()
        ghost.chase.enable_behavior()
        go.transform.position = Vector2(5, 5)

        target = _make_pacman_target()
        target.position = Vector2(10, 5)  # Target is to the right
        ghost.target = target

        node_go = GameObject("Node")
        node = node_go.add_component(Node)
        node.available_directions = [
            Vector2(1, 0),   # right — toward target
            Vector2(-1, 0),  # left — away from target
            Vector2(0, 1),   # up
        ]

        ghost.chase.on_trigger_enter_2d(node_go)
        d = ghost.movement.direction
        assert d.x == 1 and d.y == 0, f"Chase should pick right (toward target), got ({d.x},{d.y})"


# ---------------------------------------------------------------------------
# GhostFrightened
# ---------------------------------------------------------------------------

class TestGhostFrightenedContract:
    def test_on_enable_sets_speed_multiplier_half(self):
        """Unity ref: frightened mode halves ghost speed."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.frightened.on_enable()
        assert ghost.movement.speed_multiplier == 0.5

    def test_on_disable_restores_speed_multiplier(self):
        """Unity ref: leaving frightened restores normal speed."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.frightened.on_enable()
        assert ghost.movement.speed_multiplier == 0.5
        ghost.frightened.on_disable()
        assert ghost.movement.speed_multiplier == 1.0

    def test_picks_direction_maximizing_distance_from_target(self):
        """Frightened picks direction that maximizes sqrMagnitude from target."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.frightened.enable_behavior()
        go.transform.position = Vector2(5, 5)

        target = _make_pacman_target()
        target.position = Vector2(10, 5)  # Target to the right
        ghost.target = target

        node_go = GameObject("Node")
        node = node_go.add_component(Node)
        node.available_directions = [
            Vector2(1, 0),   # right — toward target (BAD)
            Vector2(-1, 0),  # left — away from target (GOOD)
        ]

        ghost.frightened.on_trigger_enter_2d(node_go)
        d = ghost.movement.direction
        assert d.x == -1 and d.y == 0, f"Frightened should flee left, got ({d.x},{d.y})"

    def test_enable_hides_body_and_eyes(self):
        """Unity ref: frightened mode hides normal body and eyes sprites."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        body = SpriteRenderer()
        eyes = SpriteRenderer()
        ghost.frightened.body = body
        ghost.frightened.eyes = eyes
        body.enabled = True
        eyes.enabled = True

        ghost.frightened.enable_behavior()
        assert body.enabled is False
        assert eyes.enabled is False

    def test_disable_restores_body_and_eyes(self):
        """Unity ref: leaving frightened restores normal sprites."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        body = SpriteRenderer()
        eyes = SpriteRenderer()
        ghost.frightened.body = body
        ghost.frightened.eyes = eyes

        ghost.frightened.enable_behavior()
        ghost.frightened.disable_behavior()
        assert body.enabled is True
        assert eyes.enabled is True


# ---------------------------------------------------------------------------
# Ghost (aggregator)
# ---------------------------------------------------------------------------

class TestGhostContract:
    def test_reset_state_disables_frightened_and_chase(self):
        """Unity ref: reset_state disables frightened and chase."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.frightened.enable_behavior()
        ghost.chase.enable_behavior()

        ghost.reset_state()
        assert ghost.frightened.enabled is False
        assert ghost.chase.enabled is False

    def test_reset_state_enables_scatter(self):
        """Unity ref: reset_state enables scatter."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.scatter.disable_behavior()

        ghost.reset_state()
        assert ghost.scatter.enabled is True

    def test_reset_state_activates_game_object(self):
        """Unity ref: reset_state sets game_object.active = True."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        go.active = False

        ghost.reset_state()
        assert go.active is True

    def test_collision_frightened_calls_ghost_eaten(self):
        """Unity ref: collision with Pacman while frightened -> ghost eaten."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.frightened.enable_behavior()

        # Set up GameManager
        gm_go = GameObject("GameManager")
        gm = gm_go.add_component(GameManager)
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        gm.ghosts = [ghost]
        gm.pacman = None

        initial_score = gm.score

        # Create pacman collision object
        pacman_go = GameObject("Pacman")
        pacman_go.layer = PACMAN_LAYER

        class FakeCollision:
            game_object = pacman_go

        ghost.on_collision_enter_2d(FakeCollision())
        assert gm.score > initial_score, "ghost_eaten should increase score"

    def test_collision_not_frightened_calls_pacman_eaten(self):
        """Unity ref: collision with Pacman while NOT frightened -> pacman eaten."""
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.frightened.disable_behavior()

        # Set up GameManager with mock pacman
        gm_go = GameObject("GameManager")
        gm = gm_go.add_component(GameManager)
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        gm.ghosts = [ghost]

        class MockPacman:
            def __init__(self):
                self.death_called = False
                self.game_object = GameObject("PacmanGO")
            def death_sequence_start(self):
                self.death_called = True
            def reset_state(self):
                pass

        mock_pac = MockPacman()
        gm.pacman = mock_pac
        initial_lives = gm.lives

        pacman_go = GameObject("PacmanCollider")
        pacman_go.layer = PACMAN_LAYER

        class FakeCollision:
            game_object = pacman_go

        ghost.on_collision_enter_2d(FakeCollision())
        assert gm.lives == initial_lives - 1, "pacman_eaten should decrement lives"


# ---------------------------------------------------------------------------
# GhostEyes
# ---------------------------------------------------------------------------

class TestGhostEyesContract:
    def _make_eyes(self, direction):
        go = _make_ghost_go()
        _init_ghost(go)
        eyes_comp = go.get_component(GhostEyes)
        sr = go.get_component(SpriteRenderer)
        eyes_comp.sprite_renderer = sr
        eyes_comp.movement = go.get_component(Movement)
        eyes_comp.movement.direction = direction
        eyes_comp.update()
        return sr

    def test_direction_up(self):
        sr = self._make_eyes(Vector2(0, 1))
        assert sr.asset_ref == "ghost_eyes_up"

    def test_direction_down(self):
        sr = self._make_eyes(Vector2(0, -1))
        assert sr.asset_ref == "ghost_eyes_down"

    def test_direction_left(self):
        sr = self._make_eyes(Vector2(-1, 0))
        assert sr.asset_ref == "ghost_eyes_left"

    def test_direction_right(self):
        sr = self._make_eyes(Vector2(1, 0))
        assert sr.asset_ref == "ghost_eyes_right"


# ---------------------------------------------------------------------------
# GameManager
# ---------------------------------------------------------------------------

class TestGameManagerContract:
    def _make_gm(self):
        gm_go = GameObject("GameManager")
        gm = gm_go.add_component(GameManager)
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        return gm

    def test_singleton_pattern(self):
        gm = self._make_gm()
        assert GameManager.instance is gm

    def test_ghost_eaten_awards_points_times_multiplier(self):
        """Unity ref: ghost_eaten awards ghost.points * ghost_multiplier."""
        gm = self._make_gm()
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.points = 200
        gm.ghosts = [ghost]

        gm._ghost_multiplier = 1
        gm.score = 0
        gm.ghost_eaten(ghost)
        assert gm.score == 200

    def test_ghost_eaten_doubles_multiplier(self):
        """Unity ref: each ghost_eaten doubles the multiplier."""
        gm = self._make_gm()
        go = _make_ghost_go()
        ghost = _init_ghost(go)
        ghost.points = 200
        gm.ghosts = [ghost]

        gm._ghost_multiplier = 1
        gm.score = 0
        gm.ghost_eaten(ghost)
        assert gm._ghost_multiplier == 2
        gm.ghost_eaten(ghost)
        assert gm._ghost_multiplier == 4
        # Second ghost should award 200*2=400
        assert gm.score == 200 + 400

    def test_pacman_eaten_decrements_lives(self):
        """Unity ref: pacman_eaten decrements lives by 1."""
        gm = self._make_gm()
        gm.lives = 3

        class MockPacman:
            def __init__(self):
                self.game_object = GameObject("PacmanGO")
            def death_sequence_start(self):
                pass
            def reset_state(self):
                pass

        gm.pacman = MockPacman()
        gm.ghosts = []
        gm.pacman_eaten()
        assert gm.lives == 2

    def test_game_over_disables_all_ghosts_and_pacman(self):
        """Unity ref: game_over sets all ghost GOs and pacman GO inactive."""
        gm = self._make_gm()

        ghost_gos = []
        ghosts = []
        for name in ["Blinky", "Pinky"]:
            go = _make_ghost_go(name)
            ghost = _init_ghost(go)
            ghosts.append(ghost)
            ghost_gos.append(go)

        gm.ghosts = ghosts

        pac_go = GameObject("Pacman")

        class MockPacman:
            game_object = pac_go
            def reset_state(self):
                pass

        gm.pacman = MockPacman()

        gm.game_over()
        for go in ghost_gos:
            assert go.active is False, f"{go.name} should be inactive after game_over"
        assert pac_go.active is False, "Pacman should be inactive after game_over"

    def test_new_game_resets_score_and_lives(self):
        """Unity ref: new_game resets score=0, lives=3."""
        gm = self._make_gm()
        gm.score = 5000
        gm.lives = 0
        gm.ghosts = []
        gm.pacman = None
        gm.new_game()
        assert gm.score == 0
        assert gm.lives == 3

    def test_power_pellet_resets_ghost_multiplier(self):
        """Unity ref: power_pellet_eaten resets ghost_multiplier to 1."""
        gm = self._make_gm()
        gm._ghost_multiplier = 4

        go = _make_ghost_go()
        ghost = _init_ghost(go)
        gm.ghosts = [ghost]
        gm.pacman = None

        class FakePellet:
            game_object = GameObject("Pellet")
            points = 50
            duration = 7.0

        gm.power_pellet_eaten(FakePellet())
        assert gm._ghost_multiplier == 1
