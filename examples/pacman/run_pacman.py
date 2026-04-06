"""Run Pacman in the Python Unity simulator.

Controls:
  W/A/S/D or Arrow keys: Move Pacman
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
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.app import run

from pacman_python.movement import Movement, OBSTACLE_LAYER
from pacman_python.node import Node
from pacman_python.passage import Passage
from pacman_python.pacman import Pacman
from pacman_python.animated_sprite import AnimatedSprite
from pacman_python.pellet import Pellet
from pacman_python.power_pellet import PowerPellet
from pacman_python.game_manager import GameManager
from pacman_python.maze_data import (
    MAZE, MAZE_ROWS, MAZE_COLS, cell_to_world, get_cell, is_intersection,
)


class QuitHandler(MonoBehaviour):
    def update(self):
        if Input.get_key_down("escape"):
            from src.engine.rendering.display import DisplayManager
            DisplayManager.instance().request_quit()


def setup_scene():
    pm = PhysicsManager.instance()
    pm.gravity = Vector2(0, 0)

    # Camera
    cam_go = GameObject("MainCamera")
    cam = cam_go.add_component(Camera)
    cam.orthographic_size = 16.0
    cam.background_color = (0, 0, 0)

    # Build maze
    passage_left = None
    passage_right = None

    for row in range(MAZE_ROWS):
        for col in range(MAZE_COLS):
            cell = get_cell(col, row)
            wx, wy = cell_to_world(col, row)

            if cell == "W":
                # Wall
                wall_go = GameObject(f"Wall_{row}_{col}")
                wall_go.layer = OBSTACLE_LAYER
                wall_go.transform.position = Vector2(wx, wy)
                rb = wall_go.add_component(Rigidbody2D)
                rb.body_type = RigidbodyType2D.STATIC
                col_w = wall_go.add_component(BoxCollider2D)
                col_w.size = Vector2(1.0, 1.0)
                sr = wall_go.add_component(SpriteRenderer)
                sr.color = (33, 33, 222)
                sr.size = Vector2(1.0, 1.0)
                sr.sorting_order = 0
                sr.asset_ref = "wall"  # Will map to specific Wall_XX in asset mapping

            elif cell in (".", "o", "N"):
                # Pellet or power pellet
                pellet_go = GameObject(f"Pellet_{row}_{col}", tag="Pellet")
                pellet_go.transform.position = Vector2(wx, wy)
                rb = pellet_go.add_component(Rigidbody2D)
                rb.body_type = RigidbodyType2D.STATIC
                col_p = pellet_go.add_component(BoxCollider2D)
                col_p.is_trigger = True
                sr = pellet_go.add_component(SpriteRenderer)
                sr.sorting_order = 2

                if cell == "o":
                    # Power pellet
                    pellet_go.tag = "PowerPellet"
                    col_p.size = Vector2(0.5, 0.5)
                    sr.color = (255, 255, 200)
                    sr.size = Vector2(0.5, 0.5)
                    sr.asset_ref = "pellet_large"
                    pp = pellet_go.add_component(PowerPellet)
                    pp.points = 50
                else:
                    # Normal pellet
                    col_p.size = Vector2(0.25, 0.25)
                    sr.color = (255, 255, 200)
                    sr.size = Vector2(0.15, 0.15)
                    sr.asset_ref = "pellet_small"
                    pellet_go.add_component(Pellet)

            elif cell == "P":
                # Pacman start — just a marker, Pacman created separately
                pass

            elif cell == "T":
                # Tunnel passage
                passage_go = GameObject(f"Passage_{row}_{col}")
                passage_go.transform.position = Vector2(wx, wy)
                rb = passage_go.add_component(Rigidbody2D)
                rb.body_type = RigidbodyType2D.STATIC
                col_t = passage_go.add_component(BoxCollider2D)
                col_t.is_trigger = True
                col_t.size = Vector2(1.0, 1.0)
                passage = passage_go.add_component(Passage)

                if col == 0:
                    passage_left = passage_go
                else:
                    passage_right = passage_go

            # Place node at intersections
            if cell not in ("W", "G") and is_intersection(col, row):
                node_go = GameObject(f"Node_{row}_{col}")
                node_go.transform.position = Vector2(wx, wy)
                rb_n = node_go.add_component(Rigidbody2D)
                rb_n.body_type = RigidbodyType2D.STATIC
                col_n = node_go.add_component(BoxCollider2D)
                col_n.is_trigger = True
                col_n.size = Vector2(0.5, 0.5)
                node_go.add_component(Node)

    # Wire passage connections
    if passage_left and passage_right:
        pl = passage_left.get_component(Passage)
        pr = passage_right.get_component(Passage)
        pl.connection = passage_right.transform
        pr.connection = passage_left.transform

    # Pacman — find start position from maze
    pacman_col, pacman_row = 14, 23  # 'P' position in maze
    px, py = cell_to_world(pacman_col, pacman_row)
    pacman_go = GameObject("Pacman", tag="Pacman")
    pacman_go.layer = 7  # Pacman layer
    pacman_go.transform.position = Vector2(px, py)
    rb_pac = pacman_go.add_component(Rigidbody2D)
    rb_pac.body_type = RigidbodyType2D.KINEMATIC
    col_pac = pacman_go.add_component(CircleCollider2D)
    col_pac.radius = 0.5
    sr_pac = pacman_go.add_component(SpriteRenderer)
    sr_pac.color = (255, 255, 0)
    sr_pac.size = Vector2(1.0, 1.0)
    sr_pac.sorting_order = 5
    sr_pac.asset_ref = "pacman_01"

    # Walking animation
    walk_anim = pacman_go.add_component(AnimatedSprite)
    walk_anim.sprite_refs = ["pacman_01", "pacman_02", "pacman_03"]
    walk_anim.animation_time = 0.15
    walk_anim.loop = True

    # Death sequence (separate GO, disabled by default)
    death_go = GameObject("PacmanDeath")
    death_go.transform.position = Vector2(px, py)
    sr_death = death_go.add_component(SpriteRenderer)
    sr_death.color = (255, 255, 0)
    sr_death.size = Vector2(1.0, 1.0)
    sr_death.sorting_order = 5
    sr_death.asset_ref = "pacman_death_01"
    death_anim = death_go.add_component(AnimatedSprite)
    death_anim.sprite_refs = [
        f"pacman_death_{i:02d}" for i in range(1, 12)
    ]
    death_anim.animation_time = 0.1
    death_anim.loop = False
    death_anim.enabled = False

    # Movement + Pacman controller
    movement = pacman_go.add_component(Movement)
    movement.initial_direction = Vector2(-1, 0)  # Start moving left
    pac = pacman_go.add_component(Pacman)
    pac.death_sequence = death_anim

    # GameManager singleton
    gm_go = GameObject("GameManager")
    gm = gm_go.add_component(GameManager)
    gm.pacman = pac

    # Quit handler
    quit_go = GameObject("QuitHandler")
    quit_go.add_component(QuitHandler)


if __name__ == "__main__":
    headless = "--headless" in sys.argv
    max_frames = None
    if "--frames" in sys.argv:
        idx = sys.argv.index("--frames")
        max_frames = int(sys.argv[idx + 1])

    print("Pacman — WASD/Arrows to move, ESC to quit")
    run(setup_scene, width=600, height=700, headless=headless, max_frames=max_frames,
        title="Pacman")
