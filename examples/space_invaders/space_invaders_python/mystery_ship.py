"""Mystery ship — periodic bonus target flying across the top.

Maps to: zigurous/MysteryShip.cs
"""

from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time
from src.engine.coroutine import WaitForSeconds


class MysteryShip(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.speed: float = 5.0
        self.cycle_time: float = 30.0
        self.score: int = 300
        self.screen_bound_x: float = 8.0
        self._direction: int = -1  # -1=left, 1=right
        self._spawned: bool = False
        self._despawn_timer: float = 0.0

    def start(self):
        self._despawn()

    def update(self):
        if not self._spawned:
            self._despawn_timer += Time.delta_time
            if self._despawn_timer >= self.cycle_time:
                self._spawn()
            return

        dx = self.speed * Time.delta_time * self._direction
        pos = self.transform.position
        self.transform.position = Vector2(pos.x + dx, pos.y)

        # Check if reached other side
        if self._direction == 1 and pos.x >= self.screen_bound_x:
            self._despawn()
        elif self._direction == -1 and pos.x <= -self.screen_bound_x:
            self._despawn()

    def _spawn(self):
        self._direction *= -1
        if self._direction == 1:
            self.transform.position = Vector2(-self.screen_bound_x, self.transform.position.y)
        else:
            self.transform.position = Vector2(self.screen_bound_x, self.transform.position.y)
        self._spawned = True
        self.game_object.active = True

    def _despawn(self):
        self._spawned = False
        self._despawn_timer = 0.0
        # Move off-screen
        if self._direction == 1:
            self.transform.position = Vector2(self.screen_bound_x, self.transform.position.y)
        else:
            self.transform.position = Vector2(-self.screen_bound_x, self.transform.position.y)

    def on_trigger_enter_2d(self, other):
        from space_invaders_python.player import LAYER_LASER
        if other.layer == LAYER_LASER:
            self._despawn()
            from space_invaders_python.game_manager import GameManager
            if GameManager._instance:
                GameManager._instance.on_mystery_ship_killed(self)
