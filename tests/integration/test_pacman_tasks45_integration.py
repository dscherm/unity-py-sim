"""Integration tests for Pacman Tasks 4+5: Ghost state machine and GameManager.

Validates that ghosts and game manager wire up correctly and run through
the game loop without errors.
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

from src.engine.core import GameObject, _clear_registry, MonoBehaviour
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


def _create_ghost(name, position=None):
    """Create a ghost GO with all required components."""
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
    if position is not None:
        go.transform.position = position
    return go


def _setup_scene():
    """Create a minimal Pacman scene with 4 ghosts and a GameManager."""
    ghost_names = ["Blinky", "Pinky", "Inky", "Clyde"]
    ghost_positions = [
        Vector2(0, 3),
        Vector2(-2, 0),
        Vector2(0, 0),
        Vector2(2, 0),
    ]

    ghost_gos = []
    for name, pos in zip(ghost_names, ghost_positions):
        go = _create_ghost(name, pos)
        ghost_gos.append(go)

    # Create GameManager
    gm_go = GameObject("GameManager")
    gm = gm_go.add_component(GameManager)

    # Run lifecycle
    lm = LifecycleManager.instance()
    lm.process_awake_queue()
    lm.process_start_queue()

    # Wire up ghosts to GameManager
    ghosts = [go.get_component(Ghost) for go in ghost_gos]
    gm.ghosts = ghosts
    gm.pacman = None

    # Set up target for chase behavior
    target_go = GameObject("PacmanTarget")
    target_go.transform.position = Vector2(14, 14)
    for ghost in ghosts:
        ghost.target = target_go.transform

    return gm, ghost_gos, ghosts


class TestSceneSetup:
    def test_four_ghosts_created(self):
        """Scene should have 4 ghosts: Blinky, Pinky, Inky, Clyde."""
        gm, ghost_gos, ghosts = _setup_scene()
        assert len(ghosts) == 4
        names = [go.name for go in ghost_gos]
        assert "Blinky" in names
        assert "Pinky" in names
        assert "Inky" in names
        assert "Clyde" in names

    def test_ghosts_have_all_behavior_components(self):
        """Each ghost should have Movement, Ghost, and all behavior components."""
        _, ghost_gos, _ = _setup_scene()
        for go in ghost_gos:
            assert go.get_component(Movement) is not None, f"{go.name} missing Movement"
            assert go.get_component(Ghost) is not None, f"{go.name} missing Ghost"
            assert go.get_component(GhostScatter) is not None, f"{go.name} missing GhostScatter"
            assert go.get_component(GhostChase) is not None, f"{go.name} missing GhostChase"
            assert go.get_component(GhostFrightened) is not None, f"{go.name} missing GhostFrightened"
            assert go.get_component(GhostHome) is not None, f"{go.name} missing GhostHome"
            assert go.get_component(GhostEyes) is not None, f"{go.name} missing GhostEyes"

    def test_game_manager_singleton_exists(self):
        """GameManager.instance should be set after scene setup."""
        gm, _, _ = _setup_scene()
        assert GameManager.instance is gm

    def test_game_manager_has_ghosts_list(self):
        """GameManager should have a list of ghost components."""
        gm, _, ghosts = _setup_scene()
        assert gm.ghosts is not None
        assert len(gm.ghosts) == 4


class TestGameLoopIntegration:
    def test_run_frames_without_crash(self):
        """Run 120 frames headless, no exceptions."""
        gm, ghost_gos, ghosts = _setup_scene()
        lm = LifecycleManager.instance()

        Time._delta_time = 1.0 / 60.0
        Time._fixed_delta_time = 1.0 / 50.0

        for frame in range(120):
            Time._frame_count = frame
            Time._time = frame * Time._delta_time
            lm.run_fixed_update()
            lm.run_update()
            lm.run_late_update()

    def test_ghost_reset_state_integration(self):
        """After reset_state, all ghosts should be active with scatter enabled."""
        gm, ghost_gos, ghosts = _setup_scene()

        for ghost in ghosts:
            ghost.reset_state()

        for ghost in ghosts:
            assert ghost.game_object.active is True
            assert ghost.scatter.enabled is True
            # Frightened and chase should be off after reset
            assert ghost.frightened.enabled is False
            assert ghost.chase.enabled is False

    def test_game_over_integration(self):
        """game_over should deactivate all ghost GameObjects."""
        gm, ghost_gos, ghosts = _setup_scene()

        gm.game_over()

        for go in ghost_gos:
            assert go.active is False, f"{go.name} should be inactive after game_over"

    def test_multiple_ghost_eaten_multiplier_chain(self):
        """Eating multiple ghosts in one power pellet should escalate points."""
        gm, _, ghosts = _setup_scene()
        gm._ghost_multiplier = 1
        gm.score = 0

        # Simulate eating 4 ghosts in sequence
        for i, ghost in enumerate(ghosts):
            ghost.points = 200
            gm.ghost_eaten(ghost)

        # Expected: 200*1 + 200*2 + 200*4 + 200*8 = 200+400+800+1600 = 3000
        assert gm.score == 3000
        assert gm._ghost_multiplier == 16
