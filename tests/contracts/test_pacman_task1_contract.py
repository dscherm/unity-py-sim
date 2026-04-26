"""Contract tests for Pacman Task 1 — movement, node, maze, physics fixes.

These tests validate behavior against Unity documentation and game design
principles, NOT against implementation details.

Unity contracts tested:
- Physics2D.OverlapBox ignores trigger colliders
- Physics2D.OverlapBox filters by LayerMask
- Static colliders at non-origin positions are found by spatial queries
- Grid movement with direction queuing (a la zigurous/unity-pacman-tutorial)
- Node intersection detection (available directions)
- Maze coordinate conversion and intersection identification
"""

import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.math.vector import Vector2
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.physics_manager import Physics2D, PhysicsManager
from src.engine.lifecycle import LifecycleManager
from src.engine.time_manager import Time


@pytest.fixture(autouse=True)
def clean_engine():
    """Reset all engine singletons between tests."""
    _clear_registry()
    PhysicsManager.reset()
    LifecycleManager.reset()
    Time._reset()
    yield
    _clear_registry()
    PhysicsManager.reset()
    LifecycleManager.reset()
    Time._reset()


def _run_lifecycle():
    """Process awake and start queues so colliders build."""
    lm = LifecycleManager.instance()
    lm.process_awake_queue()
    lm.process_start_queue()


def _make_static_wall(x: float, y: float, layer: int = 6) -> GameObject:
    """Create a static wall box at given position on given layer."""
    go = GameObject(f"Wall_{x}_{y}")
    go.layer = layer
    go.transform.position = Vector2(x, y)
    rb = go.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.STATIC
    col = go.add_component(BoxCollider2D)
    col.size = Vector2(1.0, 1.0)
    return go


def _make_trigger(x: float, y: float, layer: int = 0) -> GameObject:
    """Create a static trigger box at given position."""
    go = GameObject(f"Trigger_{x}_{y}")
    go.layer = layer
    go.transform.position = Vector2(x, y)
    rb = go.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.STATIC
    col = go.add_component(BoxCollider2D)
    col.is_trigger = True
    col.size = Vector2(0.5, 0.5)
    return go


# ---------------------------------------------------------------------------
# Physics2D.overlap_box contract tests
# ---------------------------------------------------------------------------

class TestOverlapBoxSkipsTriggers:
    """Unity doc: Physics2D.OverlapBox ignores trigger colliders by default."""

    def test_overlap_box_ignores_trigger_collider(self):
        """A trigger collider at the query point should NOT be returned."""
        _make_trigger(5.0, 5.0, layer=6)
        _run_lifecycle()

        hit = Physics2D.overlap_box(
            point=Vector2(5.0, 5.0),
            size=Vector2(1.0, 1.0),
            angle=0.0,
            layer_mask=1 << 6,
        )
        assert hit is None, "overlap_box must ignore trigger colliders"

    def test_overlap_box_finds_non_trigger_at_same_spot(self):
        """A non-trigger collider at the query point SHOULD be returned."""
        _make_static_wall(5.0, 5.0, layer=6)
        _run_lifecycle()

        hit = Physics2D.overlap_box(
            point=Vector2(5.0, 5.0),
            size=Vector2(1.0, 1.0),
            angle=0.0,
            layer_mask=1 << 6,
        )
        assert hit is not None, "overlap_box must find non-trigger colliders"

    def test_trigger_and_wall_at_same_spot_only_returns_wall(self):
        """When both trigger and wall overlap the query, only wall is returned."""
        _make_trigger(5.0, 5.0, layer=6)
        _make_static_wall(5.0, 5.0, layer=6)
        _run_lifecycle()

        hit = Physics2D.overlap_box(
            point=Vector2(5.0, 5.0),
            size=Vector2(2.0, 2.0),
            angle=0.0,
            layer_mask=1 << 6,
        )
        assert hit is not None
        assert not hit.is_trigger, "Must return the wall, not the trigger"


class TestOverlapBoxLayerMask:
    """Unity doc: Physics2D queries respect LayerMask filtering."""

    def test_wall_on_matching_layer_is_found(self):
        _make_static_wall(3.0, 3.0, layer=6)
        _run_lifecycle()

        hit = Physics2D.overlap_box(
            point=Vector2(3.0, 3.0),
            size=Vector2(1.0, 1.0),
            layer_mask=1 << 6,
        )
        assert hit is not None

    def test_wall_on_different_layer_is_not_found(self):
        _make_static_wall(3.0, 3.0, layer=6)
        _run_lifecycle()

        # Query layer 8 (not layer 6)
        hit = Physics2D.overlap_box(
            point=Vector2(3.0, 3.0),
            size=Vector2(1.0, 1.0),
            layer_mask=1 << 8,
        )
        assert hit is None, "overlap_box must not find objects on non-matching layers"

    def test_layer_mask_minus_one_finds_all(self):
        """layer_mask=-1 means all layers (Unity convention)."""
        _make_static_wall(3.0, 3.0, layer=6)
        _run_lifecycle()

        hit = Physics2D.overlap_box(
            point=Vector2(3.0, 3.0),
            size=Vector2(1.0, 1.0),
            layer_mask=-1,
        )
        assert hit is not None, "layer_mask=-1 should match all layers"


class TestStaticColliderAtNonOrigin:
    """Engine fix: static colliders placed at non-origin positions must be
    found by spatial queries. Before the fix, static bodies defaulted to
    (0,0) in pymunk's spatial hash."""

    def test_wall_at_positive_coords_found(self):
        _make_static_wall(10.0, 10.0, layer=6)
        _run_lifecycle()

        hit = Physics2D.overlap_box(
            point=Vector2(10.0, 10.0),
            size=Vector2(0.5, 0.5),
            layer_mask=1 << 6,
        )
        assert hit is not None, "Static collider at (10,10) must be found"

    def test_wall_at_negative_coords_found(self):
        _make_static_wall(-7.5, -12.0, layer=6)
        _run_lifecycle()

        hit = Physics2D.overlap_box(
            point=Vector2(-7.5, -12.0),
            size=Vector2(0.5, 0.5),
            layer_mask=1 << 6,
        )
        assert hit is not None, "Static collider at (-7.5,-12) must be found"

    def test_wall_not_found_at_origin_when_placed_far_away(self):
        """A wall at (10,10) must NOT be found by a query at origin."""
        _make_static_wall(10.0, 10.0, layer=6)
        _run_lifecycle()

        hit = Physics2D.overlap_box(
            point=Vector2(0.0, 0.0),
            size=Vector2(0.5, 0.5),
            layer_mask=1 << 6,
        )
        assert hit is None, "Wall at (10,10) must not be found at (0,0)"


# ---------------------------------------------------------------------------
# Movement contract tests
# ---------------------------------------------------------------------------

class TestMovementDirectionQueuing:
    """Pacman tutorial: direction queuing means next_direction is tried each
    frame and applied when the path opens up."""

    def _make_movement_scene(self):
        """Create a movement object with walls blocking specific directions."""
        from examples.pacman.pacman_python.movement import Movement

        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        # Wall above — occupied() checks 1.5 units ahead with a 0.75x0.75 box.
        # Place the wall at y=1.0 so the overlap is clear.
        _make_static_wall(0.0, 1.0, layer=6)

        # Pacman at origin
        pac = GameObject("Pacman")
        pac.transform.position = Vector2(0.0, 0.0)
        rb = pac.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.KINEMATIC
        pac.add_component(CircleCollider2D)
        mov = pac.add_component(Movement)
        mov.initial_direction = Vector2(0, 0)

        _run_lifecycle()
        return mov

    def test_set_direction_to_open_path_applies_immediately(self):
        """If the requested direction is open, direction is set immediately."""
        mov = self._make_movement_scene()

        # Right is open (no wall)
        mov.set_direction(Vector2(1, 0))
        assert mov.direction.x == 1 and mov.direction.y == 0
        assert mov.next_direction.x == 0 and mov.next_direction.y == 0

    def test_set_direction_to_blocked_path_queues(self):
        """If the requested direction is blocked, it goes into next_direction."""
        mov = self._make_movement_scene()

        # Up is blocked by wall at y=1.5
        mov.set_direction(Vector2(0, 1))
        # Direction should remain unchanged (was 0,0 from initial)
        assert mov.direction.x == 0 and mov.direction.y == 0
        # But next_direction should be queued
        assert mov.next_direction.x == 0 and mov.next_direction.y == 1

    def test_forced_direction_ignores_walls(self):
        """forced=True should set direction even if blocked."""
        mov = self._make_movement_scene()

        mov.set_direction(Vector2(0, 1), forced=True)
        assert mov.direction.x == 0 and mov.direction.y == 1
        assert mov.next_direction.x == 0 and mov.next_direction.y == 0


class TestMovementOccupied:
    """Movement.occupied() should return True for walls, False for open paths,
    and must ignore trigger colliders (pellets should not block movement)."""

    def _make_scene_with_wall_and_trigger(self):
        from examples.pacman.pacman_python.movement import Movement

        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        # Wall to the right at x=1.0 (adjacent cell, matching real maze grid)
        _make_static_wall(1.0, 0.0, layer=6)

        # Trigger pellet to the left at x=-1.0 (adjacent cell)
        _make_trigger(-1.0, 0.0, layer=0)

        # Pacman at origin
        pac = GameObject("Pacman")
        pac.transform.position = Vector2(0.0, 0.0)
        rb = pac.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.KINEMATIC
        pac.add_component(CircleCollider2D)
        mov = pac.add_component(Movement)
        mov.initial_direction = Vector2(0, 0)

        _run_lifecycle()
        return mov

    def test_occupied_returns_true_for_wall(self):
        mov = self._make_scene_with_wall_and_trigger()
        assert mov.occupied(Vector2(1, 0)) is True

    def test_occupied_returns_false_for_open_path(self):
        mov = self._make_scene_with_wall_and_trigger()
        # Up has no wall
        assert mov.occupied(Vector2(0, 1)) is False

    def test_occupied_ignores_triggers(self):
        """Pellets are triggers and must not block movement."""
        mov = self._make_scene_with_wall_and_trigger()
        # Left has a trigger but no wall
        assert mov.occupied(Vector2(-1, 0)) is False


class TestMovementSpeedMultiplier:
    """speed and speedMultiplier affect distance traveled per physics step."""

    def test_speed_multiplier_doubles_distance(self):
        from examples.pacman.pacman_python.movement import Movement

        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        pac = GameObject("Pacman")
        pac.transform.position = Vector2(0.0, 0.0)
        rb = pac.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.KINEMATIC
        pac.add_component(CircleCollider2D)
        mov = pac.add_component(Movement)
        mov.initial_direction = Vector2(1, 0)  # moving right

        _run_lifecycle()

        # Record position after one fixed_update at normal speed
        Time._fixed_delta_time = 1.0 / 50.0
        mov.direction = Vector2(1, 0)
        mov.fixed_update()
        pos1_x = pac.transform.position.x

        # Reset and double the multiplier
        pac.transform.position = Vector2(0.0, 0.0)
        mov.speed_multiplier = 2.0
        mov.fixed_update()
        pos2_x = pac.transform.position.x

        assert abs(pos2_x - 2.0 * pos1_x) < 0.001, (
            f"2x speed_multiplier should double distance: {pos2_x} vs 2*{pos1_x}"
        )


# ---------------------------------------------------------------------------
# Node contract tests
# ---------------------------------------------------------------------------

class TestNodeAvailableDirections:
    """Node.start() checks 4 directions for walls and builds available_directions."""

    def test_node_at_intersection_finds_open_dirs(self):
        from examples.pacman.pacman_python.node import Node

        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        # Wall above
        _make_static_wall(0.0, 1.0, layer=6)
        # Wall below
        _make_static_wall(0.0, -1.0, layer=6)

        # Node at origin
        node_go = GameObject("Node")
        node_go.transform.position = Vector2(0.0, 0.0)
        rb = node_go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.STATIC
        col = node_go.add_component(BoxCollider2D)
        col.is_trigger = True
        col.size = Vector2(0.5, 0.5)
        node = node_go.add_component(Node)

        _run_lifecycle()

        # Up and down are blocked, left and right should be available
        dir_tuples = [(d.x, d.y) for d in node.available_directions]
        assert (-1, 0) in dir_tuples, "Left should be available"
        assert (1, 0) in dir_tuples, "Right should be available"
        assert (0, 1) not in dir_tuples, "Up should be blocked"
        assert (0, -1) not in dir_tuples, "Down should be blocked"

    def test_node_with_no_walls_has_four_directions(self):
        from examples.pacman.pacman_python.node import Node

        pm = PhysicsManager.instance()
        pm.gravity = Vector2(0, 0)

        node_go = GameObject("Node")
        node_go.transform.position = Vector2(0.0, 0.0)
        rb = node_go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.STATIC
        col = node_go.add_component(BoxCollider2D)
        col.is_trigger = True
        col.size = Vector2(0.5, 0.5)
        node = node_go.add_component(Node)

        _run_lifecycle()

        assert len(node.available_directions) == 4, (
            f"Node with no walls should have 4 available directions, got {len(node.available_directions)}"
        )


# ---------------------------------------------------------------------------
# Maze data contract tests
# ---------------------------------------------------------------------------

class TestMazeData:
    """Maze coordinate conversion and intersection identification."""

    def test_cell_to_world_origin_cell(self):
        """Row 0, col 0 should map to top-left of centered maze."""
        from examples.pacman.pacman_python.maze_data import (
            cell_to_world, MAZE_OFFSET_X, MAZE_OFFSET_Y,
        )
        x, y = cell_to_world(0, 0)
        assert abs(x - MAZE_OFFSET_X) < 0.001
        assert abs(y - MAZE_OFFSET_Y) < 0.001

    def test_cell_to_world_adjacent_cells_are_one_unit_apart(self):
        """Adjacent cells differ by exactly 1 unit in x or y."""
        from examples.pacman.pacman_python.maze_data import cell_to_world

        x1, y1 = cell_to_world(5, 5)
        x2, y2 = cell_to_world(6, 5)
        assert abs((x2 - x1) - 1.0) < 0.001, "Horizontal neighbors should be 1 unit apart"

        x3, y3 = cell_to_world(5, 6)
        assert abs((y1 - y3) - 1.0) < 0.001, "Vertical neighbors should be 1 unit apart (y decreases)"

    def test_is_intersection_on_wall_is_false(self):
        from examples.pacman.pacman_python.maze_data import is_intersection
        # Row 0 is all walls
        assert is_intersection(0, 0) is False

    def test_is_intersection_finds_real_intersection(self):
        """An intersection is a path cell with 3+ open neighbors."""
        from examples.pacman.pacman_python.maze_data import is_intersection, MAZE

        # Find an actual intersection in the maze by brute force
        found = False
        for row in range(len(MAZE)):
            for col in range(len(MAZE[0])):
                if is_intersection(col, row):
                    found = True
                    break
            if found:
                break
        assert found, "Classic Pacman maze must contain at least one intersection"

    def test_get_cell_out_of_bounds_is_wall(self):
        """Out-of-bounds cells should return 'W' (wall)."""
        from examples.pacman.pacman_python.maze_data import get_cell
        assert get_cell(-1, 0) == "W"
        assert get_cell(0, -1) == "W"
        assert get_cell(100, 100) == "W"


# ---------------------------------------------------------------------------
# overlap_circle contract tests (also fixed)
# ---------------------------------------------------------------------------

class TestOverlapCircleSkipsTriggers:
    """Same trigger-skip contract for overlap_circle."""

    def test_overlap_circle_ignores_trigger(self):
        _make_trigger(5.0, 5.0, layer=6)
        _run_lifecycle()

        hit = Physics2D.overlap_circle(
            point=Vector2(5.0, 5.0),
            radius=1.0,
            layer_mask=1 << 6,
        )
        assert hit is None, "overlap_circle must ignore trigger colliders"

    def test_overlap_circle_finds_non_trigger(self):
        _make_static_wall(5.0, 5.0, layer=6)
        _run_lifecycle()

        hit = Physics2D.overlap_circle(
            point=Vector2(5.0, 5.0),
            radius=1.0,
            layer_mask=1 << 6,
        )
        assert hit is not None
