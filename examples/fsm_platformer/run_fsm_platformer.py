"""Run FSM Platformer in the Python Unity simulator.

Controls:
  Move:  A / D  or  Left / Right arrows
  Jump:  Space
  Quit:  ESC or close window

Demonstrates FSM + Command Pattern:
  Player: 5-state FSM (IDLE, RUNNING, JUMPING, FALLING, LANDING) + Commands
  Enemy:  2-state FSM (IDLE <-> WALK via TimeTransition)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.core import GameObject, MonoBehaviour
from src.engine.rendering.camera import Camera
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.app import run

from fsm_platformer_python.player_input_handler import PlayerInputHandler
from fsm_platformer_python.enemy_behaviour import EnemyBehaviour


class StateDisplay(MonoBehaviour):
    """Renders player/enemy FSM state names in the window title."""

    def __init__(self):
        super().__init__()
        self._last_player_state = ""
        self._last_enemy_state = ""

    def update(self):
        player_go = GameObject.find("Player")
        enemy_go = GameObject.find("Enemy")

        p_state = ""
        e_state = ""
        if player_go:
            pih = player_go.get_component(PlayerInputHandler)
            if pih:
                p_state = pih.state_name
        if enemy_go:
            eb = enemy_go.get_component(EnemyBehaviour)
            if eb:
                e_state = eb.state_name

        if p_state != self._last_player_state or e_state != self._last_enemy_state:
            self._last_player_state = p_state
            self._last_enemy_state = e_state
            try:
                import pygame
                pygame.display.set_caption(
                    f"FSM Platformer -- Player: {p_state}  |  Enemy: {e_state}  "
                    f"(A/D move, Space jump, ESC quit)"
                )
            except Exception:
                pass


class QuitHandler(MonoBehaviour):
    """Quit on ESC key."""

    def update(self):
        if Input.get_key_down("escape"):
            from src.engine.rendering.display import DisplayManager
            DisplayManager.instance().request_quit()


# Ground surface Y coordinate.  The ground collider top edge sits here.
GROUND_SURFACE_Y = -3.0
GROUND_THICKNESS = 1.0


def setup_scene():
    pm = PhysicsManager.instance()
    pm.gravity = Vector2(0, -9.81)

    # ---- Camera ----
    cam_go = GameObject("MainCamera")
    cam = cam_go.add_component(Camera)
    cam.orthographic_size = 6.0
    cam.background_color = (40, 40, 60)

    # ---- Ground platform (static) ----
    ground = GameObject("Ground", tag="Ground")
    ground_y = GROUND_SURFACE_Y - GROUND_THICKNESS / 2.0
    ground.transform.position = Vector2(0, ground_y)
    rb_g = ground.add_component(Rigidbody2D)
    rb_g.body_type = RigidbodyType2D.STATIC
    rb_g._body.position = (0, ground_y)
    col_g = ground.add_component(BoxCollider2D)
    col_g.size = Vector2(20, GROUND_THICKNESS)
    col_g.build()
    sr_g = ground.add_component(SpriteRenderer)
    sr_g.color = (80, 160, 80)
    sr_g.size = Vector2(20, GROUND_THICKNESS)
    sr_g.sorting_order = -1

    # ---- Player ----
    player = GameObject("Player", tag="Player")
    player.transform.position = Vector2(-2, GROUND_SURFACE_Y + 0.5)
    rb_p = player.add_component(Rigidbody2D)
    rb_p.gravity_scale = 1.0
    col_p = player.add_component(BoxCollider2D)
    col_p.size = Vector2(0.8, 1.0)
    col_p.build()
    sr_p = player.add_component(SpriteRenderer)
    sr_p.color = (100, 180, 255)
    sr_p.size = Vector2(0.8, 1.0)
    pih = player.add_component(PlayerInputHandler)
    pih.move_speed = 3.0
    pih.jump_force = 5.0
    pih.ground_y = GROUND_SURFACE_Y

    # ---- Enemy ----
    enemy = GameObject("Enemy", tag="Enemy")
    enemy.transform.position = Vector2(3, GROUND_SURFACE_Y + 0.5)
    rb_e = enemy.add_component(Rigidbody2D)
    rb_e.gravity_scale = 1.0
    col_e = enemy.add_component(BoxCollider2D)
    col_e.size = Vector2(0.8, 1.0)
    col_e.build()
    sr_e = enemy.add_component(SpriteRenderer)
    sr_e.color = (255, 100, 100)
    sr_e.size = Vector2(0.8, 1.0)
    eb = enemy.add_component(EnemyBehaviour)
    eb.idle_time = 2.0
    eb.walk_time = 3.0
    eb.walk_speed = 1.5
    eb.patrol_min_x = 1.0
    eb.patrol_max_x = 6.0

    # ---- Left wall (static) ----
    left_wall = GameObject("LeftWall")
    left_wall.transform.position = Vector2(-9.5, 0)
    rb_lw = left_wall.add_component(Rigidbody2D)
    rb_lw.body_type = RigidbodyType2D.STATIC
    rb_lw._body.position = (-9.5, 0)
    col_lw = left_wall.add_component(BoxCollider2D)
    col_lw.size = Vector2(1, 14)
    col_lw.build()

    # ---- Right wall (static) ----
    right_wall = GameObject("RightWall")
    right_wall.transform.position = Vector2(9.5, 0)
    rb_rw = right_wall.add_component(Rigidbody2D)
    rb_rw.body_type = RigidbodyType2D.STATIC
    rb_rw._body.position = (9.5, 0)
    col_rw = right_wall.add_component(BoxCollider2D)
    col_rw.size = Vector2(1, 14)
    col_rw.build()

    # ---- State display ----
    disp_go = GameObject("StateDisplay")
    sd = disp_go.add_component(StateDisplay)

    # ---- Quit handler ----
    quit_go = GameObject("QuitHandler")
    qh = quit_go.add_component(QuitHandler)


if __name__ == "__main__":
    headless = "--headless" in sys.argv
    max_frames = None
    if "--frames" in sys.argv:
        idx = sys.argv.index("--frames")
        max_frames = int(sys.argv[idx + 1])

    print("FSM Platformer -- A/D to move, Space to jump, ESC to quit")
    run(setup_scene, width=800, height=600, headless=headless, max_frames=max_frames,
        title="FSM Platformer -- Player: IDLE  |  Enemy: IDLE  (A/D move, Space jump, ESC quit)")
