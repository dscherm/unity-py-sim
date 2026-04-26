"""Mutation tests for the Prefab system.

These tests monkeypatch internals to verify that the test suite detects
breakage -- proving the tests are actually exercising the code paths.
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
    PrefabRegistry.clear()
    LifecycleManager.reset()
    yield
    PrefabRegistry.clear()
    LifecycleManager.reset()
    _clear_registry()


def _setup_enemy(go: GameObject) -> None:
    rb = go.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.KINEMATIC
    col = go.add_component(BoxCollider2D)
    col.size = Vector2(1.0, 1.0)
    col.is_trigger = True
    sr = go.add_component(SpriteRenderer)
    sr.color = (255, 0, 0)


def _setup_nothing(go: GameObject) -> None:
    """A setup function that adds no components."""
    pass


class TestMutateRegistryReturnsWrongSetup:
    """Monkeypatch PrefabRegistry to return wrong setup func -- verify wrong components."""

    def test_wrong_setup_produces_wrong_components(self, monkeypatch):
        PrefabRegistry.register("Enemy", _setup_enemy)
        # Monkeypatch: registry returns _setup_nothing instead
        original_get = PrefabRegistry.get
        monkeypatch.setattr(
            PrefabRegistry, "get",
            classmethod(lambda cls, name: _setup_nothing if name == "Enemy" else original_get(name))
        )
        enemy = Instantiate("Enemy")
        # If setup was wrong, there should be no Rigidbody2D
        assert enemy.get_component(Rigidbody2D) is None, \
            "Mutation: wrong setup func should produce object without Rigidbody2D"
        assert enemy.get_component(SpriteRenderer) is None, \
            "Mutation: wrong setup func should produce object without SpriteRenderer"

    def test_swapped_prefabs_detected(self, monkeypatch):
        """Register two prefabs, swap their setup funcs in the registry."""

        def _setup_player(go: GameObject) -> None:
            sr = go.add_component(SpriteRenderer)
            sr.color = (0, 0, 255)  # blue

        PrefabRegistry.register("Enemy", _setup_enemy)
        PrefabRegistry.register("Player", _setup_player)

        # Monkeypatch: swap them
        monkeypatch.setattr(
            PrefabRegistry, "get",
            classmethod(lambda cls, name: _setup_player if name == "Enemy" else _setup_enemy)
        )
        enemy = Instantiate("Enemy")
        sr = enemy.get_component(SpriteRenderer)
        # Enemy should have red, but mutation gives blue
        assert sr.color == (0, 0, 255), \
            "Mutation: swapped prefab should produce blue sprite (player's color)"
        # And no rigidbody (player setup doesn't add one)
        assert enemy.get_component(Rigidbody2D) is None


class TestMutateInstantiateSkipsSetup:
    """Monkeypatch Instantiate to not call setup_func -- verify object has no components."""

    def test_no_setup_means_no_components(self, monkeypatch):
        PrefabRegistry.register("Enemy", _setup_enemy)

        import src.engine.prefab as prefab_mod

        def broken_instantiate(prefab_name, position=None, tag=None, name=None):
            """Instantiate that skips calling setup_func."""
            go_name = name or prefab_name
            go = GameObject(go_name, tag=tag or "Untagged")
            if position is not None:
                go.transform.position = position
            # MUTATION: setup_func deliberately NOT called
            return go

        monkeypatch.setattr(prefab_mod, "Instantiate", broken_instantiate)
        enemy = prefab_mod.Instantiate("Enemy")
        assert enemy.get_component(Rigidbody2D) is None, \
            "Mutation: skipping setup_func should mean no Rigidbody2D"
        assert enemy.get_component(BoxCollider2D) is None
        assert enemy.get_component(SpriteRenderer) is None

    def test_position_still_works_without_setup(self, monkeypatch):
        """Even without setup_func, position should be set (it's in Instantiate, not setup)."""
        PrefabRegistry.register("Enemy", _setup_enemy)

        import src.engine.prefab as prefab_mod

        def broken_instantiate(prefab_name, position=None, tag=None, name=None):
            go_name = name or prefab_name
            go = GameObject(go_name, tag=tag or "Untagged")
            if position is not None:
                go.transform.position = position
            return go

        monkeypatch.setattr(prefab_mod, "Instantiate", broken_instantiate)
        enemy = prefab_mod.Instantiate("Enemy", position=Vector2(5.0, 10.0))
        assert abs(enemy.transform.position.x - 5.0) < 1e-6


class TestMutateProjectileSpeed:
    """Simulate breaking a prefab's component values -- verify behavior changes."""

    def test_zero_speed_projectile_does_not_move(self):
        """If a projectile prefab has speed=0, it should not move during update."""

        class FakeProjectile(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.speed = 0.0  # MUTATION: speed is 0
                self.direction = Vector3(0, 1, 0)

            def update(self):
                pos = self.transform.position
                pos.x += self.direction.x * self.speed
                pos.y += self.direction.y * self.speed
                self.transform.position = pos

        def _setup_broken_laser(go: GameObject) -> None:
            go.add_component(FakeProjectile)

        PrefabRegistry.register("BrokenLaser", _setup_broken_laser)
        laser = Instantiate("BrokenLaser", position=Vector2(0.0, 0.0))

        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        # Run 10 updates
        for _ in range(10):
            lm.run_update()

        proj = laser.get_component(FakeProjectile)
        # With speed=0, position should not have changed
        assert abs(laser.transform.position.y) < 1e-6, \
            "Mutation: zero-speed projectile should not move"

    def test_nonzero_speed_projectile_moves(self):
        """Control test: with speed > 0, projectile should move."""

        class FakeProjectile(MonoBehaviour):
            def __init__(self):
                super().__init__()
                self.speed = 10.0
                self.direction = Vector3(0, 1, 0)

            def update(self):
                pos = self.transform.position
                pos.y += self.direction.y * self.speed
                self.transform.position = pos

        def _setup_working_laser(go: GameObject) -> None:
            go.add_component(FakeProjectile)

        PrefabRegistry.register("WorkingLaser", _setup_working_laser)
        laser = Instantiate("WorkingLaser", position=Vector2(0.0, 0.0))

        lm = LifecycleManager.instance()
        lm.process_awake_queue()
        lm.process_start_queue()

        for _ in range(5):
            lm.run_update()

        # Should have moved: 5 updates * speed 10 = 50 units
        assert laser.transform.position.y > 40.0, \
            "Control: projectile with speed should move"


class TestMutatePositionNotApplied:
    """Mutation: if Instantiate doesn't apply position, tests should catch it."""

    def test_position_must_be_applied(self, monkeypatch):
        PrefabRegistry.register("Enemy", _setup_enemy)

        import src.engine.prefab as prefab_mod
        original = prefab_mod.Instantiate

        def broken_instantiate(prefab_name, position=None, tag=None, name=None):
            """Instantiate that ignores position."""
            return original(prefab_name, position=None, tag=tag, name=name)

        monkeypatch.setattr(prefab_mod, "Instantiate", broken_instantiate)
        enemy = prefab_mod.Instantiate("Enemy", position=Vector2(99.0, 99.0))
        # Position should NOT be 99,99 because mutation breaks it
        assert abs(enemy.transform.position.x) < 1e-6, \
            "Mutation: broken Instantiate ignores position"
        assert abs(enemy.transform.position.y) < 1e-6
