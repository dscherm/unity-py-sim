"""Event system — typed event bus and UnityEvent for decoupled messaging.

EventBus: Global publish/subscribe for typed events (dataclass instances).
UnityEvent: Inspector-wirable callback list matching Unity's UnityEvent pattern.

Usage:
    from dataclasses import dataclass
    from src.engine.events import EventBus, UnityEvent

    @dataclass
    class ScoreChanged:
        new_score: int
        delta: int

    # Subscribe and publish
    EventBus.subscribe(ScoreChanged, lambda e: print(f"Score: {e.new_score}"))
    EventBus.publish(ScoreChanged(new_score=100, delta=10))

    # UnityEvent
    on_click = UnityEvent()
    on_click.add_listener(lambda: print("clicked"))
    on_click.invoke()
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

T = TypeVar("T")


class EventBus:
    """Global typed event bus — publish/subscribe pattern."""

    _subscribers: dict[type, list[Callable]] = {}

    @classmethod
    def subscribe(cls, event_type: type, handler: Callable) -> None:
        """Register a handler for an event type."""
        if event_type not in cls._subscribers:
            cls._subscribers[event_type] = []
        cls._subscribers[event_type].append(handler)

    @classmethod
    def unsubscribe(cls, event_type: type, handler: Callable) -> None:
        """Remove a handler for an event type."""
        if event_type in cls._subscribers:
            try:
                cls._subscribers[event_type].remove(handler)
            except ValueError:
                pass

    @classmethod
    def publish(cls, event: Any) -> None:
        """Dispatch an event to all subscribers of its type."""
        event_type = type(event)
        for handler in cls._subscribers.get(event_type, []):
            handler(event)

    @classmethod
    def clear(cls, event_type: type | None = None) -> None:
        """Clear subscribers. If event_type given, clear only that type."""
        if event_type is None:
            cls._subscribers.clear()
        elif event_type in cls._subscribers:
            del cls._subscribers[event_type]

    @classmethod
    def subscriber_count(cls, event_type: type) -> int:
        """Number of subscribers for an event type."""
        return len(cls._subscribers.get(event_type, []))

    @classmethod
    def reset(cls) -> None:
        """Clear all subscribers."""
        cls._subscribers.clear()


class UnityEvent:
    """Callback list matching Unity's UnityEvent pattern.

    Supports zero or more arguments — handlers are called with whatever
    args are passed to invoke().
    """

    def __init__(self):
        self._listeners: list[Callable] = []

    def add_listener(self, callback: Callable) -> None:
        """Add a persistent listener."""
        self._listeners.append(callback)

    def remove_listener(self, callback: Callable) -> None:
        """Remove a listener."""
        try:
            self._listeners.remove(callback)
        except ValueError:
            pass

    def remove_all_listeners(self) -> None:
        """Remove all listeners."""
        self._listeners.clear()

    def invoke(self, *args: Any) -> None:
        """Call all registered listeners with the given arguments."""
        for listener in self._listeners:
            listener(*args)

    @property
    def listener_count(self) -> int:
        return len(self._listeners)
