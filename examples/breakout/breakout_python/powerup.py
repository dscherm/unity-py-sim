"""Powerup — drops from bricks, collected by paddle."""

import random

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time
from src.engine.rendering.renderer import SpriteRenderer


class PowerupType:
    WIDE_PADDLE = "wide_paddle"
    EXTRA_LIFE = "extra_life"
    SPEED_BALL = "speed_ball"


# Color per type
POWERUP_COLORS = {
    PowerupType.WIDE_PADDLE: (100, 200, 255),   # light blue
    PowerupType.EXTRA_LIFE: (255, 100, 200),     # pink
    PowerupType.SPEED_BALL: (255, 200, 50),      # gold
}

POWERUP_WEIGHTS = [
    (PowerupType.WIDE_PADDLE, 0.4),
    (PowerupType.EXTRA_LIFE, 0.2),
    (PowerupType.SPEED_BALL, 0.4),
]


class Powerup(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.fall_speed: float = 3.0
        self.powerup_type: str = PowerupType.WIDE_PADDLE

    def update(self):
        # Fall downward
        pos = self.transform.position
        new_y = pos.y - self.fall_speed * Time.delta_time
        self.transform.position = Vector2(pos.x, new_y)

        # Check paddle collision (simple AABB)
        paddle = GameObject.find("Paddle")
        if paddle and paddle.active:
            pp = paddle.transform.position
            if (abs(pos.x - pp.x) < 1.2 and abs(new_y - pp.y) < 0.5):
                self._apply(paddle)
                self.game_object.active = False
                return

        # Off screen
        if new_y < -7:
            self.game_object.active = False

    def _apply(self, paddle):
        from breakout_python.game_manager import GameManager

        if self.powerup_type == PowerupType.EXTRA_LIFE:
            GameManager.lives += 1
            GameManager._update_display()

        elif self.powerup_type == PowerupType.WIDE_PADDLE:
            # Widen paddle renderer
            sr = paddle.get_component(SpriteRenderer)
            if sr:
                sr.size = Vector2(3.0, 0.4)
                sr.color = POWERUP_COLORS[PowerupType.WIDE_PADDLE]
            # Reset after duration handled by PowerupTimer

        elif self.powerup_type == PowerupType.SPEED_BALL:
            ball = GameObject.find("Ball")
            if ball:
                from breakout_python.ball_controller import BallController
                bc = ball.get_component(BallController)
                if bc:
                    bc.speed = min(bc.speed * 1.3, bc.max_speed)


def maybe_spawn_powerup(position: Vector2, lifecycle_manager) -> None:
    """20% chance to spawn a powerup at the given position."""
    if random.random() > 0.20:
        return

    # Pick type by weight
    roll = random.random()
    cumulative = 0.0
    chosen = PowerupType.WIDE_PADDLE
    for ptype, weight in POWERUP_WEIGHTS:
        cumulative += weight
        if roll <= cumulative:
            chosen = ptype
            break

    name = f"Powerup_{random.randint(1000, 9999)}"
    go = GameObject(name, tag="Powerup")
    go.transform.position = Vector2(position.x, position.y)

    sr = go.add_component(SpriteRenderer)
    sr.color = POWERUP_COLORS[chosen]
    sr.size = Vector2(0.6, 0.3)

    pu = go.add_component(Powerup)
    pu.powerup_type = chosen
    lifecycle_manager.register_component(pu)
