"""Projectile — moves in a direction, destroys on trigger collision.

Maps to: zigurous/Projectile.cs
Both lasers (player, upward) and missiles (invader, downward) use this class.
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time
from src.engine.physics.collider import BoxCollider2D


class Projectile(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.direction: Vector2 = Vector2(0, 1)  # up by default
        self.speed: float = 20.0

    def update(self):
        pos = self.transform.position
        self.transform.position = Vector2(
            pos.x + self.speed * Time.delta_time * self.direction.x,
            pos.y + self.speed * Time.delta_time * self.direction.y,
        )

    def on_trigger_enter_2d(self, other):
        self._check_collision(other)

    def on_trigger_stay_2d(self, other):
        self._check_collision(other)

    def _check_collision(self, other):
        # Check if hitting a bunker
        from space_invaders_python.bunker import Bunker
        # In our engine, trigger callbacks receive GameObject directly (not Collider2D)
        target = other if hasattr(other, 'get_component') else None
        bunker = target.get_component(Bunker) if target else None

        if bunker is None or bunker.check_collision(self.transform.position):
            self.game_object.active = False
