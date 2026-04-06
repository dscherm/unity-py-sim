"""GhostBehavior — abstract base for ghost state machine behaviors.

Line-by-line port of GhostBehavior.cs from zigurous/unity-pacman-tutorial.
"""

from src.engine.core import MonoBehaviour


class GhostBehavior(MonoBehaviour):
    ghost: object = None  # Ghost component, set in awake
    duration: float = 0.0

    def awake(self) -> None:
        from pacman_python.ghost import Ghost
        self.ghost = self.get_component(Ghost)

    def enable(self, duration: float = -1.0) -> None:
        """Enable this behavior. Matches C# Enable() / Enable(float)."""
        self.enabled = True
        if duration < 0:
            duration = self.duration

        self.cancel_invoke()
        self.invoke("disable", duration)

    def disable(self) -> None:
        """Disable this behavior. Matches C# Disable()."""
        self.enabled = False
        self.cancel_invoke()
