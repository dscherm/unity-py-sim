"""Run Space Invaders in the Python Unity simulator.

Controls:
  A / D or Left / Right: Move ship
  Space or Mouse Click: Fire laser
  ESC: Quit
  Enter: Restart (after game over)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.core import GameObject, MonoBehaviour
from src.engine.rendering.camera import Camera
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.app import run

from space_invaders_python.player import Player, Layers
from space_invaders_python.invaders import Invaders
from space_invaders_python.bunker import Bunker
from space_invaders_python.mystery_ship import MysteryShip
from space_invaders_python.game_manager import GameManager
from space_invaders_python.prefabs import register_prefabs


class QuitHandler(MonoBehaviour):
    def update(self):
        if Input.get_key_down("escape"):
            from src.engine.rendering.display import DisplayManager
            DisplayManager.instance().request_quit()


def setup_scene():
    register_prefabs()
    pm = PhysicsManager.instance()
    pm.gravity = Vector2(0, 0)  # No gravity — projectiles move via transform

    # Camera
    cam_go = GameObject("MainCamera")
    cam = cam_go.add_component(Camera)
    cam.orthographic_size = 7.0
    cam.background_color = (5, 5, 15)


    # Player
    player_go = GameObject("Player", tag="Player")
    player_go.transform.position = Vector2(0, -5)
    rb_p = player_go.add_component(Rigidbody2D)
    rb_p.body_type = RigidbodyType2D.KINEMATIC
    col_p = player_go.add_component(BoxCollider2D)
    col_p.size = Vector2(1.5, 0.8)
    col_p.is_trigger = True
    sr_p = player_go.add_component(SpriteRenderer)
    sr_p.color = (50, 255, 50)
    sr_p.size = Vector2(1.5, 0.8)
    sr_p.sorting_order = 3
    sr_p.asset_ref = "player_ship"
    player = player_go.add_component(Player)


    # Invaders grid
    grid_go = GameObject("InvadersGrid")
    grid_go.transform.position = Vector2(0, 3)
    invaders = grid_go.add_component(Invaders)
    invaders.base_speed = 1.0
    invaders.missile_spawn_rate = 1.5


    # Bunkers (4 shields)
    bunker_positions = [-4.5, -1.5, 1.5, 4.5]
    for i, bx in enumerate(bunker_positions):
        bunker_go = GameObject(f"Bunker_{i}", tag="Bunker")
        bunker_go.transform.position = Vector2(bx, -3.0)

        rb_b = bunker_go.add_component(Rigidbody2D)
        rb_b.body_type = RigidbodyType2D.STATIC

        col_b = bunker_go.add_component(BoxCollider2D)
        col_b.size = Vector2(Bunker.GRID_COLS * Bunker.CELL_SIZE, Bunker.GRID_ROWS * Bunker.CELL_SIZE)
        col_b.is_trigger = True

        sr_b = bunker_go.add_component(SpriteRenderer)
        sr_b.color = (50, 200, 50)
        sr_b.size = Vector2(Bunker.GRID_COLS * Bunker.CELL_SIZE, Bunker.GRID_ROWS * Bunker.CELL_SIZE)
        sr_b.sorting_order = 1
        sr_b.asset_ref = "bunker"

        bunker = bunker_go.add_component(Bunker)


    # Mystery ship
    ship_go = GameObject("MysteryShip", tag="MysteryShip")
    ship_go.transform.position = Vector2(-8, 5.5)
    rb_s = ship_go.add_component(Rigidbody2D)
    rb_s.body_type = RigidbodyType2D.KINEMATIC
    col_s = ship_go.add_component(BoxCollider2D)
    col_s.size = Vector2(2.0, 0.8)
    col_s.is_trigger = True
    sr_s = ship_go.add_component(SpriteRenderer)
    sr_s.color = (255, 50, 50)
    sr_s.size = Vector2(2.0, 0.8)
    sr_s.sorting_order = 4
    sr_s.asset_ref = "mystery_ship"
    mystery = ship_go.add_component(MysteryShip)


    # Boundary zones (top/bottom) — destroy projectiles that leave screen
    for name, pos, size in [
        ("BoundaryTop", Vector2(0, 7.5), Vector2(20, 1)),
        ("BoundaryBottom", Vector2(0, -7.5), Vector2(20, 1)),
    ]:
        boundary = GameObject(name, tag="Boundary")
        boundary.layer = Layers.BOUNDARY
        boundary.transform.position = pos
        rb_bnd = boundary.add_component(Rigidbody2D)
        rb_bnd.body_type = RigidbodyType2D.STATIC
        col_bnd = boundary.add_component(BoxCollider2D)
        col_bnd.size = size
        col_bnd.is_trigger = True

    # GameManager
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

    print("Space Invaders — A/D to move, Space to fire, ESC to quit")
    run(setup_scene, width=800, height=700, headless=headless, max_frames=max_frames,
        title="Space Invaders — Score: 0 | Lives: 3")
