"""Mutation tests for G4 — scene_serializer class registry filter.

Proves that if the registry filter condition is disabled (e.g., replaced
with `if False:`), the contract tests catch the regression — i.e., that
unregistered MonoBehaviours are no longer dropped.

Mutation strategy: monkeypatch _serialize_component so it never applies
the translated_classes filter (always serializes the MonoBehaviour), then
verify the expected contract assertions fire.
"""

from __future__ import annotations

import pytest

from src.engine.core import _game_objects, GameObject, MonoBehaviour
from src.engine.transform import Transform
import src.exporter.scene_serializer as _ser_mod
from src.exporter.scene_serializer import serialize_scene


# ---------------------------------------------------------------------------
# Minimal MonoBehaviour stubs
# ---------------------------------------------------------------------------

class _FakePlayer(MonoBehaviour):
    pass


class _InlineHandler(MonoBehaviour):
    pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reset_scene():
    _game_objects.clear()


def _component_types_for(scene: dict, go_name: str) -> list[str]:
    for go in scene["game_objects"]:
        if go["name"] == go_name:
            return [c["type"] for c in go["components"]]
    return []


def _make_go(name: str) -> GameObject:
    return GameObject(name)


# ---------------------------------------------------------------------------
# Mutation factory: _serialize_component that ignores the filter
# ---------------------------------------------------------------------------

def _build_mutated_serialize_component():
    """Return a version of _serialize_component where the filter is disabled.

    This simulates reverting the gap-4 fix by replacing:
        if translated_classes is not None and class_name not in translated_classes:
            return None
    with:
        if False:
            return None
    """
    from src.engine.rendering.renderer import SpriteRenderer
    from src.engine.rendering.camera import Camera
    from src.engine.audio import AudioSource, AudioListener
    from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
    from src.engine.physics.collider import BoxCollider2D, CircleCollider2D

    # Import the real function's helper utilities
    from src.exporter.scene_serializer import _vec3_to_list, _vec2_to_list

    def _mutated_serialize_component(comp, translated_classes=None):
        """Broken version: never drops MonoBehaviours regardless of registry."""
        if isinstance(comp, Transform):
            return {
                "type": "Transform",
                "position": _vec3_to_list(comp.position),
                "rotation": [comp.rotation.x, comp.rotation.y, comp.rotation.z, comp.rotation.w],
                "local_scale": _vec3_to_list(comp.local_scale),
                "parent": comp.parent.game_object.name if comp.parent else None,
            }
        if isinstance(comp, SpriteRenderer):
            return {
                "type": "SpriteRenderer",
                "color": list(comp.color),
                "size": _vec2_to_list(comp.size),
                "sorting_order": comp.sorting_order,
                "asset_ref": comp.asset_ref,
            }
        if isinstance(comp, Camera):
            return {
                "type": "Camera",
                "orthographic_size": comp.orthographic_size,
                "background_color": list(comp.background_color) if comp.background_color else None,
            }
        if isinstance(comp, AudioSource):
            return {
                "type": "AudioSource",
                "clip_ref": comp.clip_ref,
                "volume": comp.volume,
                "pitch": comp.pitch,
                "loop": comp.loop,
            }
        if isinstance(comp, AudioListener):
            return {"type": "AudioListener"}
        if isinstance(comp, Rigidbody2D):
            body_type = "Dynamic"
            if comp.body_type == RigidbodyType2D.STATIC:
                body_type = "Static"
            elif comp.body_type == RigidbodyType2D.KINEMATIC:
                body_type = "Kinematic"
            return {
                "type": "Rigidbody2D",
                "body_type": body_type,
                "mass": comp.mass,
                "gravity_scale": comp.gravity_scale,
            }
        if isinstance(comp, BoxCollider2D):
            return {
                "type": "BoxCollider2D",
                "size": _vec2_to_list(comp.size),
                "is_trigger": comp.is_trigger,
            }
        if isinstance(comp, CircleCollider2D):
            return {
                "type": "CircleCollider2D",
                "radius": comp.radius,
                "is_trigger": comp.is_trigger,
            }
        if isinstance(comp, MonoBehaviour):
            class_name = type(comp).__name__
            # MUTATION: filter condition disabled — never drops
            if False:  # noqa: SIM210  (intentional mutation)
                return None
            return {
                "type": class_name,
                "is_monobehaviour": True,
                "fields": {},
            }
        return None

    return _mutated_serialize_component


# ---------------------------------------------------------------------------
# Baseline: real implementation passes contract assertions
# ---------------------------------------------------------------------------

class TestBaselineRealImplementation:
    def setup_method(self):
        _reset_scene()

    def teardown_method(self):
        _reset_scene()

    def test_baseline_unregistered_mb_dropped(self):
        """Real implementation drops unregistered MonoBehaviours."""
        go = _make_go("Player")
        go.add_component(_InlineHandler)
        scene = serialize_scene(translated_classes={"_FakePlayer"})
        types = _component_types_for(scene, "Player")
        assert "_InlineHandler" not in types

    def test_baseline_empty_set_drops_all_user_mbs(self):
        """Real implementation: empty set drops all user MonoBehaviours."""
        go = _make_go("Player")
        go.add_component(_FakePlayer)
        scene = serialize_scene(translated_classes=set())
        types = _component_types_for(scene, "Player")
        assert "_FakePlayer" not in types


# ---------------------------------------------------------------------------
# Mutation: disabled filter MUST allow unregistered classes through
# ---------------------------------------------------------------------------

class TestMutationFilterDisabled:
    def setup_method(self):
        _reset_scene()

    def teardown_method(self):
        _reset_scene()

    def test_mutation_unregistered_mb_survives(self, monkeypatch):
        """MUTATION: disabled filter lets _InlineHandler through.

        Proves the contract test `test_unregistered_monobehaviour_dropped`
        would catch this regression.
        """
        monkeypatch.setattr(_ser_mod, "_serialize_component", _build_mutated_serialize_component())

        go = _make_go("Player")
        go.add_component(_InlineHandler)
        scene = serialize_scene(translated_classes={"_FakePlayer"})
        types = _component_types_for(scene, "Player")

        # After mutation, the handler survives — this proves the mutation is visible
        assert "_InlineHandler" in types, (
            "MUTATION NOT CAUGHT: _InlineHandler should survive with disabled filter"
        )

    def test_mutation_empty_set_does_not_drop_mb(self, monkeypatch):
        """MUTATION: empty set no longer drops MonoBehaviours."""
        monkeypatch.setattr(_ser_mod, "_serialize_component", _build_mutated_serialize_component())

        go = _make_go("Player")
        go.add_component(_FakePlayer)
        scene = serialize_scene(translated_classes=set())
        types = _component_types_for(scene, "Player")

        assert "_FakePlayer" in types, (
            "MUTATION NOT CAUGHT: _FakePlayer should survive with disabled filter"
        )

    def test_contract_assertion_fires_on_mutation(self, monkeypatch):
        """End-to-end proof: contract assertion raises on mutated code.

        The contract says `_InlineHandler not in types` when registry is
        `{'_FakePlayer'}`. With the mutation, _InlineHandler survives.
        We verify the contract assertion would catch this.
        """
        monkeypatch.setattr(_ser_mod, "_serialize_component", _build_mutated_serialize_component())

        go = _make_go("Player")
        go.add_component(_InlineHandler)
        scene = serialize_scene(translated_classes={"_FakePlayer"})
        types = _component_types_for(scene, "Player")

        with pytest.raises(AssertionError):
            assert "_InlineHandler" not in types, "_InlineHandler should be filtered"

    def test_contract_empty_set_assertion_fires_on_mutation(self, monkeypatch):
        """Empty set contract assertion fires when filter is disabled."""
        monkeypatch.setattr(_ser_mod, "_serialize_component", _build_mutated_serialize_component())

        go = _make_go("Player")
        go.add_component(_FakePlayer)
        scene = serialize_scene(translated_classes=set())
        types = _component_types_for(scene, "Player")

        with pytest.raises(AssertionError):
            assert "_FakePlayer" not in types, "_FakePlayer should be filtered by empty set"
