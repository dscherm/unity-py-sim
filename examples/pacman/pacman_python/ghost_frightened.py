from __future__ import annotations
"""GhostFrightened — at nodes, pick direction maximizing distance from Pacman.

Line-by-line port of GhostFrightened.cs from zigurous/unity-pacman-tutorial.
"""

from src.engine.math.vector import Vector2
from src.engine.rendering.renderer import SpriteRenderer
from pacman_python.ghost_behavior import GhostBehavior
from pacman_python.node import Node


class GhostFrightened(GhostBehavior):
    body: SpriteRenderer | None = None
    eyes: SpriteRenderer | None = None
    _eaten: bool = False

    _original_color: tuple = (255, 255, 255)

    def enable(self, duration: float = -1.0) -> None:
        super().enable(duration)

        # Swap to vulnerable appearance — change body color to blue
        if self.body is not None:
            self._original_color = self.body.color
            self.body.color = (33, 33, 222)  # Blue vulnerable color

        self._eaten = False

    def disable(self) -> None:
        super().disable()

        # Restore normal appearance
        if self.body is not None:
            self.body.color = self._original_color

    def eaten(self) -> None:
        """Called when Pacman eats this ghost while frightened."""
        self._eaten = True
        # Send ghost back home
        self.ghost.set_position(self.ghost.home.inside.position)
        self.ghost.home.enable(self.duration)

        if self.body is not None:
            self.body.enabled = False
        if self.eyes is not None:
            self.eyes.enabled = True

    def on_enable(self) -> None:
        if self.ghost is not None and self.ghost.movement is not None:
            self.ghost.movement.speed_multiplier = 0.5
        self._eaten = False

    def on_disable(self) -> None:
        if self.ghost is not None and self.ghost.movement is not None:
            self.ghost.movement.speed_multiplier = 1.0
        self._eaten = False

    def on_trigger_enter_2d(self, other) -> None:
        # Guard: ghost not yet wired
        if self.ghost is None:
            return
        node = other.get_component(Node) if hasattr(other, 'get_component') else None

        if node is not None and self.enabled:
            direction = Vector2(0, 0)
            max_distance = float('-inf')

            # Find direction that moves farthest from target (Pacman)
            for available_direction in node.available_directions:
                new_x = self.transform.position.x + available_direction.x
                new_y = self.transform.position.y + available_direction.y
                target = self.ghost.target
                dx = target.position.x - new_x
                dy = target.position.y - new_y
                distance = dx * dx + dy * dy  # sqrMagnitude

                if distance > max_distance:
                    direction = available_direction
                    max_distance = distance

            self.ghost.movement.set_direction(direction)
