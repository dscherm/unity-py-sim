"""GhostBehavior — abstract base for ghost AI states.

Port of zigurous GhostBehavior.cs. Uses enable(duration)/disable()
with Invoke for timed transitions between states.

Lesson applied from v1: enabled property must fire on_enable/on_disable callbacks.
Lesson applied from v1: invoke method name must match exactly ("disable" not "_disable_self").
Lesson applied from v1: default duration=-1 means "use self.duration".
"""

from src.engine.core import MonoBehaviour


class GhostBehavior(MonoBehaviour):
    ghost: 'Ghost | None' = None
    duration: float = 0.0

    def awake(self) -> None:
        # Look up Ghost on same GameObject (Ghost is added before behaviors in scene setup)
        from .ghost import Ghost
        self.ghost = self.get_component(Ghost)

    def enable(self, duration: float = -1.0) -> None:
        """Enable this behavior. duration=-1 means use self.duration.

        Matches v1 exactly: just set enabled=True and invoke disable after duration.
        Do NOT force disable→enable — that kills GhostHome's exit coroutine.
        """
        self.enabled = True

        if duration < 0:
            duration = self.duration

        self.cancel_invoke()
        self.invoke("disable", duration)

    def disable(self) -> None:
        self.enabled = False
        self.cancel_invoke()
