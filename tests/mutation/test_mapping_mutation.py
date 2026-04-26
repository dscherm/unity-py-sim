"""Mutation tests for asset mapping validation.

Each test mutates a known-good mapping and verifies that
validate_mapping catches the problem.
"""

import json
from pathlib import Path

import pytest

from src.assets.mapping import validate_mapping

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_MAPPINGS = PROJECT_ROOT / "data" / "mappings"
DATA_MANIFESTS = PROJECT_ROOT / "data" / "manifests"


@pytest.fixture
def angry_birds_mapping():
    """Load the real angry_birds mapping as a mutable dict."""
    path = DATA_MAPPINGS / "angry_birds_mapping.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture
def angry_birds_manifest_path():
    return DATA_MANIFESTS / "angry_birds.json"


class TestMutationUnmapped:
    def test_remove_sprite_catches_unmapped(
        self, tmp_path, angry_birds_mapping, angry_birds_manifest_path
    ):
        """Remove bird_red from mapping -- validate should report UNMAPPED."""
        del angry_birds_mapping["sprites"]["bird_red"]
        mapping_path = tmp_path / "mutated.json"
        mapping_path.write_text(json.dumps(angry_birds_mapping), encoding="utf-8")

        issues = validate_mapping(angry_birds_manifest_path, mapping_path)
        unmapped = [i for i in issues if "UNMAPPED" in i and "bird_red" in i]
        assert len(unmapped) == 1, f"Expected UNMAPPED for bird_red, got: {issues}"


class TestMutationOrphan:
    def test_add_extra_sprite_catches_orphan(
        self, tmp_path, angry_birds_mapping, angry_birds_manifest_path
    ):
        """Add a sprite that is not in the manifest -- validate should report ORPHAN."""
        angry_birds_mapping["sprites"]["fake_sprite"] = {
            "unity_path": "Assets/Sprites/fake.png",
            "sprite_name": None,
            "ppu": 100,
            "material": "Sprite-Unlit-Default",
            "sorting_layer": "Default",
            "notes": "",
        }
        mapping_path = tmp_path / "mutated.json"
        mapping_path.write_text(json.dumps(angry_birds_mapping), encoding="utf-8")

        issues = validate_mapping(angry_birds_manifest_path, mapping_path)
        orphan = [i for i in issues if "ORPHAN" in i and "fake_sprite" in i]
        assert len(orphan) == 1, f"Expected ORPHAN for fake_sprite, got: {issues}"


class TestMutationEmpty:
    def test_empty_unity_path_catches_empty(
        self, tmp_path, angry_birds_mapping, angry_birds_manifest_path
    ):
        """Set slingshot unity_path to empty string -- validate should report EMPTY."""
        angry_birds_mapping["sprites"]["slingshot"]["unity_path"] = ""
        mapping_path = tmp_path / "mutated.json"
        mapping_path.write_text(json.dumps(angry_birds_mapping), encoding="utf-8")

        issues = validate_mapping(angry_birds_manifest_path, mapping_path)
        empty = [i for i in issues if "EMPTY" in i and "slingshot" in i]
        assert len(empty) == 1, f"Expected EMPTY for slingshot, got: {issues}"

    def test_empty_audio_path_catches_empty(
        self, tmp_path, angry_birds_mapping, angry_birds_manifest_path
    ):
        """Set bird_launch_sfx unity_path to empty -- validate should report EMPTY."""
        angry_birds_mapping["audio"]["bird_launch_sfx"]["unity_path"] = ""
        mapping_path = tmp_path / "mutated.json"
        mapping_path.write_text(json.dumps(angry_birds_mapping), encoding="utf-8")

        issues = validate_mapping(angry_birds_manifest_path, mapping_path)
        empty = [i for i in issues if "EMPTY" in i and "bird_launch_sfx" in i]
        assert len(empty) == 1, f"Expected EMPTY for bird_launch_sfx, got: {issues}"
