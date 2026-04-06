"""GhostHome — bounce inside home box, exit transition via coroutine.

Line-by-line port of GhostHome.cs from zigurous/unity-pacman-tutorial.
"""

import random
from src.engine.math.vector import Vector2
from src.engine.coroutine import WaitForSeconds
from pacman_python.ghost_behavior import GhostBehavior
from pacman_python.movement import OBSTACLE_LAYER


class GhostHome(GhostBehavior):
    inside_position: Vector2 = Vector2(0, 0)   # Position inside ghost house
    outside_position: Vector2 = Vector2(0, 0)  # Position outside ghost house exit

    def on_enable(self) -> None:
        pass  # StopAllCoroutines equivalent — coroutine system handles this

    def on_disable(self) -> None:
        # Start exit transition coroutine
        if self.game_object.active:
            self.start_coroutine(self._exit_transition())

    def on_collision_enter_2d(self, collision) -> None:
        """Reverse direction on wall collision to create bouncing effect."""
        if self.ghost is None:
            return
        go = getattr(collision, 'game_object', collision)
        if go is not None and self.enabled and go.layer == OBSTACLE_LAYER:
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

        self.ghost.movement.set_direction(Vector2(0, 1), forced=True)
        self.ghost.movement.enabled = False

        pos = Vector2(self.transform.position.x, self.transform.position.y)
        duration = 0.5
        elapsed = 0.0

        # Animate to inside position
        while elapsed < duration:
            t = elapsed / duration
            x = pos.x + (self.inside_position.x - pos.x) * t
            y = pos.y + (self.inside_position.y - pos.y) * t
            self.ghost.set_position(Vector2(x, y))
            elapsed += Time.delta_time
            yield None

        elapsed = 0.0

        # Animate to outside position
        while elapsed < duration:
            t = elapsed / duration
            x = self.inside_position.x + (self.outside_position.x - self.inside_position.x) * t
            y = self.inside_position.y + (self.outside_position.y - self.inside_position.y) * t
            self.ghost.set_position(Vector2(x, y))
            elapsed += Time.delta_time
            yield None

        # Pick random direction and re-enable movement
        dir_x = -1.0 if random.random() < 0.5 else 1.0
        self.ghost.movement.set_direction(Vector2(dir_x, 0), forced=True)
        self.ghost.movement.enabled = True
