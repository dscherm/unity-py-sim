"""Ball controller — bounces off walls, paddle, and bricks."""

import random
import math

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2
from src.engine.physics.rigidbody import Rigidbody2D


class BallController(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.speed: float = 6.0
        self.max_speed: float = 12.0
        self.attached: bool = True
        self.paddle_offset: Vector2 = Vector2(0, 0.6)

    def start(self):
        self.rb = self.get_component(Rigidbody2D)
        self.rb._sync_from_transform()
        self.paddle = GameObject.find("Paddle")

    def update(self):
        if self.attached:
            # Follow paddle
            if self.paddle:
                paddle_pos = self.paddle.transform.position
                self.transform.position = Vector2(
                    paddle_pos.x + self.paddle_offset.x,
                    paddle_pos.y + self.paddle_offset.y,
                )
                self.rb.move_position(self.transform.position)

            # Launch on space
            from src.engine.input_manager import Input
            if Input.get_key_down("space"):
                self.launch()
            return

        # Check bounds — bounce off top and sides
        pos = self.transform.position
        vel = self.rb.velocity

        # Side walls
        if pos.x < -7.5 and vel.x < 0:
            self.rb.velocity = Vector2(-vel.x, vel.y)
            self.transform.position = Vector2(-7.5, pos.y)
        elif pos.x > 7.5 and vel.x > 0:
            self.rb.velocity = Vector2(-vel.x, vel.y)
            self.transform.position = Vector2(7.5, pos.y)

        # Top wall
        if pos.y > 5.5 and vel.y > 0:
            self.rb.velocity = Vector2(vel.x, -vel.y)
            self.transform.position = Vector2(pos.x, 5.5)

        # Ball lost (below paddle)
        if pos.y < -6.0:
            from breakout_python.game_manager import GameManager
            GameManager.on_ball_lost()
            self.reset()

    def on_collision_enter_2d(self, collision):
        if collision.game_object.tag == "Paddle":
            # Angle based on hit position
            paddle_pos = collision.game_object.transform.position
            hit_x = self.transform.position.x - paddle_pos.x
            # Normalize to -1..1 based on paddle width (~2 units)
            normalized = max(-1.0, min(1.0, hit_x / 1.0))
            # Angle between 30 and 150 degrees (always upward)
            angle = math.pi * (0.25 + 0.5 * (1.0 - (normalized + 1.0) / 2.0))
            direction = Vector2(math.cos(angle), math.sin(angle)).normalized
            self.rb.velocity = direction * self.speed

        elif collision.game_object.tag == "Brick":
            # Reflect off brick
            vel = self.rb.velocity
            # Simple: reflect Y
            self.rb.velocity = Vector2(vel.x, -vel.y)

    def launch(self):
        """Launch ball upward at a slight random angle."""
        self.attached = False
        angle = math.pi / 2 + random.uniform(-0.3, 0.3)
        direction = Vector2(math.cos(angle), math.sin(angle)).normalized
        self.rb.velocity = direction * self.speed

    def reset(self):
        """Reset ball to paddle."""
        self.attached = True
        self.rb.velocity = Vector2(0, 0)
        if self.paddle:
            paddle_pos = self.paddle.transform.position
            self.transform.position = Vector2(
                paddle_pos.x + self.paddle_offset.x,
                paddle_pos.y + self.paddle_offset.y,
            )
            self.rb.move_position(self.transform.position)
