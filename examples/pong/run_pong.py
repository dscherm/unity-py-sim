"""Run Pong in the Python Unity simulator."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.core import GameObject
from src.engine.lifecycle import LifecycleManager
from src.engine.rendering.camera import Camera
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D
from src.engine.math.vector import Vector2
from src.engine.app import run

from pong_python.paddle_controller import PaddleController
from pong_python.ball_controller import BallController
from pong_python.score_manager import ScoreManager
from pong_python.game_manager import GameManager


def setup_scene():
    lm = LifecycleManager.instance()
    pm = PhysicsManager.instance()
    pm.gravity = Vector2(0, 0)  # No gravity in Pong

    # Camera
    cam_go = GameObject("MainCamera")
    cam = cam_go.add_component(Camera)
    cam.orthographic_size = 5.0
    cam.background_color = (20, 20, 30)
    lm.register_component(cam)

    # Left Paddle
    left_paddle = GameObject("LeftPaddle", tag="Paddle")
    left_paddle.transform.position = Vector2(-7, 0)
    rb_lp = left_paddle.add_component(Rigidbody2D)
    rb_lp.body_type = RigidbodyType2D.KINEMATIC
    col_lp = left_paddle.add_component(BoxCollider2D)
    col_lp.size = Vector2(0.5, 2)
    col_lp.build()
    sr_lp = left_paddle.add_component(SpriteRenderer)
    sr_lp.color = (200, 200, 200)
    sr_lp.size = Vector2(0.5, 2)
    pc_l = left_paddle.add_component(PaddleController)
    pc_l.input_axis = "Vertical"
    lm.register_component(pc_l)

    # Right Paddle
    right_paddle = GameObject("RightPaddle", tag="Paddle")
    right_paddle.transform.position = Vector2(7, 0)
    rb_rp = right_paddle.add_component(Rigidbody2D)
    rb_rp.body_type = RigidbodyType2D.KINEMATIC
    col_rp = right_paddle.add_component(BoxCollider2D)
    col_rp.size = Vector2(0.5, 2)
    col_rp.build()
    sr_rp = right_paddle.add_component(SpriteRenderer)
    sr_rp.color = (200, 200, 200)
    sr_rp.size = Vector2(0.5, 2)
    pc_r = right_paddle.add_component(PaddleController)
    pc_r.input_axis = "Vertical"  # Both use same axis for now
    lm.register_component(pc_r)

    # Ball
    ball = GameObject("Ball")
    ball.transform.position = Vector2(0, 0)
    rb_ball = ball.add_component(Rigidbody2D)
    rb_ball.mass = 0.1
    col_ball = ball.add_component(CircleCollider2D)
    col_ball.radius = 0.25
    col_ball.build()
    sr_ball = ball.add_component(SpriteRenderer)
    sr_ball.color = (255, 255, 0)
    sr_ball.size = Vector2(0.5, 0.5)
    bc = ball.add_component(BallController)
    lm.register_component(bc)

    # Top/Bottom walls (static colliders)
    for y_pos, name in [(5.5, "TopWall"), (-5.5, "BottomWall")]:
        wall = GameObject(name, tag="Wall")
        wall.transform.position = Vector2(0, y_pos)
        rb_w = wall.add_component(Rigidbody2D)
        rb_w.body_type = RigidbodyType2D.STATIC
        col_w = wall.add_component(BoxCollider2D)
        col_w.size = Vector2(20, 1)
        col_w.build()

    # Score Manager
    score_go = GameObject("ScoreManager")
    sm = score_go.add_component(ScoreManager)
    lm.register_component(sm)

    # Game Manager
    gm_go = GameObject("GameManager")
    gm = gm_go.add_component(GameManager)
    lm.register_component(gm)


if __name__ == "__main__":
    headless = "--headless" in sys.argv
    max_frames = None
    if "--frames" in sys.argv:
        idx = sys.argv.index("--frames")
        max_frames = int(sys.argv[idx + 1])

    run(setup_scene, width=800, height=600, headless=headless, max_frames=max_frames)
