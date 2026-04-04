"""Integration tests for PrefabRegistry and Instantiate().

These tests verify the prefab system works end-to-end with the engine,
including lifecycle management, component configuration, and runtime
instantiation during the game loop.
"""

import pytest

from src.engine.core import GameObject, MonoBehaviour, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.math.vector import Vector2, Vector3
from src.engine.prefab import Instantiate, PrefabRegistry
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D
from src.engine.rendering.renderer import SpriteRenderer


@pytest.fixture(autouse=True)
def clean_state():
    """Reset engine and prefab state before each test."""
    PrefabRegistry.clear()
    LifecycleManager.reset()
    yield
    PrefabRegistry.clear()
    LifecycleManager.reset()
    _clear_registry()


def _setup_enemy(go: GameObject) -> None:
    """Test prefab: enemy with rigidbody and collider."""
    rb = go.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.KINEMATIC
    col = go.add_component(BoxCollider2D)
    col.size = Vector2(1.0, 1.0)
    col.is_trigger = True
    sr = go.add_component(SpriteRenderer)
    sr.color = (255, 0, 0)


class HealthTracker(MonoBehaviour):
    """Test component that tracks lifecycle calls."""

    def __init__(self):
        super().__init__()
        self.hp = 100
        self.awake_called = False
        self.start_called = False
        self.update_count = 0

    def awake(self):
        self.awake_called = True

    def start(self):
        self.start_called = True

    def update(self):
        self.update_count += 1


def _setup_tracked_enemy(go: GameObject) -> None:
    """Prefab with a MonoBehaviour so we can observe lifecycle."""
    go.add_component(HealthTracker)
    sr = go.add_component(SpriteRenderer)
    sr.color = (0, 255, 0)


class TestPrefabRegistrationAndInstantiation:
    """Register a prefab, Instantiate it, verify components exist and are configured."""

    def test_register_and_instantiate_basic(self):
        PrefabRegistry.register("Enemy", _setup_enemy)
        enemy = Instantiate("Enemy")
        assert enemy is not None
        assert enemy.name == "Enemy"
        assert enemy.get_component(Rigidbody2D) is not None
        assert enemy.get_component(BoxCollider2D) is not None
        assert enemy.get_component(SpriteRenderer) is not None

    def test_instantiated_components_configured(self):
        PrefabRegistry.register("Enemy", _setup_enemy)
        enemy = Instantiate("Enemy")
        rb = enemy.get_component(Rigidbody2D)
        assert rb.body_type == RigidbodyType2D.KINEMATIC
        col = enemy.get_component(BoxCollider2D)
        assert col.is_trigger is True
        sr = enemy.get_component(SpriteRenderer)
        assert sr.color == (255, 0, 0)


class TestInstantiateIndependence:
    """Instantiate multiple copies, verify each is independent."""

    def test_multiple_instances_are_distinct_objects(self):
        PrefabRegistry.register("Enemy", _setup_enemy)
        a = Instantiate("Enemy")
        b = Instantiate("Enemy")
        assert a is not b
        assert a.instance_id != b.instance_id

    def test_modifying_one_does_not_affect_another(self):
        PrefabRegistry.register("Enemy", _setup_enemy)
        a = Instantiate("Enemy")
        b = Instantiate("Enemy")
        # Modify a's sprite renderer color
        sr_a = a.get_component(SpriteRenderer)
        sr_a.color = (0, 0, 0)
        sr_b = b.get_component(SpriteRenderer)
        assert sr_b.color == (255, 0, 0), "Changing one instance should not affect the other"

    def test_components_are_separate_instances(self):
        PrefabRegistry.register("Enemy", _setup_enemy)
        a = Instantiate("Enemy")
        b = Instantiate("Enemy")
        rb_a = a.get_component(Rigidbody2D)
        rb_b = b.get_component(Rigidbody2D)
        assert rb_a is not rb_b


class TestInstantiateOverrides:
    """Instantiate with position/tag/name overrides."""

    def test_position_override(self):
        PrefabRegistry.register("Enemy", _setup_enemy)
        pos = Vector2(5.0, 10.0)
        enemy = Instantiate("Enemy", position=pos)
        assert abs(enemy.transform.position.x - 5.0) < 1e-6
        assert abs(enemy.transform.position.y - 10.0) < 1e-6

    def test_tag_override(self):
        PrefabRegistry.register("Enemy", _setup_enemy)
        enemy = Instantiate("Enemy", tag="Boss")
        assert enemy.tag == "Boss"

    def test_name_override(self):
        PrefabRegistry.register("Enemy", _setup_enemy)
        enemy = Instantiate("Enemy", name="MiniBoss")
        assert enemy.name == "MiniBoss"

    def test_default_tag_is_untagged(self):
        """Unity default: GameObjects without an explicit tag are 'Untagged'."""
        PrefabRegistry.register("Enemy", _setup_enemy)
        enemy = Instantiate("Enemy")
        assert enemy.tag == "Untagged"

    def test_default_position_is_origin(self):
        PrefabRegistry.register("Enemy", _setup_enemy)
        enemy = Instantiate("Enemy")
        assert abs(enemy.transform.position.x) < 1e-6
        assert abs(enemy.transform.position.y) < 1e-6


class TestPrefabLifecycleIntegration:
    """Run through game loop -- verify instantiated objects get lifecycle methods."""

    def test_awake_and_start_called(self):
        PrefabRegistry.register("Tracked", _setup_tracked_enemy)
        enemy = Instantiate("Tracked")
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        ht = enemy.get_component(HealthTracker)
        assert ht.awake_called is True
        lm.process_start_queue()
        assert ht.start_called is True

    def test_update_called_in_loop(self):
        PrefabRegistry.register("Tracked", _setup_tracked_enemy)
        enemy = Instantiate("Tracked")
        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()
        ht = enemy.get_component(HealthTracker)
        lm.run_update()
        lm.run_update()
        lm.run_update()
        assert ht.update_count == 3

    def test_instantiate_during_update(self):
        """Runtime-created prefabs should work when Instantiated during update()."""

        spawned = []

        class Spawner(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.did_spawn = False

            def update(self):
                if not self.did_spawn:
                    self.did_spawn = True
                    obj = Instantiate("Tracked")
                    spawned.append(obj)

        PrefabRegistry.register("Tracked", _setup_tracked_enemy)
        parent = GameObject("Spawner")
        parent.add_component(Spawner)

        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        # First update: spawner creates a Tracked prefab
        lm.run_update()
        assert len(spawned) == 1

        # Process the newly created object's lifecycle
        lm.process_awake_queue()
        lm.process_start_queue()
        ht = spawned[0].get_component(HealthTracker)
        assert ht.awake_called is True
        assert ht.start_called is True

    def test_findable_after_instantiate(self):
        """Instantiated objects should be findable via GameObject.find()."""
        PrefabRegistry.register("Enemy", _setup_enemy)
        Instantiate("Enemy", tag="EnemyTag", name="FindMe")
        found = GameObject.find("FindMe")
        assert found is not None
        assert found.tag == "EnemyTag"

    def test_find_with_tag_after_instantiate(self):
        PrefabRegistry.register("Enemy", _setup_enemy)
        Instantiate("Enemy", tag="Foe")
        Instantiate("Enemy", tag="Foe")
        foes = GameObject.find_game_objects_with_tag("Foe")
        assert len(foes) == 2
