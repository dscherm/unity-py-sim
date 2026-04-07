"""GhostHome — ghost pen behavior with bounce and exit animation.

Port of zigurous GhostHome.cs. Bounces inside the pen, then
exits via a coroutine lerp animation when disabled.

Lesson applied: coroutines translate well between Python and C#.
Lesson applied: ghost house needs a gate to prevent re-entry.
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2
from src.engine.physics.rigidbody import Rigidbody2D
from src.engine.time_manager import Time
from src.engine.coroutine import WaitForSeconds

from .ghost_behavior import GhostBehavior
from .movement import Movement


class GhostHome(GhostBehavior):
    inside: GameObject | None = None   # Inside point (center of pen)
    outside: GameObject | None = None  # Outside point (above pen)

    def on_enable(self) -> None:
        self.stop_all_coroutines()

    def on_disable(self) -> None:
        self.start_coroutine(self._exit_transition())

    def on_collision_enter_2d(self, collision) -> None:
        # Bounce inside the pen — reverse direction
        if self.enabled and self.ghost and self.ghost.movement:
            movement = self.ghost.movement
            movement.set_direction(
                Vector2(-movement.direction.x, -movement.direction.y),
                forced=True,
            )

    def _exit_transition(self):
        """Coroutine: lerp from current position to inside, then to outside."""
        movement = self.ghost.movement if self.ghost else None
        if movement is None:
            return

        # Disable physics movement during transition
        movement.set_direction(Vector2(0, 0), forced=True)
        movement.enabled = False
        if movement.rb:
            movement.rb.is_kinematic = True

        position = self.ghost.game_object.transform.position

        # Lerp to inside point (0.5s)
        if self.inside:
            target = self.inside.transform.position
            elapsed = 0.0
            start_x, start_y = position.x, position.y
            while elapsed < 0.5:
                t = elapsed / 0.5
                self.ghost.game_object.transform.position = Vector2(
                    start_x + (target.x - start_x) * t,
                    start_y + (target.y - start_y) * t,
                )
                elapsed += Time.delta_time
                yield None

            self.ghost.game_object.transform.position = Vector2(target.x, target.y)

        # Lerp to outside point (0.5s)
        if self.outside:
            target = self.outside.transform.position
            position = self.ghost.game_object.transform.position
            elapsed = 0.0
            start_x, start_y = position.x, position.y
            while elapsed < 0.5:
                t = elapsed / 0.5
                self.ghost.game_object.transform.position = Vector2(
                    start_x + (target.x - start_x) * t,
                    start_y + (target.y - start_y) * t,
                )
                elapsed += Time.delta_time
                yield None

            self.ghost.game_object.transform.position = Vector2(target.x, target.y)

        # Re-enable movement, pick a direction
        if movement.rb:
            movement.rb.is_kinematic = False
        movement.enabled = True
        movement.set_direction(Vector2(-1, 0), forced=True)  # Default left
