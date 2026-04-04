"""Run Breakout in the Python Unity simulator.

Controls:
  A / D or Left / Right: Move paddle
  Space: Launch ball
  ESC: Quit
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.core import GameObject, MonoBehaviour
from src.engine.rendering.camera import Camera
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D, PhysicsMaterial2D
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.audio import AudioSource
from src.engine.debug import Debug
from src.engine.app import run

from breakout_python.paddle_controller import PaddleController
from breakout_python.ball_controller import BallController
from breakout_python.brick import Brick
from breakout_python.game_manager import GameManager
from src.engine.serialization import serializable
from dataclasses import dataclass


@serializable
@dataclass
class BrickRowConfig:
    """[System.Serializable] — color and points for one row of bricks."""
    color: tuple[int, int, int] = (255, 255, 255)
    points: int = 10


class LevelConfig:
    """Level configuration — brick rows, layout constants."""
    ROWS: list[BrickRowConfig] = [
        BrickRowConfig(color=(220, 50, 50), points=30),    # red
        BrickRowConfig(color=(220, 50, 50), points=30),    # red
        BrickRowConfig(color=(220, 140, 40), points=20),   # orange
        BrickRowConfig(color=(220, 140, 40), points=20),   # orange
        BrickRowConfig(color=(50, 180, 50), points=10),    # green
        BrickRowConfig(color=(50, 180, 50), points=10),    # green
        BrickRowConfig(color=(50, 120, 220), points=10),   # blue
        BrickRowConfig(color=(50, 120, 220), points=10),   # blue
    ]


class QuitHandler(MonoBehaviour):
    def update(self):
        if Input.get_key_down("escape"):
            from src.engine.rendering.display import DisplayManager
            DisplayManager.instance().request_quit()


def setup_scene():
    pm = PhysicsManager.instance()
    pm.gravity = Vector2(0, 0)  # No gravity — ball bounces, doesn't fall

    # Camera
    cam_go = GameObject("MainCamera")
    cam = cam_go.add_component(Camera)
    cam.orthographic_size = 7.0
    cam.background_color = (15, 15, 25)

    # Shared physics material — perfect bounce, no friction
    bounce_mat = PhysicsMaterial2D(bounciness=1.0, friction=0.0)

    # Paddle
    paddle = GameObject("Paddle", tag="Paddle")
    paddle.transform.position = Vector2(0, -5)
    rb_p = paddle.add_component(Rigidbody2D)
    rb_p.body_type = RigidbodyType2D.KINEMATIC
    col_p = paddle.add_component(BoxCollider2D)
    col_p.size = Vector2(2.0, 0.4)
    col_p.material = bounce_mat
    sr_p = paddle.add_component(SpriteRenderer)
    sr_p.color = (200, 200, 220)
    sr_p.size = Vector2(2.0, 0.4)
    sr_p.asset_ref = "paddle"
    pc = paddle.add_component(PaddleController)

    # Ball
    ball = GameObject("Ball", tag="Ball")
    ball.transform.position = Vector2(0, -4.4)
    rb_b = ball.add_component(Rigidbody2D)
    rb_b.mass = 0.1
    col_b = ball.add_component(CircleCollider2D)
    col_b.radius = 0.2
    col_b.material = bounce_mat
    sr_b = ball.add_component(SpriteRenderer)
    sr_b.color = (255, 255, 100)
    sr_b.size = Vector2(0.4, 0.4)
    sr_b.asset_ref = "ball"
    ball_audio = ball.add_component(AudioSource)
    ball_audio.clip_ref = "ball_hit"
    bc = ball.add_component(BallController)

    # Walls (left, right, top) — static colliders for physics bouncing
    for name, pos, size in [
        ("LeftWall", Vector2(-8, 0), Vector2(1, 14)),
        ("RightWall", Vector2(8, 0), Vector2(1, 14)),
        ("TopWall", Vector2(0, 6.5), Vector2(18, 1)),
    ]:
        wall = GameObject(name, tag="Wall")
        wall.transform.position = pos
        rb_w = wall.add_component(Rigidbody2D)
        rb_w.body_type = RigidbodyType2D.STATIC
        rb_w._body.position = (pos.x, pos.y)
        col_w = wall.add_component(BoxCollider2D)
        col_w.size = size
        col_w.material = bounce_mat

    # Brick grid
    cols = 10
    rows = len(LevelConfig.ROWS)
    brick_w = 1.3
    brick_h = 0.5
    gap = 0.1
    grid_width = cols * (brick_w + gap) - gap
    start_x = -grid_width / 2 + brick_w / 2
    start_y = 4.5

    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (brick_w + gap)
            y = start_y - row * (brick_h + gap)
            name = f"Brick_{row}_{col}"
            brick_go = GameObject(name, tag="Brick")
            brick_go.transform.position = Vector2(x, y)

            rb_brick = brick_go.add_component(Rigidbody2D)
            rb_brick.body_type = RigidbodyType2D.STATIC
            rb_brick._body.position = (x, y)

            col_brick = brick_go.add_component(BoxCollider2D)
            col_brick.size = Vector2(brick_w, brick_h)
            col_brick.material = bounce_mat

            sr_brick = brick_go.add_component(SpriteRenderer)
            sr_brick.color = LevelConfig.ROWS[row].color
            sr_brick.size = Vector2(brick_w, brick_h)
            sr_brick.asset_ref = "brick"

            brick_audio = brick_go.add_component(AudioSource)
            brick_audio.clip_ref = "brick_break"

            brick_comp = brick_go.add_component(Brick)
            brick_comp.points = LevelConfig.ROWS[row].points

    # Game manager
    gm_go = GameObject("GameManager")
    gm = gm_go.add_component(GameManager)
    GameManager.reset()

    # Quit handler
    quit_go = GameObject("QuitHandler")
    qh = quit_go.add_component(QuitHandler)


if __name__ == "__main__":
    headless = "--headless" in sys.argv
    max_frames = None
    if "--frames" in sys.argv:
        idx = sys.argv.index("--frames")
        max_frames = int(sys.argv[idx + 1])

    print("Breakout — A/D to move, Space to launch, ESC to quit")
    run(setup_scene, width=800, height=700, headless=headless, max_frames=max_frames,
        title="Breakout — Score: 0  |  Lives: 3  (A/D move, Space launch, ESC quit)")
