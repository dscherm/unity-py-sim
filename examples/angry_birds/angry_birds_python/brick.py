"""Destructible brick/block — takes velocity-based damage on collision."""

from src.engine.core import GameObject, MonoBehaviour
from src.engine.audio import AudioSource
from src.engine.physics.rigidbody import Rigidbody2D


class Brick(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.health: float = 70.0
        self.max_health: float = 70.0

    def on_collision_enter_2d(self, collision):
        other_rb = collision.game_object.get_component(Rigidbody2D)
        if other_rb is None:
            return

        damage = collision.relative_velocity.magnitude * 10
        if damage < 5:
            return  # Ignore tiny bumps

        if damage >= 10:
            audio = self.get_component(AudioSource)
            if audio:
                audio.play()

        self.health -= damage

        if self.health <= 0:
            GameObject.destroy(self.game_object)
        else:
            # Darken color based on damage
            self._update_color()

    def _update_color(self):
        from src.engine.rendering.renderer import SpriteRenderer
        sr = self.get_component(SpriteRenderer)
        if sr is None:
            return
        ratio = max(0.3, self.health / self.max_health)
        r, g, b = sr.color
        sr.color = (int(r * ratio), int(g * ratio), int(b * ratio))
