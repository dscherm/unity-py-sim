"""GhostChase — at nodes, pick direction minimizing distance to Pacman.

Line-by-line port of GhostChase.cs from zigurous/unity-pacman-tutorial.
"""

from src.engine.math.vector import Vector2
from pacman_python.ghost_behavior import GhostBehavior
from pacman_python.node import Node


class GhostChase(GhostBehavior):

    def on_disable(self) -> None:
        if self.ghost is not None and self.ghost.scatter is not None:
            self.ghost.scatter.enable()

    def on_trigger_enter_2d(self, other) -> None:
        # Guard: ghost behaviors not yet wired (start() hasn't run)
        if self.ghost is None or self.ghost.frightened is None:
            return
        node = other.get_component(Node) if hasattr(other, 'get_component') else None

        # Do nothing while the ghost is frightened
        if node is not None and self.enabled and not self.ghost.frightened.enabled:
            direction = Vector2(0, 0)
            min_distance = float('inf')

            # Find the available direction that moves closest to target (Pacman)
            for available_direction in node.available_directions:
                new_x = self.transform.position.x + available_direction.x
                new_y = self.transform.position.y + available_direction.y
                target = self.ghost.target
                dx = target.position.x - new_x
                dy = target.position.y - new_y
                distance = dx * dx + dy * dy  # sqrMagnitude

                if distance < min_distance:
                    direction = available_direction
                    min_distance = distance

            self.ghost.movement.set_direction(direction)
