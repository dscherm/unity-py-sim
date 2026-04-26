"""Tests for asset manifest — extracts asset references from running scenes."""

from src.engine.core import GameObject, _game_objects
from src.engine.rendering.renderer import SpriteRenderer
from src.assets.manifest import SpriteAssetInfo, AudioAssetInfo, AssetManifest


def setup_function():
    _game_objects.clear()


def teardown_function():
    _game_objects.clear()


def test_sprite_asset_info_defaults():
    info = SpriteAssetInfo(asset_ref="player_sprite")
    assert info.asset_ref == "player_sprite"
    assert info.color_hint == (255, 255, 255)
    assert info.size == (1.0, 1.0)
    assert info.sorting_order == 0
    assert info.game_objects == []


def test_audio_asset_info_defaults():
    info = AudioAssetInfo(clip_ref="bgm")
    assert info.clip_ref == "bgm"
    assert info.game_objects == []


def test_from_scene_empty():
    manifest = AssetManifest.from_scene()
    assert len(manifest.sprites) == 0
    assert len(manifest.audio) == 0


def test_from_scene_with_sprite():
    go = GameObject("Player")
    sr = go.add_component(SpriteRenderer)
    sr.asset_ref = "player_sprite"
    manifest = AssetManifest.from_scene()
    assert "player_sprite" in manifest.sprites
    assert "Player" in manifest.sprites["player_sprite"].game_objects


def test_to_dict_roundtrip():
    manifest = AssetManifest()
    manifest.sprites["test"] = SpriteAssetInfo(asset_ref="test")
    data = manifest.to_dict()
    assert "sprites" in data
    assert "test" in data["sprites"]


def test_json_roundtrip():
    manifest = AssetManifest()
    manifest.sprites["spr"] = SpriteAssetInfo(asset_ref="spr", sorting_order=5)
    manifest.tags_used = ["Player", "Enemy"]
    json_str = manifest.to_json()
    restored = AssetManifest.from_json(json_str)
    assert restored.sprites["spr"].sorting_order == 5
    assert restored.tags_used == ["Player", "Enemy"]
