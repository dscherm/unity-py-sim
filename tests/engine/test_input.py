"""Tests for Input manager."""

from src.engine.input_manager import Input


class TestInput:
    def setup_method(self):
        Input._reset()

    def test_no_keys_pressed(self):
        assert Input.get_key("w") is False

    def test_get_key(self):
        Input._set_key_state("w", True)
        assert Input.get_key("w") is True

    def test_get_key_case_insensitive(self):
        Input._set_key_state("W", True)
        assert Input.get_key("w") is True

    def test_get_key_down(self):
        Input._begin_frame()
        Input._set_key_state("w", True)
        assert Input.get_key_down("w") is True

    def test_get_key_down_not_on_hold(self):
        Input._set_key_state("w", True)
        Input._begin_frame()  # w was in previous and current
        assert Input.get_key_down("w") is False

    def test_get_key_up(self):
        Input._set_key_state("w", True)
        Input._begin_frame()
        Input._set_key_state("w", False)
        assert Input.get_key_up("w") is True

    def test_get_key_up_not_when_held(self):
        Input._set_key_state("w", True)
        Input._begin_frame()
        assert Input.get_key_up("w") is False

    def test_axis_horizontal_right(self):
        Input._set_key_state("d", True)
        assert Input.get_axis("Horizontal") == 1.0

    def test_axis_horizontal_left(self):
        Input._set_key_state("a", True)
        assert Input.get_axis("Horizontal") == -1.0

    def test_axis_vertical_up(self):
        Input._set_key_state("w", True)
        assert Input.get_axis("Vertical") == 1.0

    def test_axis_vertical_down(self):
        Input._set_key_state("s", True)
        assert Input.get_axis("Vertical") == -1.0

    def test_axis_both_cancel(self):
        Input._set_key_state("a", True)
        Input._set_key_state("d", True)
        assert Input.get_axis("Horizontal") == 0.0

    def test_axis_unknown_returns_zero(self):
        assert Input.get_axis("NonExistent") == 0.0

    def test_axis_arrow_keys(self):
        Input._set_key_state("right", True)
        assert Input.get_axis("Horizontal") == 1.0
        Input._set_key_state("right", False)
        Input._set_key_state("up", True)
        assert Input.get_axis("Vertical") == 1.0

    def test_mouse_position(self):
        Input._set_mouse_position(100.0, 200.0)
        assert Input.get_mouse_position() == (100.0, 200.0)

    def test_mouse_button(self):
        Input._set_mouse_button(0, True)
        assert Input.get_mouse_button(0) is True
        assert Input.get_mouse_button(1) is False

    def test_mouse_button_down(self):
        Input._begin_frame()
        Input._set_mouse_button(0, True)
        assert Input.get_mouse_button_down(0) is True

    def test_reset(self):
        Input._set_key_state("w", True)
        Input._set_mouse_button(0, True)
        Input._reset()
        assert Input.get_key("w") is False
        assert Input.get_mouse_button(0) is False
