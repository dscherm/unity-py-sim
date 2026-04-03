"""Player — horizontal movement, fires one laser at a time.

Line-by-line port of: zigurous/Player.cs
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2, Vector3
from src.engine.input_manager import Input
from src.engine.time_manager import Time
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.lifecycle import LifecycleManager


# Layer constants matching Unity LayerMask.NameToLayer
LAYER_LASER = 8
LAYER_MISSILE = 9
LAYER_INVADER = 10
LAYER_BOUNDARY = 11


class Player(MonoBehaviour):
    """[RequireComponent(typeof(Rigidbody2D))]
    [RequireComponent(typeof(BoxCollider2D))]"""

    def __init__(self):
        super().__init__()
        self.speed: float = 5.0
        # public Projectile laserPrefab — we instantiate directly instead
        self.laser_prefab = None  # prefab reference (not used — we build inline)
        self._laser: GameObject | None = None  # private Projectile laser

    def update(self):
        # Vector3 position = transform.position
        position = self.transform.position

        # if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow))
        if Input.get_key("a") or Input.get_key("left"):
            position = Vector2(position.x - self.speed * Time.delta_time, position.y)
        elif Input.get_key("d") or Input.get_key("right"):
            position = Vector2(position.x + self.speed * Time.delta_time, position.y)

        # Clamp: position.x = Mathf.Clamp(position.x, leftEdge.x, rightEdge.x)
        # ViewportToWorldPoint approximated by screen bounds
        left_edge = -6.5
        right_edge = 6.5
        position = Vector2(
            max(left_edge, min(right_edge, position.x)),
            position.y,
        )

        # transform.position = position
        self.transform.position = position

        # if (laser == null && (Input.GetKeyDown(KeyCode.Space) || Input.GetMouseButtonDown(0)))
        if (self._laser is None or not self._laser.active) and \
           (Input.get_key_down("space") or Input.get_mouse_button_down(0)):
            # laser = Instantiate(laserPrefab, transform.position, Quaternion.identity)
            self._laser = self._instantiate_laser()

    def _instantiate_laser(self) -> GameObject:
        """Equivalent of Instantiate(laserPrefab, transform.position, Quaternion.identity)."""
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
        proj.direction = Vector3(0, 1, 0)  # Vector3.up
        proj.speed = 20.0

        LifecycleManager.instance().register_component(proj)
        return laser

    def on_trigger_enter_2d(self, other):
        # if (other.gameObject.layer == LayerMask.NameToLayer("Missile") ||
        #     other.gameObject.layer == LayerMask.NameToLayer("Invader"))
        if other.layer == LAYER_MISSILE or other.layer == LAYER_INVADER:
            # GameManager.Instance.OnPlayerKilled(this)
            from space_invaders_python.game_manager import GameManager
            if GameManager.instance is not None:
                GameManager.instance.on_player_killed(self)
