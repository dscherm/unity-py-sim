"""Movement — grid-based movement with wall detection and direction queuing.

Line-by-line port of Movement.cs from zigurous/unity-pacman-tutorial.
"""

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2
from src.engine.physics.rigidbody import Rigidbody2D
from src.engine.physics.physics_manager import Physics2D
from src.engine.time_manager import Time


# Layer index for obstacles (walls)
OBSTACLE_LAYER: int = 6


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
        # C# reference: always moves, no occupied check in FixedUpdate
        if self.rb is None:
            return
        pos = self.rb._body.position
        position = Vector2(pos[0], pos[1])
        translation = Vector2(
            self.speed * self.speed_multiplier * Time.fixed_delta_time * self.direction.x,
            self.speed * self.speed_multiplier * Time.fixed_delta_time * self.direction.y,
        )
        new_pos = Vector2(position.x + translation.x, position.y + translation.y)
        self.rb.move_position(new_pos)

    def set_direction(self, direction: Vector2, forced: bool = False) -> None:
        """Set movement direction if the tile in that direction is available."""
        if forced or not self.occupied(direction):
            self.direction = direction
            self.next_direction = Vector2(0, 0)
        else:
            self.next_direction = direction

    def occupied(self, direction: Vector2) -> bool:
        """Check if there's an obstacle in the given direction.

        Uses Physics2D.box_cast matching C# reference:
        BoxCast(transform.position, Vector2.one * 0.75f, 0f, direction, 1.5f, obstacleLayer)
        """
        hit = Physics2D.box_cast(
            origin=Vector2(self.transform.position.x, self.transform.position.y),
            size=Vector2(0.75, 0.75),
            angle=0.0,
            direction=direction,
            distance=1.5,
            layer_mask=1 << self.obstacle_layer,
        )
        return hit is not None
