"""GhostHome — bounce inside home box, exit transition via coroutine.

Line-by-line port of GhostHome.cs from zigurous/unity-pacman-tutorial.
"""

import random
from src.engine.math.vector import Vector2
from src.engine.transform import Transform
from pacman_python.ghost_behavior import GhostBehavior
from pacman_python.movement import OBSTACLE_LAYER


class GhostHome(GhostBehavior):
    inside: Transform | None = None    # Transform at center of ghost house
    outside: Transform | None = None   # Transform at ghost house exit

    def on_enable(self) -> None:
        self.stop_all_coroutines()

    def on_disable(self) -> None:
        # Check for active self to prevent error when object is destroyed
        # Also guard against being called before ghost is wired up
        if self.ghost is not None and self.game_object.active:
            self.start_coroutine(self._exit_transition())

    def on_collision_enter_2d(self, collision) -> None:
        """Reverse direction every time the ghost hits a wall to create
        the effect of the ghost bouncing around the home."""
        go = getattr(collision, 'game_object', collision)
        if self.enabled and go is not None and go.layer == OBSTACLE_LAYER:
            self.ghost.movement.set_direction(
                Vector2(
                    -self.ghost.movement.direction.x,
                    -self.ghost.movement.direction.y,
                ),
                forced=True,
            )

    def _exit_transition(self):
        """Coroutine: animate ghost from inside to outside the ghost house."""
        from src.engine.time_manager import Time

        # Turn off movement while we manually animate the position
        self.ghost.movement.set_direction(Vector2(0, 1), forced=True)
        self.ghost.movement.rb.is_kinematic = True
        self.ghost.movement.enabled = False

        position = Vector2(self.transform.position.x, self.transform.position.y)

        duration = 0.5
        elapsed = 0.0

        # Animate to the starting point (inside)
        while elapsed < duration:
            t = elapsed / duration
            x = position.x + (self.inside.position.x - position.x) * t
            y = position.y + (self.inside.position.y - position.y) * t
            self.ghost.set_position(Vector2(x, y))
            elapsed += Time.delta_time
            yield None

        elapsed = 0.0

        # Animate exiting the ghost home (inside -> outside)
        while elapsed < duration:
            t = elapsed / duration
            x = self.inside.position.x + (self.outside.position.x - self.inside.position.x) * t
            y = self.inside.position.y + (self.outside.position.y - self.inside.position.y) * t
            self.ghost.set_position(Vector2(x, y))
            elapsed += Time.delta_time
            yield None

        # Pick a random direction left or right and re-enable movement
        dir_x = -1.0 if random.random() < 0.5 else 1.0
        self.ghost.movement.set_direction(Vector2(dir_x, 0), forced=True)
        self.ghost.movement.rb.is_kinematic = False
        self.ghost.movement.enabled = True
