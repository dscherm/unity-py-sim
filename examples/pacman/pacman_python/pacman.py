from __future__ import annotations
"""Pacman — player controller with input, rotation, and death sequence.

Line-by-line port of Pacman.cs from zigurous/unity-pacman-tutorial.
"""

import math
from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2
from src.engine.math.quaternion import Quaternion
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.collider import CircleCollider2D
from src.engine.input_manager import Input

from pacman_python.movement import Movement
from pacman_python.animated_sprite import AnimatedSprite


class Pacman(MonoBehaviour):
    death_sequence: AnimatedSprite | None = None
    sprite_renderer: SpriteRenderer | None = None
    circle_collider: CircleCollider2D | None = None
    movement: Movement | None = None

    def awake(self) -> None:
        self.sprite_renderer = self.get_component(SpriteRenderer)
        self.circle_collider = self.get_component(CircleCollider2D)
        self.movement = self.get_component(Movement)

    def update(self) -> None:
        # Set the new direction based on the current input
        if Input.get_key_down("w") or Input.get_key_down("up"):
            self.movement.set_direction(Vector2(0, 1))
        elif Input.get_key_down("s") or Input.get_key_down("down"):
            self.movement.set_direction(Vector2(0, -1))
        elif Input.get_key_down("a") or Input.get_key_down("left"):
            self.movement.set_direction(Vector2(-1, 0))
        elif Input.get_key_down("d") or Input.get_key_down("right"):
            self.movement.set_direction(Vector2(1, 0))

        # Rotate pacman to face the movement direction
        if self.movement.direction.x != 0 or self.movement.direction.y != 0:
            angle = math.atan2(self.movement.direction.y, self.movement.direction.x)
            angle_deg = math.degrees(angle)
            self.transform.rotation = Quaternion.euler(0, 0, angle_deg)

    def reset_state(self) -> None:
        self.enabled = True
        if self.sprite_renderer is not None:
            self.sprite_renderer.enabled = True
        if self.circle_collider is not None:
            self.circle_collider.enabled = True
        if self.death_sequence is not None:
            self.death_sequence.enabled = False
        if self.movement is not None:
            self.movement.reset_state()
        self.game_object.active = True

    def death_sequence_start(self) -> None:
        """Start the death animation — disables movement and normal sprite."""
        self.enabled = False
        if self.sprite_renderer is not None:
            self.sprite_renderer.enabled = False
        if self.circle_collider is not None:
            self.circle_collider.enabled = False
        if self.movement is not None:
            self.movement.enabled = False
        if self.death_sequence is not None:
            self.death_sequence.enabled = True
            self.death_sequence.restart()
