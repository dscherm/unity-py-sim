"""Tests for UI system — Canvas, RectTransform, Text, Image, Button."""

import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.math.vector import Vector2
from src.engine.ui import (
    Canvas, RectTransform, Text, Image, Button,
    RenderMode, TextAnchor,
)


@pytest.fixture(autouse=True)
def reset():
    yield
    Canvas.reset()
    _clear_registry()


class TestRectTransform:
    def test_default_values(self):
        go = GameObject("UI")
        rt = go.add_component(RectTransform)
        assert rt.anchored_position == Vector2(0, 0)
        assert rt.size_delta == Vector2(100, 30)
        assert rt.pivot == Vector2(0.5, 0.5)

    def test_screen_rect_centered(self):
        go = GameObject("UI")
        rt = go.add_component(RectTransform)
        rt.size_delta = Vector2(200, 50)
        # Default anchors at (0.5, 0.5), pivot (0.5, 0.5)
        x, y, w, h = rt.get_screen_rect(800, 600)
        assert w == 200
        assert h == 50
        # Should be centered: (400 - 100, 300 - 25)
        assert abs(x - 300) < 0.01
        assert abs(y - 275) < 0.01

    def test_screen_rect_with_offset(self):
        go = GameObject("UI")
        rt = go.add_component(RectTransform)
        rt.anchored_position = Vector2(50, 50)
        rt.size_delta = Vector2(100, 30)
        x, y, w, h = rt.get_screen_rect(800, 600)
        assert abs(x - 400) < 0.01  # 400 + 50 - 50
        assert abs(y - 335) < 0.01  # 300 + 50 - 15

    def test_anchor_top_left(self):
        go = GameObject("UI")
        rt = go.add_component(RectTransform)
        rt.anchor_min = Vector2(0, 1)
        rt.anchor_max = Vector2(0, 1)
        rt.size_delta = Vector2(100, 30)
        rt.anchored_position = Vector2(0, 0)
        x, y, w, h = rt.get_screen_rect(800, 600)
        assert abs(x - (-50)) < 0.01
        assert abs(y - (600 - 15)) < 0.01


class TestCanvas:
    def test_create_canvas(self):
        go = GameObject("Canvas")
        canvas = go.add_component(Canvas)
        assert canvas.render_mode == RenderMode.SCREEN_SPACE_OVERLAY
        assert canvas.sort_order == 0

    def test_get_all(self):
        go1 = GameObject("C1")
        c1 = go1.add_component(Canvas)
        go2 = GameObject("C2")
        c2 = go2.add_component(Canvas)
        assert len(Canvas.get_all()) == 2

    def test_destroy_removes_from_list(self):
        go = GameObject("Canvas")
        canvas = go.add_component(Canvas)
        assert len(Canvas.get_all()) == 1
        canvas.on_destroy()
        assert len(Canvas.get_all()) == 0


class TestText:
    def test_default_text(self):
        go = GameObject("Label")
        t = go.add_component(Text)
        assert t.text == ""
        assert t.font_size == 14
        assert t.color == (255, 255, 255)
        assert t.alignment == TextAnchor.UPPER_LEFT

    def test_set_text(self):
        go = GameObject("Label")
        t = go.add_component(Text)
        t.text = "Score: 100"
        assert t.text == "Score: 100"

    def test_set_font_size(self):
        go = GameObject("Label")
        t = go.add_component(Text)
        t.font_size = 24
        assert t.font_size == 24

    def test_set_color(self):
        go = GameObject("Label")
        t = go.add_component(Text)
        t.color = (255, 0, 0)
        assert t.color == (255, 0, 0)


class TestImage:
    def test_default_image(self):
        go = GameObject("Panel")
        img = go.add_component(Image)
        assert img.color == (255, 255, 255)
        assert img.sprite is None

    def test_set_color(self):
        go = GameObject("Panel")
        img = go.add_component(Image)
        img.color = (0, 0, 0)
        assert img.color == (0, 0, 0)


class TestButton:
    def test_default_button(self):
        go = GameObject("Btn")
        btn = go.add_component(Button)
        assert btn.interactable is True
        assert btn.on_click is None

    def test_click_fires_callback(self):
        clicked = [False]
        go = GameObject("Btn")
        btn = go.add_component(Button)
        btn.on_click = lambda: clicked.__setitem__(0, True)
        btn.click()
        assert clicked[0] is True

    def test_click_disabled_no_callback(self):
        clicked = [False]
        go = GameObject("Btn")
        btn = go.add_component(Button)
        btn.on_click = lambda: clicked.__setitem__(0, True)
        btn.interactable = False
        btn.click()
        assert clicked[0] is False

    def test_hit_test(self):
        go = GameObject("Btn")
        rt = go.add_component(RectTransform)
        rt.size_delta = Vector2(200, 50)
        # Centered at (400, 300) on 800x600 canvas
        btn = go.add_component(Button)
        assert btn.hit_test(400, 300, 800, 600)  # center
        assert btn.hit_test(301, 276, 800, 600)  # near top-left edge
        assert not btn.hit_test(0, 0, 800, 600)  # outside

    def test_hit_test_no_rect_transform(self):
        go = GameObject("Btn")
        btn = go.add_component(Button)
        assert btn.hit_test(400, 300, 800, 600) is False
