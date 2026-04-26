"""Integration tests for Pacman V2 ghost system.

Tests run actual scene setup and game loop frames to verify:
- Scene creates 4 ghosts with correct components
- Game loop runs 60 frames without crash
- Ghost reset_state re-enables scatter behavior
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "examples", "pacman_v2"))

from src.engine.core import GameObject
from src.engine.math.vector import Vector2
from pacman_v2_python.ghost_eyes import GhostEyes


# ── Helpers ──────────────────────────────────────────────────────

def _setup_minimal_scene():
    """Build a minimal ghost scene without the full maze (avoids sprite loading).

    This creates the core components programmatically so tests don't
    depend on pygame sprite files existing.
    """
    from src.engine.physics.physics_manager import PhysicsManager
    from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
    from src.engine.physics.collider import CircleCollider2D

    from pacman_v2_python.movement import Movement
    from pacman_v2_python.pacman import Pacman
    from pacman_v2_python.ghost import Ghost
    from pacman_v2_python.ghost_home import GhostHome
    from pacman_v2_python.ghost_scatter import GhostScatter
    from pacman_v2_python.ghost_chase import GhostChase
    from pacman_v2_python.ghost_frightened import GhostFrightened
    from pacman_v2_python.game_manager import GameManager
    from src.engine.rendering.renderer import SpriteRenderer

    pm = PhysicsManager.instance()
    pm.gravity = Vector2(0, 0)

    # Pacman
    pacman_go = GameObject("Pacman")
    pacman_go.transform.position = Vector2(5, 5)
    pacman_go.layer = 3
    rb = pacman_go.add_component(Rigidbody2D)
    col_comp = pacman_go.add_component(CircleCollider2D)
    col_comp.radius = 0.5
    mov = pacman_go.add_component(Movement)
    mov.speed = 8.0
    mov.initial_direction = Vector2(-1, 0)
    pac = pacman_go.add_component(Pacman)

    # Ghost home points
    inside_go = GameObject("GhostHome_Inside")
    inside_go.transform.position = Vector2(13, 14)
    outside_go = GameObject("GhostHome_Outside")
    outside_go.transform.position = Vector2(13, 11)

    ghost_configs = [
        ("Blinky", 14, 11, 7.0, False),
        ("Pinky", 14, 14, 7.0, True),
        ("Inky", 12, 14, 5.0, True),
        ("Clyde", 16, 14, 5.0, True),
    ]

    ghost_components = []

    for name, g_col, g_row, scatter_dur, start_in_home in ghost_configs:
        ghost_go = GameObject(f"Ghost_{name}", tag="Ghost")
        ghost_go.transform.position = Vector2(float(g_col), float(g_row))
        ghost_go.layer = 8

        rb = ghost_go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.KINEMATIC
        col_comp = ghost_go.add_component(CircleCollider2D)
        col_comp.radius = 0.5

        sr = ghost_go.add_component(SpriteRenderer)

        mov = ghost_go.add_component(Movement)
        mov.speed = 7.0
        mov.initial_direction = Vector2(0, -1) if start_in_home else Vector2(-1, 0)

        ghost_comp = ghost_go.add_component(Ghost)
        ghost_comp.target = pacman_go

        home = ghost_go.add_component(GhostHome)
        home.inside = inside_go
        home.outside = outside_go
        home.enabled = False

        scatter = ghost_go.add_component(GhostScatter)
        scatter.duration = scatter_dur
        scatter.enabled = False

        chase = ghost_go.add_component(GhostChase)
        chase.duration = 20.0
        chase.enabled = False

        frightened = ghost_go.add_component(GhostFrightened)
        frightened.duration = 8.0
        frightened.enabled = False

        if start_in_home:
            ghost_comp.initial_behavior = home
        else:
            ghost_comp.initial_behavior = scatter

        # Eyes child
        eyes_go = GameObject(f"Ghost_{name}_Eyes")
        eyes_go.transform.set_parent(ghost_go.transform)
        eyes_sr = eyes_go.add_component(SpriteRenderer)
        eyes = eyes_go.add_component(GhostEyes)

        ghost_components.append(ghost_comp)

    # GameManager
    gm_go = GameObject("GameManager")
    gm = gm_go.add_component(GameManager)
    gm.pacman = pac
    gm.ghosts = ghost_components
    gm._all_pellets = []

    return gm, ghost_components, pac


# ── Tests ────────────────────────────────────────────────────────

class TestPacmanV2SceneSetup:
    """Integration: scene creates correct ghost structure."""

    def test_scene_creates_four_ghosts(self):
        gm, ghosts, pac = _setup_minimal_scene()
        assert len(ghosts) == 4
        GameManager.instance = None

    def test_each_ghost_has_all_behavior_components(self):
        gm, ghosts, pac = _setup_minimal_scene()
        for ghost in ghosts:
            # Wire references as start() would
            ghost.movement = ghost.get_component(
                type(ghost).movement.__class__
            ) if ghost.movement is None else ghost.movement

            assert ghost.get_component(GhostHome) is not None, f"{ghost.game_object.name} missing GhostHome"
            assert ghost.get_component(GhostScatter) is not None, f"{ghost.game_object.name} missing GhostScatter"
            assert ghost.get_component(GhostChase) is not None, f"{ghost.game_object.name} missing GhostChase"
            assert ghost.get_component(GhostFrightened) is not None, f"{ghost.game_object.name} missing GhostFrightened"
        GameManager.instance = None

    def test_blinky_starts_outside_home(self):
        """Blinky should have initial_behavior = scatter (not home)."""
        gm, ghosts, pac = _setup_minimal_scene()
        blinky = ghosts[0]
        from pacman_v2_python.ghost_scatter import GhostScatter as GS
        assert isinstance(blinky.initial_behavior, GS)
        GameManager.instance = None

    def test_pinky_starts_in_home(self):
        """Pinky should have initial_behavior = home."""
        gm, ghosts, pac = _setup_minimal_scene()
        pinky = ghosts[1]
        from pacman_v2_python.ghost_home import GhostHome as GH
        assert isinstance(pinky.initial_behavior, GH)
        GameManager.instance = None

    def test_ghost_target_is_pacman(self):
        gm, ghosts, pac = _setup_minimal_scene()
        for ghost in ghosts:
            assert ghost.target is not None
            assert ghost.target.name == "Pacman"
        GameManager.instance = None


class TestPacmanV2GameLoop:
    """Integration: game loop runs without crashes."""

    def test_lifecycle_calls_no_crash(self):
        """Simulate lifecycle calls (awake/start/update) without crashing."""
        from src.engine.time_manager import Time

        gm, ghosts, pac = _setup_minimal_scene()

        # Manually run awake -> start -> updates (no full app.run needed)
        all_objects = [gm] + list(ghosts)
        for obj in all_objects:
            if hasattr(obj, "awake"):
                obj.awake()

        for obj in all_objects:
            if hasattr(obj, "start"):
                obj.start()

        # Run 60 update frames (use backing fields, not descriptors)
        Time._delta_time = 1 / 60
        Time._fixed_delta_time = 1 / 50
        for _ in range(60):
            for obj in all_objects:
                if hasattr(obj, "update"):
                    obj.update()

        GameManager.instance = None


class TestPacmanV2GhostReset:
    """Integration: ghost reset_state restores correct behavior state."""

    def test_reset_state_enables_scatter_for_blinky(self):
        gm, ghosts, pac = _setup_minimal_scene()
        blinky = ghosts[0]

        # Wire up as start() would
        blinky.movement = blinky.get_component(Movement)
        blinky.home = blinky.get_component(GhostHome)
        blinky.scatter = blinky.get_component(GhostScatter)
        blinky.chase = blinky.get_component(GhostChase)
        blinky.frightened = blinky.get_component(GhostFrightened)

        # Mess up state
        blinky.scatter.enabled = False
        blinky.chase.enabled = True
        blinky.frightened.enabled = True
        blinky.game_object.active = False

        blinky.reset_state()

        assert blinky.game_object.active is True
        assert blinky.scatter.enabled is True
        assert blinky.chase.enabled is False
        assert blinky.frightened.enabled is False
        GameManager.instance = None

    def test_reset_state_enables_home_for_pinky(self):
        gm, ghosts, pac = _setup_minimal_scene()
        pinky = ghosts[1]

        pinky.movement = pinky.get_component(Movement)
        pinky.home = pinky.get_component(GhostHome)
        pinky.scatter = pinky.get_component(GhostScatter)
        pinky.chase = pinky.get_component(GhostChase)
        pinky.frightened = pinky.get_component(GhostFrightened)

        pinky.home.enabled = False
        pinky.reset_state()

        assert pinky.home.enabled is True
        GameManager.instance = None


# Need to import these at module level for type checks in tests
from pacman_v2_python.movement import Movement
from pacman_v2_python.ghost_home import GhostHome
from pacman_v2_python.ghost_scatter import GhostScatter
from pacman_v2_python.ghost_chase import GhostChase
from pacman_v2_python.ghost_frightened import GhostFrightened
from pacman_v2_python.game_manager import GameManager
