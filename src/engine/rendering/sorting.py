"""Sorting layer system — named sorting layers for render ordering.

Matches Unity's sorting layer system. SpriteRenderers are sorted by layer
first, then by sorting_order within each layer.

Usage:
    SortingLayer.add("Foreground", 100)
    sr.sorting_layer_name = "Foreground"
"""

from __future__ import annotations


class SortingLayer:
    """Registry of named sorting layers with numeric order values."""

    _layers: dict[str, int] = {
        "Default": 0,
        "Background": -100,
        "Foreground": 100,
        "UI": 200,
    }

    @classmethod
    def add(cls, name: str, order: int) -> None:
        """Register a named sorting layer."""
        cls._layers[name] = order

    @classmethod
    def get_layer_value(cls, name: str) -> int:
        """Get the sort order for a layer name. Returns 0 for unknown."""
        return cls._layers.get(name, 0)

    @classmethod
    def get_all(cls) -> dict[str, int]:
        """Get all registered layers."""
        return dict(cls._layers)

    @classmethod
    def reset(cls) -> None:
        """Reset to default layers."""
        cls._layers = {
            "Default": 0,
            "Background": -100,
            "Foreground": 100,
            "UI": 200,
        }
