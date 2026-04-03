"""Integration tests: verify asset_ref/clip_ref are set correctly in example levels.

These tests load actual game levels headless and inspect the runtime scene graph
to confirm that every SpriteRenderer and AudioSource carries the correct
symbolic asset reference for Unity export.
"""

import sys
import os
import pytest

# Ensure project root and example dirs are on the path
_project_root = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, _project_root)
sys.path.insert(0, os.path.join(_project_root, "examples", "breakout"))

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.audio import AudioSource
from src.engine.scene import SceneManager


@pytest.fixture(autouse=True)
def _clean_engine():
    """Full engine reset between tests."""
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    SceneManager.clear()
    yield
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    SceneManager.clear()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _get_all_components_on_tagged(tag, component_cls):
    """Return list of (game_object, component) for all active GOs with *tag*."""
    gos = GameObject.find_game_objects_with_tag(tag)
    results = []
    for go in gos:
        for comp in go.get_components(component_cls):
            results.append((go, comp))
    return results


# ---------------------------------------------------------------------------
# Angry Birds level_1
# ---------------------------------------------------------------------------

class TestAngryBirdsLevel1AssetRefs:
    """Load Angry Birds level 1 and verify all asset_ref / clip_ref values."""

    @pytest.fixture(autouse=True)
    def _setup_level(self):
        from examples.angry_birds.angry_birds_python.levels import setup_level_1
        setup_level_1()

    def test_bird_sprite_renderers_have_bird_red(self):
        pairs = _get_all_components_on_tagged("Bird", SpriteRenderer)
        assert len(pairs) >= 1, "Expected at least one Bird SpriteRenderer"
        for go, sr in pairs:
            assert sr.asset_ref == "bird_red", (
                f"{go.name} SpriteRenderer.asset_ref = {sr.asset_ref!r}, expected 'bird_red'"
            )

    def test_pig_sprite_renderers_have_pig_normal(self):
        pairs = _get_all_components_on_tagged("Pig", SpriteRenderer)
        assert len(pairs) >= 1, "Expected at least one Pig SpriteRenderer"
        for go, sr in pairs:
            assert sr.asset_ref == "pig_normal", (
                f"{go.name} SpriteRenderer.asset_ref = {sr.asset_ref!r}, expected 'pig_normal'"
            )

    def test_brick_sprite_renderers_have_brick_wood(self):
        pairs = _get_all_components_on_tagged("Brick", SpriteRenderer)
        assert len(pairs) >= 1, "Expected at least one Brick SpriteRenderer"
        for go, sr in pairs:
            assert sr.asset_ref == "brick_wood", (
                f"{go.name} SpriteRenderer.asset_ref = {sr.asset_ref!r}, expected 'brick_wood'"
            )

    def test_slingshot_sprite_renderer_has_slingshot(self):
        slingshot_go = GameObject.find("Slingshot")
        assert slingshot_go is not None, "Slingshot GameObject not found"
        sr = slingshot_go.get_component(SpriteRenderer)
        assert sr is not None, "Slingshot has no SpriteRenderer"
        assert sr.asset_ref == "slingshot"

    def test_bird_audio_sources_have_bird_launch_sfx(self):
        pairs = _get_all_components_on_tagged("Bird", AudioSource)
        assert len(pairs) >= 1, "Expected at least one Bird AudioSource"
        for go, audio in pairs:
            assert audio.clip_ref == "bird_launch_sfx", (
                f"{go.name} AudioSource.clip_ref = {audio.clip_ref!r}, expected 'bird_launch_sfx'"
            )

    def test_pig_audio_sources_have_pig_hit_sfx(self):
        pairs = _get_all_components_on_tagged("Pig", AudioSource)
        assert len(pairs) >= 1, "Expected at least one Pig AudioSource"
        for go, audio in pairs:
            assert audio.clip_ref == "pig_hit_sfx", (
                f"{go.name} AudioSource.clip_ref = {audio.clip_ref!r}, expected 'pig_hit_sfx'"
            )

    def test_brick_audio_sources_have_brick_break_sfx(self):
        pairs = _get_all_components_on_tagged("Brick", AudioSource)
        assert len(pairs) >= 1, "Expected at least one Brick AudioSource"
        for go, audio in pairs:
            assert audio.clip_ref == "brick_break_sfx", (
                f"{go.name} AudioSource.clip_ref = {audio.clip_ref!r}, expected 'brick_break_sfx'"
            )

    def test_ground_has_ground_grass_asset_ref(self):
        ground_go = GameObject.find_with_tag("Ground")
        assert ground_go is not None, "Ground GameObject not found"
        sr = ground_go.get_component(SpriteRenderer)
        assert sr is not None
        assert sr.asset_ref == "ground_grass"


# ---------------------------------------------------------------------------
# Breakout
# ---------------------------------------------------------------------------

class TestBreakoutAssetRefs:
    """Load breakout scene and verify asset_ref values."""

    @pytest.fixture(autouse=True)
    def _setup_level(self):
        from examples.breakout.run_breakout import setup_scene
        setup_scene()

    def test_paddle_has_asset_ref_paddle(self):
        paddle = GameObject.find("Paddle")
        assert paddle is not None, "Paddle GameObject not found"
        sr = paddle.get_component(SpriteRenderer)
        assert sr is not None
        assert sr.asset_ref == "paddle"

    def test_ball_has_asset_ref_ball(self):
        ball = GameObject.find("Ball")
        assert ball is not None, "Ball GameObject not found"
        sr = ball.get_component(SpriteRenderer)
        assert sr is not None
        assert sr.asset_ref == "ball"

    def test_bricks_have_asset_ref_brick(self):
        pairs = _get_all_components_on_tagged("Brick", SpriteRenderer)
        assert len(pairs) >= 1, "Expected at least one Brick SpriteRenderer"
        for go, sr in pairs:
            assert sr.asset_ref == "brick", (
                f"{go.name} SpriteRenderer.asset_ref = {sr.asset_ref!r}, expected 'brick'"
            )

    def test_brick_count_is_80(self):
        """Breakout has 10 cols x 8 rows = 80 bricks."""
        pairs = _get_all_components_on_tagged("Brick", SpriteRenderer)
        assert len(pairs) == 80
