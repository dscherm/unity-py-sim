"""Paddle controller — Python equivalent of PaddleController.cs"""

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.physics.rigidbody import Rigidbody2D


class PaddleController(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.speed: float = 10.0
        self.bound_y: float = 4.0
        self.input_axis: str = "Vertical"

    def start(self):
        self.rb = self.get_component(Rigidbody2D)

    def fixed_update(self):
        input_val = Input.get_axis(self.input_axis)
        velocity = Vector2(0, input_val * self.speed)
        self.rb.velocity = velocity

        # Clamp position
        pos = self.transform.position
        if pos.y > self.bound_y:
            self.transform.position = Vector2(pos.x, self.bound_y)
            self.rb.velocity = Vector2(0, 0)
        elif pos.y < -self.bound_y:
            self.transform.position = Vector2(pos.x, -self.bound_y)
            self.rb.velocity = Vector2(0, 0)
