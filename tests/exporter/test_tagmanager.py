"""Tests for TagManager.asset generation in project scaffolder.

Validates that scaffold_project() generates a proper Unity YAML TagManager.asset
with correct tags, layers, and Unity YAML headers.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.exporter.project_scaffolder import scaffold_project


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_cs() -> dict[str, str]:
    return {
        "GameManager.cs": "using UnityEngine;\npublic class GameManager : MonoBehaviour { }\n",
    }


# Default Unity tags that must always be present
DEFAULT_UNITY_TAGS = [
    "Untagged",
    "Respawn",
    "Finish",
    "EditorOnly",
    "MainCamera",
    "Player",
    "GameController",
]

# Builtin Unity layers (indices 0-5)
BUILTIN_LAYERS = {
    0: "Default",
    1: "TransparentFX",
    2: "Ignore Raycast",
    3: "",    # reserved
    4: "Water",
    5: "UI",
}


# ---------------------------------------------------------------------------
# YAML Header tests
# ---------------------------------------------------------------------------

class TestTagManagerYAMLHeader:
    """TagManager.asset must have proper Unity YAML headers."""

    def test_starts_with_yaml_header(self, tmp_path, minimal_cs):
        scaffold_project("test", tmp_path, cs_files=minimal_cs, tags=["Wall"])
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        assert content.startswith("%YAML 1.1")

    def test_has_unity_tag_directive(self, tmp_path, minimal_cs):
        scaffold_project("test", tmp_path, cs_files=minimal_cs, tags=["Wall"])
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        assert "%TAG !u! tag:unity3d.com,2011:" in content

    def test_has_tag_manager_root(self, tmp_path, minimal_cs):
        scaffold_project("test", tmp_path, cs_files=minimal_cs, tags=["Wall"])
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        assert "TagManager:" in content


# ---------------------------------------------------------------------------
# Tags tests
# ---------------------------------------------------------------------------

class TestTagManagerTags:
    """Tags array must contain default Unity tags plus custom tags."""

    def test_custom_tags_present(self, tmp_path, minimal_cs):
        scaffold_project("test", tmp_path, cs_files=minimal_cs, tags=["Wall", "Pellet"])
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        assert "Wall" in content
        assert "Pellet" in content

    def test_default_tags_always_present(self, tmp_path, minimal_cs):
        scaffold_project("test", tmp_path, cs_files=minimal_cs, tags=["Wall"])
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        for tag in DEFAULT_UNITY_TAGS:
            assert tag in content, f"Default Unity tag '{tag}' must be present"

    def test_tags_in_tags_section(self, tmp_path, minimal_cs):
        """Custom tags must appear in the tags: array section."""
        scaffold_project("test", tmp_path, cs_files=minimal_cs, tags=["Wall", "Pellet"])
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        # Find the tags: section and verify custom tags are listed there
        lines = content.split("\n")
        in_tags = False
        found_tags = []
        for line in lines:
            stripped = line.strip()
            if stripped == "tags:":
                in_tags = True
                continue
            if in_tags:
                if stripped.startswith("- "):
                    found_tags.append(stripped[2:])
                else:
                    break
        assert "Wall" in found_tags, "Wall must be in tags array"
        assert "Pellet" in found_tags, "Pellet must be in tags array"


# ---------------------------------------------------------------------------
# Layers tests
# ---------------------------------------------------------------------------

class TestTagManagerLayers:
    """Layers must include builtin Unity layers and custom layers at correct indices."""

    def test_custom_layers_at_correct_indices(self, tmp_path, minimal_cs):
        layers = {"Wall": 6, "Pellet": 7, "Ghost": 8}
        scaffold_project("test", tmp_path, cs_files=minimal_cs, tags=["Wall"], layers=layers)
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        # Parse the layers section — layers are indexed entries
        # Layer 6 should be Wall, 7 should be Pellet, 8 should be Ghost
        lines = content.split("\n")
        in_layers = False
        layer_entries = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("layers:"):
                in_layers = True
                continue
            if in_layers:
                if stripped.startswith("- "):
                    layer_entries.append(stripped[2:])
                elif stripped == "-":
                    # Empty layer entry (e.g. "  -" with no value)
                    layer_entries.append("")
                else:
                    break
        # Indices 6, 7, 8 should map to our custom layers
        assert len(layer_entries) > 8, f"Expected at least 9 layer entries, got {len(layer_entries)}"
        assert layer_entries[6] == "Wall", f"Layer 6 should be 'Wall', got '{layer_entries[6]}'"
        assert layer_entries[7] == "Pellet", f"Layer 7 should be 'Pellet', got '{layer_entries[7]}'"
        assert layer_entries[8] == "Ghost", f"Layer 8 should be 'Ghost', got '{layer_entries[8]}'"

    def test_builtin_layers_present(self, tmp_path, minimal_cs):
        layers = {"Wall": 6}
        scaffold_project("test", tmp_path, cs_files=minimal_cs, tags=["Wall"], layers=layers)
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        # Builtin layers: Default (0), TransparentFX (1), Ignore Raycast (2), Water (4), UI (5)
        assert "Default" in content
        assert "TransparentFX" in content
        assert "Ignore Raycast" in content
        assert "Water" in content
        assert "UI" in content

    def test_reserved_layers_empty(self, tmp_path, minimal_cs):
        """Layers 3 and 6-7 (when not custom) should be empty strings."""
        layers = {"Custom": 10}
        scaffold_project("test", tmp_path, cs_files=minimal_cs, tags=[], layers=layers)
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        lines = content.split("\n")
        in_layers = False
        layer_entries = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("layers:"):
                in_layers = True
                continue
            if in_layers:
                if stripped.startswith("- "):
                    layer_entries.append(stripped[2:])
                elif stripped == "-":
                    layer_entries.append("")
                else:
                    break
        # Layer 3 is reserved in Unity — should be empty
        assert layer_entries[3] == "", f"Layer 3 (reserved) should be empty, got '{layer_entries[3]}'"


# ---------------------------------------------------------------------------
# Sorting layers tests
# ---------------------------------------------------------------------------

class TestTagManagerSortingLayers:
    """TagManager must include sorting layers section."""

    def test_has_sorting_layers_section(self, tmp_path, minimal_cs):
        scaffold_project("test", tmp_path, cs_files=minimal_cs, tags=["Wall"])
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        assert "m_SortingLayers:" in content or "sortingLayers:" in content

    def test_default_sorting_layer_present(self, tmp_path, minimal_cs):
        scaffold_project("test", tmp_path, cs_files=minimal_cs, tags=["Wall"])
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        # Default sorting layer should have name "Default"
        assert "Default" in content


# ---------------------------------------------------------------------------
# Empty/defaults tests
# ---------------------------------------------------------------------------

class TestTagManagerDefaults:
    """Even with empty tags/layers, TagManager must be valid."""

    def test_empty_tags_generates_valid_file(self, tmp_path, minimal_cs):
        """Passing empty tags list should still generate TagManager with defaults."""
        scaffold_project("test", tmp_path, cs_files=minimal_cs, tags=[], layers={})
        tm = tmp_path / "ProjectSettings" / "TagManager.asset"
        assert tm.is_file(), "TagManager.asset should be created even with empty tags/layers"
        content = tm.read_text(encoding="utf-8")
        assert content.startswith("%YAML 1.1")
        assert "TagManager:" in content

    def test_none_tags_none_layers_generates_file(self, tmp_path, minimal_cs):
        """With layers=None and tags=None, TagManager should still be generated."""
        scaffold_project("test", tmp_path, cs_files=minimal_cs, tags=None, layers=None)
        tm = tmp_path / "ProjectSettings" / "TagManager.asset"
        # Should still generate with defaults
        assert tm.is_file(), "TagManager.asset should be created with defaults"

    def test_only_layers_no_tags(self, tmp_path, minimal_cs):
        """Layers without tags should still produce valid file."""
        scaffold_project("test", tmp_path, cs_files=minimal_cs, layers={"Wall": 6})
        tm = tmp_path / "ProjectSettings" / "TagManager.asset"
        assert tm.is_file()
        content = tm.read_text(encoding="utf-8")
        assert "Wall" in content
        for tag in DEFAULT_UNITY_TAGS:
            assert tag in content
