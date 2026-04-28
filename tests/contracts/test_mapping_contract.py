"""Contract tests for src.assets.mapping — AssetMapping, SpriteMapping, AudioMapping.

Derived from expected behavior of the mapping system:
- SpriteMapping defaults match Unity conventions (ppu=100, Sprite-Unlit-Default, Default layer)
- Round-trip serialization preserves all fields
- validate_mapping detects UNMAPPED, ORPHAN, and EMPTY issues
- scaffold_mapping generates entries for all manifest refs
"""

import json
from pathlib import Path


from src.assets.mapping import (
    AssetMapping,
    AudioMapping,
    SpriteMapping,
    scaffold_mapping,
    validate_mapping,
)


# ---------------------------------------------------------------------------
# SpriteMapping defaults
# ---------------------------------------------------------------------------

class TestSpriteMappingDefaults:
    def test_ppu_defaults_to_100(self):
        sm = SpriteMapping(unity_path="Assets/Sprites/foo.png")
        assert sm.ppu == 100

    def test_material_defaults_to_sprite_unlit(self):
        sm = SpriteMapping(unity_path="Assets/Sprites/foo.png")
        assert sm.material == "Sprite-Unlit-Default"

    def test_sorting_layer_defaults_to_default(self):
        sm = SpriteMapping(unity_path="Assets/Sprites/foo.png")
        assert sm.sorting_layer == "Default"

    def test_sprite_name_defaults_to_none(self):
        sm = SpriteMapping(unity_path="Assets/Sprites/foo.png")
        assert sm.sprite_name is None

    def test_notes_defaults_to_empty_string(self):
        sm = SpriteMapping(unity_path="Assets/Sprites/foo.png")
        assert sm.notes == ""


# ---------------------------------------------------------------------------
# Round-trip serialization
# ---------------------------------------------------------------------------

class TestRoundTrip:
    def test_to_json_from_json_preserves_sprites(self):
        mapping = AssetMapping()
        mapping.sprites["hero"] = SpriteMapping(
            unity_path="Assets/Sprites/hero.png",
            sprite_name="hero_0",
            ppu=64,
            material="Custom-Mat",
            sorting_layer="Foreground",
            notes="test note",
        )
        restored = AssetMapping.from_json(mapping.to_json())
        s = restored.sprites["hero"]
        assert s.unity_path == "Assets/Sprites/hero.png"
        assert s.sprite_name == "hero_0"
        assert s.ppu == 64
        assert s.material == "Custom-Mat"
        assert s.sorting_layer == "Foreground"
        assert s.notes == "test note"

    def test_to_json_from_json_preserves_audio(self):
        mapping = AssetMapping()
        mapping.audio["boom"] = AudioMapping(
            unity_path="Assets/Audio/boom.wav",
            notes="explosion sfx",
        )
        restored = AssetMapping.from_json(mapping.to_json())
        a = restored.audio["boom"]
        assert a.unity_path == "Assets/Audio/boom.wav"
        assert a.notes == "explosion sfx"

    def test_round_trip_preserves_multiple_entries(self):
        mapping = AssetMapping()
        mapping.sprites["a"] = SpriteMapping(unity_path="Assets/a.png")
        mapping.sprites["b"] = SpriteMapping(unity_path="Assets/b.png", ppu=50)
        mapping.audio["x"] = AudioMapping(unity_path="Assets/x.wav")
        mapping.audio["y"] = AudioMapping(unity_path="Assets/y.wav", notes="n")

        restored = AssetMapping.from_json(mapping.to_json())
        assert set(restored.sprites.keys()) == {"a", "b"}
        assert set(restored.audio.keys()) == {"x", "y"}
        assert restored.sprites["b"].ppu == 50
        assert restored.audio["y"].notes == "n"

    def test_empty_mapping_round_trips(self):
        mapping = AssetMapping()
        restored = AssetMapping.from_json(mapping.to_json())
        assert len(restored.sprites) == 0
        assert len(restored.audio) == 0


# ---------------------------------------------------------------------------
# Helpers — write temp manifest and mapping files
# ---------------------------------------------------------------------------

def _write_manifest(tmp: Path, sprites: dict, audio: dict) -> Path:
    """Write a minimal manifest JSON and return its path."""
    manifest = {
        "sprites": {
            ref: {
                "asset_ref": ref,
                "color_hint": [255, 255, 255],
                "size": [1.0, 1.0],
                "sorting_order": 0,
                "game_objects": gos,
            }
            for ref, gos in sprites.items()
        },
        "audio": {
            ref: {
                "clip_ref": ref,
                "game_objects": gos,
            }
            for ref, gos in audio.items()
        },
        "tags_used": [],
    }
    p = tmp / "manifest.json"
    p.write_text(json.dumps(manifest), encoding="utf-8")
    return p


def _write_mapping(tmp: Path, sprites: dict, audio: dict) -> Path:
    """Write a minimal mapping JSON and return its path."""
    mapping_data = {
        "sprites": {
            ref: {
                "unity_path": upath,
                "sprite_name": None,
                "ppu": 100,
                "material": "Sprite-Unlit-Default",
                "sorting_layer": "Default",
                "notes": "",
            }
            for ref, upath in sprites.items()
        },
        "audio": {
            ref: {
                "unity_path": upath,
                "notes": "",
            }
            for ref, upath in audio.items()
        },
    }
    p = tmp / "mapping.json"
    p.write_text(json.dumps(mapping_data), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# validate_mapping
# ---------------------------------------------------------------------------

class TestValidateMapping:
    def test_all_refs_mapped_returns_empty(self, tmp_path):
        manifest_path = _write_manifest(
            tmp_path,
            sprites={"hero": ["Player"]},
            audio={"jump": ["Player"]},
        )
        mapping_path = _write_mapping(
            tmp_path,
            sprites={"hero": "Assets/Sprites/hero.png"},
            audio={"jump": "Assets/Audio/jump.wav"},
        )
        issues = validate_mapping(manifest_path, mapping_path)
        assert issues == []

    def test_unmapped_sprite_detected(self, tmp_path):
        manifest_path = _write_manifest(
            tmp_path,
            sprites={"hero": ["Player"], "enemy": ["Goblin"]},
            audio={},
        )
        mapping_path = _write_mapping(
            tmp_path,
            sprites={"hero": "Assets/Sprites/hero.png"},
            audio={},
        )
        issues = validate_mapping(manifest_path, mapping_path)
        unmapped = [i for i in issues if "UNMAPPED" in i and "enemy" in i]
        assert len(unmapped) == 1

    def test_unmapped_audio_detected(self, tmp_path):
        manifest_path = _write_manifest(
            tmp_path,
            sprites={},
            audio={"boom": ["Bomb"], "click": ["UI"]},
        )
        mapping_path = _write_mapping(
            tmp_path,
            sprites={},
            audio={"boom": "Assets/Audio/boom.wav"},
        )
        issues = validate_mapping(manifest_path, mapping_path)
        unmapped = [i for i in issues if "UNMAPPED" in i and "click" in i]
        assert len(unmapped) == 1

    def test_orphan_sprite_detected(self, tmp_path):
        manifest_path = _write_manifest(
            tmp_path,
            sprites={"hero": ["Player"]},
            audio={},
        )
        mapping_path = _write_mapping(
            tmp_path,
            sprites={"hero": "Assets/hero.png", "ghost": "Assets/ghost.png"},
            audio={},
        )
        issues = validate_mapping(manifest_path, mapping_path)
        orphan = [i for i in issues if "ORPHAN" in i and "ghost" in i]
        assert len(orphan) == 1

    def test_orphan_audio_detected(self, tmp_path):
        manifest_path = _write_manifest(
            tmp_path,
            sprites={},
            audio={"boom": ["Bomb"]},
        )
        mapping_path = _write_mapping(
            tmp_path,
            sprites={},
            audio={"boom": "Assets/boom.wav", "unused": "Assets/unused.wav"},
        )
        issues = validate_mapping(manifest_path, mapping_path)
        orphan = [i for i in issues if "ORPHAN" in i and "unused" in i]
        assert len(orphan) == 1

    def test_empty_unity_path_detected(self, tmp_path):
        manifest_path = _write_manifest(
            tmp_path,
            sprites={"hero": ["Player"]},
            audio={},
        )
        mapping_path = _write_mapping(
            tmp_path,
            sprites={"hero": ""},  # empty path
            audio={},
        )
        issues = validate_mapping(manifest_path, mapping_path)
        empty = [i for i in issues if "EMPTY" in i and "hero" in i]
        assert len(empty) == 1

    def test_empty_audio_unity_path_detected(self, tmp_path):
        manifest_path = _write_manifest(
            tmp_path,
            sprites={},
            audio={"boom": ["Bomb"]},
        )
        mapping_path = _write_mapping(
            tmp_path,
            sprites={},
            audio={"boom": ""},  # empty path
        )
        issues = validate_mapping(manifest_path, mapping_path)
        empty = [i for i in issues if "EMPTY" in i and "boom" in i]
        assert len(empty) == 1


# ---------------------------------------------------------------------------
# scaffold_mapping
# ---------------------------------------------------------------------------

class TestScaffoldMapping:
    def test_generates_entry_for_every_sprite(self, tmp_path):
        manifest_path = _write_manifest(
            tmp_path,
            sprites={"hero": ["P"], "enemy": ["E"], "bg": ["BG"]},
            audio={},
        )
        mapping = scaffold_mapping(manifest_path)
        assert set(mapping.sprites.keys()) == {"hero", "enemy", "bg"}

    def test_generates_entry_for_every_audio(self, tmp_path):
        manifest_path = _write_manifest(
            tmp_path,
            sprites={},
            audio={"boom": ["B"], "click": ["UI"]},
        )
        mapping = scaffold_mapping(manifest_path)
        assert set(mapping.audio.keys()) == {"boom", "click"}

    def test_sprite_unity_path_pattern(self, tmp_path):
        manifest_path = _write_manifest(
            tmp_path,
            sprites={"hero": ["P"]},
            audio={},
        )
        mapping = scaffold_mapping(manifest_path)
        assert mapping.sprites["hero"].unity_path == "Assets/Sprites/hero.png"

    def test_audio_unity_path_pattern(self, tmp_path):
        manifest_path = _write_manifest(
            tmp_path,
            sprites={},
            audio={"boom": ["B"]},
        )
        mapping = scaffold_mapping(manifest_path)
        assert mapping.audio["boom"].unity_path == "Assets/Audio/boom.wav"

    def test_scaffold_sprite_defaults(self, tmp_path):
        manifest_path = _write_manifest(
            tmp_path,
            sprites={"hero": ["P"]},
            audio={},
        )
        mapping = scaffold_mapping(manifest_path)
        s = mapping.sprites["hero"]
        assert s.ppu == 100
        assert s.material == "Sprite-Unlit-Default"


# ---------------------------------------------------------------------------
# from_file
# ---------------------------------------------------------------------------

class TestFromFile:
    def test_from_file_loads_correctly(self, tmp_path):
        mapping = AssetMapping()
        mapping.sprites["x"] = SpriteMapping(
            unity_path="Assets/x.png", ppu=42
        )
        mapping.audio["y"] = AudioMapping(unity_path="Assets/y.wav")
        fpath = tmp_path / "test.json"
        mapping.save(fpath)

        loaded = AssetMapping.from_file(fpath)
        assert "x" in loaded.sprites
        assert loaded.sprites["x"].ppu == 42
        assert "y" in loaded.audio
        assert loaded.audio["y"].unity_path == "Assets/y.wav"
