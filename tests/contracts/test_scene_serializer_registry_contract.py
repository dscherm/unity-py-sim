"""Contract tests for G4 — serialize_scene class registry filter.

Derived from the scene-export contract spec, NOT from the implementing
agent's test file (tests/exporter/test_scene_serializer.py).

Contract:
  - serialize_scene(translated_classes=None) and _serialize_component(comp,
    translated_classes=None) both accept the kwarg.
  - None (default) -> no MonoBehaviour is dropped (back-compat).
  - set containing a class name -> that MonoBehaviour is kept.
  - set not containing a class name -> that MonoBehaviour is dropped.
  - empty set() -> all user MonoBehaviours dropped; engine primitives kept.
  - Engine primitives (Transform, SpriteRenderer, Camera, Rigidbody2D,
    BoxCollider2D, CircleCollider2D, AudioSource, AudioListener) are NEVER
    filtered regardless of the registry.
  - GameObjects themselves are never dropped — only their components.
"""

from __future__ import annotations

import inspect

from src.engine.core import _game_objects, GameObject, MonoBehaviour
from src.engine.transform import Transform
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.rendering.camera import Camera
from src.engine.audio import AudioSource, AudioListener
from src.engine.physics.rigidbody import Rigidbody2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D
from src.exporter.scene_serializer import serialize_scene, _serialize_component


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_scene():
    """Clear all game objects from the scene registry."""
    _game_objects.clear()


def _make_go(name: str) -> GameObject:
    go = GameObject(name)
    return go


def _component_types_for(scene: dict, go_name: str) -> list[str]:
    for go in scene["game_objects"]:
        if go["name"] == go_name:
            return [c["type"] for c in go["components"]]
    return []


# ---------------------------------------------------------------------------
# Minimal MonoBehaviour stubs (not in src/, defined here for test isolation)
# ---------------------------------------------------------------------------

class _FakePlayer(MonoBehaviour):
    pass


class _InlineHandler(MonoBehaviour):
    pass


class _AnotherHandler(MonoBehaviour):
    pass


# ---------------------------------------------------------------------------
# Contract: API shape
# ---------------------------------------------------------------------------

class TestRegistryApiShape:
    def test_serialize_scene_accepts_translated_classes_kwarg(self):
        """serialize_scene must have a translated_classes parameter."""
        sig = inspect.signature(serialize_scene)
        assert "translated_classes" in sig.parameters, (
            "serialize_scene is missing the translated_classes parameter"
        )

    def test_serialize_scene_translated_classes_default_is_none(self):
        """translated_classes must default to None (back-compat)."""
        sig = inspect.signature(serialize_scene)
        default = sig.parameters["translated_classes"].default
        assert default is None

    def test_serialize_component_accepts_translated_classes_kwarg(self):
        """_serialize_component must have a translated_classes parameter."""
        sig = inspect.signature(_serialize_component)
        assert "translated_classes" in sig.parameters

    def test_serialize_component_translated_classes_default_is_none(self):
        """_serialize_component translated_classes must default to None."""
        sig = inspect.signature(_serialize_component)
        default = sig.parameters["translated_classes"].default
        assert default is None


# ---------------------------------------------------------------------------
# Contract: None registry (back-compat)
# ---------------------------------------------------------------------------

class TestNoneRegistryBackCompat:
    def setup_method(self):
        _reset_scene()

    def teardown_method(self):
        _reset_scene()

    def test_none_registry_keeps_all_monobehaviours(self):
        """When translated_classes is None, no MonoBehaviour is filtered."""
        go = _make_go("Player")
        go.add_component(_FakePlayer)
        go.add_component(_InlineHandler)

        scene = serialize_scene(translated_classes=None)
        types = _component_types_for(scene, "Player")
        assert "_FakePlayer" in types, "FakePlayer dropped under None registry"
        assert "_InlineHandler" in types, "InlineHandler dropped under None registry"

    def test_omitting_kwarg_keeps_all_monobehaviours(self):
        """Omitting translated_classes entirely must equal None behavior."""
        go = _make_go("Player")
        go.add_component(_FakePlayer)

        scene = serialize_scene()
        types = _component_types_for(scene, "Player")
        assert "_FakePlayer" in types, "FakePlayer dropped when kwarg omitted"


# ---------------------------------------------------------------------------
# Contract: Filtering behavior
# ---------------------------------------------------------------------------

class TestRegistryFilter:
    def setup_method(self):
        _reset_scene()

    def teardown_method(self):
        _reset_scene()

    def test_registered_monobehaviour_kept(self):
        """A class in the registry is preserved in serialized output."""
        go = _make_go("Player")
        go.add_component(_FakePlayer)

        scene = serialize_scene(translated_classes={"_FakePlayer"})
        types = _component_types_for(scene, "Player")
        assert "_FakePlayer" in types

    def test_unregistered_monobehaviour_dropped(self):
        """A class NOT in the registry is absent from serialized output."""
        go = _make_go("Player")
        go.add_component(_InlineHandler)

        scene = serialize_scene(translated_classes={"_FakePlayer"})
        types = _component_types_for(scene, "Player")
        assert "_InlineHandler" not in types, "_InlineHandler should be filtered"

    def test_mixed_components_only_drops_unregistered(self):
        """Registered classes survive; unregistered classes are dropped."""
        go = _make_go("Player")
        go.add_component(_FakePlayer)
        go.add_component(_InlineHandler)

        scene = serialize_scene(translated_classes={"_FakePlayer"})
        types = _component_types_for(scene, "Player")
        assert "_FakePlayer" in types
        assert "_InlineHandler" not in types

    def test_empty_set_drops_all_user_monobehaviours(self):
        """empty set() != None: all user MonoBehaviours are dropped."""
        go = _make_go("Player")
        go.add_component(_FakePlayer)
        go.add_component(_InlineHandler)

        scene = serialize_scene(translated_classes=set())
        types = _component_types_for(scene, "Player")
        assert "_FakePlayer" not in types
        assert "_InlineHandler" not in types

    def test_empty_set_is_distinct_from_none(self):
        """set() and None must produce different results."""
        go = _make_go("Player")
        go.add_component(_FakePlayer)

        scene_none = serialize_scene(translated_classes=None)
        scene_empty = serialize_scene(translated_classes=set())

        types_none = _component_types_for(scene_none, "Player")
        types_empty = _component_types_for(scene_empty, "Player")

        assert "_FakePlayer" in types_none
        assert "_FakePlayer" not in types_empty


# ---------------------------------------------------------------------------
# Contract: GameObjects are never dropped
# ---------------------------------------------------------------------------

class TestGameObjectsNeverDropped:
    def setup_method(self):
        _reset_scene()

    def teardown_method(self):
        _reset_scene()

    def test_gameobject_present_even_when_all_monobehaviours_filtered(self):
        """Dropping all MonoBehaviours must not remove the GameObject."""
        go = _make_go("Shell")
        go.add_component(_InlineHandler)

        scene = serialize_scene(translated_classes=set())
        go_names = [g["name"] for g in scene["game_objects"]]
        assert "Shell" in go_names, "GameObject 'Shell' was dropped — only components should be filtered"

    def test_gameobject_present_when_mixed_registry(self):
        """GameObject with partial filter is still in game_objects."""
        go = _make_go("Mixed")
        go.add_component(_FakePlayer)
        go.add_component(_InlineHandler)

        scene = serialize_scene(translated_classes={"_FakePlayer"})
        go_names = [g["name"] for g in scene["game_objects"]]
        assert "Mixed" in go_names


# ---------------------------------------------------------------------------
# Contract: Engine primitives always pass through
# ---------------------------------------------------------------------------

class TestEnginePrimitivesNeverFiltered:
    """Engine primitives must survive regardless of the translated_classes set."""

    def setup_method(self):
        _reset_scene()

    def teardown_method(self):
        _reset_scene()

    def _check_primitive_survives(self, comp_class, comp_type_name: str):
        go = _make_go("Prim")
        go.add_component(comp_class)
        scene = serialize_scene(translated_classes=set())
        types = _component_types_for(scene, "Prim")
        assert comp_type_name in types, (
            f"Engine primitive '{comp_type_name}' was filtered — it must always survive"
        )
        _reset_scene()

    def test_transform_never_filtered(self):
        go = _make_go("Prim")
        go.add_component(Transform)
        scene = serialize_scene(translated_classes=set())
        types = _component_types_for(scene, "Prim")
        assert "Transform" in types, (
            "Transform must survive empty registry — engine primitives are never filtered"
        )

    def test_sprite_renderer_never_filtered(self):
        self._check_primitive_survives(SpriteRenderer, "SpriteRenderer")

    def test_camera_never_filtered(self):
        self._check_primitive_survives(Camera, "Camera")

    def test_rigidbody2d_never_filtered(self):
        self._check_primitive_survives(Rigidbody2D, "Rigidbody2D")

    def test_box_collider_never_filtered(self):
        self._check_primitive_survives(BoxCollider2D, "BoxCollider2D")

    def test_circle_collider_never_filtered(self):
        self._check_primitive_survives(CircleCollider2D, "CircleCollider2D")

    def test_audio_source_never_filtered(self):
        self._check_primitive_survives(AudioSource, "AudioSource")

    def test_audio_listener_never_filtered(self):
        self._check_primitive_survives(AudioListener, "AudioListener")


# ---------------------------------------------------------------------------
# Contract: _serialize_component direct unit contract
# ---------------------------------------------------------------------------

class TestSerializeComponentDirectContract:
    """Test _serialize_component in isolation (not via full scene)."""

    def test_monobehaviour_in_registry_returns_dict(self):
        go = _make_go("X")
        comp = go.add_component(_FakePlayer)
        result = _serialize_component(comp, translated_classes={"_FakePlayer"})
        assert result is not None
        assert result["type"] == "_FakePlayer"
        _reset_scene()

    def test_monobehaviour_not_in_registry_returns_none(self):
        go = _make_go("X")
        comp = go.add_component(_InlineHandler)
        result = _serialize_component(comp, translated_classes={"_FakePlayer"})
        assert result is None, "_serialize_component must return None for filtered class"
        _reset_scene()

    def test_none_registry_monobehaviour_returns_dict(self):
        go = _make_go("X")
        comp = go.add_component(_InlineHandler)
        result = _serialize_component(comp, translated_classes=None)
        assert result is not None
        assert result["type"] == "_InlineHandler"
        _reset_scene()
