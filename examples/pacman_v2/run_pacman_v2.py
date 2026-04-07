"""Run Pacman V2 in the Python Unity simulator.

Port of the zigurous/unity-pacman-tutorial using real sprites.

Controls:
  W/A/S/D or Arrow keys: Move Pacman
  ESC: Quit
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pygame

from src.engine.core import GameObject, MonoBehaviour
from src.engine.rendering.camera import Camera
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D
from src.engine.math.vector import Vector2
from src.engine.input_manager import Input
from src.engine.app import run

from pacman_v2_python.maze_data import (
    MAZE, MAZE_ROWS, MAZE_COLS, cell_to_world, get_cell, select_wall_tile,
)
from pacman_v2_python.movement import Movement, OBSTACLE_LAYER as MOVEMENT_OBSTACLE_LAYER
from pacman_v2_python.pacman import Pacman
from pacman_v2_python.animated_sprite import AnimatedSprite, load_sprite_file
from pacman_v2_python.node import Node
from pacman_v2_python.pellet import Pellet
from pacman_v2_python.power_pellet import PowerPellet
from pacman_v2_python.passage import Passage
from pacman_v2_python.game_manager import GameManager
from pacman_v2_python.ghost import Ghost
from pacman_v2_python.ghost_home import GhostHome
from pacman_v2_python.ghost_scatter import GhostScatter
from pacman_v2_python.ghost_chase import GhostChase
from pacman_v2_python.ghost_frightened import GhostFrightened
from pacman_v2_python.ghost_eyes import GhostEyes
from pacman_v2_python.maze_data import is_wall

# ── Sprite Loading ───────────────────────────────────────────

SPRITES_DIR = os.path.join(os.path.dirname(__file__), "sprites")


def _ensure_display():
    """Ensure pygame has a display surface (needed for convert_alpha in headless)."""
    if not pygame.get_init():
        pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1), pygame.NOFRAME)


def load_sprite(name: str, size_px: int | None = None) -> pygame.Surface:
    """Load a PNG sprite from the sprites directory, optionally scaling."""
    _ensure_display()
    path = os.path.join(SPRITES_DIR, name)
    surf = pygame.image.load(path).convert_alpha()
    if size_px:
        surf = pygame.transform.scale(surf, (size_px, size_px))
    return surf


# Pre-load wall sprites (lazy, on first call)
_wall_sprites: dict[int, pygame.Surface] = {}


def get_wall_sprite(tile_index: int, ppu: int = 16) -> pygame.Surface:
    """Get a cached wall sprite by tile index."""
    if tile_index not in _wall_sprites:
        filename = f"Wall_{tile_index:02d}.png"
        path = os.path.join(SPRITES_DIR, filename)
        if os.path.exists(path):
            _wall_sprites[tile_index] = load_sprite(filename, ppu)
        else:
            # Fallback to Wall_00 if specific tile doesn't exist
            _wall_sprites[tile_index] = load_sprite("Wall_00.png", ppu)
    return _wall_sprites[tile_index]


# ── Scene Setup ──────────────────────────────────────────────

OBSTACLE_LAYER: int = 6


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

    # Quit handler
    quit_go = GameObject("QuitHandler")
    quit_go.add_component(QuitHandler)

    # Initialize pygame for sprite loading
    if not pygame.get_init():
        pygame.init()

    # Pixels per unit (for sprite scaling)
    screen_h = 700
    ppu = int(screen_h / (2.0 * cam.orthographic_size))

    # ── Build Maze Walls ─────────────────────────────────────
    for row in range(MAZE_ROWS):
        for col in range(MAZE_COLS):
            cell = get_cell(col, row)

            if cell == "W":
                wx, wy = cell_to_world(col, row)
                tile_idx = select_wall_tile(col, row)

                wall_go = GameObject(f"Wall_{col}_{row}")
                wall_go.transform.position.x = wx
                wall_go.transform.position.y = wy
                wall_go.layer = OBSTACLE_LAYER

                sr = wall_go.add_component(SpriteRenderer)
                sr.sprite = get_wall_sprite(tile_idx, ppu)
                sr.sorting_order = 0

                rb = wall_go.add_component(Rigidbody2D)
                rb.body_type = RigidbodyType2D.STATIC

                col_comp = wall_go.add_component(BoxCollider2D)
                col_comp.size = Vector2(1.0, 1.0)

    # ── Pacman ───────────────────────────────────────────────
    pacman_start_col, pacman_start_row = None, None
    for row in range(MAZE_ROWS):
        for col in range(MAZE_COLS):
            if get_cell(col, row) == "P":
                pacman_start_col, pacman_start_row = col, row
                break

    if pacman_start_col is not None:
        px, py = cell_to_world(pacman_start_col, pacman_start_row)
        pacman_go = GameObject("Pacman")
        pacman_go.transform.position.x = px
        pacman_go.transform.position.y = py
        pacman_go.layer = 3  # Pacman layer

        sr = pacman_go.add_component(SpriteRenderer)
        sr.color = (255, 255, 0)
        sr.size = Vector2(1.0, 1.0)
        sr.sorting_order = 5

        # Load Pacman animation sprites
        pacman_sprites = [
            load_sprite_file(f"Pacman_{i:02d}.png", ppu)
            for i in range(1, 4)
        ]
        if pacman_sprites:
            sr.sprite = pacman_sprites[0]

        rb = pacman_go.add_component(Rigidbody2D)
        from src.engine.physics.collider import CircleCollider2D
        col_comp = pacman_go.add_component(CircleCollider2D)
        col_comp.radius = 0.5

        movement = pacman_go.add_component(Movement)
        movement.speed = 8.0
        movement.initial_direction = Vector2(-1, 0)

        anim = pacman_go.add_component(AnimatedSprite)
        anim.sprites = pacman_sprites
        anim.animation_time = 0.15
        anim.loop = True

        pacman_comp = pacman_go.add_component(Pacman)

    # ── GameManager ──────────────────────────────────────────
    gm_go = GameObject("GameManager")
    gm = gm_go.add_component(GameManager)
    gm.pacman = pacman_comp

    # ── Nodes (intersections) ────────────────────────────────
    def _is_intersection(col: int, row: int) -> bool:
        if is_wall(col, row):
            return False
        open_dirs = []
        for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            if not is_wall(col + dc, row + dr):
                open_dirs.append((dc, dr))
        if len(open_dirs) >= 3:
            return True
        if len(open_dirs) == 2:
            (dc1, dr1), (dc2, dr2) = open_dirs
            if dc1 != -dc2 or dr1 != -dr2:
                return True
        return False

    for row in range(MAZE_ROWS):
        for col in range(MAZE_COLS):
            if _is_intersection(col, row):
                nx, ny = cell_to_world(col, row)
                node_go = GameObject(f"Node_{col}_{row}")
                node_go.transform.position.x = nx
                node_go.transform.position.y = ny

                node = node_go.add_component(Node)

                from src.engine.physics.collider import CircleCollider2D
                trigger = node_go.add_component(CircleCollider2D)
                trigger.radius = 0.25
                trigger.is_trigger = True

                rb = node_go.add_component(Rigidbody2D)
                rb.body_type = RigidbodyType2D.STATIC

    # ── Pellets ──────────────────────────────────────────────
    pellet_sprite = load_sprite("Pellet_Small.png", max(4, ppu // 4))
    power_pellet_sprite = load_sprite("Pellet_Large.png", max(8, ppu // 2))

    for row in range(MAZE_ROWS):
        for col in range(MAZE_COLS):
            cell = get_cell(col, row)
            if cell in (".", "N", "P"):
                px, py = cell_to_world(col, row)
                p_go = GameObject(f"Pellet_{col}_{row}")
                p_go.transform.position.x = px
                p_go.transform.position.y = py

                sr = p_go.add_component(SpriteRenderer)
                sr.sprite = pellet_sprite
                sr.sorting_order = 1

                pellet = p_go.add_component(Pellet)
                gm.register_pellet(pellet)

                trigger = p_go.add_component(CircleCollider2D)
                trigger.radius = 0.15
                trigger.is_trigger = True

                rb = p_go.add_component(Rigidbody2D)
                rb.body_type = RigidbodyType2D.STATIC

            elif cell == "o":
                px, py = cell_to_world(col, row)
                p_go = GameObject(f"PowerPellet_{col}_{row}")
                p_go.transform.position.x = px
                p_go.transform.position.y = py

                sr = p_go.add_component(SpriteRenderer)
                sr.sprite = power_pellet_sprite
                sr.sorting_order = 1

                pp = p_go.add_component(PowerPellet)
                gm.register_pellet(pp)

                trigger = p_go.add_component(CircleCollider2D)
                trigger.radius = 0.5
                trigger.is_trigger = True

                rb = p_go.add_component(Rigidbody2D)
                rb.body_type = RigidbodyType2D.STATIC

    # ── Passages (tunnels) ───────────────────────────────────
    passage_positions = []
    for row in range(MAZE_ROWS):
        for col in range(MAZE_COLS):
            if get_cell(col, row) == "T":
                passage_positions.append((col, row))

    passage_gos = []
    for col, row in passage_positions:
        tx, ty = cell_to_world(col, row)
        t_go = GameObject(f"Passage_{col}_{row}")
        t_go.transform.position.x = tx
        t_go.transform.position.y = ty

        passage = t_go.add_component(Passage)

        trigger = t_go.add_component(CircleCollider2D)
        trigger.radius = 0.5
        trigger.is_trigger = True

        rb = t_go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.STATIC

        passage_gos.append(t_go)

    # Connect passages to each other
    if len(passage_gos) >= 2:
        passage_gos[0].get_component(Passage).connection = passage_gos[1]
        passage_gos[1].get_component(Passage).connection = passage_gos[0]

    # ── Ghost Home Points ────────────────────────────────────
    # Inside point: center of ghost house
    inside_go = GameObject("GhostHome_Inside")
    inside_go.transform.position.x, inside_go.transform.position.y = cell_to_world(13, 14)

    # Outside point: above ghost house gate
    outside_go = GameObject("GhostHome_Outside")
    outside_go.transform.position.x, outside_go.transform.position.y = cell_to_world(13, 11)

    # ── Ghosts ───────────────────────────────────────────────
    ghost_body_sprites = [
        load_sprite("Ghost_Body_01.png", ppu),
        load_sprite("Ghost_Body_02.png", ppu),
    ]
    eye_sprites = {
        "up": load_sprite("Ghost_Eyes_Up.png", ppu),
        "down": load_sprite("Ghost_Eyes_Down.png", ppu),
        "left": load_sprite("Ghost_Eyes_Left.png", ppu),
        "right": load_sprite("Ghost_Eyes_Right.png", ppu),
    }

    ghost_configs = [
        {"name": "Blinky", "color": (255, 0, 0),     "col": 13, "row": 11, "initial": "scatter", "scatter_dur": 7.0, "chase_dur": 20.0},
        {"name": "Pinky",  "color": (255, 184, 255),  "col": 13, "row": 14, "initial": "home",    "scatter_dur": 7.0, "chase_dur": 20.0},
        {"name": "Inky",   "color": (0, 255, 255),    "col": 12, "row": 14, "initial": "home",    "scatter_dur": 5.0, "chase_dur": 20.0},
        {"name": "Clyde",  "color": (255, 184, 82),   "col": 14, "row": 14, "initial": "home",    "scatter_dur": 5.0, "chase_dur": 20.0},
    ]

    for cfg in ghost_configs:
        gx, gy = cell_to_world(cfg["col"], cfg["row"])
        ghost_go = GameObject(f"Ghost_{cfg['name']}")
        ghost_go.transform.position.x = gx
        ghost_go.transform.position.y = gy
        ghost_go.layer = 7  # Ghost layer

        # Body sprite with color tint
        sr = ghost_go.add_component(SpriteRenderer)
        sr.sprite = ghost_body_sprites[0]
        sr.color = cfg["color"]
        sr.sorting_order = 4

        rb = ghost_go.add_component(Rigidbody2D)
        col_comp = ghost_go.add_component(BoxCollider2D)
        col_comp.size = Vector2(1.0, 1.0)

        movement = ghost_go.add_component(Movement)
        movement.speed = 7.0
        movement.initial_direction = Vector2(0, -1) if cfg["initial"] == "home" else Vector2(-1, 0)

        # Body animation
        anim = ghost_go.add_component(AnimatedSprite)
        anim.sprites = ghost_body_sprites
        anim.animation_time = 0.2

        # Behaviors
        home = ghost_go.add_component(GhostHome)
        home.inside = inside_go
        home.outside = outside_go

        scatter = ghost_go.add_component(GhostScatter)
        scatter.duration = cfg["scatter_dur"]

        chase = ghost_go.add_component(GhostChase)
        chase.duration = cfg["chase_dur"]

        frightened = ghost_go.add_component(GhostFrightened)

        ghost = ghost_go.add_component(Ghost)
        ghost.initial_behavior = cfg["initial"]
        ghost.target = pacman_go  # All ghosts chase Pacman (simplified)

        # Eyes child object
        eyes_go = GameObject(f"Ghost_{cfg['name']}_Eyes")
        eyes_go.transform.set_parent(ghost_go.transform)

        eyes_sr = eyes_go.add_component(SpriteRenderer)
        eyes_sr.sprite = eye_sprites["left"]
        eyes_sr.sorting_order = 5

        eyes = eyes_go.add_component(GhostEyes)
        eyes.sprite_up = eye_sprites["up"]
        eyes.sprite_down = eye_sprites["down"]
        eyes.sprite_left = eye_sprites["left"]
        eyes.sprite_right = eye_sprites["right"]

        gm.register_ghost(ghost)

    # ── Ghost House Gate (obstacle walls at rows 11-12) ──────
    for col in [11, 16]:
        for row in [11, 12]:
            gx, gy = cell_to_world(col, row)
            gate_go = GameObject(f"Gate_{col}_{row}")
            gate_go.transform.position.x = gx
            gate_go.transform.position.y = gy
            gate_go.layer = OBSTACLE_LAYER

            rb = gate_go.add_component(Rigidbody2D)
            rb.body_type = RigidbodyType2D.STATIC

            col_comp = gate_go.add_component(BoxCollider2D)
            col_comp.size = Vector2(1.0, 1.0)


def main():
    headless = "--headless" in sys.argv
    max_frames = 0
    if "--frames" in sys.argv:
        idx = sys.argv.index("--frames")
        if idx + 1 < len(sys.argv):
            max_frames = int(sys.argv[idx + 1])

    run(
        scene_setup=setup_scene,
        width=600,
        height=700,
        title="Pacman V2",
        headless=headless,
        max_frames=max_frames,
    )


if __name__ == "__main__":
    main()
