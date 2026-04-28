"""Object pooling system — matches Unity's UnityEngine.Pool.ObjectPool<T>.

Reuse GameObjects instead of creating/destroying to avoid allocation overhead.

Usage:
    from src.engine.pool import ObjectPool, GameObjectPool

    # Generic pool
    pool = ObjectPool(create_func=lambda: make_bullet(), on_get=lambda b: b.reset())
    bullet = pool.get()
    pool.release(bullet)

    # GameObject pool
    go_pool = GameObjectPool(template_name="Bullet", tag="Bullet", max_size=50)
    bullet_go = go_pool.get()     # Returns inactive GO, activates it
    go_pool.release(bullet_go)    # Deactivates and returns to pool
"""

from __future__ import annotations

from typing import Callable, TypeVar, Generic

from src.engine.core import GameObject

T = TypeVar("T")


class ObjectPool(Generic[T]):
    """Generic object pool matching UnityEngine.Pool.ObjectPool<T>."""

    def __init__(
        self,
        create_func: Callable[[], T],
        on_get: Callable[[T], None] | None = None,
        on_release: Callable[[T], None] | None = None,
        on_destroy: Callable[[T], None] | None = None,
        max_size: int = 100,
    ):
        self._create = create_func
        self._on_get = on_get
        self._on_release = on_release
        self._on_destroy = on_destroy
        self._max_size = max_size
        self._pool: list[T] = []
        self._active_count: int = 0

    def get(self) -> T:
        """Get an object from the pool, or create a new one."""
        if self._pool:
            obj = self._pool.pop()
        else:
            obj = self._create()
        self._active_count += 1
        if self._on_get:
            self._on_get(obj)
        return obj

    def release(self, obj: T) -> None:
        """Return an object to the pool."""
        self._active_count = max(0, self._active_count - 1)
        if self._on_release:
            self._on_release(obj)
        if len(self._pool) < self._max_size:
            self._pool.append(obj)
        elif self._on_destroy:
            self._on_destroy(obj)

    def clear(self) -> None:
        """Destroy all pooled objects."""
        if self._on_destroy:
            for obj in self._pool:
                self._on_destroy(obj)
        self._pool.clear()

    @property
    def count_inactive(self) -> int:
        """Number of objects currently in the pool (inactive)."""
        return len(self._pool)

    @property
    def count_active(self) -> int:
        """Number of objects currently checked out."""
        return self._active_count

    def pre_warm(self, count: int) -> None:
        """Pre-create objects to avoid allocation during gameplay."""
        for _ in range(count):
            obj = self._create()
            if self._on_release:
                self._on_release(obj)
            if len(self._pool) < self._max_size:
                self._pool.append(obj)


class GameObjectPool:
    """Convenience pool for GameObjects — handles activation/deactivation."""

    def __init__(
        self,
        template_name: str = "PooledObject",
        tag: str = "Untagged",
        max_size: int = 100,
        on_get: Callable[[GameObject], None] | None = None,
        on_release: Callable[[GameObject], None] | None = None,
    ):
        self._template_name = template_name
        self._tag = tag
        self._custom_on_get = on_get
        self._custom_on_release = on_release
        self._counter = 0

        self._pool = ObjectPool(
            create_func=self._create_go,
            on_get=self._activate,
            on_release=self._deactivate,
            on_destroy=self._destroy_go,
            max_size=max_size,
        )

    def _create_go(self) -> GameObject:
        self._counter += 1
        go = GameObject(f"{self._template_name}_{self._counter}", tag=self._tag)
        go.active = False
        return go

    def _activate(self, go: GameObject) -> None:
        go.active = True
        if self._custom_on_get:
            self._custom_on_get(go)

    def _deactivate(self, go: GameObject) -> None:
        go.active = False
        if self._custom_on_release:
            self._custom_on_release(go)

    def _destroy_go(self, go: GameObject) -> None:
        go.active = False

    def get(self) -> GameObject:
        return self._pool.get()

    def release(self, go: GameObject) -> None:
        self._pool.release(go)

    def clear(self) -> None:
        self._pool.clear()

    def pre_warm(self, count: int) -> None:
        self._pool.pre_warm(count)

    @property
    def count_inactive(self) -> int:
        return self._pool.count_inactive

    @property
    def count_active(self) -> int:
        return self._pool.count_active
