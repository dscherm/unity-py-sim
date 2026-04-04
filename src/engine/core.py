"""Core Unity component system: Component, MonoBehaviour, GameObject."""

from __future__ import annotations

from typing import TypeVar, Type

T = TypeVar('T', bound='Component')

# Global registry for GameObject.find() and find_with_tag()
_game_objects: dict[int, 'GameObject'] = {}
_name_index: dict[str, list[int]] = {}
_tag_index: dict[str, list[int]] = {}

_next_instance_id: int = 0


def _get_next_id() -> int:
    global _next_instance_id
    _next_instance_id += 1
    return _next_instance_id


def _clear_registry() -> None:
    """Clear all global state. Used in tests."""
    global _next_instance_id
    _game_objects.clear()
    _name_index.clear()
    _tag_index.clear()
    _next_instance_id = 0
    # Reset coroutine manager (MonoBehaviour defined later in this module)
    try:
        if hasattr(MonoBehaviour, '_coroutine_manager'):
            del MonoBehaviour._coroutine_manager
    except NameError:
        pass


class Component:
    """Base class for all components attached to GameObjects."""

    def __init__(self) -> None:
        self._game_object: GameObject | None = None
        self.enabled: bool = True

    @property
    def game_object(self) -> GameObject:
        assert self._game_object is not None, "Component not attached to a GameObject"
        return self._game_object

    @property
    def transform(self) -> 'Transform':
        return self.game_object.transform

    def get_component(self, cls: Type[T]) -> T | None:
        return self.game_object.get_component(cls)

    # Lifecycle stubs — overridden by MonoBehaviour subclasses
    def awake(self) -> None:
        pass

    def start(self) -> None:
        pass

    def on_destroy(self) -> None:
        pass


class MonoBehaviour(Component):
    """Base class for Unity scripts. Provides lifecycle methods."""

    def start_coroutine(self, generator):
        """Start a coroutine on this MonoBehaviour."""
        from src.engine.coroutine import CoroutineManager
        if not hasattr(MonoBehaviour, '_coroutine_manager'):
            MonoBehaviour._coroutine_manager = CoroutineManager()
        return MonoBehaviour._coroutine_manager.start_coroutine(self, generator)

    def stop_coroutine(self, coroutine) -> None:
        """Stop a specific coroutine."""
        if hasattr(MonoBehaviour, '_coroutine_manager'):
            MonoBehaviour._coroutine_manager.stop_coroutine(coroutine)

    def stop_all_coroutines(self) -> None:
        """Stop all coroutines owned by this MonoBehaviour."""
        if hasattr(MonoBehaviour, '_coroutine_manager'):
            MonoBehaviour._coroutine_manager.stop_all_coroutines(self)

    def update(self) -> None:
        pass

    def fixed_update(self) -> None:
        pass

    def late_update(self) -> None:
        pass

    def on_enable(self) -> None:
        pass

    def on_disable(self) -> None:
        pass

    def on_collision_enter_2d(self, collision: object) -> None:
        pass

    def on_collision_exit_2d(self, collision: object) -> None:
        pass

    def on_trigger_enter_2d(self, other: object) -> None:
        pass

    def on_collision_stay_2d(self, collision: object) -> None:
        pass

    def on_trigger_exit_2d(self, other: object) -> None:
        pass

    def on_trigger_stay_2d(self, other: object) -> None:
        pass


class GameObject:
    """Unity-style GameObject with component system and global registry."""

    def __init__(self, name: str = "GameObject", tag: str = "Untagged") -> None:
        self.instance_id: int = _get_next_id()
        self._name: str = name
        self._tag: str = tag
        self.layer: int = 0
        self.active: bool = True
        self._components: list[Component] = []
        self._transform: 'Transform | None' = None

        # Register in global indices
        _game_objects[self.instance_id] = self
        _name_index.setdefault(name, []).append(self.instance_id)
        _tag_index.setdefault(tag, []).append(self.instance_id)

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        # Update name index
        old_ids = _name_index.get(self._name, [])
        if self.instance_id in old_ids:
            old_ids.remove(self.instance_id)
        self._name = value
        _name_index.setdefault(value, []).append(self.instance_id)

    @property
    def tag(self) -> str:
        return self._tag

    @tag.setter
    def tag(self, value: str) -> None:
        old_ids = _tag_index.get(self._tag, [])
        if self.instance_id in old_ids:
            old_ids.remove(self.instance_id)
        self._tag = value
        _tag_index.setdefault(value, []).append(self.instance_id)

    @property
    def transform(self) -> 'Transform':
        if self._transform is None:
            # Lazy import to avoid circular dependency
            from src.engine.transform import Transform
            self._transform = self.add_component(Transform)
        return self._transform

    def add_component(self, cls: Type[T], **kwargs) -> T:
        """Add a component of the given type to this GameObject.

        Automatically registers MonoBehaviour components with LifecycleManager,
        matching Unity's behavior where AddComponent triggers Awake/Start.
        """
        component = cls(**kwargs)
        component._game_object = self
        self._components.append(component)

        # Track Transform specially
        from src.engine.transform import Transform
        if isinstance(component, Transform) and self._transform is None:
            self._transform = component

        # Auto-register with LifecycleManager (Unity does this automatically)
        from src.engine.lifecycle import LifecycleManager
        LifecycleManager.instance().register_component(component)

        return component

    def get_component(self, cls: Type[T]) -> T | None:
        """Get the first component of the given type."""
        for comp in self._components:
            if isinstance(comp, cls):
                return comp
        return None

    def get_components(self, cls: Type[T]) -> list[T]:
        """Get all components of the given type."""
        return [comp for comp in self._components if isinstance(comp, cls)]

    def get_components_in_children(self, cls: Type[T]) -> list[T]:
        """Get components of type in this object and all children."""
        results = self.get_components(cls)
        for child in self.transform.children:
            results.extend(child.game_object.get_components_in_children(cls))
        return results

    @staticmethod
    def find(name: str) -> 'GameObject | None':
        """Find a GameObject by name."""
        ids = _name_index.get(name, [])
        for obj_id in ids:
            obj = _game_objects.get(obj_id)
            if obj is not None and obj.active:
                return obj
        return None

    @staticmethod
    def find_with_tag(tag: str) -> 'GameObject | None':
        """Find first active GameObject with the given tag."""
        ids = _tag_index.get(tag, [])
        for obj_id in ids:
            obj = _game_objects.get(obj_id)
            if obj is not None and obj.active:
                return obj
        return None

    @staticmethod
    def find_game_objects_with_tag(tag: str) -> list['GameObject']:
        """Find all active GameObjects with the given tag."""
        ids = _tag_index.get(tag, [])
        result = []
        for obj_id in ids:
            obj = _game_objects.get(obj_id)
            if obj is not None and obj.active:
                result.append(obj)
        return result

    @staticmethod
    def destroy(obj: 'GameObject | Component', delay: float = 0.0) -> None:
        """Mark a GameObject or Component for destruction."""
        if isinstance(obj, Component):
            go = obj.game_object
        else:
            go = obj

        # Remove from registry
        _game_objects.pop(go.instance_id, None)
        ids = _name_index.get(go.name, [])
        if go.instance_id in ids:
            ids.remove(go.instance_id)
        ids = _tag_index.get(go.tag, [])
        if go.instance_id in ids:
            ids.remove(go.instance_id)

        # Call on_destroy on all components
        for comp in go._components:
            comp.on_destroy()

        go.active = False

    def __repr__(self) -> str:
        return f"GameObject('{self.name}', tag='{self.tag}')"


# Avoid circular import at module level — Transform needs to be importable from here
# Import is deferred in the methods above
