"""GhostChase — pursue target by minimizing distance at nodes.

Port of zigurous GhostChase.cs. When chase ends, enables scatter.
"""

from src.engine.math.vector import Vector2

from .ghost_behavior import GhostBehavior
from .node import Node


class GhostChase(GhostBehavior):

    def on_disable(self) -> None:
        if self.ghost and self.ghost.scatter:
            self.ghost.scatter.enable()  # Uses scatter.duration by default

    def on_trigger_enter_2d(self, other) -> None:
        other_go = getattr(other, "game_object", other)
        node = other_go.get_component(Node)
        if node is None or not self.enabled:
            return

        if self.ghost and self.ghost.frightened and self.ghost.frightened.enabled:
            return

        movement = self.ghost.movement if self.ghost else None
        target = self.ghost.target if self.ghost else None
        if movement is None or target is None:
            return

        available = node.available_directions
        if not available:
            return

        # Pick direction that minimizes distance to target
        target_pos = target.transform.position
        best_dir = available[0]
        min_dist = float("inf")

        for d in available:
            # Don't reverse
            if d.x == -movement.direction.x and d.y == -movement.direction.y:
                continue
            pos = self.transform.position
            new_x = pos.x + d.x
            new_y = pos.y + d.y
            dx = target_pos.x - new_x
            dy = target_pos.y - new_y
            dist = dx * dx + dy * dy
            if dist < min_dist:
                min_dist = dist
                best_dir = d

        movement.set_direction(best_dir)
