"""Pig target — destroyed instantly by bird, takes velocity damage from bricks."""

from src.engine.core import GameObject, MonoBehaviour
from src.engine.audio import AudioSource
from src.engine.physics.rigidbody import Rigidbody2D


class Pig(MonoBehaviour):

    def __init__(self):
        super().__init__()
        self.health: float = 150.0
        self._hurt_threshold: float = 120.0

    def on_collision_enter_2d(self, collision):
        other_rb = collision.game_object.get_component(Rigidbody2D)
        if other_rb is None:
            return

        if collision.game_object.tag == "Bird":
            self._play_sound()
            GameObject.destroy(self.game_object)
            return

        damage = collision.relative_velocity.magnitude * 10
        self.health -= damage

        if damage >= 10:
            self._play_sound()

        if self.health < self._hurt_threshold:
            self._show_hurt()

        if self.health <= 0:
            GameObject.destroy(self.game_object)

    def _play_sound(self):
        audio = self.get_component(AudioSource)
        if audio:
            audio.play()

    def _show_hurt(self):
        from src.engine.rendering.renderer import SpriteRenderer
        sr = self.get_component(SpriteRenderer)
        if sr is not None:
            sr.color = (180, 220, 100)  # Yellowish-green = hurt
