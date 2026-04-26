"""Integration tests for UIRenderManager (Tasks 15-17).

Tests that UI rendering works end-to-end through the game loop and
as standalone calls, without crashing.
"""

import pytest
import sys
import os

# Ensure project root on path
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from src.engine.core import GameObject, _clear_registry
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.time_manager import Time
from src.engine.input_manager import Input
from src.engine.rendering.camera import Camera
from src.engine.ui import (
    Canvas, RectTransform, Text, Image, TextAnchor, UIRenderManager,
)


def reset_engine():
    """Reset all engine singletons between tests."""
    _clear_registry()
    LifecycleManager.reset()
    PhysicsManager.reset()
    Time._reset()
    Input._reset()
    Camera._reset_main()
    Canvas.reset()
    UIRenderManager._font_cache.clear()
    try:
        from src.engine.tweening import TweenManager
        TweenManager.reset()
    except Exception:
        pass


@pytest.fixture(autouse=True)
def clean_state():
    reset_engine()
    yield
    reset_engine()


# ── Integration: full game loop headless ──


def test_canvas_text_headless_no_crash():
    """Create Canvas + Text, run headless 5 frames -- no crash."""
    from src.engine.app import run

    def setup():
        cam_go = GameObject("MainCamera")
        cam_go.add_component(Camera)
        go = GameObject("ScoreText")
        go.add_component(Canvas)
        go.add_component(RectTransform)
        t = go.add_component(Text)
        t.text = "Score: 0"
        t.font_size = 24

    run(setup, headless=True, max_frames=5)
    # If we reach here, no crash occurred
    assert True


def test_canvas_image_color_headless_no_crash():
    """Create Canvas + Image with color, run headless 5 frames -- no crash."""
    from src.engine.app import run

    def setup():
        cam_go = GameObject("MainCamera")
        cam_go.add_component(Camera)
        go = GameObject("Panel")
        go.add_component(Canvas)
        go.add_component(RectTransform)
        img = go.add_component(Image)
        img.color = (100, 200, 50)

    run(setup, headless=True, max_frames=5)
    assert True


def test_multiple_canvases_headless_no_crash():
    """Multiple Canvas instances each with Text -- all render without error."""
    from src.engine.app import run

    def setup():
        cam_go = GameObject("MainCamera")
        cam_go.add_component(Camera)
        for i in range(3):
            go = GameObject(f"UIPanel_{i}")
            go.add_component(Canvas)
            go.add_component(RectTransform)
            t = go.add_component(Text)
            t.text = f"Panel {i}"

    run(setup, headless=True, max_frames=5)
    assert True


# ── Standalone UIRenderManager tests ──


def test_render_all_none_surface_no_crash():
    """UIRenderManager.render_all() with None surface exits early."""
    go = GameObject("Text1")
    go.add_component(Canvas)
    go.add_component(RectTransform)
    t = go.add_component(Text)
    t.text = "Hello"
    # Should return immediately without error
    UIRenderManager.render_all(None, 800, 600)


def test_text_alignment_all_anchors_no_crash():
    """Each TextAnchor alignment renders without crash on a real pygame surface."""
    pygame = pytest.importorskip("pygame")
    if not pygame.get_init():
        pygame.init()
    surface = pygame.Surface((800, 600))

    for anchor in TextAnchor:
        reset_engine()
        go = GameObject(f"Text_{anchor.name}")
        go.add_component(RectTransform)
        t = go.add_component(Text)
        t.text = "Aligned"
        t.font_size = 20
        t.alignment = anchor
        UIRenderManager.render_all(surface, 800, 600)


def test_rich_text_parse_returns_styled_runs():
    """Text with rich_text=True parses into styled run dicts."""
    go = GameObject("RichText")
    go.add_component(RectTransform)
    t = go.add_component(Text)
    t.rich_text = True
    t.text = '<color=#FF0000>Red</color> normal <b>bold</b>'
    t.color = (255, 255, 255)
    t.font_size = 14

    runs = t.parse_rich_text()
    assert len(runs) >= 3, f"Expected at least 3 runs, got {len(runs)}"
    # First run should have red color
    assert runs[0]["color"] == (255, 0, 0), f"Expected red, got {runs[0]['color']}"
    assert runs[0]["text"] == "Red"
    # Second run should have default color
    assert runs[1]["color"] == (255, 255, 255)
    # Third run should be bold
    assert runs[2]["bold"] is True


def test_rich_text_render_no_crash():
    """Rich text renders to pygame surface without crash."""
    pygame = pytest.importorskip("pygame")
    if not pygame.get_init():
        pygame.init()
    surface = pygame.Surface((800, 600))

    go = GameObject("RichText")
    go.add_component(RectTransform)
    t = go.add_component(Text)
    t.rich_text = True
    t.text = '<color=#00FF00>Green</color> <size=24>Big</size>'
    t.color = (255, 255, 255)
    t.font_size = 14

    UIRenderManager.render_all(surface, 800, 600)


def test_empty_text_no_crash():
    """Text component with empty string renders without crash."""
    pygame = pytest.importorskip("pygame")
    if not pygame.get_init():
        pygame.init()
    surface = pygame.Surface((800, 600))

    go = GameObject("EmptyText")
    go.add_component(RectTransform)
    t = go.add_component(Text)
    t.text = ""

    UIRenderManager.render_all(surface, 800, 600)


def test_image_with_sprite_surface_no_crash():
    """Image with a sprite (pygame.Surface) renders without crash."""
    pygame = pytest.importorskip("pygame")
    if not pygame.get_init():
        pygame.init()
    surface = pygame.Surface((800, 600))
    sprite = pygame.Surface((32, 32))
    sprite.fill((255, 0, 0))

    go = GameObject("SpriteImage")
    go.add_component(RectTransform)
    img = go.add_component(Image)
    img.sprite = sprite

    UIRenderManager.render_all(surface, 800, 600)


def test_rich_text_disabled_returns_single_run():
    """Text with rich_text=False returns a single unstyled run."""
    go = GameObject("PlainText")
    go.add_component(RectTransform)
    t = go.add_component(Text)
    t.rich_text = False
    t.text = "Hello <b>World</b>"
    t.color = (200, 200, 200)
    t.font_size = 16

    runs = t.parse_rich_text()
    assert len(runs) == 1
    # When rich_text is off, tags are NOT stripped — raw text returned
    assert runs[0]["text"] == "Hello <b>World</b>"
    assert runs[0]["bold"] is False
