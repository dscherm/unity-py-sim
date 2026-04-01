"""Unity-compatible Mathf static methods."""

from __future__ import annotations

import math


class Mathf:
    """Static math utility class mirroring Unity's Mathf."""

    PI = math.pi
    INFINITY = math.inf
    NEG_INFINITY = -math.inf
    DEG2RAD = math.pi / 180.0
    RAD2DEG = 180.0 / math.pi
    EPSILON = 1e-5

    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        return max(min_val, min(max_val, value))

    @staticmethod
    def clamp01(value: float) -> float:
        return max(0.0, min(1.0, value))

    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        t = max(0.0, min(1.0, t))
        return a + (b - a) * t

    @staticmethod
    def lerp_unclamped(a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    @staticmethod
    def inverse_lerp(a: float, b: float, value: float) -> float:
        if abs(b - a) < 1e-15:
            return 0.0
        return max(0.0, min(1.0, (value - a) / (b - a)))

    @staticmethod
    def move_towards(current: float, target: float, max_delta: float) -> float:
        if abs(target - current) <= max_delta:
            return target
        return current + math.copysign(max_delta, target - current)

    @staticmethod
    def approximately(a: float, b: float) -> bool:
        return abs(b - a) < max(1e-6 * max(abs(a), abs(b)), Mathf.EPSILON * 8.0)

    @staticmethod
    def smooth_step(from_: float, to: float, t: float) -> float:
        t = max(0.0, min(1.0, t))
        t = t * t * (3.0 - 2.0 * t)
        return from_ + (to - from_) * t

    @staticmethod
    def repeat(t: float, length: float) -> float:
        return t - math.floor(t / length) * length

    @staticmethod
    def ping_pong(t: float, length: float) -> float:
        t = Mathf.repeat(t, length * 2.0)
        return length - abs(t - length)

    @staticmethod
    def sign(f: float) -> float:
        if f > 0.0:
            return 1.0
        elif f < 0.0:
            return -1.0
        return 0.0

    @staticmethod
    def abs(f: float) -> float:
        return math.fabs(f)

    @staticmethod
    def floor(f: float) -> int:
        return math.floor(f)

    @staticmethod
    def ceil(f: float) -> int:
        return math.ceil(f)

    @staticmethod
    def round(f: float) -> int:
        return round(f)

    @staticmethod
    def min(a: float, b: float) -> float:
        return min(a, b)

    @staticmethod
    def max(a: float, b: float) -> float:
        return max(a, b)

    @staticmethod
    def sqrt(f: float) -> float:
        return math.sqrt(f)

    @staticmethod
    def pow(f: float, p: float) -> float:
        return math.pow(f, p)

    @staticmethod
    def sin(f: float) -> float:
        return math.sin(f)

    @staticmethod
    def cos(f: float) -> float:
        return math.cos(f)

    @staticmethod
    def atan2(y: float, x: float) -> float:
        return math.atan2(y, x)
