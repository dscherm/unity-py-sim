"""Tests for scene_serializer — captures running scene to portable JSON."""

from src.engine.core import GameObject, _game_objects
from src.engine.math.vector import Vector2, Vector3
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.physics.rigidbody import Rigidbody2D
from src.engine.physics.collider import BoxCollider2D
from src.exporter.scene_serializer import serialize_scene, _serialize_component


def setup_function():
    _game_objects.clear()


def teardown_function():
    _game_objects.clear()


def test_serialize_empty_scene():
    result = serialize_scene()
    assert "game_objects" in result
    assert len(result["game_objects"]) == 0


def test_serialize_single_gameobject():
    go = GameObject("TestObj")
    result = serialize_scene()
    assert len(result["game_objects"]) == 1
    assert result["game_objects"][0]["name"] == "TestObj"


def test_serialize_transform_position():
    go = GameObject("Positioned")
    go.transform.position = Vector3(1.0, 2.0, 3.0)
    result = serialize_scene()
    obj = result["game_objects"][0]
    transform = next(c for c in obj["components"] if c["type"] == "Transform")
    assert transform["position"] == [1.0, 2.0, 3.0]


def test_serialize_sprite_renderer():
    go = GameObject("Sprite")
    sr = go.add_component(SpriteRenderer)
    result = serialize_scene()
    obj = result["game_objects"][0]
    comp_types = [c["type"] for c in obj["components"]]
    assert "SpriteRenderer" in comp_types


def test_serialize_rigidbody():
    go = GameObject("Physics")
    rb = go.add_component(Rigidbody2D)
    result = serialize_scene()
    obj = result["game_objects"][0]
    comp_types = [c["type"] for c in obj["components"]]
    assert "Rigidbody2D" in comp_types


def test_serialize_collider():
    go = GameObject("Collider")
    col = go.add_component(BoxCollider2D)
    result = serialize_scene()
    obj = result["game_objects"][0]
    comp_types = [c["type"] for c in obj["components"]]
    assert "BoxCollider2D" in comp_types
