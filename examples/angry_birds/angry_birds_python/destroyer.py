"""Boundary destroyer — trigger zones at screen edges that destroy stray objects."""

from src.engine.core import GameObject, MonoBehaviour


class Destroyer(MonoBehaviour):

    def on_trigger_enter_2d(self, other):
        tag = other.tag if hasattr(other, 'tag') else ""
        if tag in ("Bird", "Pig", "Brick"):
            GameObject.destroy(other)
