"""Powerup — drops from bricks, collected by paddle."""
from __future__ import annotations

import random
from collections.abc import Generator
from dataclasses import dataclass, field
from enum import Enum

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2
from src.engine.time_manager import Time
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.coroutine import WaitForSeconds
from src.engine.audio import AudioSource
from src.engine.serialization import serializable


class PowerupType(Enum):
    WIDE_PADDLE = "wide_paddle"
    EXTRA_LIFE = "extra_life"
    SPEED_BALL = "speed_ball"


@serializable
@dataclass
class PowerupConfig:
    """[System.Serializable] — configuration for a powerup type."""
    powerup_type: PowerupType = PowerupType.WIDE_PADDLE
    color: tuple[int, int, int] = (255, 255, 255)
    weight: float = 0.0


POWERUP_CONFIGS: list[PowerupConfig] = [
    PowerupConfig(PowerupType.WIDE_PADDLE, color=(100, 200, 255), weight=0.4),
    PowerupConfig(PowerupType.EXTRA_LIFE, color=(255, 100, 200), weight=0.2),
    PowerupConfig(PowerupType.SPEED_BALL, color=(255, 200, 50), weight=0.4),
]


class Powerup(MonoBehaviour):

    def __init__(self) -> None:
        super().__init__()
        self.fall_speed: float = 3.0
        self.powerup_type: PowerupType = PowerupType.WIDE_PADDLE

    def update(self) -> None:
        # Fall downward
        pos: Vector2 = self.transform.position
        new_y: float = pos.y - self.fall_speed * Time.delta_time
        self.transform.position = Vector2(pos.x, new_y)

        # Check paddle collision (simple AABB)
        paddle: GameObject | None = GameObject.find("Paddle")
        if paddle and paddle.active:
            pp: Vector2 = paddle.transform.position
            if (abs(pos.x - pp.x) < 1.2 and abs(new_y - pp.y) < 0.5):
                self._apply(paddle)
                self.game_object.active = False
                return

        # Off screen
        if new_y < -7:
            self.game_object.active = False

    def _apply(self, paddle: GameObject) -> None:
        from breakout_python.game_manager import GameManager

        # Play collect sound
        audio: AudioSource | None = paddle.get_component(AudioSource)
        if audio:
            audio.clip_ref = "powerup_collect"

        if self.powerup_type == PowerupType.EXTRA_LIFE:
            GameManager.lives += 1
            GameManager._update_display()

        elif self.powerup_type == PowerupType.WIDE_PADDLE:
            sr: SpriteRenderer | None = paddle.get_component(SpriteRenderer)
            if sr:
                original_size: Vector2 = Vector2(sr.size.x, sr.size.y)
                original_color: tuple[int, int, int] = sr.color
                sr.size = Vector2(3.0, 0.4)
                sr.color = _get_color(PowerupType.WIDE_PADDLE)
                # Revert after 10 seconds via coroutine
                gm: GameManager | None = GameManager._get_instance()
                if gm:
                    gm.start_coroutine(self._revert_paddle(sr, original_size, original_color))

        elif self.powerup_type == PowerupType.SPEED_BALL:
            ball: GameObject | None = GameObject.find("Ball")
            if ball:
                from breakout_python.ball_controller import BallController
                bc: BallController | None = ball.get_component(BallController)
                if bc:
                    original_speed: float = bc.speed
                    bc.speed = min(bc.speed * 1.3, bc.max_speed)
                    # Revert after 8 seconds via coroutine
                    gm: GameManager | None = GameManager._get_instance()
                    if gm:
                        gm.start_coroutine(self._revert_speed(bc, original_speed))

    def _revert_paddle(self, sr: SpriteRenderer, original_size: Vector2, original_color: tuple[int, int, int]) -> Generator[WaitForSeconds, None, None]:
        yield WaitForSeconds(10.0)
        if sr and sr.game_object and sr.game_object.active:
            sr.size = original_size
            sr.color = original_color

    def _revert_speed(self, bc: BallController, original_speed: float) -> Generator[WaitForSeconds, None, None]:
        yield WaitForSeconds(8.0)
        if bc and bc.game_object and bc.game_object.active:
            bc.speed = original_speed


# Forward reference for type used in _revert_speed
from breakout_python.ball_controller import BallController


def _get_color(ptype: PowerupType) -> tuple[int, int, int]:
    """Get color for a powerup type from config."""
    for cfg in POWERUP_CONFIGS:
        if cfg.powerup_type == ptype:
            return cfg.color
    return (255, 255, 255)


def maybe_spawn_powerup(position: Vector2) -> None:
    """20% chance to spawn a powerup at the given position."""
    if random.random() > 0.20:
        return

    # Pick type by weight
    roll: float = random.random()
    cumulative: float = 0.0
    chosen: PowerupType = PowerupType.WIDE_PADDLE
    for cfg in POWERUP_CONFIGS:
        cumulative += cfg.weight
        if roll <= cumulative:
            chosen = cfg.powerup_type
            break

    name: str = f"Powerup_{random.randint(1000, 9999)}"
    go: GameObject = GameObject(name, tag="Powerup")
    go.transform.position = Vector2(position.x, position.y)

    sr: SpriteRenderer = go.add_component(SpriteRenderer)
    sr.color = _get_color(chosen)
    sr.size = Vector2(0.6, 0.3)

    pu: Powerup = go.add_component(Powerup)
    pu.powerup_type = chosen
