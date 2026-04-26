from __future__ import annotations
"""GhostFrightened — half speed, flee behavior, blue/white sprite swap.

Port of zigurous GhostFrightened.cs.
For v2 with real sprites: swaps body sprite to vulnerable blue/white PNGs.
"""

import pygame

from src.engine.math.vector import Vector2
from src.engine.rendering.renderer import SpriteRenderer

from .animated_sprite import AnimatedSprite
from .ghost_behavior import GhostBehavior
from .node import Node


class GhostFrightened(GhostBehavior):
    eaten: bool = False

    # Set by run_pacman_v2.py — the vulnerable sprite surfaces
    blue_sprite: pygame.Surface | None = None
    white_sprite: pygame.Surface | None = None

    _body_sr: SpriteRenderer | None = None
    _original_sprite: pygame.Surface | None = None
    _eyes_sr: SpriteRenderer | None = None
    _body_anim: AnimatedSprite | None = None

    def enable(self, duration: float = -1.0) -> None:
        super().enable(duration)
        self.eaten = False

        # Disable AnimatedSprite so it doesn't overwrite the blue/white sprite
        if self._body_anim is None and self.ghost:
            self._body_anim = self.ghost.game_object.get_component(AnimatedSprite)
        if self._body_anim:
            self._body_anim.enabled = False

        # Swap to blue vulnerable sprite
        if self._body_sr is None and self.ghost:
            self._body_sr = self.ghost.game_object.get_component(SpriteRenderer)
        if self._body_sr and self.blue_sprite:
            self._original_sprite = self._body_sr.sprite
            self._body_sr.sprite = self.blue_sprite
            # Ensure the renderer is visible (AnimatedSprite.on_disable hides it)
            self._body_sr.enabled = True

        # Hide eyes while frightened
        if self.ghost and self.ghost.eyes:
            eyes_sr = self.ghost.eyes.get_component(SpriteRenderer)
            if eyes_sr:
                self._eyes_sr = eyes_sr
                eyes_sr.enabled = False

        # Schedule flash at halfway point
        if duration > 0:
            self.cancel_invoke("_flash")
            self.invoke("_flash", duration / 2)

    def disable(self) -> None:
        super().disable()
        self.eaten = False

        # Restore original sprite
        if self._body_sr and self._original_sprite:
            self._body_sr.sprite = self._original_sprite

        # Re-enable AnimatedSprite (resumes normal ghost body animation)
        if self._body_anim:
            self._body_anim.enabled = True

        # Show eyes again
        if self._eyes_sr:
            self._eyes_sr.enabled = True

        self.cancel_invoke("_flash")

    def _flash(self) -> None:
        """Switch to white sprite to warn frightened mode is ending."""
        if self._body_sr and self.white_sprite:
            self._body_sr.sprite = self.white_sprite

    def on_enable(self) -> None:
        if self.ghost and self.ghost.movement:
            self.ghost.movement.speed_multiplier = 0.5
        self.eaten = False

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

        movement.set_direction(best_dir)

    def eat(self) -> None:
        self.eaten = True
        if self.ghost:
            # Teleport to home position
            if self.ghost.home and self.ghost.home.inside:
                home_pos = self.ghost.home.inside.transform.position
                self.ghost.game_object.transform.position = Vector2(home_pos.x, home_pos.y)
                if self.ghost.movement and self.ghost.movement.rb:
                    self.ghost.movement.rb.move_position(Vector2(home_pos.x, home_pos.y))
                self.ghost.home.enable()
            self.disable()
