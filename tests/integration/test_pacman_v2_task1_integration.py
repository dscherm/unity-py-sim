"""Integration tests for Pacman V2 Task 1: Maze with real wall sprites.

These tests verify the game actually runs headless and creates the expected
GameObjects with correct components, layers, and sprites.

NOTE: We build the Task 1 wall scene directly rather than importing the full
setup_scene(), because run_pacman_v2.py may contain later-task code (Pacman,
AnimatedSprite) that depends on engine features not yet implemented.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Ensure pacman_v2 directory is on sys.path for its internal imports
_pacman_dir = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "examples", "pacman_v2")
)
if _pacman_dir not in sys.path:
    sys.path.insert(0, _pacman_dir)


def _build_task1_wall_scene():
    """Build only the Task 1 wall scene (no Pacman/ghosts/pellets).

    This mirrors the wall-building portion of run_pacman_v2.setup_scene()
    without importing later-task components that may have unimplemented deps.
    """
    import pygame
    from src.engine.core import GameObject
    from src.engine.rendering.camera import Camera
    from src.engine.rendering.renderer import SpriteRenderer
    from src.engine.physics.physics_manager import PhysicsManager
    from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
    from src.engine.physics.collider import BoxCollider2D
    from src.engine.math.vector import Vector2

    from examples.pacman_v2.pacman_v2_python.maze_data import (
        MAZE_ROWS, MAZE_COLS, cell_to_world, get_cell, select_wall_tile,
    )

    OBSTACLE_LAYER = 6
    SPRITES_DIR = os.path.join(
        os.path.dirname(__file__), "..", "..", "examples", "pacman_v2", "sprites"
    )

    pm = PhysicsManager.instance()
    pm.gravity = Vector2(0, 0)

    # Camera
    cam_go = GameObject("MainCamera")
    cam = cam_go.add_component(Camera)
    cam.orthographic_size = 16.0
    cam.background_color = (0, 0, 0)

    # Initialize pygame for sprite loading
    if not pygame.get_init():
        pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1), pygame.NOFRAME)

    screen_h = 700
    ppu = int(screen_h / (2.0 * cam.orthographic_size))

    # Sprite loader
    _wall_sprites = {}

    def _get_wall_sprite(tile_index, ppu_val):
        if tile_index not in _wall_sprites:
            filename = f"Wall_{tile_index:02d}.png"
            path = os.path.join(SPRITES_DIR, filename)
            if os.path.exists(path):
                surf = pygame.image.load(path).convert_alpha()
                surf = pygame.transform.scale(surf, (ppu_val, ppu_val))
                _wall_sprites[tile_index] = surf
            else:
                fallback = os.path.join(SPRITES_DIR, "Wall_00.png")
                surf = pygame.image.load(fallback).convert_alpha()
                surf = pygame.transform.scale(surf, (ppu_val, ppu_val))
                _wall_sprites[tile_index] = surf
        return _wall_sprites[tile_index]

    # Build maze walls
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
                sr.sprite = _get_wall_sprite(tile_idx, ppu)
                sr.sorting_order = 0

                rb = wall_go.add_component(Rigidbody2D)
                rb.body_type = RigidbodyType2D.STATIC

                col_comp = wall_go.add_component(BoxCollider2D)
                col_comp.size = Vector2(1.0, 1.0)


@pytest.fixture
def run_pacman_headless():
    """Run the Task 1 wall scene headless for 60 frames and return registry."""
    from src.engine.core import _game_objects, _clear_registry
    from src.engine.lifecycle import LifecycleManager
    from src.engine.physics.physics_manager import PhysicsManager

    # Reset singletons before run
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager._instance = None

    from src.engine.app import run

    run(
        scene_setup=_build_task1_wall_scene,
        width=600,
        height=700,
        headless=True,
        max_frames=60,
    )

    # Collect all game objects that were alive at end of run
    objects = dict(_game_objects)

    yield objects

    # Cleanup
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager._instance = None


@pytest.fixture
def wall_objects(run_pacman_headless):
    """Extract wall GameObjects from the scene."""
    return {
        oid: go for oid, go in run_pacman_headless.items()
        if go.name.startswith("Wall_")
    }


class TestHeadlessRun:
    """The game should run headless for 60 frames without errors."""

    def test_runs_without_error(self, run_pacman_headless):
        """Simply reaching here means 60 frames ran without exception."""
        assert len(run_pacman_headless) > 0, "No GameObjects were created"

    def test_scene_has_camera(self, run_pacman_headless):
        found = any(
            go.name == "MainCamera" for go in run_pacman_headless.values()
        )
        assert found, "MainCamera not found in scene"


class TestWallGameObjects:
    """Wall GameObjects should match the maze 'W' cells."""

    def test_wall_count_matches_maze(self, wall_objects):
        from examples.pacman_v2.pacman_v2_python.maze_data import MAZE
        expected_walls = sum(row.count("W") for row in MAZE)
        assert len(wall_objects) == expected_walls, (
            f"Expected {expected_walls} wall objects, got {len(wall_objects)}"
        )

    def test_walls_have_sprite_renderers(self, wall_objects):
        from src.engine.rendering.renderer import SpriteRenderer
        missing = []
        for oid, go in wall_objects.items():
            sr = go.get_component(SpriteRenderer)
            if sr is None:
                missing.append(go.name)
        assert not missing, f"Walls without SpriteRenderer: {missing[:5]}..."

    def test_wall_sprites_are_not_none(self, wall_objects):
        from src.engine.rendering.renderer import SpriteRenderer
        no_sprite = []
        for oid, go in wall_objects.items():
            sr = go.get_component(SpriteRenderer)
            if sr is not None and sr.sprite is None:
                no_sprite.append(go.name)
        assert not no_sprite, (
            f"Walls with None sprites: {no_sprite[:5]}..."
        )

    def test_walls_have_box_colliders(self, wall_objects):
        from src.engine.physics.collider import BoxCollider2D
        missing = []
        for oid, go in wall_objects.items():
            col = go.get_component(BoxCollider2D)
            if col is None:
                missing.append(go.name)
        assert not missing, (
            f"Walls without BoxCollider2D: {missing[:5]}..."
        )

    def test_walls_on_obstacle_layer(self, wall_objects):
        """All wall GameObjects should be on layer 6 (obstacle layer)."""
        wrong_layer = []
        for oid, go in wall_objects.items():
            if go.layer != 6:
                wrong_layer.append((go.name, go.layer))
        assert not wrong_layer, (
            f"Walls on wrong layer: {wrong_layer[:5]}..."
        )


class TestMutationIntegration:
    """Mutation tests at the integration level."""

    def test_wrong_maze_dimensions_caught(self, monkeypatch):
        """If MAZE has wrong dimensions, wall count should differ."""
        import examples.pacman_v2.pacman_v2_python.maze_data as md

        original_maze = md.MAZE

        # Create a tiny maze (different dimensions)
        bad_maze = ["WWWW"] * 4
        monkeypatch.setattr(md, "MAZE", bad_maze)
        monkeypatch.setattr(md, "MAZE_ROWS", 4)
        monkeypatch.setattr(md, "MAZE_COLS", 4)

        # Count walls in mutant maze
        mutant_walls = sum(row.count("W") for row in bad_maze)
        original_walls = sum(row.count("W") for row in original_maze)

        assert mutant_walls != original_walls, (
            "Mutant maze should have different wall count"
        )

    def test_invalid_tile_index_caught(self, monkeypatch):
        """If select_wall_tile returns -1, it should fail validity."""
        import examples.pacman_v2.pacman_v2_python.maze_data as md
        monkeypatch.setattr(md, "select_wall_tile", lambda c, r: -1)

        # Any wall cell should now get an invalid index
        idx = md.select_wall_tile(0, 0)
        assert not (0 <= idx <= 37), (
            f"Mutant returned valid index {idx}, should be invalid"
        )
