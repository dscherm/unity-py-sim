"""Tests for Time manager."""

from src.engine.time_manager import Time


class TestTime:
    def setup_method(self):
        Time._reset()

    def test_defaults(self):
        assert Time.delta_time == 0.0
        assert Time.time == 0.0
        assert Time.frame_count == 0
        assert Time.time_scale == 1.0

    def test_fixed_delta_time_default(self):
        assert abs(Time.fixed_delta_time - 0.02) < 0.001

    def test_delta_time_updates(self):
        Time._delta_time = 0.016
        assert abs(Time.delta_time - 0.016) < 1e-5

    def test_time_scale_affects_delta(self):
        Time._delta_time = 0.016
        Time._time_scale = 2.0
        assert abs(Time.delta_time - 0.032) < 1e-5

    def test_unscaled_delta_time(self):
        Time._delta_time = 0.016
        Time._time_scale = 2.0
        assert abs(Time.unscaled_delta_time - 0.016) < 1e-5

    def test_frame_count(self):
        Time._frame_count = 100
        assert Time.frame_count == 100

    def test_time_accumulates(self):
        Time._time = 5.5
        assert abs(Time.time - 5.5) < 1e-5

    def test_reset(self):
        Time._delta_time = 1.0
        Time._time = 99.0
        Time._frame_count = 500
        Time._reset()
        assert Time.delta_time == 0.0
        assert Time.time == 0.0
        assert Time.frame_count == 0
