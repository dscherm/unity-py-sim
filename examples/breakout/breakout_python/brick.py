"""Brick — destroyable block in the grid."""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.physics.collider import BoxCollider2D


class Brick(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.points: int = 10
        self.health: int = 1

    def on_collision_enter_2d(self, collision):
        if collision.game_object.tag == "Ball" or collision.game_object.name == "Ball":
            self.health -= 1
            if self.health <= 0:
                self.destroy()

    def destroy(self):
        """Remove brick from game."""
        from breakout_python.game_manager import GameManager
        from breakout_python.powerup import maybe_spawn_powerup

        GameManager.add_score(self.points)

        # Spawn powerup chance
        maybe_spawn_powerup(self.transform.position)

        self.game_object.active = False
        # Remove physics body
        collider = self.get_component(BoxCollider2D)
        if collider and hasattr(collider, '_shape') and collider._shape:
            from src.engine.physics.physics_manager import PhysicsManager
            pm = PhysicsManager.instance()
            try:
                pm._space.remove(collider._shape, collider._shape.body)
            except Exception:
                pass
        GameManager.on_brick_destroyed()
