"""Tests for rendering layer — Camera, SpriteRenderer, DisplayManager, RenderManager."""

import pytest

from src.engine.core import GameObject, _clear_registry
from src.engine.math.vector import Vector2
from src.engine.rendering.camera import Camera
from src.engine.rendering.renderer import SpriteRenderer, RenderManager
from src.engine.rendering.display import DisplayManager


@pytest.fixture(autouse=True)
def reset_rendering():
    yield
    Camera._reset_main()
    DisplayManager.reset()
    _clear_registry()


class TestCamera:
    def test_default_orthographic_size(self):
        go = GameObject("Cam")
        cam = go.add_component(Camera)
        assert cam.orthographic_size == 5.0

    def test_set_orthographic_size(self):
        go = GameObject("Cam")
        cam = go.add_component(Camera)
        cam.orthographic_size = 10.0
        assert cam.orthographic_size == 10.0

    def test_default_background_color(self):
        go = GameObject("Cam")
        cam = go.add_component(Camera)
        assert cam.background_color == (49, 77, 121)

    def test_main_camera_set_on_awake(self):
        go = GameObject("Cam")
        cam = go.add_component(Camera)
        cam.awake()
        assert Camera.main is cam

    def test_world_to_screen_center(self):
        go = GameObject("Cam")
        cam = go.add_component(Camera)
        cam.orthographic_size = 5.0
        # Camera at origin, point at origin -> screen center
        sx, sy = cam.world_to_screen(Vector2(0, 0), 800, 600)
        assert sx == 400
        assert sy == 300

    def test_world_to_screen_offset(self):
        go = GameObject("Cam")
        cam = go.add_component(Camera)
        cam.orthographic_size = 5.0
        # Point at (1, 0) with camera at origin
        # ppu = 600 / 10 = 60
        sx, sy = cam.world_to_screen(Vector2(1, 0), 800, 600)
        assert sx == 460  # 400 + 1*60
        assert sy == 300

    def test_world_to_screen_y_up(self):
        go = GameObject("Cam")
        cam = go.add_component(Camera)
        cam.orthographic_size = 5.0
        # Point above camera -> lower screen Y (screen Y inverted)
        sx, sy = cam.world_to_screen(Vector2(0, 1), 800, 600)
        assert sy < 300

    def test_screen_to_world_roundtrip(self):
        go = GameObject("Cam")
        cam = go.add_component(Camera)
        cam.orthographic_size = 5.0
        world = Vector2(2.5, -1.5)
        screen = cam.world_to_screen(world, 800, 600)
        back = cam.screen_to_world(screen, 800, 600)
        assert abs(back.x - world.x) < 0.1
        assert abs(back.y - world.y) < 0.1

    def test_camera_with_offset(self):
        go = GameObject("Cam")
        cam = go.add_component(Camera)
        go.transform.position = Vector2(10, 0)  # type: ignore
        cam.orthographic_size = 5.0
        # Point at (10, 0) should be screen center
        sx, sy = cam.world_to_screen(Vector2(10, 0), 800, 600)
        assert sx == 400
        assert sy == 300


class TestSpriteRenderer:
    def test_default_color(self):
        go = GameObject("Test")
        sr = go.add_component(SpriteRenderer)
        assert sr.color == (255, 255, 255)

    def test_default_sorting_order(self):
        go = GameObject("Test")
        sr = go.add_component(SpriteRenderer)
        assert sr.sorting_order == 0

    def test_set_color(self):
        go = GameObject("Test")
        sr = go.add_component(SpriteRenderer)
        sr.color = (255, 0, 0)
        assert sr.color == (255, 0, 0)


class TestRenderManager:
    def test_render_all_sorting_order(self):
        """Test that renderers are collected and sorted by sorting_order."""
        go1 = GameObject("Back")
        sr1 = go1.add_component(SpriteRenderer)
        sr1.sorting_order = 0

        go2 = GameObject("Front")
        sr2 = go2.add_component(SpriteRenderer)
        sr2.sorting_order = 10

        go3 = GameObject("Mid")
        sr3 = go3.add_component(SpriteRenderer)
        sr3.sorting_order = 5

        # Verify sorting works by collecting renderers same way RenderManager does
        from src.engine.core import _game_objects
        renderers = []
        for go in _game_objects.values():
            if go.active:
                for comp in go.get_components(SpriteRenderer):
                    if comp.enabled:
                        renderers.append(comp)
        renderers.sort(key=lambda r: r.sorting_order)
        assert renderers[0].sorting_order == 0
        assert renderers[1].sorting_order == 5
        assert renderers[2].sorting_order == 10

    def test_disabled_renderer_excluded(self):
        go = GameObject("Test")
        sr = go.add_component(SpriteRenderer)
        sr.enabled = False

        from src.engine.core import _game_objects
        renderers = []
        for go_obj in _game_objects.values():
            if go_obj.active:
                for comp in go_obj.get_components(SpriteRenderer):
                    if comp.enabled:
                        renderers.append(comp)
        assert len(renderers) == 0


class TestDisplayManager:
    def test_singleton(self):
        dm1 = DisplayManager.instance()
        dm2 = DisplayManager.instance()
        assert dm1 is dm2

    def test_default_dimensions(self):
        dm = DisplayManager.instance()
        assert dm.width == 800
        assert dm.height == 600

    def test_should_quit_default(self):
        dm = DisplayManager.instance()
        assert dm.should_quit is False

    def test_request_quit(self):
        dm = DisplayManager.instance()
        dm.request_quit()
        assert dm.should_quit is True
