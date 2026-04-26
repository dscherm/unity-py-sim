"""Bird projectile — starts kinematic, becomes dynamic on throw."""

from src.engine.core import GameObject, MonoBehaviour
from src.engine.audio import AudioClip, AudioSource
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import CircleCollider2D
from src.engine.coroutine import WaitForSeconds

from .constants import Constants
from .enums import BirdState


class Bird(MonoBehaviour):

    def start(self):
        self.state = BirdState.BEFORE_THROWN
        rb = self.get_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.KINEMATIC
        self._destroy_started = False

    def fixed_update(self):
        if self.state == BirdState.THROWN and not self._destroy_started:
            rb = self.get_component(Rigidbody2D)
            if rb.velocity.sqr_magnitude <= Constants.MIN_VELOCITY:
                self._destroy_started = True
                self.start_coroutine(self._destroy_after(Constants.BIRD_DESTROY_DELAY))

    def on_throw(self):
        """Called by slingshot when bird is released."""
        rb = self.get_component(Rigidbody2D)
        rb.body_type = RigidbodyType2D.DYNAMIC
        self.state = BirdState.THROWN
        # Play throw sound
        audio = self.get_component(AudioSource)
        if audio:
            audio.play()

    def _destroy_after(self, seconds):
        yield WaitForSeconds(seconds)
        GameObject.destroy(self.game_object)
