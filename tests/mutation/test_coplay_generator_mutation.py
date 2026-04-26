"""Mutation tests for coplay_generator — monkeypatch breakage to prove tests catch regressions.

Each test patches internal behavior and verifies the output changes accordingly.
"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from src.exporter.coplay_generator import generate_scene_script

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SCENE_PATH = DATA_DIR / "exports" / "angry_birds_scene.json"
MAPPING_PATH = DATA_DIR / "mappings" / "angry_birds_mapping.json"


@pytest.fixture(scope="module")
def scene_data():
    return json.loads(SCENE_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def mapping_data():
    return json.loads(MAPPING_PATH.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Mutation: Remove sprite_mappings -> output should use color fallback
# ---------------------------------------------------------------------------

class TestRemoveSpriteMappings:
    def test_no_mapping_produces_color_fallback(self, scene_data):
        """When mapping_data is None, every SpriteRenderer should use color fallback."""
        cs = generate_scene_script(scene_data, mapping_data=None, namespace="AngryBirds")
        # No sprite variable assignments should be present
        assert "sprite_bird_red" not in cs
        assert "sprite_pig_normal" not in cs
        # Color fallback lines should be present for renderers
        assert "_sr.color = new Color(" in cs

    def test_empty_sprites_dict_produces_color_fallback(self, scene_data):
        """When sprites dict is empty, asset_refs cannot be resolved -> color fallback."""
        empty_mapping = {"sprites": {}, "audio": {}}
        cs = generate_scene_script(scene_data, empty_mapping, namespace="AngryBirds")
        assert "LOAD SPRITE ASSETS" not in cs
        assert "_sr.color = new Color(" in cs


# ---------------------------------------------------------------------------
# Mutation: Remove namespace -> MonoBehaviour should not have prefix
# ---------------------------------------------------------------------------

class TestRemoveNamespace:
    def test_no_namespace_prefix(self, scene_data, mapping_data):
        """When namespace is empty, component types should not be prefixed."""
        cs = generate_scene_script(scene_data, mapping_data, namespace="")
        assert "AngryBirds." not in cs
        # But the component types themselves should still be present
        assert "AddComponent<Bird>()" in cs
        assert "AddComponent<Pig>()" in cs
        assert "AddComponent<Slingshot>()" in cs

    def test_with_namespace_has_prefix(self, scene_data, mapping_data):
        """Complementary: with namespace, prefix should appear."""
        cs = generate_scene_script(scene_data, mapping_data, namespace="AngryBirds")
        assert "AngryBirds.Bird" in cs
        assert "AngryBirds.Pig" in cs
        assert "AngryBirds.Slingshot" in cs


# ---------------------------------------------------------------------------
# Mutation: Monkeypatch _safe_var_name to return garbage -> output breaks
# ---------------------------------------------------------------------------

class TestMutateSafeVarName:
    def test_broken_var_names_change_output(self, scene_data, mapping_data):
        """If _safe_var_name is broken, the output should change significantly."""
        normal_cs = generate_scene_script(scene_data, mapping_data, namespace="AngryBirds")

        with patch(
            "src.exporter.coplay_generator._safe_var_name",
            side_effect=lambda name: "BROKEN",
        ):
            broken_cs = generate_scene_script(scene_data, mapping_data, namespace="AngryBirds")

        # The broken version should NOT match the normal version
        assert normal_cs != broken_cs
        # The broken version should have "BROKEN" everywhere instead of proper names
        assert "BROKEN" in broken_cs


# ---------------------------------------------------------------------------
# Mutation: Monkeypatch _to_camel_case to return identity -> cross-refs change
# ---------------------------------------------------------------------------

class TestMutateCamelCase:
    def test_broken_camel_case_changes_cross_refs(self, scene_data, mapping_data):
        """If _to_camel_case is identity, field names in cross-refs should be snake_case."""
        normal_cs = generate_scene_script(scene_data, mapping_data, namespace="AngryBirds")

        with patch(
            "src.exporter.coplay_generator._to_camel_case",
            side_effect=lambda s: s,  # identity — no conversion
        ):
            broken_cs = generate_scene_script(scene_data, mapping_data, namespace="AngryBirds")

        # The slingshot has bird_to_throw -> should become birdToThrow normally
        assert "birdToThrow" in normal_cs
        # With identity patch, it should remain snake_case
        assert "bird_to_throw" in broken_cs
        assert "birdToThrow" not in broken_cs
