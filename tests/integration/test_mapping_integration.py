"""Integration tests for asset mapping against real project data files.

Tests load actual mapping and manifest files from data/ to verify
the Angry Birds and Breakout mappings are correct and complete.
"""

from pathlib import Path

import pytest

from src.assets.mapping import AssetMapping, scaffold_mapping, validate_mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_MAPPINGS = PROJECT_ROOT / "data" / "mappings"
DATA_MANIFESTS = PROJECT_ROOT / "data" / "manifests"


class TestAngryBirdsMappingIntegration:
    @pytest.fixture
    def mapping(self):
        return AssetMapping.from_file(DATA_MAPPINGS / "angry_birds_mapping.json")

    def test_has_5_sprite_mappings(self, mapping):
        assert len(mapping.sprites) == 5

    def test_has_3_audio_mappings(self, mapping):
        assert len(mapping.audio) == 3

    def test_bird_red_points_to_sprite_sheet(self, mapping):
        bird = mapping.sprites["bird_red"]
        # Should point to a PNG sprite sheet
        assert bird.unity_path.endswith(".png")
        assert "Sprites" in bird.unity_path or "sprites" in bird.unity_path.lower()

    def test_slingshot_points_to_slingshot_png(self, mapping):
        sling = mapping.sprites["slingshot"]
        assert "slingshot" in sling.unity_path.lower()
        assert sling.unity_path.endswith(".png")

    def test_validate_against_manifest_passes(self):
        manifest_path = DATA_MANIFESTS / "angry_birds.json"
        mapping_path = DATA_MAPPINGS / "angry_birds_mapping.json"
        issues = validate_mapping(manifest_path, mapping_path)
        assert issues == [], f"Expected 0 issues, got: {issues}"


class TestBreakoutMappingIntegration:
    def test_scaffold_generates_3_sprite_entries(self):
        manifest_path = DATA_MANIFESTS / "breakout.json"
        mapping = scaffold_mapping(manifest_path)
        assert len(mapping.sprites) == 3
        assert set(mapping.sprites.keys()) == {"paddle", "ball", "brick"}

    def test_scaffold_generates_no_audio_entries(self):
        """Breakout manifest has no audio refs."""
        manifest_path = DATA_MANIFESTS / "breakout.json"
        mapping = scaffold_mapping(manifest_path)
        assert len(mapping.audio) == 0

    def test_validate_breakout_scaffolded_mapping_passes(self, tmp_path):
        """Scaffold from breakout manifest, save it, validate it -- should pass."""
        manifest_path = DATA_MANIFESTS / "breakout.json"
        mapping = scaffold_mapping(manifest_path)
        mapping_path = tmp_path / "breakout_mapping.json"
        mapping.save(mapping_path)
        issues = validate_mapping(manifest_path, mapping_path)
        assert issues == [], f"Expected 0 issues, got: {issues}"

    def test_validate_existing_breakout_mapping_passes(self):
        """The checked-in breakout mapping should also pass validation."""
        manifest_path = DATA_MANIFESTS / "breakout.json"
        mapping_path = DATA_MAPPINGS / "breakout_mapping.json"
        issues = validate_mapping(manifest_path, mapping_path)
        assert issues == [], f"Expected 0 issues, got: {issues}"
