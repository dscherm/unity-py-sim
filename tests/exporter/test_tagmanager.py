"""Tests for TagManager.asset generation in project scaffolder.

Validates that scaffold_project() generates a proper Unity YAML TagManager.asset
with correct tags, layers, and Unity YAML headers.
"""

from __future__ import annotations


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
                if stripped == '- ""' or stripped == "-":
                    layer_entries.append("")
                elif stripped.startswith("- "):
                    layer_entries.append(stripped[2:])
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
                if stripped == '- ""' or stripped == "-":
                    # Empty layer: `- ""` (Unity 6 canonical, empty-string scalar)
                    # or bare `-` (legacy null scalar).  Both mean "empty slot".
                    layer_entries.append("")
                elif stripped.startswith("- "):
                    layer_entries.append(stripped[2:])
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


# ---------------------------------------------------------------------------
# Unity 6 canonical format (coplay_generator_gaps.md gap 8)
# ---------------------------------------------------------------------------


def _yaml_body(content: str) -> str:
    """Strip the %YAML / %TAG / --- directives so yaml.safe_load can parse."""
    return "\n".join(
        line for line in content.split("\n")
        if not line.startswith("%") and not line.startswith("---")
    )


class TestTagManagerUnity6Format:
    """Gap 8: TagManager.asset must be parseable and use Unity 6 canonical scalars.

    The original bug (data/lessons/coplay_generator_gaps.md gap 8): Unity 6
    rejected the file with `Parser Failure at line N: Expect ':' between key
    and value within mapping` because empty layer slots were emitted as bare
    `-` (null scalar) instead of `- ""` (empty-string scalar).
    """

    def test_tagmanager_parses_as_yaml(self, tmp_path, minimal_cs):
        import yaml
        scaffold_project("test", tmp_path, cs_files=minimal_cs,
                         tags=["Wall"], layers={"Wall": 6})
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        data = yaml.safe_load(_yaml_body(content))
        assert isinstance(data, dict) and "TagManager" in data
        tm = data["TagManager"]
        assert tm.get("serializedVersion") == 2
        assert isinstance(tm.get("tags"), list)
        assert isinstance(tm.get("layers"), list)
        # Sorting layers key must be the Unity 6 m_ prefix
        assert "m_SortingLayers" in tm

    def test_layers_array_has_32_entries(self, tmp_path, minimal_cs):
        import yaml
        scaffold_project("test", tmp_path, cs_files=minimal_cs,
                         tags=[], layers={"Wall": 6})
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        data = yaml.safe_load(_yaml_body(content))
        layers_arr = data["TagManager"]["layers"]
        assert len(layers_arr) == 32, f"Unity expects 32 layer slots, got {len(layers_arr)}"

    def test_empty_layer_slots_are_empty_string_not_null(self, tmp_path, minimal_cs):
        """Empty layer slots must serialize as `- ""` (empty-string scalar),
        never as bare `-` (null scalar).  The bare form triggers a Unity 6
        parser failure: `Expect ':' between key and value within mapping`."""
        scaffold_project("test", tmp_path, cs_files=minimal_cs,
                         tags=[], layers={"Custom": 10})
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        # Scan the raw text of the layers: section.  No standalone `  -` line
        # (trailing whitespace stripped) may appear between `layers:` and the
        # next top-level key.
        in_layers = False
        bare_dash_count = 0
        for line in content.split("\n"):
            stripped_right = line.rstrip()
            inner = stripped_right.strip()
            if inner == "layers:":
                in_layers = True
                continue
            if in_layers:
                # Exit on next section header (indent-0 token ending in `:`)
                if inner.endswith(":") and not inner.startswith("-"):
                    break
                if inner == "-":
                    bare_dash_count += 1
        assert bare_dash_count == 0, (
            f"Found {bare_dash_count} bare `-` null-scalar entries in layers: section. "
            "Unity 6 parser rejects these; emit `- \"\"` (empty-string scalar) instead."
        )

    def test_empty_layer_slots_parse_as_empty_string(self, tmp_path, minimal_cs):
        """Under yaml.safe_load, the empty layer slots at reserved indices
        (3, 6, 7 when no custom layer assigned) must produce empty-string
        values, not None (Unity 6 canonical)."""
        import yaml
        scaffold_project("test", tmp_path, cs_files=minimal_cs,
                         tags=[], layers={})
        content = (tmp_path / "ProjectSettings" / "TagManager.asset").read_text(encoding="utf-8")
        data = yaml.safe_load(_yaml_body(content))
        layers_arr = data["TagManager"]["layers"]
        # Reserved index 3 must be empty string, not None
        assert layers_arr[3] == "", (
            f"Layer 3 should be empty-string scalar, got {layers_arr[3]!r}"
        )
