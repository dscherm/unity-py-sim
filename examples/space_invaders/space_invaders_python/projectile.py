"""Projectile — moves in a direction, destroyed on trigger collision.

Line-by-line port of: zigurous/Projectile.cs
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2, Vector3
from src.engine.time_manager import Time
from src.engine.physics.collider import BoxCollider2D


class Projectile(MonoBehaviour):
    """[RequireComponent(typeof(Rigidbody2D))]
    [RequireComponent(typeof(BoxCollider2D))]"""

    def __init__(self):
        super().__init__()
        self.direction: Vector3 = Vector3(0, 1, 0)  # Vector3.up
        self.speed: float = 20.0

    def awake(self):
        self.box_collider = self.get_component(BoxCollider2D)

    def update(self):
        # transform.position += speed * Time.deltaTime * direction
        pos = self.transform.position
        dx = self.speed * Time.delta_time * self.direction.x
        dy = self.speed * Time.delta_time * self.direction.y
        self.transform.position = Vector2(pos.x + dx, pos.y + dy)

    def on_trigger_enter_2d(self, other):
        self._check_collision(other)

    def on_trigger_stay_2d(self, other):
        self._check_collision(other)

    def _check_collision(self, other):
        # Bunker bunker = other.gameObject.GetComponent<Bunker>();
        from space_invaders_python.bunker import Bunker
        bunker = other.get_component(Bunker) if hasattr(other, 'get_component') else None

        # if (bunker == null || bunker.CheckCollision(boxCollider, transform.position))
        if bunker is None or bunker.check_collision(self.box_collider, self.transform.position):
            # Destroy(gameObject)
            self.game_object.active = False
