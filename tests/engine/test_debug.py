"""Tests for Debug static class — logging and draw lines."""

import pytest

from src.engine.debug import Debug
from src.engine.math.vector import Vector2, Vector3


@pytest.fixture(autouse=True)
def reset():
    Debug._reset()
    yield
    Debug._reset()


class TestDebugLog:
    def test_log_calls_handler(self):
        messages = []
        Debug._log_handler = lambda level, msg: messages.append((level, msg))
        Debug.log("hello")
        assert messages == [("log", "hello")]

    def test_log_warning(self):
        messages = []
        Debug._log_handler = lambda level, msg: messages.append((level, msg))
        Debug.log_warning("caution")
        assert messages == [("warning", "caution")]

    def test_log_error(self):
        messages = []
        Debug._log_handler = lambda level, msg: messages.append((level, msg))
        Debug.log_error("fail")
        assert messages == [("error", "fail")]

    def test_log_converts_to_string(self):
        messages = []
        Debug._log_handler = lambda level, msg: messages.append((level, msg))
        Debug.log(42)
        assert messages == [("log", "42")]

    def test_log_without_handler_prints(self, capsys):
        Debug.log("test message")
        captured = capsys.readouterr()
        assert "[Log] test message" in captured.out


class TestDebugDrawLine:
    def test_draw_line_adds_line(self):
        Debug.draw_line(Vector2(0, 0), Vector2(1, 1))
        lines = Debug.get_lines()
        assert len(lines) == 1

    def test_draw_line_color(self):
        Debug.draw_line(Vector2(0, 0), Vector2(1, 1), color=(255, 0, 0))
        assert Debug.get_lines()[0].color == (255, 0, 0)

    def test_draw_ray(self):
        Debug.draw_ray(Vector2(0, 0), Vector2(5, 0))
        line = Debug.get_lines()[0]
        assert abs(line.end.x - 5.0) < 0.01
        assert abs(line.end.y - 0.0) < 0.01

    def test_draw_ray_3d(self):
        Debug.draw_ray(Vector3(1, 2, 3), Vector3(0, 1, 0))
        line = Debug.get_lines()[0]
        assert abs(line.end.y - 3.0) < 0.01

    def test_duration_zero_removed_after_tick(self):
        Debug.draw_line(Vector2(0, 0), Vector2(1, 1), duration=0.0)
        assert len(Debug.get_lines()) == 1
        Debug.tick(0.016)
        assert len(Debug.get_lines()) == 0

    def test_duration_persists(self):
        Debug.draw_line(Vector2(0, 0), Vector2(1, 1), duration=1.0)
        Debug.tick(0.5)
        assert len(Debug.get_lines()) == 1
        Debug.tick(0.5)
        assert len(Debug.get_lines()) == 0

    def test_multiple_lines(self):
        Debug.draw_line(Vector2(0, 0), Vector2(1, 0))
        Debug.draw_line(Vector2(0, 0), Vector2(0, 1))
        Debug.draw_line(Vector2(0, 0), Vector2(1, 1))
        assert len(Debug.get_lines()) == 3
