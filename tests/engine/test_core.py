"""Tests for Component, MonoBehaviour, and GameObject."""

import pytest

from src.engine.core import Component, MonoBehaviour, GameObject
from src.engine.transform import Transform


class TestComponent:
    def test_component_has_game_object(self):
        go = GameObject("Test")
        comp = go.add_component(Component)
        assert comp.game_object is go

    def test_component_enabled_by_default(self):
        go = GameObject("Test")
        comp = go.add_component(Component)
        assert comp.enabled is True

    def test_component_unattached_raises(self):
        comp = Component()
        with pytest.raises(AssertionError):
            _ = comp.game_object


class TestMonoBehaviour:
    def test_lifecycle_stubs_exist(self):
        go = GameObject("Test")
        mb = go.add_component(MonoBehaviour)
        # Should not raise
        mb.awake()
        mb.start()
        mb.update()
        mb.fixed_update()
        mb.late_update()
        mb.on_destroy()
        mb.on_enable()
        mb.on_disable()

    def test_custom_monobehaviour(self):
        class Counter(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.count = 0

            def update(self):
                self.count += 1

        go = GameObject("Counter")
        counter = go.add_component(Counter)
        counter.update()
        counter.update()
        assert counter.count == 2


class TestGameObject:
    def test_creation(self):
        go = GameObject("Player")
        assert go.name == "Player"
        assert go.tag == "Untagged"
        assert go.active is True

    def test_custom_tag(self):
        go = GameObject("Enemy", tag="Enemy")
        assert go.tag == "Enemy"

    def test_transform_auto_created(self):
        go = GameObject("Test")
        assert go.transform is not None
        assert isinstance(go.transform, Transform)

    def test_add_component(self):
        go = GameObject("Test")
        comp = go.add_component(MonoBehaviour)
        assert comp.game_object is go

    def test_get_component(self):
        go = GameObject("Test")
        mb = go.add_component(MonoBehaviour)
        found = go.get_component(MonoBehaviour)
        assert found is mb

    def test_get_component_returns_none(self):
        go = GameObject("Test")
        assert go.get_component(MonoBehaviour) is None

    def test_get_components(self):
        go = GameObject("Test")
        go.add_component(MonoBehaviour)
        go.add_component(MonoBehaviour)
        assert len(go.get_components(MonoBehaviour)) == 2

    def test_find_by_name(self):
        go = GameObject("Player")
        found = GameObject.find("Player")
        assert found is go

    def test_find_returns_none(self):
        assert GameObject.find("NonExistent") is None

    def test_find_with_tag(self):
        go = GameObject("Enemy1", tag="Enemy")
        found = GameObject.find_with_tag("Enemy")
        assert found is go

    def test_find_game_objects_with_tag(self):
        e1 = GameObject("E1", tag="Enemy")
        e2 = GameObject("E2", tag="Enemy")
        p1 = GameObject("P1", tag="Player")
        enemies = GameObject.find_game_objects_with_tag("Enemy")
        assert len(enemies) == 2
        assert e1 in enemies
        assert e2 in enemies

    def test_destroy(self):
        go = GameObject("Temp")
        name = go.name
        GameObject.destroy(go)
        assert go.active is False
        assert GameObject.find(name) is None

    def test_destroy_calls_on_destroy(self):
        destroyed = []

        class Tracker(MonoBehaviour):
            def on_destroy(self):
                destroyed.append(True)

        go = GameObject("Tracked")
        go.add_component(Tracker)
        GameObject.destroy(go)
        assert len(destroyed) == 1

    def test_name_setter_updates_index(self):
        go = GameObject("OldName")
        go.name = "NewName"
        assert GameObject.find("OldName") is None
        assert GameObject.find("NewName") is go

    def test_tag_setter_updates_index(self):
        go = GameObject("Test", tag="OldTag")
        go.tag = "NewTag"
        assert GameObject.find_with_tag("OldTag") is None
        assert GameObject.find_with_tag("NewTag") is go

    def test_get_components_in_children(self):
        parent = GameObject("Parent")
        child = GameObject("Child")
        child.transform.set_parent(parent.transform)
        parent.add_component(MonoBehaviour)
        child.add_component(MonoBehaviour)
        results = parent.get_components_in_children(MonoBehaviour)
        assert len(results) == 2

    def test_unique_instance_ids(self):
        g1 = GameObject("A")
        g2 = GameObject("B")
        assert g1.instance_id != g2.instance_id

    def test_repr(self):
        go = GameObject("Player", tag="Hero")
        assert "Player" in repr(go)
        assert "Hero" in repr(go)
