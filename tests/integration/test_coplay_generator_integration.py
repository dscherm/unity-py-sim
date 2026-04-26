"""Integration tests for coplay_generator using the real Angry Birds scene + mapping data.

These tests load the actual exported scene and mapping JSON files and verify that
the generated C# output contains all expected Unity constructs for the Angry Birds game.
"""

import json
from pathlib import Path

import pytest

from src.exporter.coplay_generator import generate_from_files, generate_scene_script

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SCENE_PATH = DATA_DIR / "exports" / "angry_birds_scene.json"
MAPPING_PATH = DATA_DIR / "mappings" / "angry_birds_mapping.json"


@pytest.fixture(scope="module")
def angry_birds_cs():
    """Generate the full C# script from the real Angry Birds data."""
    scene = json.loads(SCENE_PATH.read_text(encoding="utf-8"))
    mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    return generate_scene_script(scene, mapping, namespace="AngryBirds")


@pytest.fixture(scope="module")
def angry_birds_cs_no_namespace():
    """Generate without namespace for comparison."""
    scene = json.loads(SCENE_PATH.read_text(encoding="utf-8"))
    mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    return generate_scene_script(scene, mapping, namespace="")


# ---------------------------------------------------------------------------
# Integration: All 5 sprite loads present
# ---------------------------------------------------------------------------

class TestSpriteLoads:
    def test_bird_red_sprite_loaded(self, angry_birds_cs):
        assert "sprite_bird_red" in angry_birds_cs
        assert "angry_birds_ocs_sprites__update__by_jared33-d5mg197.png" in angry_birds_cs

    def test_pig_normal_sprite_loaded(self, angry_birds_cs):
        assert "sprite_pig_normal" in angry_birds_cs
        assert "small_helmet_pig_sprites_by_chinzapep-d57z4bs.png" in angry_birds_cs

    def test_brick_wood_sprite_loaded(self, angry_birds_cs):
        assert "sprite_brick_wood" in angry_birds_cs
        assert "INGAME_BLOCKS_WOOD_1.png" in angry_birds_cs

    def test_slingshot_sprite_loaded(self, angry_birds_cs):
        assert "sprite_slingshot" in angry_birds_cs
        assert "slingshot.png" in angry_birds_cs

    def test_ground_grass_sprite_loaded(self, angry_birds_cs):
        assert "sprite_ground_grass" in angry_birds_cs
        assert "forest-2.png" in angry_birds_cs


# ---------------------------------------------------------------------------
# Integration: Namespace-prefixed MonoBehaviour components
# ---------------------------------------------------------------------------

class TestNamespacedComponents:
    def test_slingshot_has_namespace(self, angry_birds_cs):
        assert "AngryBirds.Slingshot" in angry_birds_cs

    def test_bird_has_namespace(self, angry_birds_cs):
        assert "AngryBirds.Bird" in angry_birds_cs

    def test_pig_has_namespace(self, angry_birds_cs):
        assert "AngryBirds.Pig" in angry_birds_cs

    def test_brick_has_namespace(self, angry_birds_cs):
        assert "AngryBirds.Brick" in angry_birds_cs

    def test_destroyer_has_namespace(self, angry_birds_cs):
        assert "AngryBirds.Destroyer" in angry_birds_cs

    def test_game_manager_has_namespace(self, angry_birds_cs):
        assert "AngryBirds.GameManager" in angry_birds_cs

    def test_no_namespace_when_empty(self, angry_birds_cs_no_namespace):
        assert "AngryBirds." not in angry_birds_cs_no_namespace


# ---------------------------------------------------------------------------
# Integration: Tag creation
# ---------------------------------------------------------------------------

class TestTagCreation:
    def test_bird_tag(self, angry_birds_cs):
        assert '_EnsureTag(tagsProp, "Bird")' in angry_birds_cs

    def test_brick_tag(self, angry_birds_cs):
        assert '_EnsureTag(tagsProp, "Brick")' in angry_birds_cs

    def test_ground_tag(self, angry_birds_cs):
        assert '_EnsureTag(tagsProp, "Ground")' in angry_birds_cs

    def test_pig_tag(self, angry_birds_cs):
        assert '_EnsureTag(tagsProp, "Pig")' in angry_birds_cs


# ---------------------------------------------------------------------------
# Integration: Rigidbody2D static for Ground and Destroyers
# ---------------------------------------------------------------------------

class TestRigidbodyTypes:
    def test_static_bodies_present(self, angry_birds_cs):
        assert "RigidbodyType2D.Static" in angry_birds_cs

    def test_ground_is_static(self, angry_birds_cs):
        # Ground's variable should have a Rigidbody2D set to Static
        lines = angry_birds_cs.split("\n")
        # Find the Ground section and verify Static follows
        ground_section = False
        found_static = False
        for line in lines:
            if "--- Ground ---" in line or "go_Ground" in line:
                ground_section = True
            if ground_section and "RigidbodyType2D.Static" in line:
                found_static = True
                break
            if ground_section and "--- " in line and "Ground" not in line:
                break
        assert found_static, "Ground should have RigidbodyType2D.Static"


# ---------------------------------------------------------------------------
# Integration: isTrigger for Destroyers
# ---------------------------------------------------------------------------

class TestDestroyerTriggers:
    def test_destroyer_bottom_trigger(self, angry_birds_cs):
        assert "go_Destroyer_Bottom_bc.isTrigger = true" in angry_birds_cs

    def test_destroyer_left_trigger(self, angry_birds_cs):
        assert "go_Destroyer_Left_bc.isTrigger = true" in angry_birds_cs

    def test_destroyer_right_trigger(self, angry_birds_cs):
        assert "go_Destroyer_Right_bc.isTrigger = true" in angry_birds_cs


# ---------------------------------------------------------------------------
# Integration: generate_from_files produces non-empty output
# ---------------------------------------------------------------------------

class TestGenerateFromFiles:
    def test_from_files_produces_output(self):
        cs = generate_from_files(str(SCENE_PATH), str(MAPPING_PATH), namespace="AngryBirds")
        assert len(cs) > 100
        assert "using UnityEngine;" in cs
        assert "GeneratedSceneSetup" in cs

    def test_from_files_without_mapping(self):
        cs = generate_from_files(str(SCENE_PATH), namespace="AngryBirds")
        assert len(cs) > 100
        # Without mapping, no sprite loads should be present
        assert "LOAD SPRITE ASSETS" not in cs
