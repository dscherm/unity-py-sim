"""Unity-compatible coroutine system using Python generators."""

from __future__ import annotations

from typing import Generator


class YieldInstruction:
    """Base class for coroutine yield instructions."""
    pass


class WaitForSeconds(YieldInstruction):
    """Pause a coroutine for a given number of seconds (scaled by Time.timeScale)."""

    def __init__(self, seconds: float) -> None:
        self.seconds = seconds
        self._elapsed = 0.0

    def is_done(self, delta_time: float) -> bool:
        self._elapsed += delta_time
        return self._elapsed >= self.seconds


class WaitForSecondsRealtime(YieldInstruction):
    """Pause a coroutine for real-time seconds (unaffected by timeScale)."""

    def __init__(self, seconds: float) -> None:
        self.seconds = seconds
        self._elapsed = 0.0

    def is_done(self, delta_time: float) -> bool:
        self._elapsed += delta_time
        return self._elapsed >= self.seconds


class WaitForEndOfFrame(YieldInstruction):
    """Wait until end of frame."""

    def is_done(self, delta_time: float) -> bool:
        return True  # Always done after one tick


class WaitForFixedUpdate(YieldInstruction):
    """Wait until next FixedUpdate."""

    def __init__(self) -> None:
        self._ticked = False

    def is_done(self, delta_time: float) -> bool:
        if self._ticked:
            return True
        self._ticked = True
        return False


class WaitUntil(YieldInstruction):
    """Wait until a predicate returns True."""

    def __init__(self, predicate) -> None:
        self._predicate = predicate

    def is_done(self, delta_time: float) -> bool:
        return self._predicate()


class WaitWhile(YieldInstruction):
    """Wait while a predicate returns True."""

    def __init__(self, predicate) -> None:
        self._predicate = predicate

    def is_done(self, delta_time: float) -> bool:
        return not self._predicate()


class Coroutine:
    """Handle to a running coroutine. Can be yielded to wait for completion."""

    def __init__(self, generator: Generator) -> None:
        self._generator = generator
        self._current_yield: YieldInstruction | Coroutine | None = None
        self._finished = False

    @property
    def is_finished(self) -> bool:
        return self._finished

    def tick(self, delta_time: float) -> bool:
        """Advance the coroutine. Returns True if still running, False if finished."""
        if self._finished:
            return False

        # Check if waiting on a yield instruction
        if isinstance(self._current_yield, YieldInstruction):
            if not self._current_yield.is_done(delta_time):
                return True  # Still waiting
        elif isinstance(self._current_yield, Coroutine):
            if not self._current_yield.is_finished:
                return True  # Still waiting on nested coroutine

        # Advance the generator
        try:
            result = next(self._generator)
            if isinstance(result, (YieldInstruction, Coroutine)):
                self._current_yield = result
            else:
                # yield None or any other value = wait one frame
                self._current_yield = None
            return True
        except StopIteration:
            self._finished = True
            return False


class CoroutineManager:
    """Manages all active coroutines. Ticked by LifecycleManager after Update."""

    def __init__(self) -> None:
        self._coroutines: list[tuple[object, Coroutine]] = []  # (owner, coroutine)

    def start_coroutine(self, owner: object, generator: Generator) -> Coroutine:
        """Start a new coroutine owned by a MonoBehaviour."""
        coroutine = Coroutine(generator)
        self._coroutines.append((owner, coroutine))
        # Immediately advance to the first yield
        coroutine.tick(0.0)
        return coroutine

    def stop_coroutine(self, coroutine: Coroutine) -> None:
        """Stop a specific coroutine."""
        self._coroutines = [(o, c) for o, c in self._coroutines if c is not coroutine]
        coroutine._finished = True

    def stop_all_coroutines(self, owner: object) -> None:
        """Stop all coroutines owned by a specific MonoBehaviour."""
        remaining = []
        for o, c in self._coroutines:
            if o is owner:
                c._finished = True
            else:
                remaining.append((o, c))
        self._coroutines = remaining

    def tick(self, delta_time: float) -> None:
        """Advance all active coroutines."""
        still_running = []
        for owner, coroutine in self._coroutines:
            if coroutine.tick(delta_time):
                still_running.append((owner, coroutine))
        self._coroutines = still_running
