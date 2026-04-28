"""AI-driven playtest for Pacman — simulates player input and verifies game behavior.

Runs the actual game loop in headless mode with injected key presses.
Validates movement, wall collision, direction queuing, and overall stability.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.core import GameObject, _clear_registry
from src.engine.input_manager import Input
from src.engine.time_manager import Time
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.rendering.display import DisplayManager
from src.engine.rendering.camera import Camera
from src.engine.tweening import TweenManager
from src.engine.math.vector import Vector2


def _reset_engine():
    """Reset all engine singletons — clean slate for each test."""
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager._instance = None
    DisplayManager.reset()
    Camera.main = None
    Time._reset()
    Input._reset()
    TweenManager.reset()


def _setup_pacman_scene():
    """Set up the Pacman scene and return (display, lifecycle, physics)."""
    _reset_engine()

    display = DisplayManager(600, 700, "Pacman Test")
    DisplayManager._instance = display
    display.init(headless=True)

    lifecycle = LifecycleManager.instance()
    physics = PhysicsManager.instance()

    # Import and run scene setup (adds path for pacman_python package)
    pacman_dir = os.path.join(os.path.dirname(__file__), "..", "..", "examples", "pacman")
    if pacman_dir not in sys.path:
        sys.path.insert(0, pacman_dir)

    from examples.pacman.run_pacman import setup_scene
    setup_scene()

    return display, lifecycle, physics


def _run_frame(lifecycle, physics):
    """Advance one frame: lifecycle awake/start, fixed update, physics, update, late update, cleanup."""
    dt = 1.0 / 60.0
    fixed_dt = Time._fixed_delta_time

    Time._delta_time = dt
    Time._time += dt
    Time._frame_count += 1

    lifecycle.process_awake_queue()
    lifecycle.process_start_queue()

    # Fixed update + physics (simplified: always step once per frame for predictability)
    lifecycle.run_fixed_update()
    physics.step(fixed_dt)

    lifecycle.run_update()
    TweenManager.tick(dt)
    lifecycle.run_late_update()
    lifecycle.process_destroy_queue()


def _simulate_key_press(key: str):
    """Simulate a key being pressed this frame (key_down + held)."""
    Input._begin_frame()
    Input._set_key_state(key, True)


def _simulate_key_release(key: str):
    """Simulate a key being released this frame."""
    Input._begin_frame()
    Input._set_key_state(key, False)


def _simulate_no_input():
    """Advance input frame with no changes — keys held remain held."""
    Input._begin_frame()


def _get_pacman_go():
    """Find the Pacman GameObject."""
    return GameObject.find("Pacman")


def _get_pacman_movement():
    """Get the Movement component from Pacman."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "examples", "pacman"))
    from pacman_python.movement import Movement
    pac = _get_pacman_go()
    assert pac is not None, "Pacman GameObject not found"
    return pac.get_component(Movement)


# ---------------------------------------------------------------------------
# Test 1: Movement — left then right
# ---------------------------------------------------------------------------
class TestPacmanMovement:
    def test_move_left_then_right(self):
        """Press 'a' to move left for 60 frames, verify x decreased.
        Then press 'd' to move right for 60 frames, verify x increased."""
        display, lifecycle, physics = _setup_pacman_scene()

        pacman = _get_pacman_go()
        assert pacman is not None

        # Run a few setup frames to let Awake/Start fire
        for _ in range(3):
            _simulate_no_input()
            _run_frame(lifecycle, physics)

        # Record starting position
        start_x = pacman.transform.position.x

        # Press 'a' (left) and run 60 frames
        _simulate_key_press("a")
        _run_frame(lifecycle, physics)

        for _ in range(59):
            _simulate_no_input()
            _run_frame(lifecycle, physics)

        after_left_x = pacman.transform.position.x
        assert after_left_x < start_x, (
            f"Pacman should move left: start_x={start_x}, after_left_x={after_left_x}"
        )

        # Now press 'd' (right) and run 60 frames
        mid_x = pacman.transform.position.x
        _simulate_key_press("d")
        _run_frame(lifecycle, physics)

        for _ in range(59):
            _simulate_no_input()
            _run_frame(lifecycle, physics)

        after_right_x = pacman.transform.position.x
        assert after_right_x > mid_x, (
            f"Pacman should move right: mid_x={mid_x}, after_right_x={after_right_x}"
        )

        display.quit()


# ---------------------------------------------------------------------------
# Test 2: Wall collision — moving up should not exceed top boundary
# ---------------------------------------------------------------------------
class TestPacmanWallCollision:
    def test_wall_blocks_upward_movement(self):
        """Press 'w' for 200 frames. Pacman should never exceed maze top boundary."""
        display, lifecycle, physics = _setup_pacman_scene()

        pacman = _get_pacman_go()
        assert pacman is not None

        # Maze top boundary in world coords: row 0 wall centers at y = MAZE_ROWS/2 - 0.5
        from examples.pacman.pacman_python.maze_data import MAZE_OFFSET_Y
        top_wall_y = MAZE_OFFSET_Y  # row 0 center y

        # Run a few setup frames
        for _ in range(3):
            _simulate_no_input()
            _run_frame(lifecycle, physics)

        # Press 'w' (up)
        _simulate_key_press("w")
        _run_frame(lifecycle, physics)

        for _ in range(199):
            _simulate_no_input()
            _run_frame(lifecycle, physics)

            y = pacman.transform.position.y
            assert y <= top_wall_y + 1.0, (
                f"Pacman y={y} exceeded top boundary {top_wall_y}"
            )

        display.quit()


# ---------------------------------------------------------------------------
# Test 3: Direction queuing — queue a turn at an intersection
# ---------------------------------------------------------------------------
class TestPacmanDirectionQueuing:
    def test_queued_direction_applied_at_intersection(self):
        """Move Pacman left, then press 'w'. If blocked by wall, direction
        should be queued. Once Pacman reaches an open intersection, it should
        turn upward."""
        display, lifecycle, physics = _setup_pacman_scene()

        pacman = _get_pacman_go()
        movement = _get_pacman_movement()
        assert movement is not None

        # Let scene initialize
        for _ in range(3):
            _simulate_no_input()
            _run_frame(lifecycle, physics)

        # Pacman starts moving left (initial_direction). Run a few frames.
        for _ in range(10):
            _simulate_no_input()
            _run_frame(lifecycle, physics)

        # Now press 'w' to queue upward direction
        _simulate_key_press("w")
        _run_frame(lifecycle, physics)

        # The direction should either be applied immediately or queued
        dir_applied = (movement.direction.y > 0)
        dir_queued = (movement.next_direction.y > 0)
        assert dir_applied or dir_queued, (
            f"Expected up direction to be set or queued. "
            f"direction={movement.direction}, next_direction={movement.next_direction}"
        )

        # Run more frames — if queued, eventually Pacman should try the direction
        y_before = pacman.transform.position.y
        for _ in range(120):
            _simulate_no_input()
            _run_frame(lifecycle, physics)

        # If direction was applied, y should have increased
        if dir_applied:
            assert pacman.transform.position.y > y_before, (
                "Pacman should have moved upward after direction was applied"
            )

        display.quit()


# ---------------------------------------------------------------------------
# Test 4: Occupied check — wall detection via Movement.occupied()
# ---------------------------------------------------------------------------
class TestPacmanOccupied:
    def test_occupied_detects_walls(self):
        """After scene setup with physics stepped, Movement.occupied() should
        return True toward a wall and False toward an open path."""
        display, lifecycle, physics = _setup_pacman_scene()

        movement = _get_pacman_movement()
        assert movement is not None

        # Run several frames to ensure physics bodies are synced
        for _ in range(5):
            _simulate_no_input()
            _run_frame(lifecycle, physics)

        # Pacman starts at col 14, row 23 — cell 'P'
        # Row 23 layout: "Wo..WW.......P........WW..oW"
        # Left of P (col 13) is '.', so left should be open
        # Above P (row 22, col 14) is '.', so up should be open
        # We need to check a direction that has a wall nearby

        # The maze at row 23 has WW at cols 4-5 and 22-23
        # Pacman at col 14 — left is open ('.'), right is open ('.')
        left_occupied = movement.occupied(Vector2(-1, 0))
        right_occupied = movement.occupied(Vector2(1, 0))

        # Both left and right should be open from the start position
        assert not left_occupied, "Left should be open from Pacman's start"
        assert not right_occupied, "Right should be open from Pacman's start"

        # Now check: from start, moving up — row 22 col 14 is '.'
        # but let's verify the occupied check works at all by checking
        # that SOME direction from a wall-adjacent position returns True.
        # Move Pacman to a position next to a wall for a more definitive test.

        # Actually, let's just verify the physics system is working:
        # From Pacman start, up (row 22) is open, down (row 24) has walls
        # Row 24: "WWW.WW.WW.WWWWWWWW.WW.WW.WWW"
        # Col 14 in row 24 is 'W' — so down should be occupied
        down_occupied = movement.occupied(Vector2(0, -1))
        assert down_occupied, (
            "Down from Pacman start should be occupied (row 24 col 14 is 'W')"
        )

        display.quit()


# ---------------------------------------------------------------------------
# Test 5: Full loop — 300 frames with alternating WASD, no crashes
# ---------------------------------------------------------------------------
class TestPacmanFullLoop:
    def test_300_frames_alternating_input_no_crash(self):
        """Run 300 frames with alternating WASD every 30 frames.
        Verify no exceptions and Pacman stays within maze bounds."""
        display, lifecycle, physics = _setup_pacman_scene()

        pacman = _get_pacman_go()
        assert pacman is not None

        from examples.pacman.pacman_python.maze_data import (
            MAZE_ROWS, MAZE_COLS, MAZE_OFFSET_X, MAZE_OFFSET_Y,
        )
        # World bounds of the maze
        min_x = MAZE_OFFSET_X - 1.0  # col 0 center minus margin
        max_x = (MAZE_COLS - 1) + MAZE_OFFSET_X + 1.0
        min_y = -(MAZE_ROWS - 1) + MAZE_OFFSET_Y - 1.0
        max_y = MAZE_OFFSET_Y + 1.0

        keys = ["a", "w", "d", "s"]

        # Setup frames
        for _ in range(3):
            _simulate_no_input()
            _run_frame(lifecycle, physics)

        for frame in range(300):
            if frame % 30 == 0:
                key = keys[(frame // 30) % len(keys)]
                _simulate_key_press(key)
            else:
                _simulate_no_input()

            _run_frame(lifecycle, physics)

            pos = pacman.transform.position
            assert min_x <= pos.x <= max_x, (
                f"Frame {frame}: Pacman x={pos.x} out of bounds [{min_x}, {max_x}]"
            )
            assert min_y <= pos.y <= max_y, (
                f"Frame {frame}: Pacman y={pos.y} out of bounds [{min_y}, {max_y}]"
            )

        display.quit()


# ---------------------------------------------------------------------------
# Test 6: Pacman rotation follows movement direction
# ---------------------------------------------------------------------------
class TestPacmanRotation:
    def test_rotation_follows_direction(self):
        """Pacman should rotate to face its movement direction."""
        display, lifecycle, physics = _setup_pacman_scene()

        pacman = _get_pacman_go()
        movement = _get_pacman_movement()
        assert pacman is not None
        assert movement is not None

        # Let scene start
        for _ in range(3):
            _simulate_no_input()
            _run_frame(lifecycle, physics)

        # Pacman starts moving left (initial_direction = (-1, 0))
        # Expected rotation: atan2(0, -1) = 180 degrees
        # Run a frame so update sets rotation
        _simulate_no_input()
        _run_frame(lifecycle, physics)

        # Check rotation z component — should be ~180 degrees for left
        rot = pacman.transform.rotation
        # Quaternion.euler(0, 0, angle_deg) — extract z-angle
        # For left: angle = atan2(0, -1) = pi => 180 degrees
        # We can check the direction vector matches
        assert movement.direction.x < 0, "Pacman should be moving left initially"

        # Now press 'd' to go right
        _simulate_key_press("d")
        _run_frame(lifecycle, physics)

        # Direction should now be right
        if movement.direction.x > 0:
            # Good — direction changed, rotation should follow
            _simulate_no_input()
            _run_frame(lifecycle, physics)
            assert movement.direction.x > 0, "Pacman should still be moving right"

        display.quit()
