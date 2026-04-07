"""GhostBehavior — abstract base for ghost AI states.

Port of zigurous GhostBehavior.cs. Uses enable(duration)/disable()
with Invoke for timed transitions between states.

Lesson applied: enabled property must fire on_enable/on_disable callbacks.
"""

from src.engine.core import MonoBehaviour


class GhostBehavior(MonoBehaviour):
    ghost: 'Ghost | None' = None  # Set by Ghost controller
    duration: float = 0.0

    def enable(self, duration: float) -> None:
        self.duration = duration
        self.enabled = True
        self.cancel_invoke("_disable_self")
        if duration > 0:
            self.invoke("_disable_self", duration)

    def disable(self) -> None:
        self.enabled = False
        self.cancel_invoke("_disable_self")

    def _disable_self(self) -> None:
        self.disable()
