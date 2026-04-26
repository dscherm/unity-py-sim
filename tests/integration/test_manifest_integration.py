"""Integration tests for AssetManifest — generate manifests from actual example setups."""

import pytest

from src.engine.core import _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.assets.manifest import generate_manifest_from_setup


@pytest.fixture(autouse=True)
def clean_engine():
    """Ensure clean engine state before and after each test."""
    _clear_registry()
    LifecycleManager._instance = None
    PhysicsManager._instance = None
    yield
    _clear_registry()
    LifecycleManager._instance = None
    PhysicsManager._instance = None


# ---- Angry Birds integration ----

class TestAngryBirdsManifest:
    @pytest.fixture()
    def manifest(self):
        from examples.angry_birds.angry_birds_python.levels import setup_level_1
        return generate_manifest_from_setup(setup_level_1)

    def test_sprite_count(self, manifest):
        assert len(manifest.sprites) == 5, (
            f"Expected 5 sprite refs, got {len(manifest.sprites)}: {list(manifest.sprites.keys())}"
        )

    def test_audio_count(self, manifest):
        assert len(manifest.audio) == 3, (
            f"Expected 3 audio refs, got {len(manifest.audio)}: {list(manifest.audio.keys())}"
        )

    def test_sprite_names(self, manifest):
        expected = {"bird_red", "pig_normal", "brick_wood", "slingshot", "ground_grass"}
        actual = set(manifest.sprites.keys())
        assert actual == expected, f"Sprite mismatch: {actual.symmetric_difference(expected)}"

    def test_audio_names(self, manifest):
        expected = {"bird_launch_sfx", "brick_break_sfx", "pig_hit_sfx"}
        actual = set(manifest.audio.keys())
        assert actual == expected, f"Audio mismatch: {actual.symmetric_difference(expected)}"

    def test_tags_include_bird_pig_brick(self, manifest):
        for tag in ("Bird", "Pig", "Brick"):
            assert tag in manifest.tags_used, f"Tag '{tag}' missing from tags_used: {manifest.tags_used}"

    def test_bird_red_used_by_three_birds(self, manifest):
        """Level 1 has 3 birds, all using bird_red."""
        bird_info = manifest.sprites["bird_red"]
        assert len(bird_info.game_objects) == 3

    def test_brick_wood_used_by_six_bricks(self, manifest):
        """Level 1 has 6 bricks."""
        brick_info = manifest.sprites["brick_wood"]
        assert len(brick_info.game_objects) == 6

    def test_pig_normal_used_by_two_pigs(self, manifest):
        """Level 1 has 2 pigs."""
        pig_info = manifest.sprites["pig_normal"]
        assert len(pig_info.game_objects) == 2


# ---- Breakout integration ----

class TestBreakoutManifest:
    @pytest.fixture()
    def manifest(self):
        from examples.breakout.run_breakout import setup_scene
        return generate_manifest_from_setup(setup_scene)

    def test_sprite_count(self, manifest):
        assert len(manifest.sprites) == 3, (
            f"Expected 3 sprite refs, got {len(manifest.sprites)}: {list(manifest.sprites.keys())}"
        )

    def test_sprite_names(self, manifest):
        expected = {"paddle", "ball", "brick"}
        actual = set(manifest.sprites.keys())
        assert actual == expected, f"Sprite mismatch: {actual.symmetric_difference(expected)}"

    def test_brick_used_by_80_objects(self, manifest):
        """Breakout has 10 columns x 8 rows = 80 bricks."""
        brick_info = manifest.sprites["brick"]
        assert len(brick_info.game_objects) == 80, (
            f"Expected 80 brick objects, got {len(brick_info.game_objects)}"
        )

    def test_audio_refs(self, manifest):
        """Breakout example has audio for ball hit and brick break."""
        assert len(manifest.audio) > 0
        audio_refs = set(manifest.audio.keys())
        assert "ball_hit" in audio_refs
        assert "brick_break" in audio_refs
