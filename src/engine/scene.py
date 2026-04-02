"""Scene management — global registry access and scene setup."""

from __future__ import annotations

from typing import Callable

from src.engine.core import _game_objects, _clear_registry, GameObject


class SceneManager:
    """Provides scene-level operations on the global GameObject registry."""

    _scenes: dict[str, Callable] = {}
    _scene_by_index: list[str] = []
    _active_scene: str | None = None
    _dont_destroy: set[int] = set()  # instance_ids of persistent GameObjects

    @staticmethod
    def get_all_game_objects() -> list[GameObject]:
        """Return all active GameObjects."""
        return [go for go in _game_objects.values() if go.active]

    @staticmethod
    def clear() -> None:
        """Destroy all GameObjects and reset the registry."""
        _clear_registry()
        SceneManager._scenes.clear()
        SceneManager._scene_by_index.clear()
        SceneManager._active_scene = None
        SceneManager._dont_destroy.clear()

    @staticmethod
    def register_scene(name: str, setup: Callable) -> None:
        """Register a scene setup callable by name."""
        if name not in SceneManager._scenes:
            SceneManager._scene_by_index.append(name)
        SceneManager._scenes[name] = setup

    @staticmethod
    def load_scene(name_or_index) -> None:
        """Load a scene by name or index. Destroys all non-persistent GameObjects."""
        if isinstance(name_or_index, int):
            if 0 <= name_or_index < len(SceneManager._scene_by_index):
                name = SceneManager._scene_by_index[name_or_index]
            else:
                raise ValueError(f"Scene index {name_or_index} out of range")
        else:
            name = name_or_index

        if name not in SceneManager._scenes:
            raise ValueError(f"Scene '{name}' not registered")

        # Destroy all non-persistent GameObjects
        for go in list(_game_objects.values()):
            if go.instance_id not in SceneManager._dont_destroy:
                GameObject.destroy(go)

        SceneManager._active_scene = name
        SceneManager._scenes[name]()

    @staticmethod
    def get_active_scene() -> str | None:
        """Return the name of the active scene."""
        return SceneManager._active_scene

    @staticmethod
    def get_scene_count() -> int:
        """Return number of registered scenes."""
        return len(SceneManager._scenes)


def dont_destroy_on_load(game_object: GameObject) -> None:
    """Mark a GameObject to persist across scene loads."""
    SceneManager._dont_destroy.add(game_object.instance_id)
