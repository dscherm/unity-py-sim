"""Player — horizontal movement, fires one laser at a time.

Maps to: zigurous/Player.cs
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.time_manager import Time
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.lifecycle import LifecycleManager


# Layer constants (matching Unity LayerMask)
LAYER_LASER = 8
LAYER_MISSILE = 9
LAYER_INVADER = 10
LAYER_BOUNDARY = 11


class Player(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.speed: float = 5.0
        self.screen_bound_x: float = 6.5
        self._laser: GameObject | None = None

    def update(self):
        pos = self.transform.position

        # Movement
        if Input.get_key("a") or Input.get_key("left"):
            pos = Vector2(pos.x - self.speed * Time.delta_time, pos.y)
        elif Input.get_key("d") or Input.get_key("right"):
            pos = Vector2(pos.x + self.speed * Time.delta_time, pos.y)

        # Clamp to screen
        pos = Vector2(
            max(-self.screen_bound_x, min(self.screen_bound_x, pos.x)),
            pos.y,
        )
        self.transform.position = pos

        # Fire — only one laser active at a time
        if self._laser is None or not self._laser.active:
            if Input.get_key_down("space") or Input.get_mouse_button_down(0):
                self._fire_laser()

    def _fire_laser(self):
        from space_invaders_python.projectile import Projectile

        laser = GameObject("Laser", tag="Laser")
        laser.layer = LAYER_LASER
        laser.transform.position = Vector2(
            self.transform.position.x,
            self.transform.position.y + 0.5,
        )

        rb = laser.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.KINEMATIC

        col = laser.add_component(BoxCollider2D)
        col.size = Vector2(0.2, 0.6)
        col.is_trigger = True
        col.build()

        sr = laser.add_component(SpriteRenderer)
        sr.color = (100, 255, 100)
        sr.size = Vector2(0.2, 0.6)
        sr.sorting_order = 5

        proj = laser.add_component(Projectile)
        proj.direction = Vector2(0, 1)
        proj.speed = 20.0

        LifecycleManager.instance().register_component(proj)
        self._laser = laser

    def on_trigger_enter_2d(self, other):
        if other.layer in (LAYER_MISSILE, LAYER_INVADER):
            from space_invaders_python.game_manager import GameManager
            if GameManager._instance:
                GameManager._instance.on_player_killed()
