"""End-to-end integration: SpriteRenderer + asset resolver.

Drives SpriteRenderer.render() against a headless pygame surface with
set_active_game("flappy_bird") active. Derived from:

- Unity SpriteRenderer spec: sprite is drawn centered on the GameObject's
  position; color tints multiplicatively; size matches the sprite's physical
  pixels scaled by pixels-per-unit.
- pygame behavior: Surface.blit, BLEND_RGBA_MULT, transform.scale.
- The mapping JSON: bird_01 -> Bird_01.png (17x12 per current art pack).
"""

from __future__ import annotations

import os

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from src.assets import resolver  # noqa: E402
from src.assets.resolver import (  # noqa: E402
    clear_cache,
    load_sprite_surface,
    set_active_game,
)
from src.engine.core import GameObject  # noqa: E402
from src.engine.math.vector import Vector2  # noqa: E402
from src.engine.rendering.camera import Camera  # noqa: E402
from src.engine.rendering.renderer import SpriteRenderer  # noqa: E402


SCREEN_W, SCREEN_H = 400, 300


@pytest.fixture(scope="module", autouse=True)
def _pygame_display():
    """Initialize a dummy pygame display so image.convert_alpha() works."""
    pygame.display.init()
    surf = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    yield surf
    pygame.display.quit()


@pytest.fixture(autouse=True)
def _isolate_resolver():
    set_active_game(None)
    clear_cache()
    yield
    set_active_game(None)
    clear_cache()


def _make_camera() -> Camera:
    cam_go = GameObject("Camera")
    cam = cam_go.add_component(Camera)
    cam.orthographic_size = 5.0
    return cam


def _make_sprite(asset_ref: str, size: tuple[float, float] = (1.0, 1.0)) -> SpriteRenderer:
    go = GameObject("Sprite")
    sr = go.add_component(SpriteRenderer)
    sr.asset_ref = asset_ref
    sr.size = Vector2(*size)
    return sr


# ---------------------------------------------------------------------------
# Happy path: bird_01 loads from disk on first render
# ---------------------------------------------------------------------------


class TestSpriteLoadsOnRender:
    def test_asset_ref_triggers_sprite_load(self, _pygame_display):
        set_active_game("flappy_bird")
        sr = _make_sprite("bird_01")
        cam = _make_camera()
        surface = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

        assert sr.sprite is None  # pre-render state

        sr.render(surface, cam, SCREEN_W, SCREEN_H)

        assert sr.sprite is not None, "render() should lazily resolve asset_ref"
        assert isinstance(sr.sprite, pygame.Surface)

    def test_loaded_sprite_has_expected_dimensions(self, _pygame_display):
        """Bird_01.png in the current art pack is 17x12. This is a behavioral
        assertion about the source PNG, not the renderer: if it changes, the
        art pack changed.
        """
        set_active_game("flappy_bird")
        sr = _make_sprite("bird_01")
        cam = _make_camera()
        surface = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        sr.render(surface, cam, SCREEN_W, SCREEN_H)

        assert sr.sprite is not None
        assert sr.sprite.get_width() == 17
        assert sr.sprite.get_height() == 12

    def test_resolver_direct_call_matches_renderer_source(self, _pygame_display):
        """Whatever the renderer loaded must equal what load_sprite_surface
        returns — they share the same cache.
        """
        set_active_game("flappy_bird")
        direct = load_sprite_surface("bird_01")

        sr = _make_sprite("bird_01")
        cam = _make_camera()
        surface = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        sr.render(surface, cam, SCREEN_W, SCREEN_H)

        assert sr.sprite is direct


# ---------------------------------------------------------------------------
# Sad paths: missing game, missing ref, missing file
# ---------------------------------------------------------------------------


class TestFallbackToColoredRect:
    """When the resolver returns None, render must silently fall back to
    drawing a colored rect — no exception, no sprite cached."""

    def test_no_active_game_falls_back_silently(self, _pygame_display):
        # No set_active_game called
        sr = _make_sprite("bird_01")
        sr.color = (255, 64, 64)
        cam = _make_camera()
        surface = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

        # Should not raise.
        sr.render(surface, cam, SCREEN_W, SCREEN_H)
        assert sr.sprite is None

    def test_unknown_ref_falls_back_silently(self, _pygame_display):
        set_active_game("flappy_bird")
        sr = _make_sprite("no_such_ref_exists_12345")
        cam = _make_camera()
        surface = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

        sr.render(surface, cam, SCREEN_W, SCREEN_H)
        assert sr.sprite is None

    def test_mapping_exists_but_file_missing_falls_back(
        self, _pygame_display, tmp_path, monkeypatch
    ):
        """Set up a mapping that references a file that does not exist.
        The renderer must fall back without crashing."""
        # Point resolver roots at a temp dir with a bogus mapping.
        mappings = tmp_path / "mappings"
        assets = tmp_path / "assets" / "toy_game" / "Sprites"
        mappings.mkdir(parents=True)
        assets.mkdir(parents=True)
        (mappings / "toy_game_mapping.json").write_text(
            '{"sprites": {"ghost": {"unity_path": "Assets/Sprites/Ghost.png"}}}',
            encoding="utf-8",
        )
        # deliberately DO NOT create Ghost.png

        monkeypatch.setattr(resolver, "_MAPPINGS_ROOT", mappings)
        monkeypatch.setattr(resolver, "_ASSETS_ROOT", tmp_path / "assets")

        set_active_game("toy_game")
        sr = _make_sprite("ghost")
        cam = _make_camera()
        surface = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)

        sr.render(surface, cam, SCREEN_W, SCREEN_H)  # must not raise
        assert sr.sprite is None  # fallback path


# ---------------------------------------------------------------------------
# Color tint contract (BLEND_RGBA_MULT)
# ---------------------------------------------------------------------------


class TestColorTint:
    """When SpriteRenderer.color != white, the rendered sprite is tinted.

    Unity's SpriteRenderer.color multiplies RGB channels into the sprite
    texture. The Python impl uses pygame BLEND_RGBA_MULT, which means a
    non-white color must darken at least one channel of a non-transparent
    pixel. We verify by scanning the blitted surface for a pixel that
    differs from what white-tint would produce.
    """

    def _render_and_return_surface(
        self, color: tuple[int, int, int], _pygame_display
    ):
        sr = _make_sprite("bird_01")
        sr.color = color
        cam = _make_camera()
        surface = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        surface.fill((0, 0, 0, 0))
        sr.render(surface, cam, SCREEN_W, SCREEN_H)
        return surface

    def _find_opaque_pixel(self, surface: pygame.Surface) -> tuple[int, int, int, int]:
        """Scan the surface for a pixel with alpha > 0 and return its RGBA."""
        w, h = surface.get_width(), surface.get_height()
        for y in range(h):
            for x in range(w):
                px = surface.get_at((x, y))
                if px.a > 0:
                    return (px.r, px.g, px.b, px.a)
        return (0, 0, 0, 0)

    def test_red_tint_zeroes_green_and_blue(self, _pygame_display):
        """BLEND_RGBA_MULT with color (255,0,0) must zero green/blue on any
        non-transparent pixel (bird sprite has non-zero R/G/B originally).
        """
        set_active_game("flappy_bird")
        white = self._render_and_return_surface((255, 255, 255), _pygame_display)
        red = self._render_and_return_surface((255, 0, 0), _pygame_display)

        # White-render must have at least one opaque pixel (sanity).
        wpx = self._find_opaque_pixel(white)
        assert wpx[3] > 0, "sprite has no opaque pixel — test fixture broken"

        # Red-render: every opaque pixel must have G=0 and B=0.
        w, h = red.get_width(), red.get_height()
        saw_opaque = False
        for y in range(h):
            for x in range(w):
                p = red.get_at((x, y))
                if p.a > 0:
                    saw_opaque = True
                    assert p.g == 0, f"green channel not zeroed at ({x},{y}): {p}"
                    assert p.b == 0, f"blue channel not zeroed at ({x},{y}): {p}"
        assert saw_opaque, "tinted sprite produced no opaque pixels"

    def test_white_tint_preserves_original(self, _pygame_display):
        """Control: color=(255,255,255) is the no-op path — sprite pixels
        should be unaltered by a tint.
        """
        set_active_game("flappy_bird")
        # Grab the source sprite directly
        src = load_sprite_surface("bird_01")
        assert src is not None

        # Render with white; no tint path should fire.
        rendered = self._render_and_return_surface(
            (255, 255, 255), _pygame_display
        )

        # Find a non-transparent source pixel and verify it shows up somewhere
        # on the rendered surface (possibly scaled, we just check RGB values).
        source_colors: set[tuple[int, int, int]] = set()
        for y in range(src.get_height()):
            for x in range(src.get_width()):
                p = src.get_at((x, y))
                if p.a > 0:
                    source_colors.add((p.r, p.g, p.b))

        rendered_colors: set[tuple[int, int, int]] = set()
        for y in range(rendered.get_height()):
            for x in range(rendered.get_width()):
                p = rendered.get_at((x, y))
                if p.a > 0:
                    rendered_colors.add((p.r, p.g, p.b))

        overlap = source_colors & rendered_colors
        assert overlap, (
            "white tint should preserve sprite RGB values; none of "
            f"{len(source_colors)} source colors appeared in render"
        )

    def test_non_white_changes_sprite_relative_to_white(self, _pygame_display):
        """Differential: the same sprite rendered with red vs. white must
        produce at least one pixel that differs, proving the tint fired.
        """
        set_active_game("flappy_bird")
        white = self._render_and_return_surface((255, 255, 255), _pygame_display)
        red = self._render_and_return_surface((255, 0, 0), _pygame_display)

        differed = False
        for y in range(white.get_height()):
            for x in range(white.get_width()):
                if white.get_at((x, y)) != red.get_at((x, y)):
                    differed = True
                    break
            if differed:
                break
        assert differed, "red tint produced identical output to white — tint no-op"
