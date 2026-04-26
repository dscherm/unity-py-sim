"""Contract tests for AssetManifest — derived from expected behavior, not implementation."""

import pytest

from src.engine.core import GameObject, _game_objects, _clear_registry
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.audio import AudioSource
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.math.vector import Vector2
from src.assets.manifest import (
    AssetManifest,
    SpriteAssetInfo,
    AudioAssetInfo,
    generate_manifest_from_setup,
)


@pytest.fixture(autouse=True)
def clean_scene():
    """Ensure a clean engine state before and after every test."""
    _clear_registry()
    LifecycleManager._instance = None
    PhysicsManager._instance = None
    yield
    _clear_registry()
    LifecycleManager._instance = None
    PhysicsManager._instance = None


# ---- Contract 1: empty scene returns empty manifest ----

class TestEmptyScene:
    def test_empty_scene_returns_empty_manifest(self):
        manifest = AssetManifest.from_scene()
        assert manifest.sprites == {}
        assert manifest.audio == {}
        assert manifest.tags_used == []


# ---- Contract 2: from_scene() finds SpriteRenderer.asset_ref ----

class TestSpriteDetection:
    def test_finds_sprite_asset_ref(self):
        go = GameObject("Hero")
        sr = go.add_component(SpriteRenderer)
        sr.asset_ref = "hero_sprite"

        manifest = AssetManifest.from_scene()

        assert "hero_sprite" in manifest.sprites
        assert manifest.sprites["hero_sprite"].asset_ref == "hero_sprite"
        assert "Hero" in manifest.sprites["hero_sprite"].game_objects


# ---- Contract 3: from_scene() finds AudioSource.clip_ref ----

class TestAudioDetection:
    def test_finds_audio_clip_ref(self):
        go = GameObject("SoundEmitter")
        audio = go.add_component(AudioSource)
        audio.clip_ref = "explosion_sfx"

        manifest = AssetManifest.from_scene()

        assert "explosion_sfx" in manifest.audio
        assert manifest.audio["explosion_sfx"].clip_ref == "explosion_sfx"
        assert "SoundEmitter" in manifest.audio["explosion_sfx"].game_objects


# ---- Contract 4: ignores None asset_refs (the default) ----

class TestIgnoresNoneRefs:
    def test_ignores_none_sprite_asset_ref(self):
        go = GameObject("Bare")
        sr = go.add_component(SpriteRenderer)
        # asset_ref defaults to None — should not appear in manifest
        assert sr.asset_ref is None

        manifest = AssetManifest.from_scene()
        assert manifest.sprites == {}

    def test_ignores_none_audio_clip_ref(self):
        go = GameObject("Bare")
        audio = go.add_component(AudioSource)
        assert audio.clip_ref is None

        manifest = AssetManifest.from_scene()
        assert manifest.audio == {}


# ---- Contract 5: collects tags_used, excluding "Untagged" ----

class TestTagsUsed:
    def test_collects_tags_excluding_untagged(self):
        go1 = GameObject("Bird_1", tag="Bird")
        go1.add_component(SpriteRenderer).asset_ref = "bird"
        go2 = GameObject("Wall", tag="Untagged")
        go2.add_component(SpriteRenderer).asset_ref = "wall"
        go3 = GameObject("Pig_1", tag="Pig")
        go3.add_component(SpriteRenderer).asset_ref = "pig"

        manifest = AssetManifest.from_scene()

        assert "Untagged" not in manifest.tags_used
        assert "Bird" in manifest.tags_used
        assert "Pig" in manifest.tags_used

    def test_tags_are_sorted(self):
        GameObject("C", tag="Zebra")
        GameObject("A", tag="Alpha")
        GameObject("B", tag="Middle")

        manifest = AssetManifest.from_scene()

        assert manifest.tags_used == ["Alpha", "Middle", "Zebra"]


# ---- Contract 6: deduplicates asset_refs, accumulates game_object names ----

class TestDeduplication:
    def test_same_asset_ref_accumulates_game_objects(self):
        for i in range(3):
            go = GameObject(f"Brick_{i}", tag="Brick")
            sr = go.add_component(SpriteRenderer)
            sr.asset_ref = "brick_wood"

        manifest = AssetManifest.from_scene()

        assert len(manifest.sprites) == 1, "Should deduplicate by asset_ref"
        info = manifest.sprites["brick_wood"]
        assert len(info.game_objects) == 3
        assert set(info.game_objects) == {"Brick_0", "Brick_1", "Brick_2"}

    def test_same_clip_ref_accumulates_game_objects(self):
        for i in range(2):
            go = GameObject(f"Emitter_{i}")
            audio = go.add_component(AudioSource)
            audio.clip_ref = "hit_sfx"

        manifest = AssetManifest.from_scene()

        assert len(manifest.audio) == 1
        info = manifest.audio["hit_sfx"]
        assert len(info.game_objects) == 2


# ---- Contract 7: SpriteAssetInfo captures color_hint, size, sorting_order from first occurrence ----

class TestSpriteMetadata:
    def test_captures_color_hint_from_first_occurrence(self):
        go1 = GameObject("First")
        sr1 = go1.add_component(SpriteRenderer)
        sr1.asset_ref = "shared"
        sr1.color = (255, 0, 0)
        sr1.size = Vector2(2.0, 3.0)
        sr1.sorting_order = 5

        go2 = GameObject("Second")
        sr2 = go2.add_component(SpriteRenderer)
        sr2.asset_ref = "shared"
        sr2.color = (0, 255, 0)  # different color — should be ignored
        sr2.size = Vector2(9.0, 9.0)
        sr2.sorting_order = 99

        manifest = AssetManifest.from_scene()
        info = manifest.sprites["shared"]

        # First occurrence wins for metadata
        assert info.color_hint == (255, 0, 0)
        assert info.size == (2.0, 3.0)
        assert info.sorting_order == 5


# ---- Contract 8: to_json()/from_json() round-trip preserves all data ----

class TestRoundTrip:
    def test_round_trip_preserves_sprites(self):
        original = AssetManifest()
        original.sprites["hero"] = SpriteAssetInfo(
            asset_ref="hero",
            color_hint=(100, 200, 50),
            size=(1.5, 2.0),
            sorting_order=3,
            game_objects=["Player1", "Player2"],
        )
        original.audio["boom"] = AudioAssetInfo(
            clip_ref="boom",
            game_objects=["Cannon"],
        )
        original.tags_used = ["Enemy", "Player"]

        json_text = original.to_json()
        restored = AssetManifest.from_json(json_text)

        assert set(restored.sprites.keys()) == {"hero"}
        hero = restored.sprites["hero"]
        assert hero.asset_ref == "hero"
        assert hero.color_hint == [100, 200, 50]  # JSON round-trip: tuples -> lists
        assert hero.size == [1.5, 2.0]
        assert hero.sorting_order == 3
        assert hero.game_objects == ["Player1", "Player2"]

        assert set(restored.audio.keys()) == {"boom"}
        assert restored.audio["boom"].clip_ref == "boom"
        assert restored.audio["boom"].game_objects == ["Cannon"]

        assert restored.tags_used == ["Enemy", "Player"]

    def test_round_trip_empty_manifest(self):
        original = AssetManifest()
        restored = AssetManifest.from_json(original.to_json())
        assert restored.sprites == {}
        assert restored.audio == {}
        assert restored.tags_used == []


# ---- Contract 9: generate_manifest_from_setup() cleans up scene state ----

class TestGenerateManifestCleanup:
    def test_cleans_up_scene_after_extraction(self):
        def my_setup():
            go = GameObject("Temp", tag="Temp")
            sr = go.add_component(SpriteRenderer)
            sr.asset_ref = "temp_sprite"

        manifest = generate_manifest_from_setup(my_setup)

        # Manifest should have captured the data
        assert "temp_sprite" in manifest.sprites

        # But the global registry should be clean after extraction
        assert len(_game_objects) == 0, (
            "generate_manifest_from_setup must clear _game_objects after extraction"
        )

    def test_cleans_up_scene_before_extraction(self):
        # Pre-pollute the scene
        stale = GameObject("StaleObject")
        sr = stale.add_component(SpriteRenderer)
        sr.asset_ref = "stale_ref"

        def fresh_setup():
            go = GameObject("Fresh")
            go.add_component(SpriteRenderer).asset_ref = "fresh_ref"

        manifest = generate_manifest_from_setup(fresh_setup)

        # Should only have the fresh setup's assets, not the stale ones
        assert "fresh_ref" in manifest.sprites
        assert "stale_ref" not in manifest.sprites
