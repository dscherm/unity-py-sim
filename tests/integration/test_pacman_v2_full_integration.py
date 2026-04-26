"""Full integration tests for Pacman V2 — run through app.run headless.

Validates that the complete game scene sets up correctly and runs without errors.
Derived from Unity Pacman specs (zigurous tutorial), NOT from existing tests.
"""

import os
import sys

# Ensure project root on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Add pacman_v2 directory to sys.path BEFORE any imports so that
# run_pacman_v2's `from pacman_v2_python.*` imports resolve, and
# the test imports use the SAME module identity (avoiding isinstance mismatches).
_pacman_v2_dir = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "examples", "pacman_v2")
)
if _pacman_v2_dir not in sys.path:
    sys.path.insert(0, _pacman_v2_dir)

from src.engine.core import GameObject, _game_objects

# Import component classes through the SAME module path that run_pacman_v2 uses
# (pacman_v2_python.*) so isinstance checks work after app.run().
from pacman_v2_python.movement import Movement
from pacman_v2_python.animated_sprite import AnimatedSprite
from pacman_v2_python.pacman import Pacman
from pacman_v2_python.ghost import Ghost
from pacman_v2_python.ghost_home import GhostHome
from pacman_v2_python.ghost_scatter import GhostScatter
from pacman_v2_python.ghost_chase import GhostChase
from pacman_v2_python.ghost_frightened import GhostFrightened
from pacman_v2_python.node import Node
from pacman_v2_python.passage import Passage
from pacman_v2_python.power_pellet import PowerPellet
from pacman_v2_python.game_manager import GameManager


def _run_headless(frames: int = 300):
    """Run Pacman V2 headless for the given number of frames."""
    from src.engine.core import _clear_registry
    from src.engine.lifecycle import LifecycleManager
    from src.engine.physics.physics_manager import PhysicsManager

    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager._instance = None

    GameManager.instance = None

    from examples.pacman_v2.run_pacman_v2 import setup_scene
    from src.engine.app import run

    run(
        scene_setup=setup_scene,
        width=600,
        height=700,
        title="Pacman V2 Test",
        headless=True,
        max_frames=frames,
    )


class TestPacmanV2FullRun:
    """Test that the full game runs headless without errors."""

    def test_runs_300_frames_headless_without_errors(self):
        """Full game should run 300 frames in headless mode with no exceptions."""
        _run_headless(300)
        # If we reach here, no exception was raised — that's the assertion.

    def test_pacman_gameobject_exists_with_components(self):
        """Pacman GO must exist with Movement, AnimatedSprite, and Pacman components."""
        _run_headless(5)

        pacman_go = GameObject.find("Pacman")
        assert pacman_go is not None, "Pacman GameObject not found"

        assert pacman_go.get_component(Movement) is not None, "Pacman missing Movement"
        assert pacman_go.get_component(AnimatedSprite) is not None, "Pacman missing AnimatedSprite"
        assert pacman_go.get_component(Pacman) is not None, "Pacman missing Pacman component"

    def test_four_ghosts_exist_with_all_components(self):
        """4 Ghost GameObjects (Blinky, Pinky, Inky, Clyde) must exist with full component set."""
        _run_headless(5)

        ghost_names = ["Blinky", "Pinky", "Inky", "Clyde"]
        for name in ghost_names:
            go = GameObject.find(f"Ghost_{name}")
            assert go is not None, f"Ghost_{name} not found"
            assert go.get_component(Ghost) is not None, f"{name} missing Ghost"
            assert go.get_component(Movement) is not None, f"{name} missing Movement"
            assert go.get_component(GhostHome) is not None, f"{name} missing GhostHome"
            assert go.get_component(GhostScatter) is not None, f"{name} missing GhostScatter"
            assert go.get_component(GhostChase) is not None, f"{name} missing GhostChase"
            assert go.get_component(GhostFrightened) is not None, f"{name} missing GhostFrightened"

    def test_pellet_count_matches_expected(self):
        """Pellet count should be ~242 regular + 4 power pellets = 246 total."""
        _run_headless(5)

        gm = GameManager.instance
        assert gm is not None, "GameManager singleton not set"

        total_pellets = len(gm._all_pellets)
        # Expected: 242 regular pellets + 4 power pellets = 246
        assert 240 <= total_pellets <= 250, (
            f"Expected ~246 pellets, got {total_pellets}"
        )

        power_count = sum(1 for p in gm._all_pellets if isinstance(p, PowerPellet))
        assert power_count == 4, f"Expected 4 power pellets, got {power_count}"

    def test_node_gameobjects_exist_at_intersections(self):
        """Node GameObjects should exist at maze intersections."""
        _run_headless(5)

        node_gos = [
            go for go in _game_objects.values()
            if go.name.startswith("Node_") and go.active
        ]
        # Classic Pacman has dozens of intersection nodes
        assert len(node_gos) > 20, (
            f"Expected >20 Node GameObjects, got {len(node_gos)}"
        )

        for go in node_gos[:5]:  # Spot check a few
            assert go.get_component(Node) is not None, f"{go.name} missing Node component"

    def test_passage_gameobjects_exist(self):
        """Two Passage GameObjects (tunnel entries) must exist."""
        _run_headless(5)

        passage_gos = [
            go for go in _game_objects.values()
            if go.name.startswith("Passage_") and go.active
        ]
        assert len(passage_gos) == 2, (
            f"Expected 2 Passage GameObjects, got {len(passage_gos)}"
        )

        for go in passage_gos:
            p = go.get_component(Passage)
            assert p is not None, f"{go.name} missing Passage component"
            assert p.connection is not None, f"{go.name} Passage has no connection"

    def test_game_manager_singleton_is_set(self):
        """GameManager.instance must be set after scene setup."""
        _run_headless(5)

        assert GameManager.instance is not None, "GameManager.instance is None"
        assert isinstance(GameManager.instance, GameManager)
        assert GameManager.instance.pacman is not None, "GameManager has no pacman reference"
        assert len(GameManager.instance.ghosts) == 4, (
            f"Expected 4 registered ghosts, got {len(GameManager.instance.ghosts)}"
        )
