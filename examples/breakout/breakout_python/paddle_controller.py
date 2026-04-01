"""Paddle controller — moves horizontally, clamped to screen bounds."""

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.time_manager import Time
from src.engine.physics.rigidbody import Rigidbody2D


class PaddleController(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.speed: float = 12.0
        self.bound_x: float = 6.5
        self.ball_attached: bool = True

    def start(self):
        self.rb = self.get_component(Rigidbody2D)
        self.rb._sync_from_transform()

    def update(self):
        input_val = Input.get_axis("Horizontal")
        if abs(input_val) > 0.01:
            pos = self.transform.position
            new_x = pos.x + input_val * self.speed * Time.delta_time
            new_x = max(-self.bound_x, min(self.bound_x, new_x))
            self.transform.position = Vector2(new_x, pos.y)
            self.rb.move_position(Vector2(new_x, pos.y))

    def launch_ball(self):
        """Release the ball from the paddle."""
        self.ball_attached = False
