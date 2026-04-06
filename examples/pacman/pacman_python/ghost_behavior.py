"""GhostBehavior — abstract base for ghost state machine behaviors.

Line-by-line port of GhostBehavior.cs from zigurous/unity-pacman-tutorial.
Uses coroutine-based duration timer (Unity reference uses Invoke).
"""

from src.engine.core import MonoBehaviour
from src.engine.coroutine import WaitForSeconds


class GhostBehavior(MonoBehaviour):
    ghost: object = None  # Ghost component, set in Ghost.awake()
    duration: float = 0.0
    _duration_coroutine: object = None

    def start(self) -> None:
        from pacman_python.ghost import Ghost
        self.ghost = self.get_component(Ghost)

    def enable_behavior(self, duration: float = -1.0) -> None:
        """Enable this behavior for the given duration."""
        self.enabled = True
        if duration < 0:
            duration = self.duration

        # Cancel previous timer
        if self._duration_coroutine is not None:
            self._duration_coroutine = None

        if duration > 0:
            self._duration_coroutine = self.start_coroutine(
                self._disable_after(duration)
            )

    def disable_behavior(self) -> None:
        """Disable this behavior."""
        self.enabled = False
        self._duration_coroutine = None

    def _disable_after(self, duration: float):
        """Coroutine: wait then disable."""
        yield WaitForSeconds(duration)
        self.disable_behavior()
