"""GhostScatter — random direction at nodes, avoids reversing.

Line-by-line port of GhostScatter.cs from zigurous/unity-pacman-tutorial.
"""

import random
from src.engine.math.vector import Vector2
from pacman_python.ghost_behavior import GhostBehavior
from pacman_python.node import Node


class GhostScatter(GhostBehavior):

    def on_disable(self) -> None:
        if self.ghost is not None and self.ghost.chase is not None:
            self.ghost.chase.enable()

    def on_trigger_enter_2d(self, other) -> None:
        # Guard: ghost behaviors not yet wired (start() hasn't run)
        if self.ghost is None or self.ghost.frightened is None:
            return
        node = other.get_component(Node) if hasattr(other, 'get_component') else None

        # Do nothing while the ghost is frightened
        if node is not None and self.enabled and not self.ghost.frightened.enabled:
            dirs = node.available_directions
            if not dirs:
                return

            # Pick a random available direction
            index = random.randint(0, len(dirs) - 1)

            # Prefer not to go back the same direction so increment the
            # index to the next available direction
            if len(dirs) > 1:
                reverse = Vector2(
                    -self.ghost.movement.direction.x,
                    -self.ghost.movement.direction.y,
                )
                if (dirs[index].x == reverse.x and dirs[index].y == reverse.y):
                    index = (index + 1) % len(dirs)

            self.ghost.movement.set_direction(dirs[index])
