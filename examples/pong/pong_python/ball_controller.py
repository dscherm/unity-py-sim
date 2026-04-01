"""Ball controller — Python equivalent of BallController.cs"""

import random

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2
from src.engine.physics.rigidbody import Rigidbody2D


class BallController(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.initial_speed: float = 8.0
        self.speed_increase: float = 0.5
        self.current_speed: float = 8.0

    def start(self):
        self.rb = self.get_component(Rigidbody2D)
        self.current_speed = self.initial_speed
        self.launch()

    def launch(self):
        x_dir = 1.0 if random.random() > 0.5 else -1.0
        y_dir = random.uniform(-0.5, 0.5)
        direction = Vector2(x_dir, y_dir).normalized
        self.rb.velocity = direction * self.current_speed

    def reset(self):
        self.transform.position = Vector2(0, 0)
        self.rb.velocity = Vector2(0, 0)
        self.current_speed = self.initial_speed

    def on_collision_enter_2d(self, collision):
        if collision.game_object.tag == "Paddle":
            self.current_speed += self.speed_increase

            # Reflect with angle based on hit position
            hit_y = self.transform.position.y - collision.game_object.transform.position.y
            normalized_hit = hit_y / 1.0  # Paddle half-height
            x_dir = -1.0 if self.rb.velocity.x > 0 else 1.0
            direction = Vector2(x_dir, normalized_hit).normalized
            self.rb.velocity = direction * self.current_speed
