"""Tests for trajectory prediction."""


from src.engine.math.vector import Vector2
from src.engine.trajectory import predict_trajectory


class TestTrajectory:
    def test_straight_horizontal(self):
        """No gravity, horizontal launch — straight line."""
        points = predict_trajectory(
            start=Vector2(0, 0),
            velocity=Vector2(10, 0),
            gravity=Vector2(0, 0),
            segments=5,
            time_step=0.1,
        )
        assert len(points) == 5
        # Points should be along x axis
        for i, p in enumerate(points):
            assert abs(p.x - 10 * i * 0.1) < 0.01
            assert abs(p.y) < 0.01

    def test_parabolic_arc(self):
        """With gravity, should form a parabola."""
        points = predict_trajectory(
            start=Vector2(0, 0),
            velocity=Vector2(10, 10),
            gravity=Vector2(0, -9.81),
            segments=10,
            time_step=0.1,
        )
        assert len(points) == 10
        # First point at origin
        assert abs(points[0].x) < 0.01
        assert abs(points[0].y) < 0.01
        # Points should rise initially
        assert points[3].y > points[1].y  # Rising early on
        # Y velocity decreases over time due to gravity
        dy_early = points[2].y - points[1].y
        dy_late = points[9].y - points[8].y
        assert dy_late < dy_early  # Gravity slows vertical rise

    def test_pure_freefall(self):
        """No initial velocity, just gravity."""
        points = predict_trajectory(
            start=Vector2(0, 10),
            velocity=Vector2(0, 0),
            gravity=Vector2(0, -9.81),
            segments=5,
            time_step=0.2,
        )
        # y should decrease
        for i in range(1, len(points)):
            assert points[i].y < points[i - 1].y

    def test_segment_count(self):
        points = predict_trajectory(
            start=Vector2(0, 0),
            velocity=Vector2(5, 5),
            gravity=Vector2(0, -9.81),
            segments=20,
        )
        assert len(points) == 20

    def test_first_point_is_start(self):
        start = Vector2(3, 7)
        points = predict_trajectory(
            start=start,
            velocity=Vector2(10, 10),
            gravity=Vector2(0, -9.81),
        )
        assert abs(points[0].x - 3) < 0.01
        assert abs(points[0].y - 7) < 0.01
