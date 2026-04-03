"""Mystery ship — periodic bonus target flying across the top.

Line-by-line port of: zigurous/MysteryShip.cs
"""

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2, Vector3
from src.engine.time_manager import Time
from src.engine.coroutine import WaitForSeconds


class MysteryShip(MonoBehaviour):
    """[RequireComponent(typeof(BoxCollider2D))]"""

    def __init__(self):
        super().__init__()
        self.speed: float = 5.0
        self.cycle_time: float = 30.0
        self.score: int = 300

        # private Vector2 leftDestination, rightDestination
        self.left_destination: Vector2 = Vector2(-8, 0)
        self.right_destination: Vector2 = Vector2(8, 0)
        # private int direction = -1
        self.direction: int = -1
        # private bool spawned
        self.spawned: bool = False
        self._invoke_timer: float = 0.0
        self._invoke_pending: bool = False

    def start(self):
        # Vector3 leftEdge = Camera.main.ViewportToWorldPoint(Vector3.zero)
        # Vector3 rightEdge = Camera.main.ViewportToWorldPoint(Vector3.right)
        # leftDestination = new Vector2(leftEdge.x - 1f, transform.position.y)
        # rightDestination = new Vector2(rightEdge.x + 1f, transform.position.y)
        y = self.transform.position.y
        self.left_destination = Vector2(-8.0, y)
        self.right_destination = Vector2(8.0, y)

        self._despawn()

    def update(self):
        # Invoke timer (simulates Invoke(nameof(Spawn), cycleTime))
        if self._invoke_pending:
            self._invoke_timer += Time.delta_time
            if self._invoke_timer >= self.cycle_time:
                self._invoke_pending = False
                self._spawn()

        # if (!spawned) return
        if not self.spawned:
            return

        # if (direction == 1) MoveRight(); else MoveLeft();
        if self.direction == 1:
            self._move_right()
        else:
            self._move_left()

    def _move_right(self):
        """private void MoveRight()"""
        # transform.position += speed * Time.deltaTime * Vector3.right
        pos = self.transform.position
        self.transform.position = Vector2(
            pos.x + self.speed * Time.delta_time,
            pos.y,
        )
        # if (transform.position.x >= rightDestination.x) Despawn()
        if self.transform.position.x >= self.right_destination.x:
            self._despawn()

    def _move_left(self):
        """private void MoveLeft()"""
        pos = self.transform.position
        self.transform.position = Vector2(
            pos.x - self.speed * Time.delta_time,
            pos.y,
        )
        if self.transform.position.x <= self.left_destination.x:
            self._despawn()

    def _spawn(self):
        """private void Spawn()"""
        # direction *= -1
        self.direction *= -1

        # if (direction == 1) transform.position = leftDestination
        if self.direction == 1:
            self.transform.position = Vector2(self.left_destination.x, self.left_destination.y)
        else:
            self.transform.position = Vector2(self.right_destination.x, self.right_destination.y)

        self.spawned = True

    def _despawn(self):
        """private void Despawn()"""
        self.spawned = False

        if self.direction == 1:
            self.transform.position = Vector2(self.right_destination.x, self.right_destination.y)
        else:
            self.transform.position = Vector2(self.left_destination.x, self.left_destination.y)

        # Invoke(nameof(Spawn), cycleTime)
        self._invoke_timer = 0.0
        self._invoke_pending = True

    def on_trigger_enter_2d(self, other):
        from space_invaders_python.player import LAYER_LASER
        # if (other.gameObject.layer == LayerMask.NameToLayer("Laser"))
        if other.layer == LAYER_LASER:
            self._despawn()
            # GameManager.Instance.OnMysteryShipKilled(this)
            from space_invaders_python.game_manager import GameManager
            if GameManager.instance is not None:
                GameManager.instance.on_mystery_ship_killed(self)
