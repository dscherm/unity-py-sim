"""Tests for scene_serializer — captures running scene to portable JSON."""

from src.engine.core import GameObject, MonoBehaviour, _game_objects
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


# ---------------------------------------------------------------------------
# Gap 4: translated-class registry filter
# ---------------------------------------------------------------------------


# Test-local MonoBehaviour subclasses.  Defined at module scope so the class
# name survives into the registry lookup exactly as it would from a real file.
class FakePlayer(MonoBehaviour):
    """Represents a translated class with a .cs counterpart."""
    pass


class InlineHandler(MonoBehaviour):
    """Represents an inline MonoBehaviour defined in a run_*.py file that
    has no .cs counterpart — should be filtered out when a registry is given."""
    pass


class TestTranslatedClassRegistryFilter:
    """Gap 4 (data/lessons/coplay_generator_gaps.md): serialize_scene accepts
    a set of translated class names.  Components whose class is not in the
    set are dropped from the serialized output so the downstream coplay
    generator never emits references to classes that have no .cs file.
    Chosen over translating run_*.py via the deep-interview contrarian lane
    (.omc/specs/deep-interview-coplay-gaps-upstream.md).
    """

    def test_untranslated_monobehaviour_dropped(self):
        go = GameObject("PlayButton")
        _ = go.transform  # ensure the Transform exists (GameObject lazy-creates it)
        go.add_component(InlineHandler)

        data = serialize_scene(translated_classes={"FakePlayer"})
        obj = next(g for g in data["game_objects"] if g["name"] == "PlayButton")
        comp_types = [c["type"] for c in obj["components"]]

        assert "InlineHandler" not in comp_types
        # Transform survives — the GameObject itself is kept
        assert "Transform" in comp_types

    def test_translated_monobehaviour_kept(self):
        go = GameObject("Bird")
        go.add_component(FakePlayer)

        data = serialize_scene(translated_classes={"FakePlayer"})
        obj = next(g for g in data["game_objects"] if g["name"] == "Bird")
        comp_types = [c["type"] for c in obj["components"]]

        assert "FakePlayer" in comp_types

    def test_mixed_scene_filters_only_untranslated(self):
        """PlayButton has InlineHandler (not translated), Bird has FakePlayer
        (translated).  Same registry, only InlineHandler drops."""
        button = GameObject("PlayButton")
        button.add_component(InlineHandler)
        bird = GameObject("Bird")
        bird.add_component(FakePlayer)

        data = serialize_scene(translated_classes={"FakePlayer"})
        by_name = {g["name"]: g for g in data["game_objects"]}

        button_types = [c["type"] for c in by_name["PlayButton"]["components"]]
        bird_types = [c["type"] for c in by_name["Bird"]["components"]]
        assert "InlineHandler" not in button_types
        assert "FakePlayer" in bird_types

    def test_no_registry_preserves_current_behavior(self):
        """Passing translated_classes=None must keep every MonoBehaviour —
        back-compat for callers that never pass a registry."""
        go = GameObject("Button")
        go.add_component(InlineHandler)

        data = serialize_scene()  # no registry
        obj = data["game_objects"][0]
        comp_types = [c["type"] for c in obj["components"]]
        assert "InlineHandler" in comp_types

    def test_empty_registry_drops_all_monobehaviours(self):
        """Empty set is distinct from None — it means 'no class has a .cs counterpart'."""
        go = GameObject("X")
        _ = go.transform
        go.add_component(InlineHandler)

        data = serialize_scene(translated_classes=set())
        obj = data["game_objects"][0]
        comp_types = [c["type"] for c in obj["components"]]
        assert "InlineHandler" not in comp_types
        # Engine components (Transform) still pass through — only user-authored
        # MonoBehaviours are subject to the registry filter.
        assert "Transform" in comp_types

    def test_string_list_field_emits_sprite_array_ref(self):
        """Gap 6: a list of asset-ref strings on a MonoBehaviour field becomes
        a SpriteArrayRef in the scene JSON so the CoPlay generator can wire
        it as a Unity sprite-array SerializeField."""
        class BirdAnim(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.sprites = ["bird_01", "bird_02", "bird_03"]

        go = GameObject("Bird")
        go.add_component(BirdAnim)

        data = serialize_scene()
        obj = next(g for g in data["game_objects"] if g["name"] == "Bird")
        bird_anim = next(c for c in obj["components"] if c.get("type") == "BirdAnim")
        sprites_field = bird_anim["fields"]["sprites"]
        assert sprites_field["_type"] == "SpriteArrayRef"
        assert sprites_field["refs"] == ["bird_01", "bird_02", "bird_03"]

    def test_empty_list_not_emitted_as_sprite_array(self):
        """Empty list has no asset-name information; skip serialization rather
        than emitting a 0-length SpriteArrayRef (easier to spot gaps)."""
        class EmptyContainer(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.sprites = []

        go = GameObject("X")
        go.add_component(EmptyContainer)
        data = serialize_scene()
        fields = data["game_objects"][0]["components"][0]["fields"]
        assert "sprites" not in fields or fields["sprites"] != {"_type": "SpriteArrayRef", "refs": []}

    def test_mixed_list_not_treated_as_sprite_array(self):
        """Lists mixing strings and non-strings are not sprite arrays."""
        class MixedBag(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.stuff = ["a", 1, "b"]

        go = GameObject("M")
        go.add_component(MixedBag)
        data = serialize_scene()
        fields = data["game_objects"][0]["components"][0]["fields"]
        # `stuff` is skipped entirely — not a SpriteArrayRef, not a scalar.
        assert fields.get("stuff") != {"_type": "SpriteArrayRef", "refs": ["a", 1, "b"]}

    def test_monobehaviour_list_field_emits_ref_array(self):
        """Pacman V2 GameManager pattern: `self.ghosts: list[Ghost]` holds
        references to Ghost components attached to other GameObjects in the
        scene.  The serializer must emit a `MonoBehaviourRefArray` entry
        so the CoPlay generator can wire the list via SerializedObject at
        scene-setup time.  Without this, GameManager.ghosts is an empty
        list at runtime and nothing moves."""
        class Enemy(MonoBehaviour):
            pass

        class Boss(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.enemies = []

        e1_go = GameObject("Enemy1")
        e1 = e1_go.add_component(Enemy)
        e2_go = GameObject("Enemy2")
        e2 = e2_go.add_component(Enemy)

        boss_go = GameObject("Boss")
        boss = boss_go.add_component(Boss)
        boss.enemies = [e1, e2]

        data = serialize_scene()
        boss_obj = next(g for g in data["game_objects"] if g["name"] == "Boss")
        boss_comp = next(c for c in boss_obj["components"] if c.get("type") == "Boss")
        enemies_field = boss_comp["fields"]["enemies"]
        assert enemies_field["_type"] == "MonoBehaviourRefArray"
        assert enemies_field["component_type"] == "Enemy"
        # refs list GameObject names in order so CoPlay can look up GetComponent<T>() on each.
        assert enemies_field["refs"] == ["Enemy1", "Enemy2"]

    def test_underscore_private_field_is_serialized(self):
        """Python-convention `_foo` fields translate to `[SerializeField]
        private` in C# — the scene serializer must include them so the
        Inspector wiring survives, otherwise GameManager._all_pellets
        stays empty and the game doesn't work."""
        class Holder(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self._count = 7

        go = GameObject("H")
        go.add_component(Holder)
        data = serialize_scene()
        holder_comp = next(c for c in data["game_objects"][0]["components"] if c.get("type") == "Holder")
        # The Python field name survives — the translator/CoPlay pass handles
        # `_count` → `count` camelCasing; what matters is the VALUE is captured.
        assert 7 in holder_comp["fields"].values() or holder_comp["fields"].get("_count") == 7 or holder_comp["fields"].get("count") == 7

    def test_engine_components_never_filtered(self):
        """Transform, SpriteRenderer, Rigidbody2D, colliders, Camera, etc. are
        engine primitives, not user classes.  They must pass through the
        filter regardless of registry contents."""
        go = GameObject("Thing")
        _ = go.transform
        go.add_component(SpriteRenderer)
        go.add_component(Rigidbody2D)
        go.add_component(BoxCollider2D)

        data = serialize_scene(translated_classes=set())  # empty registry
        obj = data["game_objects"][0]
        comp_types = [c["type"] for c in obj["components"]]
        assert "Transform" in comp_types
        assert "SpriteRenderer" in comp_types
        assert "Rigidbody2D" in comp_types
        assert "BoxCollider2D" in comp_types
