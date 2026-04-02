"""Unity lifecycle manager — orchestrates the Awake/Start/Update/FixedUpdate/LateUpdate loop."""

from __future__ import annotations

from src.engine.core import Component, MonoBehaviour


class LifecycleManager:
    """Singleton that manages component lifecycle in Unity's execution order."""

    _instance: LifecycleManager | None = None

    def __init__(self) -> None:
        self._awake_queue: list[Component] = []
        self._start_queue: list[Component] = []
        self._update_list: list[MonoBehaviour] = []
        self._fixed_update_list: list[MonoBehaviour] = []
        self._late_update_list: list[MonoBehaviour] = []
        self._destroy_queue: list[Component] = []

    @classmethod
    def instance(cls) -> LifecycleManager:
        if cls._instance is None:
            cls._instance = LifecycleManager()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    def register_component(self, comp: Component) -> None:
        """Register a component for lifecycle management. Called when added to a GameObject."""
        self._awake_queue.append(comp)

    def unregister_component(self, comp: Component) -> None:
        """Remove a component from all lifecycle lists."""
        for lst in (self._update_list, self._fixed_update_list, self._late_update_list):
            if comp in lst:
                lst.remove(comp)
        # Remove from queues too
        if comp in self._awake_queue:
            self._awake_queue.remove(comp)
        if comp in self._start_queue:
            self._start_queue.remove(comp)

    def schedule_destroy(self, comp: Component) -> None:
        """Schedule a component for destruction at end of frame."""
        if comp not in self._destroy_queue:
            self._destroy_queue.append(comp)

    def process_awake_queue(self) -> None:
        """Process all components waiting for Awake."""
        while self._awake_queue:
            comp = self._awake_queue.pop(0)
            if comp.enabled:
                comp.awake()
                self._start_queue.append(comp)

    def process_start_queue(self) -> None:
        """Process all components waiting for Start."""
        while self._start_queue:
            comp = self._start_queue.pop(0)
            if comp.enabled:
                comp.start()
                if isinstance(comp, MonoBehaviour):
                    self._update_list.append(comp)
                    self._fixed_update_list.append(comp)
                    self._late_update_list.append(comp)

    def run_fixed_update(self) -> None:
        """Run FixedUpdate on all registered MonoBehaviours."""
        for comp in list(self._fixed_update_list):
            if comp.enabled:
                comp.fixed_update()

    def run_update(self) -> None:
        """Run Update on all registered MonoBehaviours."""
        for comp in list(self._update_list):
            if comp.enabled:
                comp.update()
        # Tick coroutines after Update (Unity order)
        self._tick_coroutines()

    def _tick_coroutines(self) -> None:
        """Advance all active coroutines."""
        from src.engine.time_manager import Time
        if hasattr(MonoBehaviour, '_coroutine_manager'):
            MonoBehaviour._coroutine_manager.tick(Time.delta_time)

    def run_late_update(self) -> None:
        """Run LateUpdate on all registered MonoBehaviours."""
        for comp in list(self._late_update_list):
            if comp.enabled:
                comp.late_update()

    def process_destroy_queue(self) -> None:
        """Process pending destructions."""
        while self._destroy_queue:
            comp = self._destroy_queue.pop(0)
            self.unregister_component(comp)
            comp.on_destroy()
