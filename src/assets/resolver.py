"""Runtime asset resolver — loads real PNGs into the Python simulator.

Bridges the gap between Python's symbolic ``asset_ref`` and the on-disk
sprite packs kept under ``data/assets/<game>/Sprites/``. The resolver is
consulted lazily by :class:`SpriteRenderer` on its first render call per
instance; when the mapping + file are present, a real sprite is blitted
instead of the colored-rectangle fallback.

Flow:
    1. Example calls ``set_active_game("flappy_bird")`` in ``setup_scene``.
    2. Resolver loads ``data/mappings/flappy_bird_mapping.json`` and pins it.
    3. On first render, ``SpriteRenderer`` calls ``load_sprite_surface(asset_ref)``.
    4. The resolver derives ``data/assets/flappy_bird/Sprites/<basename>`` from
       the mapping's ``unity_path`` and returns a cached ``pygame.Surface``.

Misses (no active game, missing mapping entry, missing file, load error) are
memoized so a failing lookup is cheap on subsequent frames.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.assets.mapping import AssetMapping


_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ASSETS_ROOT = _PROJECT_ROOT / "data" / "assets"
_MAPPINGS_ROOT = _PROJECT_ROOT / "data" / "mappings"

_active_game: str | None = None
_active_mapping: AssetMapping | None = None
_surface_cache: dict[tuple[str, str], Any] = {}
_missing: set[tuple[str, str]] = set()


def set_active_game(game_name: str | None) -> None:
    """Pin the active game for sprite resolution.

    Pass ``None`` to clear. Loading the mapping here (rather than per-lookup)
    means a missing mapping is a single disk probe, not one per sprite.
    """
    global _active_game, _active_mapping
    clear_cache()
    if game_name is None:
        _active_game = None
        _active_mapping = None
        return
    _active_game = game_name
    mapping_path = _MAPPINGS_ROOT / f"{game_name}_mapping.json"
    _active_mapping = AssetMapping.from_file(mapping_path) if mapping_path.exists() else None


def get_active_game() -> str | None:
    return _active_game


def _derive_png_path(asset_ref: str) -> Path | None:
    if _active_game is None or _active_mapping is None:
        return None
    sm = _active_mapping.sprites.get(asset_ref)
    if sm is None or not sm.unity_path:
        return None
    filename = Path(sm.unity_path).name
    return _ASSETS_ROOT / _active_game / "Sprites" / filename


def load_sprite_surface(asset_ref: str | None) -> Any:
    """Return a cached ``pygame.Surface`` for ``asset_ref``, or ``None``.

    ``None`` covers every failure mode (no active game, unmapped ref, missing
    file, pygame image load error). Callers fall back to colored-rectangle
    rendering when ``None`` is returned.
    """
    if asset_ref is None or _active_game is None:
        return None

    key = (_active_game, asset_ref)
    cached = _surface_cache.get(key)
    if cached is not None:
        return cached
    if key in _missing:
        return None

    png_path = _derive_png_path(asset_ref)
    if png_path is None or not png_path.exists():
        _missing.add(key)
        return None

    try:
        import pygame
        surface = pygame.image.load(str(png_path))
        if pygame.display.get_init() and pygame.display.get_surface() is not None:
            surface = surface.convert_alpha()
    except Exception:
        _missing.add(key)
        return None

    _surface_cache[key] = surface
    return surface


def clear_cache() -> None:
    """Drop cached surfaces and miss memos. Call on scene reset."""
    _surface_cache.clear()
    _missing.clear()
