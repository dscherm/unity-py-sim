"""Run Pong in the Python Unity simulator.

Controls:
  Left paddle:  W / S
  Right paddle:  Up / Down arrows
  Quit: ESC or close window
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.core import GameObject, MonoBehaviour
from src.engine.lifecycle import LifecycleManager
from src.engine.rendering.camera import Camera
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.time_manager import Time
from src.engine.app import run

from pong_python.paddle_controller import PaddleController
from pong_python.ball_controller import BallController
from pong_python.score_manager import ScoreManager


class GoalZone(MonoBehaviour):
    """Trigger zone at left/right edge — detects when ball passes."""

    def __init__(self):
        super().__init__()
        self.side: str = "left"
        self.game_mgr = None

    def start(self):
        pass

    def update(self):
        # Check if ball has passed this goal zone
        ball_obj = GameObject.find("Ball")
        if ball_obj is None:
            return
        ball_x = ball_obj.transform.position.x
        if self.side == "left" and ball_x < -8.5:
            self._on_goal(ball_obj)
        elif self.side == "right" and ball_x > 8.5:
            self._on_goal(ball_obj)

    def _on_goal(self, ball_obj):
        bc = ball_obj.get_component(BallController)
        if bc is None:
            return
        if self.side == "left":
            ScoreManager.add_score_right()
        else:
            ScoreManager.add_score_left()
        bc.reset()
        bc.launch()


class ScoreDisplay(MonoBehaviour):
    """Renders scores as text in the pygame window title."""

    def __init__(self):
        super().__init__()
        self._last_left = -1
        self._last_right = -1

    def update(self):
        if (ScoreManager.score_left != self._last_left or
                ScoreManager.score_right != self._last_right):
            self._last_left = ScoreManager.score_left
            self._last_right = ScoreManager.score_right
            try:
                import pygame
                pygame.display.set_caption(
                    f"Pong — Left: {self._last_left}  |  Right: {self._last_right}  "
                    f"(W/S vs Up/Down, ESC to quit)"
                )
            except Exception:
                pass


class QuitHandler(MonoBehaviour):
    """Quit on ESC key."""

    def update(self):
        if Input.get_key_down("escape"):
            from src.engine.rendering.display import DisplayManager
            DisplayManager.instance().request_quit()


def setup_scene():
    lm = LifecycleManager.instance()
    pm = PhysicsManager.instance()
    pm.gravity = Vector2(0, 0)

    # Camera
    cam_go = GameObject("MainCamera")
    cam = cam_go.add_component(Camera)
    cam.orthographic_size = 6.0
    cam.background_color = (20, 20, 30)
    lm.register_component(cam)

    # Left Paddle (W/S)
    left_paddle = GameObject("LeftPaddle", tag="Paddle")
    left_paddle.transform.position = Vector2(-7, 0)
    rb_lp = left_paddle.add_component(Rigidbody2D)
    rb_lp.body_type = RigidbodyType2D.KINEMATIC
    col_lp = left_paddle.add_component(BoxCollider2D)
    col_lp.size = Vector2(0.5, 2)
    col_lp.build()
    sr_lp = left_paddle.add_component(SpriteRenderer)
    sr_lp.color = (100, 180, 255)
    sr_lp.size = Vector2(0.5, 2)
    pc_l = left_paddle.add_component(PaddleController)
    pc_l.input_axis = "Vertical1"
    lm.register_component(pc_l)

    # Right Paddle (Up/Down)
    right_paddle = GameObject("RightPaddle", tag="Paddle")
    right_paddle.transform.position = Vector2(7, 0)
    rb_rp = right_paddle.add_component(Rigidbody2D)
    rb_rp.body_type = RigidbodyType2D.KINEMATIC
    col_rp = right_paddle.add_component(BoxCollider2D)
    col_rp.size = Vector2(0.5, 2)
    col_rp.build()
    sr_rp = right_paddle.add_component(SpriteRenderer)
    sr_rp.color = (255, 130, 100)
    sr_rp.size = Vector2(0.5, 2)
    pc_r = right_paddle.add_component(PaddleController)
    pc_r.input_axis = "Vertical2"
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

    # Top/Bottom walls
    for y_pos, name in [(5.5, "TopWall"), (-5.5, "BottomWall")]:
        wall = GameObject(name, tag="Wall")
        wall.transform.position = Vector2(0, y_pos)
        rb_w = wall.add_component(Rigidbody2D)
        rb_w.body_type = RigidbodyType2D.STATIC
        rb_w._body.position = (0, y_pos)
        col_w = wall.add_component(BoxCollider2D)
        col_w.size = Vector2(20, 1)
        col_w.build()

    # Center line (visual only)
    center_line = GameObject("CenterLine")
    sr_cl = center_line.add_component(SpriteRenderer)
    sr_cl.color = (60, 60, 80)
    sr_cl.size = Vector2(0.05, 12)
    sr_cl.sorting_order = -1

    # Goal zones (detect scoring)
    for side, x_pos in [("left", -9), ("right", 9)]:
        gz_go = GameObject(f"Goal_{side}")
        gz = gz_go.add_component(GoalZone)
        gz.side = side
        lm.register_component(gz)

    # Score manager
    score_go = GameObject("ScoreManager")
    sm = score_go.add_component(ScoreManager)
    ScoreManager.reset_scores()
    lm.register_component(sm)

    # Score display
    disp_go = GameObject("ScoreDisplay")
    sd = disp_go.add_component(ScoreDisplay)
    lm.register_component(sd)

    # Quit handler
    quit_go = GameObject("QuitHandler")
    qh = quit_go.add_component(QuitHandler)
    lm.register_component(qh)


if __name__ == "__main__":
    headless = "--headless" in sys.argv
    max_frames = None
    if "--frames" in sys.argv:
        idx = sys.argv.index("--frames")
        max_frames = int(sys.argv[idx + 1])

    print("Pong — Left: W/S  |  Right: Up/Down  |  ESC to quit")
    run(setup_scene, width=800, height=600, headless=headless, max_frames=max_frames,
        title="Pong — Left: 0  |  Right: 0  (W/S vs Up/Down, ESC to quit)")
