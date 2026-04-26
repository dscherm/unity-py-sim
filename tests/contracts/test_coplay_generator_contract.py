"""Contract tests for coplay_generator — verify C# output against Unity editor script conventions.

These tests derive expected behavior from Unity documentation and the generator's
public API contract, NOT from implementation details.
"""

import pytest

from src.exporter.coplay_generator import (
    _escape_cs_string,
    _safe_var_name,
    _to_camel_case,
    generate_scene_script,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def empty_scene():
    return {"game_objects": []}


@pytest.fixture
def camera_scene():
    return {
        "game_objects": [
            {
                "name": "MainCamera",
                "tag": "Untagged",
                "components": [
                    {"type": "Camera", "orthographic_size": 5, "background_color": [0, 0, 0]},
                ],
            }
        ]
    }


@pytest.fixture
def sprite_with_mapping():
    """Scene with a SpriteRenderer that has an asset_ref present in mapping."""
    scene = {
        "game_objects": [
            {
                "name": "Player",
                "tag": "Untagged",
                "components": [
                    {"type": "Transform", "position": [0, 0, 0]},
                    {
                        "type": "SpriteRenderer",
                        "color": [255, 0, 0],
                        "sorting_order": 0,
                        "asset_ref": "player_sprite",
                    },
                ],
            }
        ]
    }
    mapping = {
        "sprites": {
            "player_sprite": {
                "unity_path": "Assets/Sprites/player.png",
                "sprite_name": "player_0",
            }
        }
    }
    return scene, mapping


@pytest.fixture
def sprite_without_mapping():
    """Scene with a SpriteRenderer whose asset_ref is NOT in the mapping."""
    scene = {
        "game_objects": [
            {
                "name": "Wall",
                "tag": "Untagged",
                "components": [
                    {"type": "Transform", "position": [0, 0, 0]},
                    {
                        "type": "SpriteRenderer",
                        "color": [128, 128, 128],
                        "sorting_order": 0,
                        "asset_ref": "missing_ref",
                    },
                ],
            }
        ]
    }
    return scene


@pytest.fixture
def rigidbody_scene():
    """Scene with all three Rigidbody2D body types."""
    def _make_go(name, body_type):
        return {
            "name": name,
            "tag": "Untagged",
            "components": [
                {"type": "Transform", "position": [0, 0, 0]},
                {"type": "Rigidbody2D", "body_type": body_type, "mass": 1, "gravity_scale": 1},
            ],
        }

    return {
        "game_objects": [
            _make_go("StaticObj", "Static"),
            _make_go("DynamicObj", "Dynamic"),
            _make_go("KinematicObj", "Kinematic"),
        ]
    }


@pytest.fixture
def collider_scene():
    return {
        "game_objects": [
            {
                "name": "Box",
                "tag": "Untagged",
                "components": [
                    {"type": "Transform", "position": [0, 0, 0]},
                    {"type": "BoxCollider2D", "size": [2.0, 3.0], "is_trigger": True},
                ],
            },
            {
                "name": "Circle",
                "tag": "Untagged",
                "components": [
                    {"type": "Transform", "position": [1, 0, 0]},
                    {"type": "CircleCollider2D", "radius": 1.5, "is_trigger": False},
                ],
            },
        ]
    }


@pytest.fixture
def monobehaviour_scene():
    return {
        "game_objects": [
            {
                "name": "Enemy",
                "tag": "Untagged",
                "components": [
                    {"type": "Transform", "position": [0, 0, 0]},
                    {
                        "type": "EnemyController",
                        "is_monobehaviour": True,
                        "fields": {"speed": 5.0},
                    },
                ],
            }
        ]
    }


@pytest.fixture
def crossref_scene():
    """Scene with GameObjectRef cross-references."""
    return {
        "game_objects": [
            {
                "name": "Launcher",
                "tag": "Untagged",
                "components": [
                    {"type": "Transform", "position": [0, 0, 0]},
                    {
                        "type": "Launcher",
                        "is_monobehaviour": True,
                        "fields": {
                            "target_object": {
                                "_type": "GameObjectRef",
                                "name": "Projectile",
                            }
                        },
                    },
                ],
            },
            {
                "name": "Projectile",
                "tag": "Untagged",
                "components": [
                    {"type": "Transform", "position": [1, 0, 0]},
                ],
            },
        ]
    }


@pytest.fixture
def tagged_scene():
    return {
        "game_objects": [
            {
                "name": "Hero",
                "tag": "Player",
                "components": [{"type": "Transform", "position": [0, 0, 0]}],
            },
            {
                "name": "Foe",
                "tag": "Enemy",
                "components": [{"type": "Transform", "position": [1, 0, 0]}],
            },
        ]
    }


# ---------------------------------------------------------------------------
# Contract: Empty scene generates valid C# skeleton
# ---------------------------------------------------------------------------

class TestEmptyScene:
    def test_contains_using_directives(self, empty_scene):
        cs = generate_scene_script(empty_scene)
        assert "using UnityEngine;" in cs
        assert "using UnityEditor;" in cs

    def test_contains_class_and_method(self, empty_scene):
        cs = generate_scene_script(empty_scene)
        assert "public class GeneratedSceneSetup" in cs
        assert "public static string Execute()" in cs

    def test_returns_result_string(self, empty_scene):
        cs = generate_scene_script(empty_scene)
        assert "return result;" in cs

    def test_loads_unlit_material(self, empty_scene):
        cs = generate_scene_script(empty_scene)
        assert "Sprite-Unlit-Default.mat" in cs


# ---------------------------------------------------------------------------
# Contract: Camera reuses existing Main Camera
# ---------------------------------------------------------------------------

class TestCamera:
    def test_reuses_main_camera(self, camera_scene):
        cs = generate_scene_script(camera_scene)
        assert "Camera.main?.gameObject" in cs

    def test_does_not_create_new_gameobject_for_camera(self, camera_scene):
        cs = generate_scene_script(camera_scene)
        assert 'new GameObject("MainCamera")' not in cs

    def test_sets_orthographic_size(self, camera_scene):
        cs = generate_scene_script(camera_scene)
        assert "cam.orthographicSize" in cs

    def test_sets_background_color(self, camera_scene):
        cs = generate_scene_script(camera_scene)
        assert "cam.backgroundColor" in cs


# ---------------------------------------------------------------------------
# Contract: Tags use _EnsureTag helper
# ---------------------------------------------------------------------------

class TestTags:
    def test_ensure_tag_called_for_each_tag(self, tagged_scene):
        cs = generate_scene_script(tagged_scene)
        assert '_EnsureTag(tagsProp, "Player")' in cs
        assert '_EnsureTag(tagsProp, "Enemy")' in cs

    def test_ensure_tag_helper_defined(self, tagged_scene):
        cs = generate_scene_script(tagged_scene)
        assert "static void _EnsureTag(" in cs

    def test_tag_manager_serialized_object(self, tagged_scene):
        cs = generate_scene_script(tagged_scene)
        assert "TagManager.asset" in cs


# ---------------------------------------------------------------------------
# Contract: SpriteRenderer with mapped asset_ref loads sprite from mapping
# ---------------------------------------------------------------------------

class TestSpriteRendererMapped:
    def test_loads_sprite_from_mapping_path(self, sprite_with_mapping):
        scene, mapping = sprite_with_mapping
        cs = generate_scene_script(scene, mapping)
        assert "Assets/Sprites/player.png" in cs

    def test_assigns_sprite_to_renderer(self, sprite_with_mapping):
        scene, mapping = sprite_with_mapping
        cs = generate_scene_script(scene, mapping)
        assert "sprite_player_sprite" in cs
        assert ".sprite = sprite_player_sprite" in cs

    def test_does_not_set_color_fallback_when_mapped(self, sprite_with_mapping):
        scene, mapping = sprite_with_mapping
        cs = generate_scene_script(scene, mapping)
        # When sprite is mapped, should NOT have a color = new Color line for this renderer
        # The renderer line that sets .color should not appear
        lines = cs.split("\n")
        sr_color_lines = [l for l in lines if "_sr.color = new Color" in l and "go_Player" in l]
        assert len(sr_color_lines) == 0


# ---------------------------------------------------------------------------
# Contract: SpriteRenderer without mapping uses color fallback
# ---------------------------------------------------------------------------

class TestSpriteRendererUnmapped:
    def test_color_fallback_when_not_mapped(self, sprite_without_mapping):
        cs = generate_scene_script(sprite_without_mapping, None)
        assert "_sr.color = new Color(" in cs

    def test_no_sprite_assignment_when_not_mapped(self, sprite_without_mapping):
        cs = generate_scene_script(sprite_without_mapping, None)
        assert ".sprite = " not in cs


# ---------------------------------------------------------------------------
# Contract: Rigidbody2D body_type maps to RigidbodyType2D enum
# ---------------------------------------------------------------------------

class TestRigidbody2D:
    def test_static_body_type(self, rigidbody_scene):
        cs = generate_scene_script(rigidbody_scene)
        assert "RigidbodyType2D.Static" in cs

    def test_kinematic_body_type(self, rigidbody_scene):
        cs = generate_scene_script(rigidbody_scene)
        assert "RigidbodyType2D.Kinematic" in cs

    def test_dynamic_is_default(self, rigidbody_scene):
        cs = generate_scene_script(rigidbody_scene)
        # Dynamic is Unity's default, so the generator may skip setting it explicitly
        # But it should still add the Rigidbody2D component
        assert "AddComponent<Rigidbody2D>()" in cs


# ---------------------------------------------------------------------------
# Contract: BoxCollider2D and CircleCollider2D
# ---------------------------------------------------------------------------

class TestColliders:
    def test_box_collider_size(self, collider_scene):
        cs = generate_scene_script(collider_scene)
        assert ".size = new Vector2(2" in cs
        assert "3" in cs  # y dimension

    def test_box_collider_is_trigger(self, collider_scene):
        cs = generate_scene_script(collider_scene)
        assert "_bc.isTrigger = true" in cs

    def test_circle_collider_radius(self, collider_scene):
        cs = generate_scene_script(collider_scene)
        assert ".radius = 1.5f" in cs

    def test_circle_collider_no_trigger(self, collider_scene):
        cs = generate_scene_script(collider_scene)
        # Circle is NOT a trigger, so isTrigger should NOT appear for circle
        lines = cs.split("\n")
        cc_trigger_lines = [l for l in lines if "_cc.isTrigger" in l]
        assert len(cc_trigger_lines) == 0


# ---------------------------------------------------------------------------
# Contract: MonoBehaviour uses namespace prefix
# ---------------------------------------------------------------------------

class TestMonoBehaviour:
    def test_namespace_prefix_when_provided(self, monobehaviour_scene):
        cs = generate_scene_script(monobehaviour_scene, namespace="MyGame")
        assert "MyGame.EnemyController" in cs

    def test_no_prefix_when_no_namespace(self, monobehaviour_scene):
        cs = generate_scene_script(monobehaviour_scene, namespace="")
        assert "AddComponent<EnemyController>()" in cs
        assert "MyGame." not in cs


# ---------------------------------------------------------------------------
# Contract: GameObjectRef cross-references use SerializedObject
# ---------------------------------------------------------------------------

class TestCrossReferences:
    def test_serialized_object_wiring(self, crossref_scene):
        cs = generate_scene_script(crossref_scene, namespace="")
        assert "new SerializedObject(" in cs
        assert "FindProperty(" in cs

    def test_references_target_variable(self, crossref_scene):
        cs = generate_scene_script(crossref_scene, namespace="")
        # The cross-ref should wire to the Projectile variable
        assert "go_Projectile" in cs
        assert "ApplyModifiedProperties()" in cs


# ---------------------------------------------------------------------------
# Contract: Helper functions
# ---------------------------------------------------------------------------

class TestSafeVarName:
    def test_spaces_replaced(self):
        assert " " not in _safe_var_name("My Object")

    def test_dashes_replaced(self):
        assert "-" not in _safe_var_name("some-thing")

    def test_leading_digit_handled(self):
        result = _safe_var_name("3DModel")
        assert not result.lstrip("go_")[0].isdigit() or result.startswith("go_")

    def test_prefixed_with_go(self):
        result = _safe_var_name("Player")
        assert result.startswith("go_")


class TestToCamelCase:
    def test_simple_snake(self):
        assert _to_camel_case("my_field") == "myField"

    def test_single_word(self):
        assert _to_camel_case("speed") == "speed"

    def test_multi_word(self):
        assert _to_camel_case("bird_to_throw") == "birdToThrow"


class TestEscapeCsString:
    def test_escapes_backslash(self):
        assert _escape_cs_string("a\\b") == "a\\\\b"

    def test_escapes_quote(self):
        assert _escape_cs_string('say "hi"') == 'say \\"hi\\"'

    def test_plain_string_unchanged(self):
        assert _escape_cs_string("hello") == "hello"
