"""Behavioral contracts for src.assets.resolver.

Written independently based on:
- pygame Surface spec (https://www.pygame.org/docs/ref/surface.html) — Surface objects
  must support get_width/get_height/get_rect.
- The feature description: resolver maps asset_ref via
  data/mappings/<game>_mapping.json, picks basename(unity_path), loads from
  data/assets/<game>/Sprites/<basename>, caches hits, memoizes misses.

These contracts describe what the API *should* guarantee, not what it happens
to do. They intentionally avoid peeking at resolver internals beyond the
public surface (set_active_game, get_active_game, load_sprite_surface,
clear_cache).
"""

from __future__ import annotations

import os

import pytest

# Headless pygame — must be set before any pygame import triggers display init.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

from src.assets import resolver  # noqa: E402
from src.assets.resolver import (  # noqa: E402
    clear_cache,
    get_active_game,
    load_sprite_surface,
    set_active_game,
)


@pytest.fixture(autouse=True)
def _isolate_resolver_state():
    """Every test starts with resolver cleared and ends the same."""
    set_active_game(None)
    clear_cache()
    yield
    set_active_game(None)
    clear_cache()


# ---------------------------------------------------------------------------
# Null / empty state contracts
# ---------------------------------------------------------------------------


class TestNullState:
    """With no active game pinned, every lookup returns None — no exceptions."""

    def test_no_active_game_returns_none_for_known_ref(self):
        assert get_active_game() is None
        # "bird_01" is a real ref in flappy_bird_mapping.json, but without an
        # active game pinned the resolver cannot know which game it belongs to.
        assert load_sprite_surface("bird_01") is None

    def test_load_none_asset_ref_returns_none(self):
        set_active_game("flappy_bird")
        assert load_sprite_surface(None) is None

    def test_load_none_asset_ref_without_game_returns_none(self):
        assert load_sprite_surface(None) is None


# ---------------------------------------------------------------------------
# set_active_game(None) contract
# ---------------------------------------------------------------------------


class TestSetActiveGameNone:
    """Passing None clears the pinned game; subsequent lookups return None."""

    def test_none_clears_active_game(self):
        set_active_game("flappy_bird")
        assert get_active_game() == "flappy_bird"
        set_active_game(None)
        assert get_active_game() is None

    def test_after_clear_known_ref_resolves_to_none(self):
        set_active_game("flappy_bird")
        surface = load_sprite_surface("bird_01")
        assert surface is not None  # sanity: mapping+file exist
        set_active_game(None)
        assert load_sprite_surface("bird_01") is None


# ---------------------------------------------------------------------------
# Unknown-ref miss caching contract
# ---------------------------------------------------------------------------


class TestMissMemoization:
    """Unknown refs return None — and the miss is memoized.

    The second call must not re-probe the mapping or the disk. We prove this
    by ruining the mapping after the first miss; if the second call still
    returned None cheaply, the behavior came from the memo, not re-resolution.
    """

    def test_unknown_ref_returns_none(self):
        set_active_game("flappy_bird")
        assert load_sprite_surface("this_ref_does_not_exist_anywhere") is None

    def test_unknown_ref_miss_is_cached(self):
        set_active_game("flappy_bird")
        assert load_sprite_surface("definitely_missing") is None

        # Break the mapping completely. If the resolver re-probed each call,
        # it might raise or behave differently. Memoized miss should be silent.
        original = resolver._active_mapping
        resolver._active_mapping = None
        try:
            assert load_sprite_surface("definitely_missing") is None
        finally:
            resolver._active_mapping = original


# ---------------------------------------------------------------------------
# Cache invalidation on game switch
# ---------------------------------------------------------------------------


class TestCacheInvalidationOnGameSwitch:
    """Switching games must drop the previous game's cache.

    Same asset_ref string in game A and game B should resolve to the
    corresponding per-game PNG, not cross-contaminate.
    """

    def test_switching_game_resolves_independently(self):
        # Both flappy_bird and pacman mappings exist in data/mappings/.
        set_active_game("flappy_bird")
        fb_surface = load_sprite_surface("bird_01")
        assert fb_surface is not None

        set_active_game("pacman")
        # "bird_01" is not in pacman mapping — must not return the flappy surface.
        assert load_sprite_surface("bird_01") is None

        # Going back to flappy must re-resolve correctly.
        set_active_game("flappy_bird")
        fb2 = load_sprite_surface("bird_01")
        assert fb2 is not None
        assert fb2.get_width() == fb_surface.get_width()
        assert fb2.get_height() == fb_surface.get_height()

    def test_set_active_game_clears_cached_misses(self):
        set_active_game("flappy_bird")
        # Cache a miss.
        assert load_sprite_surface("totally_unknown_ref") is None
        set_active_game("pacman")
        # After the game switch the cache must be gone — the miss set for
        # flappy should not survive into pacman's namespace.
        # (Access to _missing is a white-box check, but only to confirm the
        # contract "set_active_game invalidates cache".)
        assert ("flappy_bird", "totally_unknown_ref") not in resolver._missing


# ---------------------------------------------------------------------------
# Return-type contract — duck-typed pygame Surface
# ---------------------------------------------------------------------------


class TestReturnTypeContract:
    """Returned objects must quack like pygame.Surface."""

    def test_returned_object_has_surface_api(self):
        set_active_game("flappy_bird")
        surf = load_sprite_surface("bird_01")
        assert surf is not None
        # Duck-typed Surface API per pygame docs.
        assert hasattr(surf, "get_width")
        assert hasattr(surf, "get_height")
        assert hasattr(surf, "get_rect")
        assert callable(surf.get_width)
        assert callable(surf.get_height)
        assert callable(surf.get_rect)
        # And the methods must actually produce sensible values.
        w = surf.get_width()
        h = surf.get_height()
        rect = surf.get_rect()
        assert isinstance(w, int) and w > 0
        assert isinstance(h, int) and h > 0
        assert rect.width == w
        assert rect.height == h

    def test_returned_object_is_pygame_surface(self):
        """Stronger contract: SpriteRenderer blits this, so it *must* be a Surface."""
        set_active_game("flappy_bird")
        surf = load_sprite_surface("bird_01")
        assert isinstance(surf, pygame.Surface)

    def test_cache_returns_same_instance(self):
        """Caching contract: repeated lookups return the same Surface object."""
        set_active_game("flappy_bird")
        s1 = load_sprite_surface("bird_01")
        s2 = load_sprite_surface("bird_01")
        assert s1 is s2


# ---------------------------------------------------------------------------
# clear_cache contract
# ---------------------------------------------------------------------------


class TestClearCache:
    """clear_cache() wipes both hits and miss memos."""

    def test_clear_cache_forces_reload(self):
        set_active_game("flappy_bird")
        s1 = load_sprite_surface("bird_01")
        assert s1 is not None
        clear_cache()
        s2 = load_sprite_surface("bird_01")
        assert s2 is not None
        # After clear, a fresh Surface instance is expected.
        assert s1 is not s2

    def test_clear_cache_resets_miss_memo(self):
        set_active_game("flappy_bird")
        assert load_sprite_surface("nonexistent_ref_xyz") is None
        clear_cache()
        assert ("flappy_bird", "nonexistent_ref_xyz") not in resolver._missing


# ---------------------------------------------------------------------------
# Full coverage contract — all flappy_bird sprites resolve
# ---------------------------------------------------------------------------


class TestAllFlappyBirdSpritesResolve:
    """Every sprite ref in flappy_bird_mapping.json with a file present
    on disk must resolve to a Surface when flappy_bird is active.

    Derived from the mapping file contents, not from resolver code.
    """

    def test_all_flappy_bird_sprites_resolve(self):
        set_active_game("flappy_bird")
        from pathlib import Path

        from src.assets.mapping import AssetMapping

        project_root = Path(__file__).resolve().parents[2]
        mapping_file = project_root / "data" / "mappings" / "flappy_bird_mapping.json"
        sprites_dir = project_root / "data" / "assets" / "flappy_bird" / "Sprites"
        mapping = AssetMapping.from_file(mapping_file)

        # For each ref whose PNG actually exists on disk, the resolver must
        # return a non-None Surface.
        resolved_any = False
        for ref, sm in mapping.sprites.items():
            png = sprites_dir / Path(sm.unity_path).name
            if not png.exists():
                continue
            surf = load_sprite_surface(ref)
            assert surf is not None, f"expected resolver to load {ref} -> {png}"
            assert isinstance(surf, pygame.Surface)
            resolved_any = True
        assert resolved_any, "test sanity: at least one flappy sprite must exist on disk"
