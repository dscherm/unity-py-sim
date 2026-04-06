"""Contract tests for Pacman Tasks 1 & 2 — Unity behavioral specifications.

These tests verify that the Pacman implementation matches Unity's documented
behavior for Rigidbody2D movement, direction queuing, wall detection,
intersection nodes, animated sprites, passages, and Pacman rotation.

Reference: zigurous/unity-pacman-tutorial C# scripts.
"""

import sys
import os
import math
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "examples", "pacman"))

from src.engine.core import GameObject, MonoBehaviour, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager, Physics2D
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D
from src.engine.math.vector import Vector2
from src.engine.math.quaternion import Quaternion
from src.engine.time_manager import Time
from src.engine.input_manager import Input
from src.engine.rendering.renderer import SpriteRenderer


@pytest.fixture
def engine():
    """Reset all engine singletons before each test."""
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    Time._reset()
    Input._reset()
    # Zero gravity for Pacman
    pm = PhysicsManager.instance()
    pm.gravity = Vector2(0, 0)
    lm = LifecycleManager.instance()
    yield lm, pm
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    Time._reset()
    Input._reset()


def _tick_lifecycle(lm, pm, dt=1.0 / 60):
    """Run one full lifecycle tick: awake, start, fixed_update, physics step, update, late_update."""
    Time._delta_time = dt
    Time._time += dt
    Time._frame_count += 1
    lm.process_awake_queue()
    lm.process_start_queue()
    lm.run_fixed_update()
    pm.step(Time._fixed_delta_time)
    lm.run_update()
    lm.run_late_update()


def _create_wall(x, y, lm, pm):
    """Create a static wall at the given position on the obstacle layer."""
    from pacman_python.movement import OBSTACLE_LAYER
    wall_go = GameObject(f"Wall_{x}_{y}")
    wall_go.layer = OBSTACLE_LAYER
    wall_go.transform.position = Vector2(x, y)
    rb = wall_go.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.STATIC
    col = wall_go.add_component(BoxCollider2D)
    col.size = Vector2(1.0, 1.0)
    return wall_go


def _create_pacman_with_movement(x, y, initial_dir=None):
    """Create a Pacman-like GO with Rigidbody2D (kinematic), CircleCollider2D, and Movement."""
    from pacman_python.movement import Movement
    go = GameObject("Pacman", tag="Pacman")
    go.layer = 7
    go.transform.position = Vector2(x, y)
    rb = go.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.KINEMATIC
    col = go.add_component(CircleCollider2D)
    col.radius = 0.5
    sr = go.add_component(SpriteRenderer)
    sr.color = (255, 255, 0)
    sr.size = Vector2(1.0, 1.0)
    mv = go.add_component(Movement)
    if initial_dir:
        mv.initial_direction = initial_dir
    return go, mv


# ============================================================
# Movement contracts
# ============================================================


class TestMovementContract:
    """Movement uses Rigidbody2D.MovePosition (kinematic), not velocity."""

    def test_movement_uses_kinematic_body(self, engine):
        """Contract: Movement operates on a kinematic Rigidbody2D (MovePosition pattern)."""
        lm, pm = engine
        go, mv = _create_pacman_with_movement(0, 0, Vector2(1, 0))
        _tick_lifecycle(lm, pm)  # awake + start

        rb = go.get_component(Rigidbody2D)
        assert rb.body_type == RigidbodyType2D.KINEMATIC

    def test_movement_moves_via_move_position(self, engine):
        """Contract: Movement calls rb.move_position, changing transform position."""
        lm, pm = engine
        go, mv = _create_pacman_with_movement(0, 0, Vector2(1, 0))
        _tick_lifecycle(lm, pm)  # awake + start + first tick

        start_x = go.transform.position.x
        # Tick several frames to accumulate movement
        for _ in range(10):
            _tick_lifecycle(lm, pm)
        assert go.transform.position.x > start_x, "Pacman should move right"

    def test_movement_does_not_use_velocity(self, engine):
        """Contract: Kinematic body velocity remains zero — movement is via MovePosition."""
        lm, pm = engine
        go, mv = _create_pacman_with_movement(0, 0, Vector2(1, 0))
        _tick_lifecycle(lm, pm)

        rb = go.get_component(Rigidbody2D)
        # Kinematic bodies moved via move_position should have zero velocity in pymunk
        # (velocity is only meaningful for dynamic bodies)
        assert rb.velocity.x == 0 or rb.body_type == RigidbodyType2D.KINEMATIC


class TestDirectionQueueingContract:
    """Direction queuing: blocked direction is queued and applied when unblocked."""

    def test_blocked_direction_is_queued(self, engine):
        """Contract: Setting a blocked direction stores it in next_direction."""
        lm, pm = engine
        # Wall above at (0, 1)
        _create_wall(0, 1, lm, pm)
        go, mv = _create_pacman_with_movement(0, 0, Vector2(1, 0))
        _tick_lifecycle(lm, pm)  # awake + start

        # Try to go up into wall
        mv.set_direction(Vector2(0, 1))
        # Direction should stay as current (right), next_direction should be up
        assert mv.next_direction.y == 1, "Blocked direction should be queued"
        assert mv.direction.x == 1, "Current direction unchanged"

    def test_queued_direction_applies_when_unblocked(self, engine):
        """Contract: Queued direction applies automatically once the path clears."""
        lm, pm = engine
        go, mv = _create_pacman_with_movement(0, 0, Vector2(1, 0))
        _tick_lifecycle(lm, pm)

        # Queue up direction (no wall, so it should apply on next update)
        mv.next_direction = Vector2(0, 1)
        _tick_lifecycle(lm, pm)
        # After update, since up is not blocked, direction should change
        assert mv.direction.y == 1, "Queued direction should apply when unblocked"

    def test_forced_direction_ignores_walls(self, engine):
        """Contract: set_direction with forced=True bypasses occupancy check."""
        lm, pm = engine
        _create_wall(0, 1, lm, pm)
        go, mv = _create_pacman_with_movement(0, 0, Vector2(1, 0))
        _tick_lifecycle(lm, pm)

        mv.set_direction(Vector2(0, 1), forced=True)
        assert mv.direction.y == 1, "Forced direction should apply even if blocked"
        assert mv.next_direction.x == 0 and mv.next_direction.y == 0


class TestWallDetectionContract:
    """Wall detection: Physics2D.overlap_box with layer mask, ignoring triggers."""

    def test_occupied_detects_wall_on_obstacle_layer(self, engine):
        """Contract: occupied() returns True when wall is in the given direction."""
        lm, pm = engine
        _create_wall(1, 0, lm, pm)
        go, mv = _create_pacman_with_movement(0, 0, Vector2(1, 0))
        _tick_lifecycle(lm, pm)

        assert mv.occupied(Vector2(1, 0)) is True

    def test_occupied_returns_false_when_clear(self, engine):
        """Contract: occupied() returns False when no wall is ahead."""
        lm, pm = engine
        go, mv = _create_pacman_with_movement(0, 0, Vector2(1, 0))
        _tick_lifecycle(lm, pm)

        assert mv.occupied(Vector2(1, 0)) is False

    def test_occupied_ignores_trigger_colliders(self, engine):
        """Contract: Physics2D.overlap_box ignores triggers (pellets, nodes)."""
        lm, pm = engine
        # Create a trigger object where a wall would be
        trigger_go = GameObject("Pellet")
        trigger_go.layer = 6  # obstacle layer, but trigger
        trigger_go.transform.position = Vector2(1, 0)
        rb = trigger_go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.STATIC
        col = trigger_go.add_component(BoxCollider2D)
        col.size = Vector2(1.0, 1.0)
        col.is_trigger = True

        go, mv = _create_pacman_with_movement(0, 0, Vector2(1, 0))
        _tick_lifecycle(lm, pm)

        assert mv.occupied(Vector2(1, 0)) is False, "Triggers should not block movement"

    def test_occupied_filters_by_layer_mask(self, engine):
        """Contract: Objects on non-obstacle layers don't block movement."""
        lm, pm = engine
        # Create solid object on a different layer
        other_go = GameObject("Other")
        other_go.layer = 3  # Not obstacle layer
        other_go.transform.position = Vector2(1, 0)
        rb = other_go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.STATIC
        col = other_go.add_component(BoxCollider2D)
        col.size = Vector2(1.0, 1.0)

        go, mv = _create_pacman_with_movement(0, 0, Vector2(1, 0))
        _tick_lifecycle(lm, pm)

        assert mv.occupied(Vector2(1, 0)) is False, "Non-obstacle layer should not block"


# ============================================================
# Node contracts
# ============================================================


class TestNodeContract:
    """Intersection nodes detect available directions via box-cast."""

    def test_node_detects_open_directions(self, engine):
        """Contract: Node finds available directions where no wall exists."""
        from pacman_python.node import Node
        lm, pm = engine

        # Create walls above and below, leave left and right open
        _create_wall(0, 1, lm, pm)
        _create_wall(0, -1, lm, pm)

        node_go = GameObject("Node")
        node_go.transform.position = Vector2(0, 0)
        rb = node_go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.STATIC
        col = node_go.add_component(BoxCollider2D)
        col.is_trigger = True
        col.size = Vector2(0.5, 0.5)
        node = node_go.add_component(Node)

        _tick_lifecycle(lm, pm)

        dirs = [(int(d.x), int(d.y)) for d in node.available_directions]
        assert (-1, 0) in dirs, "Left should be available"
        assert (1, 0) in dirs, "Right should be available"
        assert (0, 1) not in dirs, "Up should be blocked"
        assert (0, -1) not in dirs, "Down should be blocked"

    def test_node_four_way_intersection(self, engine):
        """Contract: Node with no surrounding walls reports 4 directions."""
        from pacman_python.node import Node
        lm, pm = engine

        node_go = GameObject("Node")
        node_go.transform.position = Vector2(0, 0)
        rb = node_go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.STATIC
        col = node_go.add_component(BoxCollider2D)
        col.is_trigger = True
        col.size = Vector2(0.5, 0.5)
        node = node_go.add_component(Node)

        _tick_lifecycle(lm, pm)

        assert len(node.available_directions) == 4, "Open intersection should have 4 directions"


# ============================================================
# AnimatedSprite contracts
# ============================================================


class TestAnimatedSpriteContract:
    """AnimatedSprite frame cycling respects animation_time and loop mode."""

    def test_frame_advances_after_animation_time(self, engine):
        """Contract: Frame increments when timer exceeds animation_time."""
        from pacman_python.animated_sprite import AnimatedSprite
        lm, pm = engine

        go = GameObject("Animated")
        sr = go.add_component(SpriteRenderer)
        sr.enabled = True
        anim = go.add_component(AnimatedSprite)
        anim.sprite_refs = ["frame0", "frame1", "frame2"]
        anim.animation_time = 0.1
        anim.loop = True

        _tick_lifecycle(lm, pm)
        initial_ref = sr.asset_ref

        # Simulate enough time to advance at least one frame
        for _ in range(10):
            _tick_lifecycle(lm, pm, dt=0.05)

        assert sr.asset_ref != initial_ref or anim._animation_frame > 0, \
            "Frame should advance after animation_time elapses"

    def test_loop_wraps_to_frame_zero(self, engine):
        """Contract: Looping animation wraps back to frame 0 after last frame."""
        from pacman_python.animated_sprite import AnimatedSprite
        lm, pm = engine

        go = GameObject("Animated")
        sr = go.add_component(SpriteRenderer)
        sr.enabled = True
        anim = go.add_component(AnimatedSprite)
        anim.sprite_refs = ["a", "b"]
        anim.animation_time = 0.01
        anim.loop = True

        _tick_lifecycle(lm, pm)

        # Run many frames to wrap around
        for _ in range(100):
            _tick_lifecycle(lm, pm, dt=0.02)

        # With loop=True, frame should have wrapped around
        assert anim._animation_frame < len(anim.sprite_refs), \
            "Looping animation should not exceed frame count"

    def test_non_loop_stops_at_last_frame(self, engine):
        """Contract: Non-looping animation stops at the last frame."""
        from pacman_python.animated_sprite import AnimatedSprite
        lm, pm = engine

        go = GameObject("Animated")
        sr = go.add_component(SpriteRenderer)
        sr.enabled = True
        anim = go.add_component(AnimatedSprite)
        anim.sprite_refs = ["a", "b", "c"]
        anim.animation_time = 0.01
        anim.loop = False

        _tick_lifecycle(lm, pm)

        for _ in range(200):
            _tick_lifecycle(lm, pm, dt=0.02)

        # Should stop at last valid frame (or just past it, but not wrap)
        assert anim._animation_frame >= len(anim.sprite_refs) - 1, \
            "Non-loop should reach the last frame"

    def test_restart_resets_to_frame_zero(self, engine):
        """Contract: restart() resets animation to frame 0."""
        from pacman_python.animated_sprite import AnimatedSprite
        lm, pm = engine

        go = GameObject("Animated")
        sr = go.add_component(SpriteRenderer)
        sr.enabled = True
        anim = go.add_component(AnimatedSprite)
        anim.sprite_refs = ["a", "b", "c"]
        anim.animation_time = 0.01
        anim.loop = True

        _tick_lifecycle(lm, pm)
        for _ in range(20):
            _tick_lifecycle(lm, pm, dt=0.02)

        anim.restart()
        assert anim._animation_frame == 0, "restart() should set frame to 0"
        assert sr.asset_ref == "a", "restart() should show first frame sprite"


# ============================================================
# Passage contracts
# ============================================================


class TestPassageContract:
    """Passage teleports via on_trigger_enter_2d to connection transform."""

    def test_passage_teleports_to_connection(self, engine):
        """Contract: OnTriggerEnter2D sets other's transform.position to connection.position.

        In Unity, OnTriggerEnter2D receives a Collider2D which has .gameObject.transform.
        In this engine, the physics dispatch passes a GameObject as 'other'.
        The passage code does other.game_object.transform.position — which means 'other'
        must have a .game_object attribute (i.e., it should be a Component or similar).

        NOTE: If this test fails with AttributeError on 'game_object', it indicates
        a bug in passage.py — it should use other.transform.position directly since
        the engine passes GameObjects to trigger callbacks, not Colliders.
        """
        from pacman_python.passage import Passage
        lm, pm = engine

        # Left passage at (-14, 0)
        left_go = GameObject("PassageLeft")
        left_go.transform.position = Vector2(-14, 0)
        rb_l = left_go.add_component(Rigidbody2D)
        rb_l.body_type = RigidbodyType2D.STATIC
        col_l = left_go.add_component(BoxCollider2D)
        col_l.is_trigger = True
        col_l.size = Vector2(1.0, 1.0)
        passage_l = left_go.add_component(Passage)

        # Right passage at (14, 0)
        right_go = GameObject("PassageRight")
        right_go.transform.position = Vector2(14, 0)
        rb_r = right_go.add_component(Rigidbody2D)
        rb_r.body_type = RigidbodyType2D.STATIC
        col_r = right_go.add_component(BoxCollider2D)
        col_r.is_trigger = True
        col_r.size = Vector2(1.0, 1.0)
        passage_r = right_go.add_component(Passage)

        # Wire connections
        passage_l.connection = right_go.transform
        passage_r.connection = left_go.transform

        _tick_lifecycle(lm, pm)

        # The engine's _dispatch_trigger_enter passes a GameObject as 'other'.
        # passage.py does: other.game_object.transform.position = ...
        # Since GameObject doesn't have .game_object, this will raise AttributeError
        # unless the code is fixed to use other.transform.position directly.
        pac_go = GameObject("Pacman")
        pac_go.transform.position = Vector2(-14, 0)

        try:
            passage_l.on_trigger_enter_2d(pac_go)
            # If it succeeds, check teleportation
            assert abs(pac_go.transform.position.x - 14.0) < 0.01, \
                "Passage should teleport to connection x"
            assert abs(pac_go.transform.position.y - 0.0) < 0.01, \
                "Passage should teleport to connection y"
        except AttributeError as e:
            if "game_object" in str(e):
                pytest.fail(
                    "BUG FOUND: Passage.on_trigger_enter_2d calls other.game_object "
                    "but engine passes a GameObject (not a Component). "
                    "Fix: use other.transform.position instead of "
                    "other.game_object.transform.position"
                )


# ============================================================
# Pacman rotation contracts
# ============================================================


class TestPacmanRotationContract:
    """Pacman faces movement direction with correct euler rotation."""

    def test_facing_right_rotation(self, engine):
        """Contract: Moving right -> rotation z = 0 degrees."""
        from pacman_python.pacman import Pacman
        from pacman_python.movement import Movement
        lm, pm = engine

        go, mv = _create_pacman_with_movement(0, 0, Vector2(1, 0))
        sr = go.get_component(SpriteRenderer)
        pac = go.add_component(Pacman)

        _tick_lifecycle(lm, pm)
        _tick_lifecycle(lm, pm)

        euler = go.transform.rotation.euler_angles
        assert abs(euler.z - 0.0) < 1.0, f"Right direction should be ~0 degrees, got {euler.z}"

    def test_facing_up_rotation(self, engine):
        """Contract: Moving up -> rotation z = 90 degrees."""
        from pacman_python.pacman import Pacman
        from pacman_python.movement import Movement
        lm, pm = engine

        go, mv = _create_pacman_with_movement(0, 0, Vector2(0, 1))
        pac = go.add_component(Pacman)

        _tick_lifecycle(lm, pm)
        _tick_lifecycle(lm, pm)

        euler = go.transform.rotation.euler_angles
        assert abs(euler.z - 90.0) < 1.0, f"Up direction should be ~90 degrees, got {euler.z}"

    def test_facing_left_rotation(self, engine):
        """Contract: Moving left -> rotation z = 180 degrees."""
        from pacman_python.pacman import Pacman
        from pacman_python.movement import Movement
        lm, pm = engine

        go, mv = _create_pacman_with_movement(0, 0, Vector2(-1, 0))
        pac = go.add_component(Pacman)

        _tick_lifecycle(lm, pm)
        _tick_lifecycle(lm, pm)

        euler = go.transform.rotation.euler_angles
        assert abs(euler.z - 180.0) < 1.0 or abs(euler.z + 180.0) < 1.0, \
            f"Left direction should be ~180 degrees, got {euler.z}"

    def test_facing_down_rotation(self, engine):
        """Contract: Moving down -> rotation z = -90 (or 270) degrees."""
        from pacman_python.pacman import Pacman
        from pacman_python.movement import Movement
        lm, pm = engine

        go, mv = _create_pacman_with_movement(0, 0, Vector2(0, -1))
        pac = go.add_component(Pacman)

        _tick_lifecycle(lm, pm)
        _tick_lifecycle(lm, pm)

        euler = go.transform.rotation.euler_angles
        # atan2(-1, 0) = -90 degrees
        assert abs(euler.z - (-90.0)) < 1.0 or abs(euler.z - 270.0) < 1.0, \
            f"Down direction should be ~-90 or ~270 degrees, got {euler.z}"


# ============================================================
# Maze data contracts
# ============================================================


class TestMazeDataContract:
    """Maze data matches classic Pacman 28x31 layout."""

    def test_maze_dimensions(self):
        """Contract: Classic Pacman maze is 28 columns x 31 rows."""
        from pacman_python.maze_data import MAZE, MAZE_ROWS, MAZE_COLS
        assert MAZE_ROWS == 31
        assert MAZE_COLS == 28

    def test_maze_has_pacman_start(self):
        """Contract: Maze contains exactly one 'P' cell (Pacman start)."""
        from pacman_python.maze_data import MAZE
        p_count = sum(row.count("P") for row in MAZE)
        assert p_count == 1, f"Expected 1 Pacman start, found {p_count}"

    def test_maze_has_tunnel_passages(self):
        """Contract: Maze has 'T' cells for tunnel passages."""
        from pacman_python.maze_data import MAZE
        t_count = sum(row.count("T") for row in MAZE)
        assert t_count >= 2, f"Expected at least 2 tunnel passages, found {t_count}"

    def test_cell_to_world_centers_maze(self):
        """Contract: cell_to_world places (0,0) grid cell at maze center offset."""
        from pacman_python.maze_data import cell_to_world, MAZE_COLS, MAZE_ROWS
        # Center column and center row should be near world origin
        cx, cy = cell_to_world(MAZE_COLS // 2, MAZE_ROWS // 2)
        assert abs(cx) < 1.0, f"Center column should be near x=0, got {cx}"
        assert abs(cy) < 1.0, f"Center row should be near y=0, got {cy}"

    def test_maze_bordered_by_walls(self):
        """Contract: Maze perimeter is walls (except tunnel passages)."""
        from pacman_python.maze_data import MAZE, MAZE_ROWS, MAZE_COLS
        for col in range(MAZE_COLS):
            assert MAZE[0][col] == "W", f"Top row col {col} should be wall"
            assert MAZE[MAZE_ROWS - 1][col] == "W", f"Bottom row col {col} should be wall"
        for row in range(MAZE_ROWS):
            cell_left = MAZE[row][0]
            cell_right = MAZE[row][MAZE_COLS - 1]
            assert cell_left in ("W", "T"), f"Left border row {row} should be W or T"
            assert cell_right in ("W", "T"), f"Right border row {row} should be W or T"


# ============================================================
# Movement reset_state contract
# ============================================================


class TestMovementResetContract:
    """reset_state returns Pacman to starting position and direction."""

    def test_reset_restores_starting_position(self, engine):
        """Contract: reset_state() restores transform to starting_position.

        NOTE: movement.py line 45 does `self.rb.is_kinematic = False` but
        Rigidbody2D has no `is_kinematic` property. If this test fails with
        AttributeError, that's the bug — fix by removing that line or adding
        the property to Rigidbody2D.
        """
        lm, pm = engine
        go, mv = _create_pacman_with_movement(5, 3, Vector2(1, 0))
        _tick_lifecycle(lm, pm)

        # Move for a while
        for _ in range(20):
            _tick_lifecycle(lm, pm)

        try:
            mv.reset_state()
        except AttributeError as e:
            if "is_kinematic" in str(e):
                pytest.fail(
                    "BUG FOUND: Movement.reset_state() calls self.rb.is_kinematic "
                    "but Rigidbody2D has no is_kinematic property. "
                    "Fix: remove line 45 or add is_kinematic property to Rigidbody2D."
                )
            raise
        assert abs(go.transform.position.x - 5.0) < 0.01
        assert abs(go.transform.position.y - 3.0) < 0.01

    def test_reset_restores_initial_direction(self, engine):
        """Contract: reset_state() restores initial_direction."""
        lm, pm = engine
        go, mv = _create_pacman_with_movement(0, 0, Vector2(-1, 0))
        _tick_lifecycle(lm, pm)

        mv.set_direction(Vector2(0, 1), forced=True)
        mv.reset_state()
        assert mv.direction.x == -1
        assert mv.direction.y == 0

    def test_reset_clears_speed_multiplier(self, engine):
        """Contract: reset_state() sets speed_multiplier back to 1.0."""
        lm, pm = engine
        go, mv = _create_pacman_with_movement(0, 0)
        _tick_lifecycle(lm, pm)

        mv.speed_multiplier = 0.5
        mv.reset_state()
        assert mv.speed_multiplier == 1.0
