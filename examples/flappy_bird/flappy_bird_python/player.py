from __future__ import annotations
"""Player — Flappy Bird player controller.

Line-by-line translation of Player.cs from zigurous/unity-flappy-bird-tutorial.
"""

from src.engine.core import MonoBehaviour
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.input_manager import Input
from src.engine.time_manager import Time
from src.engine.math.vector import Vector3


class Player(MonoBehaviour):

    def __init__(self) -> None:
        super().__init__()
        self.sprites: list = []  # Sprite[]
        self.strength: float = 5.0
        self.gravity: float = -9.81
        self.tilt: float = 5.0

        self._sprite_renderer: SpriteRenderer | None = None
        self._direction: Vector3 = Vector3(0, 0, 0)
        self._sprite_index: int = 0

    def awake(self) -> None:
        self._sprite_renderer = self.get_component(SpriteRenderer)

    def start(self) -> None:
        self.invoke_repeating("animate_sprite", 0.15, 0.15)

    def on_enable(self) -> None:
        position = self.transform.position
        position = Vector3(position.x, 0.0, position.z)
        self.transform.position = position
        self._direction = Vector3.zero

    def update(self) -> None:
        if Input.get_key_down("space") or Input.get_mouse_button_down(0):
            self._direction = Vector3.up * self.strength

        # Apply gravity and update the position
        self._direction = Vector3(
            self._direction.x,
            self._direction.y + self.gravity * Time.delta_time,
            self._direction.z,
        )
        self.transform.position = self.transform.position + self._direction * Time.delta_time

        # Tilt the bird based on the direction
        rotation = self.transform.euler_angles
        rotation = Vector3(rotation.x, rotation.y, self._direction.y * self.tilt)
        self.transform.euler_angles = rotation

    def animate_sprite(self) -> None:
        self._sprite_index += 1

        if self._sprite_index >= len(self.sprites):
            self._sprite_index = 0

        if self._sprite_index < len(self.sprites) and self._sprite_index >= 0:
            if self._sprite_renderer is not None:
                self._sprite_renderer.sprite = self.sprites[self._sprite_index]

    def on_trigger_enter_2d(self, other) -> None:
        if other.game_object.compare_tag("Obstacle"):
            from examples.flappy_bird.flappy_bird_python.game_manager import GameManager
            GameManager.instance.game_over()
        elif other.game_object.compare_tag("Scoring"):
            from examples.flappy_bird.flappy_bird_python.game_manager import GameManager
            GameManager.instance.increase_score()
