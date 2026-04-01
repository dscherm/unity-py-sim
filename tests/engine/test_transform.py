"""Tests for Transform component."""

import math
import pytest

from src.engine.core import GameObject
from src.engine.transform import Transform
from src.engine.math.vector import Vector3
from src.engine.math.quaternion import Quaternion


class TestTransform:
    def test_default_position(self):
        go = GameObject("Test")
        assert go.transform.position == Vector3(0, 0, 0)

    def test_set_position(self):
        go = GameObject("Test")
        go.transform.position = Vector3(1, 2, 3)
        assert go.transform.position == Vector3(1, 2, 3)

    def test_default_rotation(self):
        go = GameObject("Test")
        assert go.transform.rotation == Quaternion.identity

    def test_default_scale(self):
        go = GameObject("Test")
        assert go.transform.local_scale == Vector3(1, 1, 1)

    def test_translate(self):
        go = GameObject("Test")
        go.transform.position = Vector3(1, 0, 0)
        go.transform.translate(Vector3(2, 3, 0))
        assert go.transform.position == Vector3(3, 3, 0)

    def test_rotate(self):
        go = GameObject("Test")
        go.transform.rotate(Vector3(0, 90, 0))
        forward = go.transform.forward
        # After 90-degree Y rotation, forward should point along X
        assert abs(forward.x - 1.0) < 0.01 or abs(forward.x + 1.0) < 0.01

    def test_forward_default(self):
        go = GameObject("Test")
        assert go.transform.forward == Vector3(0, 0, 1)

    def test_right_default(self):
        go = GameObject("Test")
        assert go.transform.right == Vector3(1, 0, 0)

    def test_up_default(self):
        go = GameObject("Test")
        assert go.transform.up == Vector3(0, 1, 0)


class TestTransformHierarchy:
    def test_set_parent(self):
        parent = GameObject("Parent")
        child = GameObject("Child")
        child.transform.set_parent(parent.transform)
        assert child.transform.parent is parent.transform
        assert child.transform in parent.transform.children

    def test_child_count(self):
        parent = GameObject("Parent")
        c1 = GameObject("C1")
        c2 = GameObject("C2")
        c1.transform.set_parent(parent.transform)
        c2.transform.set_parent(parent.transform)
        assert parent.transform.child_count == 2

    def test_unparent(self):
        parent = GameObject("Parent")
        child = GameObject("Child")
        child.transform.set_parent(parent.transform)
        child.transform.set_parent(None)
        assert child.transform.parent is None
        assert parent.transform.child_count == 0

    def test_reparent(self):
        p1 = GameObject("P1")
        p2 = GameObject("P2")
        child = GameObject("Child")
        child.transform.set_parent(p1.transform)
        assert p1.transform.child_count == 1
        child.transform.set_parent(p2.transform)
        assert p1.transform.child_count == 0
        assert p2.transform.child_count == 1


class TestTransformCoordinates:
    def test_transform_point_identity(self):
        go = GameObject("Test")
        local = Vector3(1, 2, 3)
        world = go.transform.transform_point(local)
        assert world == local

    def test_transform_point_with_position(self):
        go = GameObject("Test")
        go.transform.position = Vector3(10, 0, 0)
        world = go.transform.transform_point(Vector3(1, 0, 0))
        assert world == Vector3(11, 0, 0)

    def test_transform_point_with_scale(self):
        go = GameObject("Test")
        go.transform.local_scale = Vector3(2, 2, 2)
        world = go.transform.transform_point(Vector3(1, 1, 1))
        assert world == Vector3(2, 2, 2)

    def test_inverse_transform_point_roundtrip(self):
        go = GameObject("Test")
        go.transform.position = Vector3(5, 10, 15)
        go.transform.rotation = Quaternion.euler(30, 45, 0)
        go.transform.local_scale = Vector3(2, 2, 2)

        local = Vector3(1, 2, 3)
        world = go.transform.transform_point(local)
        back = go.transform.inverse_transform_point(world)
        assert abs(back.x - local.x) < 0.01
        assert abs(back.y - local.y) < 0.01
        assert abs(back.z - local.z) < 0.01

    def test_look_at(self):
        go = GameObject("Test")
        go.transform.look_at(Vector3(0, 0, 10))
        # Should face forward (0, 0, 1)
        fwd = go.transform.forward
        assert abs(fwd.z - 1.0) < 0.1
