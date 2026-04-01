"""Unity-compatible Vector2 and Vector3 classes backed by numpy."""

from __future__ import annotations

import math
import numpy as np


class _StaticProperty:
    """Descriptor that acts as a read-only property on the class itself."""

    def __init__(self, fn):
        self._fn = fn

    def __get__(self, obj, objtype=None):
        return self._fn()


class Vector2:
    """2D vector mirroring Unity's Vector2."""

    __slots__ = ('_data',)

    def __init__(self, x: float = 0.0, y: float = 0.0):
        self._data = np.array([x, y], dtype=np.float64)

    @property
    def x(self) -> float:
        return float(self._data[0])

    @x.setter
    def x(self, value: float) -> None:
        self._data[0] = value

    @property
    def y(self) -> float:
        return float(self._data[1])

    @y.setter
    def y(self, value: float) -> None:
        self._data[1] = value

    @property
    def magnitude(self) -> float:
        return float(np.linalg.norm(self._data))

    @property
    def sqr_magnitude(self) -> float:
        return float(np.dot(self._data, self._data))

    @property
    def normalized(self) -> Vector2:
        mag = self.magnitude
        if mag < 1e-10:
            return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

    def normalize(self) -> None:
        mag = self.magnitude
        if mag > 1e-10:
            self._data /= mag

    @staticmethod
    def dot(a: Vector2, b: Vector2) -> float:
        return float(np.dot(a._data, b._data))

    @staticmethod
    def distance(a: Vector2, b: Vector2) -> float:
        return float(np.linalg.norm(a._data - b._data))

    @staticmethod
    def lerp(a: Vector2, b: Vector2, t: float) -> Vector2:
        t = max(0.0, min(1.0, t))
        result = a._data + (b._data - a._data) * t
        return Vector2(float(result[0]), float(result[1]))

    @staticmethod
    def angle(from_: Vector2, to: Vector2) -> float:
        denom = math.sqrt(from_.sqr_magnitude * to.sqr_magnitude)
        if denom < 1e-15:
            return 0.0
        d = max(-1.0, min(1.0, Vector2.dot(from_, to) / denom))
        return math.degrees(math.acos(d))

    def __add__(self, other: Vector2) -> Vector2:
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vector2) -> Vector2:
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vector2:
        return Vector2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vector2:
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Vector2:
        return Vector2(self.x / scalar, self.y / scalar)

    def __neg__(self) -> Vector2:
        return Vector2(-self.x, -self.y)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector2):
            return NotImplemented
        return bool(np.allclose(self._data, other._data, atol=1e-5))

    def __repr__(self) -> str:
        return f"Vector2({self.x:.4f}, {self.y:.4f})"

    # Static constructors — accessed as Vector2.zero, Vector2.up, etc.
    zero = _StaticProperty(lambda: Vector2(0, 0))
    one = _StaticProperty(lambda: Vector2(1, 1))
    up = _StaticProperty(lambda: Vector2(0, 1))
    down = _StaticProperty(lambda: Vector2(0, -1))
    left = _StaticProperty(lambda: Vector2(-1, 0))
    right = _StaticProperty(lambda: Vector2(1, 0))


class Vector3:
    """3D vector mirroring Unity's Vector3."""

    __slots__ = ('_data',)

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self._data = np.array([x, y, z], dtype=np.float64)

    @property
    def x(self) -> float:
        return float(self._data[0])

    @x.setter
    def x(self, value: float) -> None:
        self._data[0] = value

    @property
    def y(self) -> float:
        return float(self._data[1])

    @y.setter
    def y(self, value: float) -> None:
        self._data[1] = value

    @property
    def z(self) -> float:
        return float(self._data[2])

    @z.setter
    def z(self, value: float) -> None:
        self._data[2] = value

    @property
    def magnitude(self) -> float:
        return float(np.linalg.norm(self._data))

    @property
    def sqr_magnitude(self) -> float:
        return float(np.dot(self._data, self._data))

    @property
    def normalized(self) -> Vector3:
        mag = self.magnitude
        if mag < 1e-10:
            return Vector3(0, 0, 0)
        return Vector3(self.x / mag, self.y / mag, self.z / mag)

    def normalize(self) -> None:
        mag = self.magnitude
        if mag > 1e-10:
            self._data /= mag

    @staticmethod
    def dot(a: Vector3, b: Vector3) -> float:
        return float(np.dot(a._data, b._data))

    @staticmethod
    def cross(a: Vector3, b: Vector3) -> Vector3:
        result = np.cross(a._data, b._data)
        return Vector3(float(result[0]), float(result[1]), float(result[2]))

    @staticmethod
    def distance(a: Vector3, b: Vector3) -> float:
        return float(np.linalg.norm(a._data - b._data))

    @staticmethod
    def lerp(a: Vector3, b: Vector3, t: float) -> Vector3:
        t = max(0.0, min(1.0, t))
        result = a._data + (b._data - a._data) * t
        return Vector3(float(result[0]), float(result[1]), float(result[2]))

    @staticmethod
    def angle(from_: Vector3, to: Vector3) -> float:
        denom = math.sqrt(from_.sqr_magnitude * to.sqr_magnitude)
        if denom < 1e-15:
            return 0.0
        d = max(-1.0, min(1.0, Vector3.dot(from_, to) / denom))
        return math.degrees(math.acos(d))

    @staticmethod
    def project(vector: Vector3, on_normal: Vector3) -> Vector3:
        sqr_mag = on_normal.sqr_magnitude
        if sqr_mag < 1e-15:
            return Vector3(0, 0, 0)
        d = Vector3.dot(vector, on_normal) / sqr_mag
        return on_normal * d

    @staticmethod
    def reflect(in_direction: Vector3, in_normal: Vector3) -> Vector3:
        factor = -2.0 * Vector3.dot(in_normal, in_direction)
        return Vector3(
            factor * in_normal.x + in_direction.x,
            factor * in_normal.y + in_direction.y,
            factor * in_normal.z + in_direction.z,
        )

    def __add__(self, other: Vector3) -> Vector3:
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vector3) -> Vector3:
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> Vector3:
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> Vector3:
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Vector3:
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __neg__(self) -> Vector3:
        return Vector3(-self.x, -self.y, -self.z)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vector3):
            return NotImplemented
        return bool(np.allclose(self._data, other._data, atol=1e-5))

    def __repr__(self) -> str:
        return f"Vector3({self.x:.4f}, {self.y:.4f}, {self.z:.4f})"

    # Static constructors — accessed as Vector3.zero, Vector3.forward, etc.
    zero = _StaticProperty(lambda: Vector3(0, 0, 0))
    one = _StaticProperty(lambda: Vector3(1, 1, 1))
    up = _StaticProperty(lambda: Vector3(0, 1, 0))
    down = _StaticProperty(lambda: Vector3(0, -1, 0))
    left = _StaticProperty(lambda: Vector3(-1, 0, 0))
    right = _StaticProperty(lambda: Vector3(1, 0, 0))
    forward = _StaticProperty(lambda: Vector3(0, 0, 1))
    back = _StaticProperty(lambda: Vector3(0, 0, -1))
