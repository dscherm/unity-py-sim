"""Integration tests for Pacman Tasks 1 & 2 — full scene via run_pacman setup.

These tests set up the Pacman scene, run the engine loop headless for N frames,
and verify observable behaviors: Pacman exists, moves, walls block, passages
teleport, and animated sprites advance frames.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "examples", "pacman"))

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.time_manager import Time
from src.engine.input_manager import Input
from src.engine.rendering.renderer import SpriteRenderer


@pytest.fixture
def pacman_scene():
    """Set up a full Pacman scene and return after awake/start."""
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    Time._reset()
    Input._reset()

    from run_pacman import setup_scene
    from src.engine.rendering.display import DisplayManager

    # Initialize display in headless mode
    dm = DisplayManager(600, 700, "test")
    DisplayManager._instance = dm
    dm.init(headless=True)

    setup_scene()

    lm = LifecycleManager.instance()
    pm = PhysicsManager.instance()

    # Process awake + start
    lm.process_awake_queue()
    lm.process_start_queue()

    yield lm, pm

    dm.quit()
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    Time._reset()
    Input._reset()


def _run_frames(lm, pm, n, dt=1.0 / 60):
    """Run n frames of the game loop."""
    for _ in range(n):
        Input._begin_frame()
        Time._delta_time = dt
        Time._time += dt
        Time._frame_count += 1
        lm.process_awake_queue()
        lm.process_start_queue()
        lm.run_fixed_update()
        pm.step(Time._fixed_delta_time)
        lm.run_update()
        lm.run_late_update()


class TestPacmanSceneSetup:
    """Verify the scene is set up correctly."""

    def test_pacman_exists_in_scene(self, pacman_scene):
        """Pacman GameObject should exist with correct tag."""
        pac = GameObject.find("Pacman")
        assert pac is not None, "Pacman not found in scene"
        assert pac.tag == "Pacman"

    def test_walls_exist_on_obstacle_layer(self, pacman_scene):
        """Walls should be created on the obstacle layer (6)."""
        from pacman_python.movement import OBSTACLE_LAYER
        wall = GameObject.find("Wall_0_0")
        assert wall is not None, "Wall at row=0, col=0 should exist"
        assert wall.layer == OBSTACLE_LAYER

    def test_pellets_exist_with_tag(self, pacman_scene):
        """Pellets should exist with Pellet or PowerPellet tags."""
        pellets = GameObject.find_game_objects_with_tag("Pellet")
        power = GameObject.find_game_objects_with_tag("PowerPellet")
        total = len(pellets) + len(power)
        assert total > 0, "Scene should contain pellets"

    def test_passages_exist(self, pacman_scene):
        """Passage GameObjects should exist for tunnels."""
        from pacman_python.passage import Passage
        # There should be two passage GOs
        left = None
        right = None
        for name_prefix in ["Passage_14_0", "Passage_14_27"]:
            p = GameObject.find(name_prefix)
            if p is not None:
                comp = p.get_component(Passage)
                if comp is not None:
                    if left is None:
                        left = comp
                    else:
                        right = comp
        # At minimum, check that passage objects were created
        assert left is not None or right is not None or \
            GameObject.find("Passage_14_0") is not None or \
            GameObject.find("Passage_14_27") is not None, \
            "Passage objects should exist in scene"

    def test_nodes_exist_at_intersections(self, pacman_scene):
        """Node GameObjects should be placed at maze intersections."""
        # Find any node
        node = None
        for go_name in ["Node_5_1", "Node_5_6", "Node_1_1"]:
            candidate = GameObject.find(go_name)
            if candidate is not None:
                node = candidate
                break
        # Fallback: search more broadly
        if node is None:
            # Just check that at least one Node component exists
            # by finding any node-named GO
            from src.engine.core import _game_objects
            for go in _game_objects.values():
                if go.name.startswith("Node_"):
                    node = go
                    break
        assert node is not None, "At least one Node should exist at an intersection"


class TestPacmanMovement:
    """Verify Pacman moves through the maze."""

    def test_pacman_moves_from_start_position(self, pacman_scene):
        """Pacman should move from its starting position over several frames."""
        lm, pm = pacman_scene
        pac = GameObject.find("Pacman")
        start_x = pac.transform.position.x
        start_y = pac.transform.position.y

        _run_frames(lm, pm, 30)

        # Pacman starts moving left (initial_direction = (-1, 0))
        end_x = pac.transform.position.x
        assert end_x < start_x, \
            f"Pacman should move left from start: start={start_x}, end={end_x}"

    def test_walls_block_pacman(self, pacman_scene):
        """Pacman should not pass through walls."""
        lm, pm = pacman_scene
        pac = GameObject.find("Pacman")

        # Run many frames — Pacman should stop when it hits a wall
        _run_frames(lm, pm, 200)

        # Pacman moves left from start; verify position is still within maze bounds
        from pacman_python.maze_data import MAZE_OFFSET_X
        min_x = MAZE_OFFSET_X - 1  # leftmost wall position with margin
        assert pac.transform.position.x >= min_x, \
            f"Pacman should be stopped by wall, not at x={pac.transform.position.x}"

    def test_input_changes_direction(self, pacman_scene):
        """Pressing a key should change Pacman's movement direction."""
        from pacman_python.movement import Movement
        lm, pm = pacman_scene

        pac = GameObject.find("Pacman")
        mv = pac.get_component(Movement)

        _run_frames(lm, pm, 5)

        # To trigger get_key_down, key must be in current but not previous.
        # _begin_frame copies current->previous, so we need:
        # 1. begin_frame (previous = current which has no 'w')
        # 2. set 'w' pressed (current now has 'w', previous does not)
        # 3. run update (which checks get_key_down)
        Input._begin_frame()
        Input._set_key_state("w", True)

        # Now run a single tick manually (not via _run_frames which calls _begin_frame again)
        dt = 1.0 / 60
        Time._delta_time = dt
        Time._time += dt
        Time._frame_count += 1
        lm.process_awake_queue()
        lm.process_start_queue()
        lm.run_fixed_update()
        pm.step(Time._fixed_delta_time)
        lm.run_update()
        lm.run_late_update()

        # Direction should have changed (or been queued)
        dir_changed = (mv.direction.y == 1) or (mv.next_direction.y == 1)
        assert dir_changed, "Pressing W should set or queue upward direction"


class TestAnimatedSpriteIntegration:
    """Verify animated sprites advance frames during gameplay."""

    def test_walk_animation_advances(self, pacman_scene):
        """Pacman's walk animation should cycle through frames."""
        from pacman_python.animated_sprite import AnimatedSprite
        lm, pm = pacman_scene

        pac = GameObject.find("Pacman")
        anim = pac.get_component(AnimatedSprite)
        assert anim is not None, "Pacman should have AnimatedSprite"

        initial_frame = anim._animation_frame

        # Run enough frames for animation to advance (animation_time = 0.15s)
        _run_frames(lm, pm, 30, dt=1.0 / 60)  # 0.5 seconds

        assert anim._animation_frame != initial_frame or anim._timer > 0, \
            "Animation frame should advance over time"

    def test_sprite_ref_changes_with_animation(self, pacman_scene):
        """SpriteRenderer.asset_ref should change as animation advances.

        The animation cycles through 3 frames (pacman_01, _02, _03) with
        animation_time=0.15s. We check that the ref changes mid-cycle by
        capturing it at a point where it should not be at frame 0.
        """
        from pacman_python.animated_sprite import AnimatedSprite
        lm, pm = pacman_scene

        pac = GameObject.find("Pacman")
        sr = pac.get_component(SpriteRenderer)
        anim = pac.get_component(AnimatedSprite)

        # Track all observed refs during the run
        observed_refs = set()
        observed_refs.add(sr.asset_ref)

        for _ in range(30):
            _run_frames(lm, pm, 1, dt=1.0 / 60)
            if sr.asset_ref:
                observed_refs.add(sr.asset_ref)

        # With 3 frames and 0.5s of runtime, we should see multiple refs
        assert len(observed_refs) >= 2, \
            f"Animation should cycle through multiple sprites, only saw: {observed_refs}"


class TestPassageIntegration:
    """Verify passage tunnels work in the full scene."""

    def test_passage_connections_are_wired(self, pacman_scene):
        """Both passage objects should have their connection wired."""
        from pacman_python.passage import Passage
        from src.engine.core import _game_objects

        passages = []
        for go in _game_objects.values():
            if go.name.startswith("Passage_"):
                p = go.get_component(Passage)
                if p is not None:
                    passages.append(p)

        assert len(passages) >= 2, f"Expected 2 passages, found {len(passages)}"

        # Both should have connections
        for p in passages:
            assert p.connection is not None, \
                f"Passage {p.game_object.name} should have a connection"
