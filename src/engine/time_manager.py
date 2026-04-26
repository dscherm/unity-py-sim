"""Unity-compatible Time static class."""

from __future__ import annotations


class _TimeAccessor:
    """Descriptor that computes Time values on access."""

    def __init__(self, attr: str, scaled: bool = False):
        self._attr = attr
        self._scaled = scaled

    def __get__(self, obj, objtype=None):
        val = getattr(Time, self._attr)
        if self._scaled:
            return val * Time._time_scale
        return val


class Time:
    """Static class mirroring Unity's Time. Updated by the game loop each frame."""

    _delta_time: float = 0.0
    _fixed_delta_time: float = 1.0 / 50.0
    _time: float = 0.0
    _frame_count: int = 0
    _time_scale: float = 1.0

    # Public accessors — accessed as Time.delta_time, Time.time, etc.
    delta_time = _TimeAccessor('_delta_time', scaled=True)
    unscaled_delta_time = _TimeAccessor('_delta_time')
    fixed_delta_time = _TimeAccessor('_fixed_delta_time')
    time = _TimeAccessor('_time')
    frame_count = _TimeAccessor('_frame_count')
    time_scale = _TimeAccessor('_time_scale')

    @staticmethod
    def set_time_scale(value: float) -> None:
        """Set the time scale. Matches Unity's Time.timeScale = value."""
        Time._time_scale = value

    @staticmethod
    def _reset() -> None:
        Time._delta_time = 0.0
        Time._fixed_delta_time = 1.0 / 50.0
        Time._time = 0.0
        Time._frame_count = 0
        Time._time_scale = 1.0
