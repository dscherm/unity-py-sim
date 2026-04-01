"""Unity-compatible Quaternion class backed by pyrr."""

from __future__ import annotations

import math
import numpy as np
from pyrr import quaternion as pyrr_quat

from src.engine.math.vector import Vector3, _StaticProperty


class Quaternion:
    """Quaternion mirroring Unity's Quaternion. Stored as (x, y, z, w)."""

    __slots__ = ('_data',)

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0, w: float = 1.0):
        self._data = np.array([x, y, z, w], dtype=np.float64)

    @property
    def x(self) -> float:
        return float(self._data[0])

    @property
    def y(self) -> float:
        return float(self._data[1])

    @property
    def z(self) -> float:
        return float(self._data[2])

    @property
    def w(self) -> float:
        return float(self._data[3])

    @property
    def euler_angles(self) -> Vector3:
        """Convert quaternion to euler angles (degrees) in Unity's ZXY order."""
        x, y, z, w = self._data

        # Roll (X)
        sinr_cosp = 2.0 * (w * x + y * z)
        cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)

        # Pitch (Y)
        sinp = 2.0 * (w * y - z * x)
        if abs(sinp) >= 1.0:
            pitch = math.copysign(math.pi / 2.0, sinp)
        else:
            pitch = math.asin(sinp)

        # Yaw (Z)
        siny_cosp = 2.0 * (w * z + x * y)
        cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)

        return Vector3(math.degrees(roll), math.degrees(pitch), math.degrees(yaw))

    @staticmethod
    def euler(x: float, y: float, z: float) -> Quaternion:
        """Create quaternion from euler angles in degrees."""
        x_rad = math.radians(x) * 0.5
        y_rad = math.radians(y) * 0.5
        z_rad = math.radians(z) * 0.5

        cx, sx = math.cos(x_rad), math.sin(x_rad)
        cy, sy = math.cos(y_rad), math.sin(y_rad)
        cz, sz = math.cos(z_rad), math.sin(z_rad)

        qw = cx * cy * cz + sx * sy * sz
        qx = sx * cy * cz - cx * sy * sz
        qy = cx * sy * cz + sx * cy * sz
        qz = cx * cy * sz - sx * sy * cz

        return Quaternion(qx, qy, qz, qw)

    @staticmethod
    def angle_axis(angle: float, axis: Vector3) -> Quaternion:
        """Create quaternion from angle (degrees) and axis."""
        rad = math.radians(angle) * 0.5
        s = math.sin(rad)
        norm = axis.normalized
        return Quaternion(norm.x * s, norm.y * s, norm.z * s, math.cos(rad))

    @staticmethod
    def slerp(a: Quaternion, b: Quaternion, t: float) -> Quaternion:
        """Spherical linear interpolation between two quaternions."""
        t = max(0.0, min(1.0, t))
        result = pyrr_quat.slerp(a._data, b._data, t)
        return Quaternion(float(result[0]), float(result[1]), float(result[2]), float(result[3]))

    @staticmethod
    def angle(a: Quaternion, b: Quaternion) -> float:
        """Returns the angle in degrees between two rotations."""
        dot = min(abs(Quaternion._dot(a, b)), 1.0)
        return math.degrees(2.0 * math.acos(dot))

    @staticmethod
    def _dot(a: Quaternion, b: Quaternion) -> float:
        return float(np.dot(a._data, b._data))

    def __mul__(self, other: Quaternion) -> Quaternion:
        """Quaternion multiplication (rotation composition)."""
        result = pyrr_quat.cross(self._data, other._data)
        return Quaternion(float(result[0]), float(result[1]), float(result[2]), float(result[3]))

    def rotate_vector(self, v: Vector3) -> Vector3:
        """Rotate a Vector3 by this quaternion."""
        qv = np.array([v.x, v.y, v.z, 0.0], dtype=np.float64)
        conj = pyrr_quat.conjugate(self._data)
        result = pyrr_quat.cross(pyrr_quat.cross(self._data, qv), conj)
        return Vector3(float(result[0]), float(result[1]), float(result[2]))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Quaternion):
            return NotImplemented
        return bool(np.allclose(self._data, other._data, atol=1e-5))

    def __repr__(self) -> str:
        return f"Quaternion({self.x:.4f}, {self.y:.4f}, {self.z:.4f}, {self.w:.4f})"

    identity = _StaticProperty(lambda: Quaternion(0, 0, 0, 1))
