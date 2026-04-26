"""Contract tests for Prefab system -- derived from Unity documentation behavior.

Unity's Instantiate() contract:
- Object.Instantiate returns a NEW object each call (clone, not reference)
- The instantiated object has ALL components the prefab defines
- Instantiating with a position sets transform.position
- Instantiating a null/missing prefab returns null (our Python equivalent: KeyError)
- Instantiated objects are immediately active
- Instantiated objects register in the scene hierarchy (findable)
"""

import pytest

from src.engine.core import GameObject, MonoBehaviour, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.math.vector import Vector2
from src.engine.prefab import Instantiate, PrefabRegistry
from src.engine.physics.rigidbody import Rigidbody2D
from src.engine.physics.collider import BoxCollider2D
from src.engine.rendering.renderer import SpriteRenderer


@pytest.fixture(autouse=True)
def clean_state():
    PrefabRegistry.clear()
    LifecycleManager.reset()
    yield
    PrefabRegistry.clear()
    LifecycleManager.reset()
    _clear_registry()


def _multi_component_setup(go: GameObject) -> None:
    """Prefab with 3 component types."""
    go.add_component(Rigidbody2D)
    go.add_component(BoxCollider2D)
    go.add_component(SpriteRenderer)


class TestUnityInstantiateReturnsNewObject:
    """Unity contract: Instantiate returns a new GameObject every call, never the same one."""

    def test_two_calls_return_different_objects(self):
        PrefabRegistry.register("Thing", _multi_component_setup)
        a = Instantiate("Thing")
        b = Instantiate("Thing")
        assert a is not b

    def test_instance_ids_are_unique(self):
        PrefabRegistry.register("Thing", _multi_component_setup)
        ids = {Instantiate("Thing").instance_id for _ in range(10)}
        assert len(ids) == 10, "All instantiated objects must have unique instance_ids"

    def test_return_type_is_game_object(self):
        PrefabRegistry.register("Thing", _multi_component_setup)
        result = Instantiate("Thing")
        assert isinstance(result, GameObject)


class TestInstantiatedObjectHasAllComponents:
    """Unity contract: Instantiated objects have all components the prefab defines."""

    def test_all_three_components_present(self):
        PrefabRegistry.register("Thing", _multi_component_setup)
        obj = Instantiate("Thing")
        assert obj.get_component(Rigidbody2D) is not None
        assert obj.get_component(BoxCollider2D) is not None
        assert obj.get_component(SpriteRenderer) is not None

    def test_single_component_prefab(self):
        PrefabRegistry.register("Simple", lambda go: go.add_component(SpriteRenderer))
        obj = Instantiate("Simple")
        assert obj.get_component(SpriteRenderer) is not None
        assert obj.get_component(Rigidbody2D) is None

    def test_monobehaviour_component_in_prefab(self):
        class CustomScript(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.value = 42

        PrefabRegistry.register("Scripted", lambda go: go.add_component(CustomScript))
        obj = Instantiate("Scripted")
        script = obj.get_component(CustomScript)
        assert script is not None
        assert script.value == 42


class TestInstantiateWithPositionSetsTransform:
    """Unity contract: Instantiating with position sets transform.position."""

    def test_position_applied_to_transform(self):
        PrefabRegistry.register("Thing", _multi_component_setup)
        pos = Vector2(3.14, 2.72)
        obj = Instantiate("Thing", position=pos)
        assert abs(obj.transform.position.x - 3.14) < 1e-6
        assert abs(obj.transform.position.y - 2.72) < 1e-6

    def test_negative_position(self):
        PrefabRegistry.register("Thing", _multi_component_setup)
        pos = Vector2(-100.0, -200.0)
        obj = Instantiate("Thing", position=pos)
        assert abs(obj.transform.position.x - (-100.0)) < 1e-6
        assert abs(obj.transform.position.y - (-200.0)) < 1e-6

    def test_zero_position_is_default(self):
        """Without position arg, transform should be at origin."""
        PrefabRegistry.register("Thing", _multi_component_setup)
        obj = Instantiate("Thing")
        assert abs(obj.transform.position.x) < 1e-6
        assert abs(obj.transform.position.y) < 1e-6


class TestUnregisteredPrefabRaisesError:
    """Our Python equivalent of Unity returning null for missing prefabs: raise KeyError."""

    def test_missing_prefab_raises_key_error(self):
        with pytest.raises(KeyError, match="Prefab 'DoesNotExist' not registered"):
            Instantiate("DoesNotExist")

    def test_case_sensitive_name(self):
        PrefabRegistry.register("Laser", _multi_component_setup)
        with pytest.raises(KeyError):
            Instantiate("laser")  # wrong case

    def test_empty_registry_raises(self):
        with pytest.raises(KeyError):
            Instantiate("Anything")


class TestInstantiatedObjectIsActive:
    """Unity contract: Instantiated objects are immediately active."""

    def test_active_by_default(self):
        PrefabRegistry.register("Thing", _multi_component_setup)
        obj = Instantiate("Thing")
        assert obj.active is True

    def test_findable_immediately(self):
        """Active objects are findable via GameObject.find()."""
        PrefabRegistry.register("Thing", _multi_component_setup)
        obj = Instantiate("Thing", name="Unique123")
        found = GameObject.find("Unique123")
        assert found is obj


class TestPrefabRegistryClear:
    """PrefabRegistry.clear() removes all registered prefabs."""

    def test_clear_empties_registry(self):
        PrefabRegistry.register("A", _multi_component_setup)
        PrefabRegistry.register("B", _multi_component_setup)
        PrefabRegistry.clear()
        with pytest.raises(KeyError):
            Instantiate("A")

    def test_re_register_after_clear(self):
        PrefabRegistry.register("A", _multi_component_setup)
        PrefabRegistry.clear()
        PrefabRegistry.register("A", lambda go: go.add_component(SpriteRenderer))
        obj = Instantiate("A")
        assert obj.get_component(SpriteRenderer) is not None
        assert obj.get_component(Rigidbody2D) is None  # old setup gone
