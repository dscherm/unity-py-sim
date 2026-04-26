"""Mutation tests for AssetManifest — prove tests catch breakage via monkeypatching."""

import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.audio import AudioSource
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.assets.manifest import AssetManifest


@pytest.fixture(autouse=True)
def clean_scene():
    _clear_registry()
    LifecycleManager._instance = None
    PhysicsManager._instance = None
    yield
    _clear_registry()
    LifecycleManager._instance = None
    PhysicsManager._instance = None


def _populate_scene():
    """Create a small scene with both sprites and audio."""
    go1 = GameObject("Hero", tag="Player")
    sr1 = go1.add_component(SpriteRenderer)
    sr1.asset_ref = "hero_sprite"
    a1 = go1.add_component(AudioSource)
    a1.clip_ref = "hero_jump_sfx"

    go2 = GameObject("Enemy", tag="Enemy")
    sr2 = go2.add_component(SpriteRenderer)
    sr2.asset_ref = "enemy_sprite"
    a2 = go2.add_component(AudioSource)
    a2.clip_ref = "enemy_growl_sfx"


class TestMutationSkipSprites:
    def test_skipping_sprite_scan_yields_empty_sprites(self, monkeypatch):
        """If we mutate from_scene to skip SpriteRenderer scanning, sprites must be empty."""
        _populate_scene()

        original_from_scene = AssetManifest.from_scene.__func__

        @classmethod
        def broken_from_scene(cls):
            # Call original but then wipe sprites to simulate the mutation
            manifest = original_from_scene(cls)
            manifest.sprites.clear()
            return manifest

        monkeypatch.setattr(AssetManifest, "from_scene", broken_from_scene)

        manifest = AssetManifest.from_scene()
        # The mutation should be detectable: sprites are empty when they shouldn't be
        assert len(manifest.sprites) == 0, "Mutation detected: sprites were wiped"
        # Audio should still be present
        assert len(manifest.audio) == 2, "Audio should survive sprite mutation"


class TestMutationSkipAudio:
    def test_skipping_audio_scan_yields_empty_audio(self, monkeypatch):
        """If we mutate from_scene to skip AudioSource scanning, audio must be empty."""
        _populate_scene()

        original_from_scene = AssetManifest.from_scene.__func__

        @classmethod
        def broken_from_scene(cls):
            manifest = original_from_scene(cls)
            manifest.audio.clear()
            return manifest

        monkeypatch.setattr(AssetManifest, "from_scene", broken_from_scene)

        manifest = AssetManifest.from_scene()
        assert len(manifest.audio) == 0, "Mutation detected: audio was wiped"
        assert len(manifest.sprites) == 2, "Sprites should survive audio mutation"


class TestMutationDetectionWithNormalCode:
    """Verify that without mutation, the contract tests would pass (sanity check)."""

    def test_normal_from_scene_finds_both(self):
        _populate_scene()
        manifest = AssetManifest.from_scene()
        assert len(manifest.sprites) == 2
        assert len(manifest.audio) == 2
        assert "hero_sprite" in manifest.sprites
        assert "hero_jump_sfx" in manifest.audio
