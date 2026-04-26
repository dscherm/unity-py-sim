"""GhostScatter — random direction at nodes (avoids reversing).

Port of zigurous GhostScatter.cs. When scatter ends, enables chase.
"""

import random

from src.engine.math.vector import Vector2

from .ghost_behavior import GhostBehavior
from .node import Node


class GhostScatter(GhostBehavior):

    def on_disable(self) -> None:
        if self.ghost and self.ghost.chase:
            self.ghost.chase.enable()  # Uses chase.duration by default

    def on_trigger_enter_2d(self, other) -> None:
        other_go = getattr(other, "game_object", other)
        node = other_go.get_component(Node)
        if node is None or not self.enabled:
            return

        # Don't pick direction if frightened is active
        if self.ghost and self.ghost.frightened and self.ghost.frightened.enabled:
            return

        movement = self.ghost.movement if self.ghost else None
        if movement is None:
            return

        available = node.available_directions
        if not available:
            return

        # Pick random direction, avoid reversing
        direction = random.choice(available)
        reverse = Vector2(-movement.direction.x, -movement.direction.y)

        if direction.x == reverse.x and direction.y == reverse.y and len(available) > 1:
            idx = available.index(direction)
            direction = available[(idx + 1) % len(available)]

        movement.set_direction(direction)
