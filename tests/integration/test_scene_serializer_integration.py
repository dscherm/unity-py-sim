"""Integration tests for scene_serializer against real game scenes.

Tests serialize actual Angry Birds and Breakout scenes and verify the output
matches expected game structure (object counts, component types, field values).
"""

import json

import pytest

from src.engine.core import _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.rendering.camera import Camera
from src.engine.audio import AudioListener

from src.exporter.scene_serializer import serialize_from_setup, _sanitize_for_json


@pytest.fixture(autouse=True)
def clean_scene():
    _clear_registry()
    LifecycleManager._instance = None
    PhysicsManager._instance = None
    Camera._reset_main()
    AudioListener.reset()
    yield
    _clear_registry()
    LifecycleManager._instance = None
    PhysicsManager._instance = None
    Camera._reset_main()
    AudioListener.reset()


def _get_go(scene, name):
    """Find a game object by name in scene data."""
    matches = [g for g in scene["game_objects"] if g["name"] == name]
    assert matches, f"No GameObject named '{name}' found"
    return matches[0]


def _get_comp(go_data, comp_type):
    """Find a component by type name in a game object's data."""
    matches = [c for c in go_data["components"] if c["type"] == comp_type]
    assert matches, f"No {comp_type} found on {go_data['name']}"
    return matches[0]


def _get_monobehaviour(go_data, type_name):
    """Find a MonoBehaviour component by type name."""
    matches = [
        c for c in go_data["components"]
        if c.get("is_monobehaviour") and c["type"] == type_name
    ]
    assert matches, f"No MonoBehaviour '{type_name}' on {go_data['name']}"
    return matches[0]


# ---------------------------------------------------------------------------
# Angry Birds level_1
# ---------------------------------------------------------------------------

class TestAngryBirdsLevel1:
    @pytest.fixture()
    def scene(self):
        from examples.angry_birds.angry_birds_python.levels import setup_level_1
        return serialize_from_setup(setup_level_1)

    def test_total_gameobject_count(self, scene):
        """Level 1 should contain 18 GameObjects:
        MainCamera, Ground, Slingshot, 3 Destroyers,
        3 Birds, 6 Bricks, 2 Pigs, GameManager = 18.
        """
        assert len(scene["game_objects"]) == 18

    def test_main_camera_has_camera_component(self, scene):
        cam_go = _get_go(scene, "MainCamera")
        cam = _get_comp(cam_go, "Camera")
        assert cam["orthographic_size"] == pytest.approx(6.0)

    def test_ground_rigidbody_is_static(self, scene):
        ground = _get_go(scene, "Ground")
        rb = _get_comp(ground, "Rigidbody2D")
        assert rb["body_type"] == "Static"

    def test_ground_box_collider_size(self, scene):
        ground = _get_go(scene, "Ground")
        col = _get_comp(ground, "BoxCollider2D")
        assert col["size"] == [30, 1]

    def test_bird1_has_rigidbody(self, scene):
        bird = _get_go(scene, "Bird_1")
        rb = _get_comp(bird, "Rigidbody2D")
        assert rb["body_type"] == "Dynamic"
        assert rb["mass"] == pytest.approx(1.0)

    def test_bird1_has_circle_collider(self, scene):
        bird = _get_go(scene, "Bird_1")
        col = _get_comp(bird, "CircleCollider2D")
        assert col["radius"] == pytest.approx(0.3)

    def test_bird1_sprite_renderer_asset_ref(self, scene):
        bird = _get_go(scene, "Bird_1")
        sr = _get_comp(bird, "SpriteRenderer")
        assert sr["asset_ref"] == "bird_red"

    def test_slingshot_has_monobehaviour(self, scene):
        sling = _get_go(scene, "Slingshot")
        mb = _get_monobehaviour(sling, "Slingshot")
        assert mb["is_monobehaviour"] is True

    def test_all_expected_tags_present(self, scene):
        tags = {g["tag"] for g in scene["game_objects"]}
        for expected in ["Bird", "Brick", "Pig", "Ground"]:
            assert expected in tags, f"Tag '{expected}' not found in scene"

    def test_bird_count(self, scene):
        birds = [g for g in scene["game_objects"] if g["tag"] == "Bird"]
        assert len(birds) == 3

    def test_pig_count(self, scene):
        pigs = [g for g in scene["game_objects"] if g["tag"] == "Pig"]
        assert len(pigs) == 2

    def test_brick_count(self, scene):
        bricks = [g for g in scene["game_objects"] if g["tag"] == "Brick"]
        assert len(bricks) == 6

    def test_scene_json_roundtrip(self, scene):
        """Serialized scene must survive JSON encode/decode without loss."""
        sanitized = _sanitize_for_json(scene)
        json_str = json.dumps(sanitized)
        reloaded = json.loads(json_str)
        assert reloaded["version"] == scene["version"]
        assert len(reloaded["game_objects"]) == len(scene["game_objects"])


# ---------------------------------------------------------------------------
# Breakout
# ---------------------------------------------------------------------------

class TestBreakoutScene:
    @pytest.fixture()
    def scene(self):
        import sys
        import os
        # Ensure breakout_python is importable
        breakout_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "examples", "breakout"
        )
        breakout_dir = os.path.normpath(breakout_dir)
        if breakout_dir not in sys.path:
            sys.path.insert(0, breakout_dir)

        from examples.breakout.run_breakout import setup_scene
        return serialize_from_setup(setup_scene)

    def test_paddle_exists(self, scene):
        paddle = _get_go(scene, "Paddle")
        assert paddle["tag"] == "Paddle"

    def test_ball_exists(self, scene):
        ball = _get_go(scene, "Ball")
        assert ball["tag"] == "Ball"

    def test_brick_count_is_80(self, scene):
        """Breakout has 8 rows x 10 columns = 80 bricks."""
        bricks = [g for g in scene["game_objects"] if g["tag"] == "Brick"]
        assert len(bricks) == 80

    def test_paddle_has_sprite_renderer(self, scene):
        paddle = _get_go(scene, "Paddle")
        sr = _get_comp(paddle, "SpriteRenderer")
        assert sr["asset_ref"] == "paddle"

    def test_ball_has_circle_collider(self, scene):
        ball = _get_go(scene, "Ball")
        col = _get_comp(ball, "CircleCollider2D")
        assert col["radius"] == pytest.approx(0.2)

    def test_walls_present(self, scene):
        wall_names = {"LeftWall", "RightWall", "TopWall"}
        found = {g["name"] for g in scene["game_objects"] if g["name"] in wall_names}
        assert found == wall_names

    def test_game_manager_exists(self, scene):
        gm = _get_go(scene, "GameManager")
        mb = _get_monobehaviour(gm, "GameManager")
        assert mb["is_monobehaviour"] is True
