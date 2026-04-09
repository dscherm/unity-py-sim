"""Unity-compatible Random static class."""

from __future__ import annotations

import random as _random


class Random:
    """Static class mirroring Unity's UnityEngine.Random."""

    @staticmethod
    def range(min_val: float, max_val: float) -> float:
        """Return a random float between min (inclusive) and max (inclusive).

        Matches Unity's Random.Range(float min, float max).
        """
        return _random.uniform(min_val, max_val)

    @staticmethod
    def range_int(min_val: int, max_val: int) -> int:
        """Return a random int between min (inclusive) and max (exclusive).

        Matches Unity's Random.Range(int min, int max).
        """
        return _random.randint(min_val, max_val - 1)
