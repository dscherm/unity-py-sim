"""Scene management — global registry access and scene setup."""

from __future__ import annotations

from src.engine.core import _game_objects, _clear_registry, GameObject


class SceneManager:
    """Provides scene-level operations on the global GameObject registry."""

    @staticmethod
    def get_all_game_objects() -> list[GameObject]:
        """Return all active GameObjects."""
        return [go for go in _game_objects.values() if go.active]

    @staticmethod
    def clear() -> None:
        """Destroy all GameObjects and reset the registry."""
        _clear_registry()
