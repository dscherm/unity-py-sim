from __future__ import annotations
"""Movement — continuous physics-based movement matching zigurous Movement.cs.

Uses Rigidbody2D.MovePosition in FixedUpdate with direction queuing.
Occupied() check uses Physics2D.box_cast against obstacleLayer.

Lesson applied: grid-snapping on direction changes (from v1 gotchas).
Lesson applied: KINEMATIC to DYNAMIC loses mass — always set body_type carefully.
"""

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2
from src.engine.physics.rigidbody import Rigidbody2D
from src.engine.physics.physics_manager import Physics2D
from src.engine.time_manager import Time


OBSTACLE_LAYER: int = 6
CELL_SIZE: float = 1.0
GRID_OFFSET: float = 0.5


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
        new_pos = Vector2(self.starting_position.x, self.starting_position.y)
        self.transform.position = new_pos
        # Sync rigidbody position (lesson: teleport must sync rb)
        if self.rb:
            self.rb.move_position(new_pos)
            # Don't change body_type — ghosts are KINEMATIC and should stay that way
        self.enabled = True

    def update(self) -> None:
        if self.next_direction.x != 0 or self.next_direction.y != 0:
            self.set_direction(self.next_direction)

    def fixed_update(self) -> None:
        if self.rb is None or (self.direction.x == 0 and self.direction.y == 0):
            return
        if self.occupied(self.direction):
            return
        pos = self.transform.position
        step = self.speed * self.speed_multiplier * Time.fixed_delta_time
        new_pos = Vector2(
            pos.x + self.direction.x * step,
            pos.y + self.direction.y * step,
        )
        self.rb.move_position(new_pos)
        self.transform.position = new_pos

    def set_direction(self, direction: Vector2, forced: bool = False) -> None:
        if forced:
            self.direction = direction
            self.next_direction = Vector2(0, 0)
            return

        pos = self.transform.position
        changing_axis = (
            (direction.x != 0 and self.direction.y != 0) or
            (direction.y != 0 and self.direction.x != 0)
        )

        if changing_axis:
            if direction.x != 0:
                snapped = Vector2(pos.x, round(pos.y / CELL_SIZE) * CELL_SIZE)
            else:
                snapped = Vector2(
                    round((pos.x - GRID_OFFSET) / CELL_SIZE) * CELL_SIZE + GRID_OFFSET,
                    pos.y,
                )
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
                self.transform.position = snapped
                self.rb.move_position(snapped)
                self.direction = direction
                self.next_direction = Vector2(0, 0)
            else:
                self.next_direction = direction
        else:
            if not self.occupied(direction):
                self.direction = direction
                self.next_direction = Vector2(0, 0)
            else:
                self.next_direction = direction

    def occupied(self, direction: Vector2) -> bool:
        pos = self.transform.position
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
