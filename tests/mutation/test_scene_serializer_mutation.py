"""Mutation tests for scene_serializer — prove tests catch breakages.

These tests monkeypatch key functions in the serializer to simulate bugs,
then verify the output changes in detectable ways.
"""

import json

import pytest

from src.engine.core import _clear_registry, GameObject
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.physics.rigidbody import Rigidbody2D
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.rendering.camera import Camera
from src.engine.audio import AudioListener
from src.engine.math.vector import Vector2

import src.exporter.scene_serializer as serializer_module
from src.exporter.scene_serializer import (
    serialize_scene,
    serialize_scene_json,
)


@pytest.fixture(autouse=True)
def clean_scene():
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


class TestSerializeComponentMutation:
    def test_sprite_renderer_missing_when_returns_none(self, monkeypatch):
        """If _serialize_component returns None for SpriteRenderer,
        the SpriteRenderer must be absent from the serialized output."""
        original = serializer_module._serialize_component

        def patched(comp, **kwargs):
            if isinstance(comp, SpriteRenderer):
                return None
            return original(comp, **kwargs)

        monkeypatch.setattr(serializer_module, "_serialize_component", patched)

        go = GameObject("Test")
        sr = go.add_component(SpriteRenderer)
        sr.asset_ref = "test_sprite"
        sr.color = (255, 0, 0)
        sr.size = Vector2(1, 1)

        result = serialize_scene()
        go_data = result["game_objects"][0]
        sprite_comps = [c for c in go_data["components"] if c.get("type") == "SpriteRenderer"]
        assert len(sprite_comps) == 0, "SpriteRenderer should be missing when _serialize_component returns None"

    def test_rigidbody_still_present_when_sprite_patched(self, monkeypatch):
        """Other components must still serialize when SpriteRenderer is patched out."""
        original = serializer_module._serialize_component

        def patched(comp, **kwargs):
            if isinstance(comp, SpriteRenderer):
                return None
            return original(comp, **kwargs)

        monkeypatch.setattr(serializer_module, "_serialize_component", patched)

        go = GameObject("Test")
        go.add_component(Rigidbody2D)
        go.add_component(SpriteRenderer)

        result = serialize_scene()
        go_data = result["game_objects"][0]
        rb_comps = [c for c in go_data["components"] if c.get("type") == "Rigidbody2D"]
        assert len(rb_comps) == 1


class TestSanitizeMutation:
    def test_infinity_breaks_strict_json_without_sanitize(self, monkeypatch):
        """If _sanitize_for_json is an identity function, Infinity values
        must cause json.dumps(allow_nan=False) to raise ValueError.
        Python's json.dumps allows nan/inf by default (non-standard),
        but strict JSON parsers reject them."""
        monkeypatch.setattr(serializer_module, "_sanitize_for_json", lambda x: x)

        go = GameObject("Inf")
        sr = go.add_component(SpriteRenderer)
        sr.size = Vector2(float("inf"), 1.0)

        scene = serialize_scene()
        with pytest.raises(ValueError):
            json.dumps(scene, allow_nan=False)

    def test_nan_breaks_strict_json_without_sanitize(self, monkeypatch):
        """NaN values must also cause json.dumps(allow_nan=False) to raise ValueError."""
        monkeypatch.setattr(serializer_module, "_sanitize_for_json", lambda x: x)

        go = GameObject("NaN")
        sr = go.add_component(SpriteRenderer)
        sr.size = Vector2(float("nan"), 1.0)

        scene = serialize_scene()
        with pytest.raises(ValueError):
            json.dumps(scene, allow_nan=False)

    def test_sanitized_json_is_valid(self):
        """With sanitize enabled, Infinity/NaN produce valid JSON."""
        go = GameObject("Special")
        sr = go.add_component(SpriteRenderer)
        sr.size = Vector2(float("inf"), float("nan"))

        json_str = serialize_scene_json()
        # Must not raise
        data = json.loads(json_str)
        go_data = data["game_objects"][0]
        sr_data = next(c for c in go_data["components"] if c["type"] == "SpriteRenderer")
        assert sr_data["size"][0] == 999999.0
        assert sr_data["size"][1] == 0.0


class TestVersionMutation:
    def test_version_field_present(self):
        """Removing the version field would break consumers."""
        result = serialize_scene()
        assert "version" in result

    def test_version_value_is_two(self):
        result = serialize_scene()
        assert result["version"] == 2
