"""Prefab registry and Instantiate() — matches Unity's prefab instantiation pattern.

In Unity, prefabs are templates configured in the editor. Instantiate() clones them
at runtime. This module provides an equivalent for the Python simulator:

    # Register a prefab template
    PrefabRegistry.register("Laser", _setup_laser)

    # Instantiate at runtime (translates to UnityEngine.Object.Instantiate())
    laser = Instantiate("Laser", position=pos)
"""

from __future__ import annotations

from typing import Callable

from src.engine.core import GameObject
from src.engine.math.vector import Vector2


# Type for prefab setup functions: takes a GameObject, configures components
PrefabSetupFunc = Callable[[GameObject], None]


class PrefabRegistry:
    """Registry of prefab templates, keyed by name."""

    _prefabs: dict[str, PrefabSetupFunc] = {}

    @classmethod
    def register(cls, name: str, setup_func: PrefabSetupFunc) -> None:
        """Register a prefab template.

        Args:
            name: Prefab name (e.g. "Laser", "Missile", "Invader")
            setup_func: Function that takes a GameObject and adds components to it.
        """
        cls._prefabs[name] = setup_func

    @classmethod
    def get(cls, name: str) -> PrefabSetupFunc | None:
        return cls._prefabs.get(name)

    @classmethod
    def clear(cls) -> None:
        cls._prefabs.clear()


def Instantiate(
    prefab_name: str,
    position: Vector2 | None = None,
    tag: str | None = None,
    name: str | None = None,
) -> GameObject:
    """Instantiate a prefab by name at the given position.

    Translates to: UnityEngine.Object.Instantiate(prefab, position, Quaternion.identity)

    Args:
        prefab_name: Name of the registered prefab
        position: World position (default: origin)
        tag: Optional tag override
        name: Optional name override (defaults to prefab_name)
    """
    setup_func = PrefabRegistry.get(prefab_name)
    if setup_func is None:
        raise KeyError(f"Prefab '{prefab_name}' not registered. "
                       f"Available: {list(PrefabRegistry._prefabs.keys())}")

    go_name = name or prefab_name
    go = GameObject(go_name, tag=tag or "Untagged")

    if position is not None:
        go.transform.position = position

    setup_func(go)
    return go
