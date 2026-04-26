from __future__ import annotations
"""Pacman player controller — port of zigurous Pacman.cs.

Reads WASD/arrow input, sets movement direction, rotates sprite to face
movement direction using Atan2. Death sequence disables all components
and plays the death animation.

Lesson applied: Awake runs regardless of enabled state.
Lesson applied: enabled property fires on_enable/on_disable callbacks.
"""

import math

from src.engine.core import MonoBehaviour
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.collider import CircleCollider2D
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input

from .movement import Movement
from .animated_sprite import AnimatedSprite


class Pacman(MonoBehaviour):
    death_sequence: AnimatedSprite | None = None
    _sprite_renderer: SpriteRenderer | None = None
    _collider: CircleCollider2D | None = None
    movement: Movement | None = None

    def awake(self) -> None:
        self._sprite_renderer = self.get_component(SpriteRenderer)
        self._collider = self.get_component(CircleCollider2D)
        self.movement = self.get_component(Movement)

    def update(self) -> None:
        if Input.get_key_down("w") or Input.get_key_down("up"):
            self.movement.set_direction(Vector2(0, 1))
        elif Input.get_key_down("s") or Input.get_key_down("down"):
            self.movement.set_direction(Vector2(0, -1))
        elif Input.get_key_down("a") or Input.get_key_down("left"):
            self.movement.set_direction(Vector2(-1, 0))
        elif Input.get_key_down("d") or Input.get_key_down("right"):
            self.movement.set_direction(Vector2(1, 0))

        # Rotate sprite to face movement direction (matching C# Atan2 rotation)
        direction = self.movement.direction
        if direction.x != 0 or direction.y != 0:
            angle = math.atan2(direction.y, direction.x)
            self.transform.rotation_z = math.degrees(angle)

    def reset_state(self) -> None:
        self.enabled = True
        if self._sprite_renderer:
            self._sprite_renderer.enabled = True
        if self._collider:
            self._collider.enabled = True
        if self.movement:
            self.movement.reset_state()
        if self.death_sequence:
            self.death_sequence.enabled = False
        self.game_object.active = True

    def death_sequence_start(self) -> None:
        self.enabled = False
        if self._sprite_renderer:
            self._sprite_renderer.enabled = False
        if self._collider:
            self._collider.enabled = False
        if self.movement:
            self.movement.enabled = False
        if self.death_sequence:
            self.death_sequence.enabled = True
            self.death_sequence.restart()
