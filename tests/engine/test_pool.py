"""Tests for ObjectPool and GameObjectPool."""


from src.engine.pool import ObjectPool, GameObjectPool
from src.engine.core import GameObject


class TestObjectPool:
    def test_get_creates_object(self):
        pool = ObjectPool(create_func=lambda: {"id": 1})
        obj = pool.get()
        assert obj == {"id": 1}

    def test_release_returns_to_pool(self):
        pool = ObjectPool(create_func=lambda: [])
        obj = pool.get()
        assert pool.count_inactive == 0
        pool.release(obj)
        assert pool.count_inactive == 1

    def test_get_reuses_released_object(self):
        pool = ObjectPool(create_func=lambda: [])
        obj1 = pool.get()
        pool.release(obj1)
        obj2 = pool.get()
        assert obj2 is obj1

    def test_max_size_enforced(self):
        pool = ObjectPool(create_func=lambda: {}, max_size=2)
        objs = [pool.get() for _ in range(3)]
        for o in objs:
            pool.release(o)
        assert pool.count_inactive == 2  # third is discarded

    def test_on_get_callback(self):
        called = []
        pool = ObjectPool(create_func=lambda: "x", on_get=lambda o: called.append(o))
        pool.get()
        assert called == ["x"]

    def test_on_release_callback(self):
        called = []
        pool = ObjectPool(create_func=lambda: "y", on_release=lambda o: called.append(o))
        obj = pool.get()
        pool.release(obj)
        assert called == ["y"]

    def test_on_destroy_when_over_max(self):
        destroyed = []
        pool = ObjectPool(
            create_func=lambda: {},
            on_destroy=lambda o: destroyed.append(o),
            max_size=0,
        )
        obj = pool.get()
        pool.release(obj)
        assert len(destroyed) == 1

    def test_clear_destroys_all(self):
        destroyed = []
        pool = ObjectPool(create_func=lambda: {}, on_destroy=lambda o: destroyed.append(o))
        obj1 = pool.get()
        obj2 = pool.get()
        pool.release(obj1)
        pool.release(obj2)
        pool.clear()
        assert len(destroyed) == 2
        assert pool.count_inactive == 0

    def test_pre_warm(self):
        pool = ObjectPool(create_func=lambda: {}, max_size=10)
        pool.pre_warm(5)
        assert pool.count_inactive == 5

    def test_active_count_tracking(self):
        pool = ObjectPool(create_func=lambda: {})
        assert pool.count_active == 0
        o1 = pool.get()
        o2 = pool.get()
        assert pool.count_active == 2
        pool.release(o1)
        assert pool.count_active == 1


class TestGameObjectPool:
    def test_get_returns_active_gameobject(self):
        pool = GameObjectPool(template_name="Bullet", max_size=10)
        go = pool.get()
        assert isinstance(go, GameObject)
        assert go.active is True

    def test_release_deactivates(self):
        pool = GameObjectPool(template_name="Bullet")
        go = pool.get()
        pool.release(go)
        assert go.active is False

    def test_get_reactivates_pooled(self):
        pool = GameObjectPool(template_name="Bullet")
        go = pool.get()
        pool.release(go)
        go2 = pool.get()
        assert go2 is go
        assert go2.active is True

    def test_naming_convention(self):
        pool = GameObjectPool(template_name="Enemy")
        go1 = pool.get()
        go2 = pool.get()
        assert "Enemy_1" == go1.name
        assert "Enemy_2" == go2.name

    def test_tag_assigned(self):
        pool = GameObjectPool(template_name="Bullet", tag="Projectile")
        go = pool.get()
        assert go.tag == "Projectile"

    def test_pre_warm_creates_inactive(self):
        pool = GameObjectPool(template_name="X", max_size=10)
        pool.pre_warm(3)
        assert pool.count_inactive == 3

    def test_custom_on_get_callback(self):
        called = []
        pool = GameObjectPool(
            template_name="T",
            on_get=lambda go: called.append(go.name),
        )
        pool.get()
        assert len(called) == 1

    def test_clear_empties_pool(self):
        pool = GameObjectPool(template_name="T")
        go = pool.get()
        pool.release(go)
        assert pool.count_inactive == 1
        pool.clear()
        assert pool.count_inactive == 0
