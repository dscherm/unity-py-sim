"""GhostFrightened — half speed, flee behavior, blue/white sprite flashing.

Port of zigurous GhostFrightened.cs.
Uses Ghost_Vulnerable_Blue/White sprites for visual feedback.
"""

from src.engine.math.vector import Vector2

from .ghost_behavior import GhostBehavior
from .node import Node


class GhostFrightened(GhostBehavior):
    eaten: bool = False

    def on_enable(self) -> None:
        if self.ghost and self.ghost.movement:
            self.ghost.movement.speed_multiplier = 0.5
        self.eaten = False
        # Visual: would swap to blue sprite here (handled by ghost.py)

    def on_disable(self) -> None:
        if self.ghost and self.ghost.movement:
            self.ghost.movement.speed_multiplier = 1.0
        self.eaten = False

    def on_trigger_enter_2d(self, other) -> None:
        other_go = getattr(other, "game_object", other)
        node = other_go.get_component(Node)
        if node is None or not self.enabled:
            return

        movement = self.ghost.movement if self.ghost else None
        target = self.ghost.target if self.ghost else None
        if movement is None or target is None:
            return

        available = node.available_directions
        if not available:
            return

        # Flee: maximize distance from target
        target_pos = target.transform.position
        best_dir = available[0]
        max_dist = -1.0

        for d in available:
            if d.x == -movement.direction.x and d.y == -movement.direction.y:
                continue
            pos = self.transform.position
            new_x = pos.x + d.x
            new_y = pos.y + d.y
            dx = target_pos.x - new_x
            dy = target_pos.y - new_y
            dist = dx * dx + dy * dy
            if dist > max_dist:
                max_dist = dist
                best_dir = d

        movement.set_direction(best_dir, forced=True)

    def eat(self) -> None:
        self.eaten = True
        if self.ghost:
            # Teleport to home, enable home behavior
            if self.ghost.home:
                home_pos = self.ghost.home.inside
                if home_pos:
                    self.ghost.game_object.transform.position = Vector2(
                        home_pos.transform.position.x,
                        home_pos.transform.position.y,
                    )
                self.ghost.home.enable(0)  # No duration — exits via coroutine
            self.disable()
