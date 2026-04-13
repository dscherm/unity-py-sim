from __future__ import annotations
"""GhostHome — ghost pen behavior with bounce and exit animation.

Port of zigurous GhostHome.cs, matching v1's working implementation.

Lesson from v1: on_disable must check game_object.active before starting coroutine.
Lesson from v1: exit transition must set is_kinematic and disable movement.
Lesson from v1: use ghost.set_position or sync rigidbody after position change.
"""

import random

from src.engine.core import GameObject
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time

from .ghost_behavior import GhostBehavior
from .movement import OBSTACLE_LAYER


class GhostHome(GhostBehavior):
    inside: GameObject | None = None   # Inside point (center of pen)
    outside: GameObject | None = None  # Outside point (above pen)

    def on_enable(self) -> None:
        self.stop_all_coroutines()

    def on_disable(self) -> None:
        # Guard: don't start exit if ghost isn't wired or object is inactive
        if self.ghost is not None and self.game_object.active:
            self.start_coroutine(self._exit_transition())

    def on_collision_enter_2d(self, collision) -> None:
        """Bounce inside the pen — reverse direction on wall collision."""
        other_go = getattr(collision, "game_object", collision)
        if self.enabled and other_go is not None and other_go.layer == OBSTACLE_LAYER:
            if self.ghost and self.ghost.movement:
                movement = self.ghost.movement
                movement.set_direction(
                    Vector2(-movement.direction.x, -movement.direction.y),
                    forced=True,
                )

    def _exit_transition(self):
        """Coroutine: animate ghost from current position → inside → outside."""
        movement = self.ghost.movement if self.ghost else None
        if movement is None:
            return

        # Disable physics movement during transition
        movement.set_direction(Vector2(0, 1), forced=True)
        if movement.rb:
            movement.rb.is_kinematic = True
        movement.enabled = False

        ghost_go = self.ghost.game_object
        start_pos = Vector2(ghost_go.transform.position.x, ghost_go.transform.position.y)

        # Phase 1: lerp to inside point (0.5s)
        if self.inside:
            target = self.inside.transform.position
            elapsed = 0.0
            while elapsed < 0.5:
                t = elapsed / 0.5
                x = start_pos.x + (target.x - start_pos.x) * t
                y = start_pos.y + (target.y - start_pos.y) * t
                ghost_go.transform.position = Vector2(x, y)
                if movement.rb:
                    movement.rb.move_position(Vector2(x, y))
                elapsed += Time.delta_time
                yield None
            ghost_go.transform.position = Vector2(target.x, target.y)
            if movement.rb:
                movement.rb.move_position(Vector2(target.x, target.y))

        # Phase 2: lerp to outside point (0.5s)
        if self.outside:
            inside_pos = Vector2(ghost_go.transform.position.x, ghost_go.transform.position.y)
            target = self.outside.transform.position
            elapsed = 0.0
            while elapsed < 0.5:
                t = elapsed / 0.5
                x = inside_pos.x + (target.x - inside_pos.x) * t
                y = inside_pos.y + (target.y - inside_pos.y) * t
                ghost_go.transform.position = Vector2(x, y)
                if movement.rb:
                    movement.rb.move_position(Vector2(x, y))
                elapsed += Time.delta_time
                yield None
            ghost_go.transform.position = Vector2(target.x, target.y)
            if movement.rb:
                movement.rb.move_position(Vector2(target.x, target.y))

        # Re-enable movement, pick random left/right
        dir_x = -1.0 if random.random() < 0.5 else 1.0
        movement.set_direction(Vector2(dir_x, 0), forced=True)
        if movement.rb:
            movement.rb.is_kinematic = False
        movement.enabled = True
