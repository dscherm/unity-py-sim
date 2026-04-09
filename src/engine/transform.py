"""Unity-compatible Transform component."""

from __future__ import annotations

from src.engine.core import Component
from src.engine.math.vector import Vector2, Vector3
from src.engine.math.quaternion import Quaternion


class Transform(Component):
    """Transform component — position, rotation, scale, and parent-child hierarchy."""

    def __init__(self) -> None:
        super().__init__()
        self._position: Vector3 = Vector3(0, 0, 0)
        self._rotation: Quaternion = Quaternion(0, 0, 0, 1)
        self._local_scale: Vector3 = Vector3(1, 1, 1)
        self._parent: Transform | None = None
        self._children: list[Transform] = []

    @property
    def position(self) -> Vector3:
        return self._position

    @position.setter
    def position(self, value: Vector3 | Vector2) -> None:
        if isinstance(value, Vector2):
            self._position = Vector3(value.x, value.y, 0)
        else:
            self._position = value

    @property
    def rotation(self) -> Quaternion:
        return self._rotation

    @rotation.setter
    def rotation(self, value: Quaternion) -> None:
        self._rotation = value

    @property
    def local_scale(self) -> Vector3:
        return self._local_scale

    @local_scale.setter
    def local_scale(self, value: Vector3) -> None:
        self._local_scale = value

    @property
    def euler_angles(self) -> Vector3:
        """Get rotation as euler angles in degrees. Matches Unity's transform.eulerAngles."""
        return self._rotation.euler_angles

    @euler_angles.setter
    def euler_angles(self, value: Vector3) -> None:
        """Set rotation from euler angles in degrees. Matches Unity's transform.eulerAngles = ..."""
        self._rotation = Quaternion.euler(value.x, value.y, value.z)

    @property
    def parent(self) -> Transform | None:
        return self._parent

    @property
    def children(self) -> list[Transform]:
        return list(self._children)

    @property
    def child_count(self) -> int:
        return len(self._children)

    @property
    def forward(self) -> Vector3:
        return self._rotation.rotate_vector(Vector3(0, 0, 1))

    @property
    def right(self) -> Vector3:
        return self._rotation.rotate_vector(Vector3(1, 0, 0))

    @property
    def up(self) -> Vector3:
        return self._rotation.rotate_vector(Vector3(0, 1, 0))

    def set_parent(self, new_parent: Transform | None) -> None:
        """Set the parent of this transform."""
        if self._parent is not None:
            self._parent._children.remove(self)
        self._parent = new_parent
        if new_parent is not None:
            new_parent._children.append(self)

    def translate(self, delta: Vector3 | Vector2) -> None:
        """Move by delta in world space. Accepts Vector2 (z=0) or Vector3."""
        if isinstance(delta, Vector2):
            delta = Vector3(delta.x, delta.y, 0)
        self._position = self._position + delta

    def rotate(self, euler_angles: Vector3) -> None:
        """Rotate by euler angles (degrees)."""
        rot = Quaternion.euler(euler_angles.x, euler_angles.y, euler_angles.z)
        self._rotation = self._rotation * rot

    def look_at(self, target: Vector3) -> None:
        """Rotate to face a target position (simplified — Y-up)."""
        direction = target - self._position
        if direction.magnitude < 1e-10:
            return
        direction = direction.normalized
        # Simple look-at: compute yaw and pitch
        import math
        yaw = math.degrees(math.atan2(direction.x, direction.z))
        pitch = math.degrees(math.asin(-direction.y))
        self._rotation = Quaternion.euler(pitch, yaw, 0)

    def transform_point(self, local_point: Vector3) -> Vector3:
        """Convert a local-space point to world space."""
        rotated = self._rotation.rotate_vector(Vector3(
            local_point.x * self._local_scale.x,
            local_point.y * self._local_scale.y,
            local_point.z * self._local_scale.z,
        ))
        return self._position + rotated

    def inverse_transform_point(self, world_point: Vector3) -> Vector3:
        """Convert a world-space point to local space."""
        delta = world_point - self._position
        inv_rot = Quaternion(
            -self._rotation.x, -self._rotation.y, -self._rotation.z, self._rotation.w
        )
        local = inv_rot.rotate_vector(delta)
        sx = self._local_scale.x if abs(self._local_scale.x) > 1e-10 else 1.0
        sy = self._local_scale.y if abs(self._local_scale.y) > 1e-10 else 1.0
        sz = self._local_scale.z if abs(self._local_scale.z) > 1e-10 else 1.0
        return Vector3(local.x / sx, local.y / sy, local.z / sz)
