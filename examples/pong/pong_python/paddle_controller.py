"""Paddle controller — Python equivalent of PaddleController.cs"""

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.time_manager import Time
from src.engine.physics.rigidbody import Rigidbody2D


class PaddleController(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.speed: float = 10.0
        self.bound_y: float = 4.0
        self.input_axis: str = "Vertical"

    def start(self):
        self.rb = self.get_component(Rigidbody2D)
        self.rb._sync_from_transform()

    def update(self):
        input_val = Input.get_axis(self.input_axis)
        if abs(input_val) > 0.01:
            pos = self.transform.position
            new_y = pos.y + input_val * self.speed * Time.delta_time
            new_y = max(-self.bound_y, min(self.bound_y, new_y))
            self.transform.position = Vector2(pos.x, new_y)
            self.rb.move_position(Vector2(pos.x, new_y))
