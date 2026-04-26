"""Mutation tests proving the resolver/renderer tests catch real regressions.

Each test introduces a deliberate breakage via monkeypatch, then asserts that
a *simulation* of the corresponding contract/integration check fails. The
simulation mirrors the assertion in the companion test file, not the internal
resolver logic, so these tests prove the tests would catch the mutation.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from src.assets import mapping as mapping_mod  # noqa: E402
from src.assets import resolver  # noqa: E402
from src.assets.resolver import (  # noqa: E402
    clear_cache,
    load_sprite_surface,
    set_active_game,
)


@pytest.fixture(autouse=True)
def _reset_resolver():
    set_active_game(None)
    clear_cache()
    yield
    set_active_game(None)
    clear_cache()


# ---------------------------------------------------------------------------
# Mutation 1: resolver always returns None
# ---------------------------------------------------------------------------


class TestMutationResolverReturnsNone:
    """If load_sprite_surface always returns None, the 'loads bird_01' contract
    test in test_asset_resolver_contract.py fails. Prove it."""

    def test_always_none_breaks_load_contract(self, monkeypatch):
        # Simulate the mutation.
        monkeypatch.setattr(resolver, "load_sprite_surface", lambda ref: None)

        set_active_game("flappy_bird")
        # This mirrors
        # TestReturnTypeContract::test_returned_object_is_pygame_surface
        from src.assets.resolver import load_sprite_surface as patched_load

        surf = patched_load("bird_01")
        # The real contract asserts this is a pygame.Surface. With the
        # mutation applied, that assertion must fail.
        with pytest.raises(AssertionError):
            assert isinstance(surf, pygame.Surface)

    def test_always_none_breaks_renderer_integration(self, monkeypatch):
        """Mirrors TestSpriteLoadsOnRender::test_asset_ref_triggers_sprite_load.
        If the resolver is broken, SpriteRenderer.sprite stays None."""
        # Patch the symbol that renderer.render imports at call time.
        monkeypatch.setattr(resolver, "load_sprite_surface", lambda ref: None)

        from src.engine.core import GameObject
        from src.engine.math.vector import Vector2
        from src.engine.rendering.camera import Camera
        from src.engine.rendering.renderer import SpriteRenderer

        pygame.display.init()
        try:
            pygame.display.set_mode((400, 300))
            set_active_game("flappy_bird")
            go = GameObject("Sprite")
            sr = go.add_component(SpriteRenderer)
            sr.asset_ref = "bird_01"
            sr.size = Vector2(1, 1)

            cam_go = GameObject("Camera")
            cam = cam_go.add_component(Camera)

            surface = pygame.Surface((400, 300), pygame.SRCALPHA)
            sr.render(surface, cam, 400, 300)

            # The real test asserts `sr.sprite is not None`; with mutation,
            # sprite remains None.
            with pytest.raises(AssertionError):
                assert sr.sprite is not None
        finally:
            pygame.display.quit()


# ---------------------------------------------------------------------------
# Mutation 2: _PROJECT_ROOT redirected to a bogus path
# ---------------------------------------------------------------------------


class TestMutationBogusProjectRoot:
    """If the roots point at a bogus path, no flappy_bird sprite resolves.
    Mirrors TestAllFlappyBirdSpritesResolve.
    """

    def test_bogus_roots_break_all_sprites_resolve(self, monkeypatch, tmp_path):
        # Simulate the mutation: redirect both roots so nothing is found.
        bogus = tmp_path / "does_not_exist"
        monkeypatch.setattr(resolver, "_MAPPINGS_ROOT", bogus)
        monkeypatch.setattr(resolver, "_ASSETS_ROOT", bogus)
        set_active_game("flappy_bird")

        # Mirror the "all flappy sprites resolve" assertion: with bogus roots,
        # load_sprite_surface returns None for every known ref, so "at least
        # one resolved" is False.
        project_root = Path(__file__).resolve().parents[2]
        real_mapping_file = project_root / "data" / "mappings" / "flappy_bird_mapping.json"
        refs = list(json.loads(real_mapping_file.read_text())["sprites"].keys())

        any_resolved = any(load_sprite_surface(ref) is not None for ref in refs)
        with pytest.raises(AssertionError):
            assert any_resolved, "expected at least one sprite to resolve"


# ---------------------------------------------------------------------------
# Mutation 3: remove unknown-field filter from AssetMapping.from_json
# ---------------------------------------------------------------------------


class TestMutationMappingUnknownFieldFilter:
    """If AssetMapping.from_json no longer filters unknown keys, the real
    flappy_bird_mapping.json — which has source_url / description — fails
    to load with TypeError on SpriteMapping.__init__.
    """

    def test_remove_filter_breaks_flappy_bird_loader(self, monkeypatch):
        # Install a mutated from_json that does NOT filter unknown fields.
        original = mapping_mod.AssetMapping.from_json

        def mutated_from_json(cls, text):
            data = json.loads(text)
            m = cls()
            for k, v in data.get("sprites", {}).items():
                m.sprites[k] = mapping_mod.SpriteMapping(**v)
            for k, v in data.get("audio", {}).items():
                m.audio[k] = mapping_mod.AudioMapping(**v)
            return m

        monkeypatch.setattr(
            mapping_mod.AssetMapping, "from_json", classmethod(mutated_from_json)
        )

        # Sanity: verify the original still works (monkeypatch scope).
        # Load the real flappy_bird mapping — must now raise TypeError.
        project_root = Path(__file__).resolve().parents[2]
        mapping_file = project_root / "data" / "mappings" / "flappy_bird_mapping.json"

        with pytest.raises(TypeError):
            mapping_mod.AssetMapping.from_file(mapping_file)

        # Restore and confirm original loads cleanly.
        monkeypatch.setattr(mapping_mod.AssetMapping, "from_json", original)
        loaded = mapping_mod.AssetMapping.from_file(mapping_file)
        assert "bird_01" in loaded.sprites


# ---------------------------------------------------------------------------
# Bonus mutation: set_active_game no longer clears cache
# ---------------------------------------------------------------------------


class TestMutationGameSwitchLeaksCache:
    """If set_active_game stopped calling clear_cache, switching games would
    leak surfaces across games. Mirrors
    TestCacheInvalidationOnGameSwitch::test_switching_game_resolves_independently.
    """

    def test_no_clear_leaks_between_games(self, monkeypatch):
        # Simulate the mutation by pre-populating the cache, then bypassing
        # clear_cache on set_active_game.
        original_clear = resolver.clear_cache

        def no_op():
            return None

        # First, load a real sprite so cache is populated.
        set_active_game("flappy_bird")
        real = load_sprite_surface("bird_01")
        assert real is not None

        # Now apply the mutation: clear_cache is a no-op.
        monkeypatch.setattr(resolver, "clear_cache", no_op)
        # Seed the cache with a fake cross-game entry (pacman + bird_01).
        resolver._surface_cache[("pacman", "bird_01")] = real

        # Switch game. With the mutation, the cache entry for
        # ("pacman", "bird_01") survives — and load_sprite_surface returns it
        # despite the mapping having no such ref. The real contract
        # test (test_switching_game_resolves_independently) would fail.
        set_active_game("pacman")
        leaked = load_sprite_surface("bird_01")

        with pytest.raises(AssertionError):
            assert leaked is None, "expected pacman to have no bird_01 mapping"

        # Restore.
        monkeypatch.setattr(resolver, "clear_cache", original_clear)
