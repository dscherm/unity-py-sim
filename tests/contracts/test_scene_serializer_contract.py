"""Contract tests for scene_serializer — derived from Unity scene export expectations.

These tests verify that serialize_scene() produces the expected JSON-compatible
structure for each component type, independent of implementation details.
"""

import math

import pytest

from src.engine.core import _clear_registry, GameObject, MonoBehaviour
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D, PhysicsMaterial2D
from src.engine.rendering.camera import Camera
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.audio import AudioSource, AudioListener
from src.engine.math.vector import Vector2, Vector3
from src.engine.transform import Transform

from src.exporter.scene_serializer import (
    serialize_scene,
    serialize_from_setup,
    _serialize_component,
    _sanitize_for_json,
)


@pytest.fixture(autouse=True)
def clean_scene():
    """Reset all global state before and after each test."""
    _clear_registry()
    LifecycleManager._instance = None
    PhysicsManager._instance = None
    Camera._reset_main()
    AudioListener.reset()
    yield
    _clear_registry()
    LifecycleManager._instance = None
    PhysicsManager._instance = None
    Camera._reset_main()
    AudioListener.reset()


class TestEmptyScene:
    def test_empty_scene_structure(self):
        """An empty scene must serialize to version 1 with an empty game_objects list."""
        result = serialize_scene()
        assert result == {"version": 1, "game_objects": []}

    def test_version_is_integer_one(self):
        result = serialize_scene()
        assert result["version"] == 1
        assert isinstance(result["version"], int)

    def test_game_objects_is_list(self):
        result = serialize_scene()
        assert isinstance(result["game_objects"], list)


class TestGameObjectBasics:
    def test_bare_gameobject_serializes_name_tag_layer_active(self):
        """A GameObject with no manually added components should serialize its metadata."""
        go = GameObject("Player", tag="Hero")
        go.layer = 5
        result = serialize_scene()

        go_data = result["game_objects"][0]
        assert go_data["name"] == "Player"
        assert go_data["tag"] == "Hero"
        assert go_data["layer"] == 5
        assert go_data["active"] is True

    def test_inactive_gameobject_serializes_active_false(self):
        go = GameObject("Disabled")
        go.active = False
        result = serialize_scene()
        assert result["game_objects"][0]["active"] is False

    def test_default_tag_is_untagged(self):
        go = GameObject("Something")
        result = serialize_scene()
        assert result["game_objects"][0]["tag"] == "Untagged"

    def test_default_layer_is_zero(self):
        go = GameObject("Something")
        result = serialize_scene()
        assert result["game_objects"][0]["layer"] == 0


class TestTransformSerialization:
    def test_transform_position(self):
        go = GameObject("Obj")
        go.transform.position = Vector3(1.5, 2.5, 3.5)
        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        tf = next(c for c in comps if c["type"] == "Transform")
        assert tf["position"] == [1.5, 2.5, 3.5]

    def test_transform_rotation_is_quaternion(self):
        go = GameObject("Obj")
        # Access transform to trigger lazy creation
        go.transform.position = Vector3(0, 0, 0)
        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        tf = next(c for c in comps if c["type"] == "Transform")
        # Rotation should be a 4-element list [x, y, z, w]
        assert len(tf["rotation"]) == 4

    def test_transform_local_scale(self):
        go = GameObject("Obj")
        go.transform.local_scale = Vector3(2.0, 3.0, 1.0)
        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        tf = next(c for c in comps if c["type"] == "Transform")
        assert tf["local_scale"] == [2.0, 3.0, 1.0]

    def test_transform_parent_none_when_no_parent(self):
        go = GameObject("Root")
        # Access transform to trigger lazy creation
        go.transform.position = Vector3(0, 0, 0)
        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        tf = next(c for c in comps if c["type"] == "Transform")
        assert tf["parent"] is None

    def test_transform_parent_name_when_parented(self):
        parent = GameObject("Parent")
        child = GameObject("Child")
        child.transform.set_parent(parent.transform)
        result = serialize_scene()
        # Find the child GO data
        child_data = next(g for g in result["game_objects"] if g["name"] == "Child")
        tf = next(c for c in child_data["components"] if c["type"] == "Transform")
        assert tf["parent"] == "Parent"


class TestSpriteRendererSerialization:
    def test_sprite_renderer_fields(self):
        go = GameObject("Sprite")
        sr = go.add_component(SpriteRenderer)
        sr.color = (255, 0, 128)
        sr.size = Vector2(2.0, 3.0)
        sr.sorting_order = 5
        sr.asset_ref = "my_sprite"

        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        sr_data = next(c for c in comps if c["type"] == "SpriteRenderer")

        assert sr_data["color"] == [255, 0, 128]
        assert sr_data["size"] == [2.0, 3.0]
        assert sr_data["sorting_order"] == 5
        assert sr_data["asset_ref"] == "my_sprite"

    def test_sprite_renderer_null_asset_ref(self):
        go = GameObject("Sprite")
        sr = go.add_component(SpriteRenderer)
        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        sr_data = next(c for c in comps if c["type"] == "SpriteRenderer")
        assert sr_data["asset_ref"] is None


class TestCameraSerialization:
    def test_camera_fields(self):
        go = GameObject("Cam")
        cam = go.add_component(Camera)
        cam.orthographic_size = 10.0
        cam.background_color = (30, 40, 50)

        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        cam_data = next(c for c in comps if c["type"] == "Camera")
        assert cam_data["orthographic_size"] == 10.0
        assert cam_data["background_color"] == [30, 40, 50]


class TestAudioSourceSerialization:
    def test_audio_source_fields(self):
        go = GameObject("Audio")
        src = go.add_component(AudioSource)
        src.clip_ref = "explosion_sfx"
        src.volume = 0.8
        src.pitch = 1.2
        src.loop = True

        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        audio_data = next(c for c in comps if c["type"] == "AudioSource")
        assert audio_data["clip_ref"] == "explosion_sfx"
        assert audio_data["volume"] == pytest.approx(0.8)
        assert audio_data["pitch"] == pytest.approx(1.2)
        assert audio_data["loop"] is True

    def test_audio_listener_serializes(self):
        go = GameObject("Listener")
        go.add_component(AudioListener)
        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        al_data = next(c for c in comps if c["type"] == "AudioListener")
        assert al_data["type"] == "AudioListener"


class TestRigidbody2DSerialization:
    def test_dynamic_body_type(self):
        go = GameObject("Dyn")
        rb = go.add_component(Rigidbody2D)
        rb.mass = 2.5
        rb.gravity_scale = 0.5

        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        rb_data = next(c for c in comps if c["type"] == "Rigidbody2D")
        assert rb_data["body_type"] == "Dynamic"
        assert rb_data["mass"] == pytest.approx(2.5)
        assert rb_data["gravity_scale"] == pytest.approx(0.5)

    def test_static_body_type(self):
        go = GameObject("Static")
        rb = go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.STATIC

        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        rb_data = next(c for c in comps if c["type"] == "Rigidbody2D")
        assert rb_data["body_type"] == "Static"

    def test_kinematic_body_type(self):
        go = GameObject("Kin")
        rb = go.add_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.KINEMATIC

        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        rb_data = next(c for c in comps if c["type"] == "Rigidbody2D")
        assert rb_data["body_type"] == "Kinematic"


class TestBoxCollider2DSerialization:
    def test_box_collider_fields(self):
        go = GameObject("Box")
        go.add_component(Rigidbody2D)  # collider needs rigidbody
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(3.0, 4.0)
        col.is_trigger = True
        col.shared_material = PhysicsMaterial2D(bounciness=0.7, friction=0.3)
        col.build()

        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        col_data = next(c for c in comps if c["type"] == "BoxCollider2D")
        assert col_data["size"] == [3.0, 4.0]
        assert col_data["is_trigger"] is True
        assert col_data["physics_material"]["bounciness"] == pytest.approx(0.7)
        assert col_data["physics_material"]["friction"] == pytest.approx(0.3)

    def test_box_collider_no_material(self):
        go = GameObject("Box")
        go.add_component(Rigidbody2D)
        col = go.add_component(BoxCollider2D)
        col.size = Vector2(1, 1)
        col.build()

        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        col_data = next(c for c in comps if c["type"] == "BoxCollider2D")
        assert "physics_material" not in col_data


class TestCircleCollider2DSerialization:
    def test_circle_collider_fields(self):
        go = GameObject("Circle")
        go.add_component(Rigidbody2D)
        col = go.add_component(CircleCollider2D)
        col.radius = 1.5
        col.is_trigger = False
        col.shared_material = PhysicsMaterial2D(bounciness=0.9, friction=0.1)
        col.build()

        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        col_data = next(c for c in comps if c["type"] == "CircleCollider2D")
        assert col_data["radius"] == pytest.approx(1.5)
        assert col_data["is_trigger"] is False
        assert col_data["physics_material"]["bounciness"] == pytest.approx(0.9)

    def test_circle_collider_no_material(self):
        go = GameObject("Circle")
        go.add_component(Rigidbody2D)
        col = go.add_component(CircleCollider2D)
        col.radius = 0.5
        col.build()

        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        col_data = next(c for c in comps if c["type"] == "CircleCollider2D")
        assert "physics_material" not in col_data


class TestMonoBehaviourSerialization:
    def test_monobehaviour_type_name_and_flag(self):
        class PlayerController(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.speed = 5.0
                self.jump_height = 2.0

        go = GameObject("Player")
        pc = go.add_component(PlayerController)

        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        mb_data = next(c for c in comps if c.get("is_monobehaviour"))
        assert mb_data["type"] == "PlayerController"
        assert mb_data["is_monobehaviour"] is True

    def test_monobehaviour_public_field_types(self):
        class TestBehaviour(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.int_field = 42
                self.float_field = 3.14
                self.str_field = "hello"
                self.bool_field = True
                self.none_field = None

        go = GameObject("Test")
        go.add_component(TestBehaviour)

        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        mb_data = next(c for c in comps if c.get("is_monobehaviour"))
        fields = mb_data["fields"]
        assert fields["int_field"] == 42
        assert fields["float_field"] == pytest.approx(3.14)
        assert fields["str_field"] == "hello"
        assert fields["bool_field"] is True
        assert fields["none_field"] is None

    def test_monobehaviour_vector_fields(self):
        class VecBehaviour(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.pos2d = Vector2(1.0, 2.0)
                self.pos3d = Vector3(3.0, 4.0, 5.0)

        go = GameObject("Vec")
        go.add_component(VecBehaviour)

        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        mb_data = next(c for c in comps if c.get("is_monobehaviour"))
        fields = mb_data["fields"]
        assert fields["pos2d"] == {"_type": "Vector2", "value": [1.0, 2.0]}
        assert fields["pos3d"] == {"_type": "Vector3", "value": [3.0, 4.0, 5.0]}

    def test_monobehaviour_gameobject_ref(self):
        """Fields that reference other GameObjects should serialize as GameObjectRef."""
        class Follower(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.target = None

        target_go = GameObject("Target")
        follower_go = GameObject("Follower")
        fc = follower_go.add_component(Follower)
        fc.target = target_go

        result = serialize_scene()
        follower_data = next(g for g in result["game_objects"] if g["name"] == "Follower")
        comps = follower_data["components"]
        mb_data = next(c for c in comps if c.get("is_monobehaviour"))
        assert mb_data["fields"]["target"] == {"_type": "GameObjectRef", "name": "Target"}

    def test_monobehaviour_private_fields_excluded(self):
        class Secret(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self._private = "hidden"
                self.public_val = 10

        go = GameObject("Sec")
        go.add_component(Secret)

        result = serialize_scene()
        comps = result["game_objects"][0]["components"]
        mb_data = next(c for c in comps if c.get("is_monobehaviour"))
        assert "_private" not in mb_data["fields"]
        assert "public_val" in mb_data["fields"]


class TestSanitizeForJson:
    def test_positive_infinity_becomes_999999(self):
        assert _sanitize_for_json(float("inf")) == 999999.0

    def test_negative_infinity_becomes_neg_999999(self):
        assert _sanitize_for_json(float("-inf")) == -999999.0

    def test_nan_becomes_zero(self):
        assert _sanitize_for_json(float("nan")) == 0.0

    def test_normal_float_unchanged(self):
        assert _sanitize_for_json(3.14) == 3.14

    def test_nested_dict_sanitized(self):
        data = {"a": float("inf"), "b": {"c": float("nan")}}
        result = _sanitize_for_json(data)
        assert result == {"a": 999999.0, "b": {"c": 0.0}}

    def test_nested_list_sanitized(self):
        data = [float("inf"), [float("-inf"), float("nan")]]
        result = _sanitize_for_json(data)
        assert result == [999999.0, [-999999.0, 0.0]]

    def test_string_unchanged(self):
        assert _sanitize_for_json("hello") == "hello"

    def test_none_unchanged(self):
        assert _sanitize_for_json(None) is None


class TestSerializeFromSetup:
    def test_cleans_up_scene_after(self):
        """serialize_from_setup must leave the scene empty after completion."""
        from src.engine.core import _game_objects

        def my_setup():
            GameObject("A")
            GameObject("B")

        result = serialize_from_setup(my_setup)
        assert len(result["game_objects"]) == 2
        # Scene must be clean afterwards
        assert len(_game_objects) == 0

    def test_returns_valid_structure(self):
        def my_setup():
            go = GameObject("Test")
            go.add_component(SpriteRenderer)

        result = serialize_from_setup(my_setup)
        assert result["version"] == 1
        assert len(result["game_objects"]) == 1
        assert result["game_objects"][0]["name"] == "Test"
