"""Trajectory prediction using kinematic equations."""

from __future__ import annotations

from src.engine.math.vector import Vector2


def predict_trajectory(
    start: Vector2,
    velocity: Vector2,
    gravity: Vector2,
    segments: int = 15,
    time_step: float = 0.1,
) -> list[Vector2]:
    """Compute predicted trajectory points using kinematic equations.

    pos(t) = start + velocity * t + 0.5 * gravity * t^2

    Args:
        start: Launch position.
        velocity: Initial velocity.
        gravity: Gravity vector (e.g. Vector2(0, -9.81)).
        segments: Number of trajectory points to compute.
        time_step: Time between each segment.

    Returns:
        List of Vector2 positions along the trajectory.
    """
    points = []
    for i in range(segments):
        t = i * time_step
        x = start.x + velocity.x * t + 0.5 * gravity.x * t * t
        y = start.y + velocity.y * t + 0.5 * gravity.y * t * t
        points.append(Vector2(x, y))
    return points
