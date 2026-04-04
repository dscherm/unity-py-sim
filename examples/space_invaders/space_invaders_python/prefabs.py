"""Prefab definitions for Space Invaders.

In Unity these would be .prefab assets configured in the editor.
Here we register setup functions that configure components on a GameObject.
"""

from src.engine.core import GameObject
from src.engine.math.vector import Vector2, Vector3
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.prefab import PrefabRegistry

from space_invaders_python.projectile import Projectile


def _setup_laser(go: GameObject) -> None:
    """Configure a laser projectile prefab."""
    rb = go.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.KINEMATIC

    col = go.add_component(BoxCollider2D)
    col.size = Vector2(0.2, 0.6)
    col.is_trigger = True

    sr = go.add_component(SpriteRenderer)
    sr.color = (100, 255, 100)
    sr.size = Vector2(0.2, 0.6)
    sr.sorting_order = 5

    proj = go.add_component(Projectile)
    proj.direction = Vector3(0, 1, 0)  # Vector3.up
    proj.speed = 20.0


def _setup_missile(go: GameObject) -> None:
    """Configure a missile projectile prefab."""
    rb = go.add_component(Rigidbody2D)
    rb.body_type = RigidbodyType2D.KINEMATIC

    col = go.add_component(BoxCollider2D)
    col.size = Vector2(0.2, 0.6)
    col.is_trigger = True

    sr = go.add_component(SpriteRenderer)
    sr.color = (255, 80, 80)
    sr.size = Vector2(0.2, 0.6)
    sr.sorting_order = 5

    proj = go.add_component(Projectile)
    proj.direction = Vector3(0, -1, 0)  # Vector3.down
    proj.speed = 10.0


def register_prefabs() -> None:
    """Register all Space Invaders prefabs."""
    PrefabRegistry.register("Laser", _setup_laser)
    PrefabRegistry.register("Missile", _setup_missile)
