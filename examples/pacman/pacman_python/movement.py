"""Movement — grid-based movement with wall detection and direction queuing.

Line-by-line port of Movement.cs from zigurous/unity-pacman-tutorial.
Grid-snapping added to handle engine difference (no physics-resolved MovePosition).
"""

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2
from src.engine.physics.rigidbody import Rigidbody2D
from src.engine.physics.physics_manager import Physics2D
from src.engine.time_manager import Time


# Layer index for obstacles (walls)
OBSTACLE_LAYER: int = 6

# Grid cell size — maze uses 1-unit cells, offset by 0.5
CELL_SIZE: float = 1.0
GRID_OFFSET: float = 0.5  # Maze cells are at x.5 positions


class Movement(MonoBehaviour):
    speed: float = 8.0
    speed_multiplier: float = 1.0
    initial_direction: Vector2 = Vector2(0, 0)
    obstacle_layer: int = OBSTACLE_LAYER

    rb: Rigidbody2D | None = None
    direction: Vector2 = Vector2(0, 0)
    next_direction: Vector2 = Vector2(0, 0)
    starting_position: Vector2 = Vector2(0, 0)

    def awake(self) -> None:
        self.rb = self.get_component(Rigidbody2D)
        self.starting_position = Vector2(
            self.transform.position.x, self.transform.position.y
        )

    def start(self) -> None:
        self.reset_state()

    def reset_state(self) -> None:
        self.speed_multiplier = 1.0
        self.direction = Vector2(self.initial_direction.x, self.initial_direction.y)
        self.next_direction = Vector2(0, 0)
        self.transform.position = Vector2(
            self.starting_position.x, self.starting_position.y
        )
        self.rb.is_kinematic = False
        self.enabled = True

    def update(self) -> None:
        # Try to move in the next direction while it's queued to make
        # movements more responsive
        if self.next_direction.x != 0 or self.next_direction.y != 0:
            self.set_direction(self.next_direction)

    def fixed_update(self) -> None:
        if self.rb is None:
            return
        if self.direction.x == 0 and self.direction.y == 0:
            return
        if self.occupied(self.direction):
            return
        pos = self.transform.position
        position = Vector2(pos.x, pos.y)
        step = self.speed * self.speed_multiplier * Time.fixed_delta_time
        new_pos = Vector2(
            position.x + self.direction.x * step,
            position.y + self.direction.y * step,
        )
        self.rb.move_position(new_pos)
        self.transform.position = new_pos

    def set_direction(self, direction: Vector2, forced: bool = False) -> None:
        """Set movement direction if the tile in that direction is available.

        When turning, check from the grid-snapped position (not current position)
        to account for overshooting intersections. Then snap before moving.
        """
        if forced:
            self.direction = direction
            self.next_direction = Vector2(0, 0)
            return

        # For turns (changing axis), check from snapped position
        pos = self.transform.position
        changing_axis = (
            (direction.x != 0 and self.direction.y != 0) or
            (direction.y != 0 and self.direction.x != 0)
        )

        if changing_axis:
            # Snap to nearest grid on the perpendicular axis and check from there
            # X cells are at half-integers (offset 0.5), Y cells at integers (offset 0.0)
            if direction.x != 0:
                # Turning horizontal — snap Y to integer grid
                snapped = Vector2(pos.x, round(pos.y / CELL_SIZE) * CELL_SIZE)
            else:
                # Turning vertical — snap X to half-integer grid
                snapped = Vector2(round((pos.x - GRID_OFFSET) / CELL_SIZE) * CELL_SIZE + GRID_OFFSET, pos.y)
            # Check occupied from snapped position
            check_pos = Vector2(
                snapped.x + direction.x * 1.0,
                snapped.y + direction.y * 1.0,
            )
            hit = Physics2D.overlap_box(
                point=check_pos,
                size=Vector2(0.4, 0.4),
                angle=0.0,
                layer_mask=1 << self.obstacle_layer,
            )
            if hit is None:
                # Apply snap and change direction
                self.transform.position = snapped
                self.rb.move_position(snapped)
                self.direction = direction
                self.next_direction = Vector2(0, 0)
            else:
                self.next_direction = direction
        else:
            # Same axis or reversing — no snap needed
            if not self.occupied(direction):
                self.direction = direction
                self.next_direction = Vector2(0, 0)
            else:
                self.next_direction = direction

    def occupied(self, direction: Vector2) -> bool:
        """Check if there's an obstacle in the given direction.

        Uses overlap_box at 1 cell ahead, matching the intent of the C#
        BoxCast(transform.position, Vector2.one * 0.75f, 0f, direction, 1.5f).
        """
        pos = self.transform.position
        # Check half a cell ahead with a small box — lets character move
        # right up to the wall edge (within 0.5 cells)
        check_pos = Vector2(
            pos.x + direction.x * 0.5,
            pos.y + direction.y * 0.5,
        )
        hit = Physics2D.overlap_box(
            point=check_pos,
            size=Vector2(0.25, 0.25),
            angle=0.0,
            layer_mask=1 << self.obstacle_layer,
        )
        return hit is not None
