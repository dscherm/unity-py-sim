"""Contract tests for `_copy_project_sprites`.

Derived from Unity asset-pipeline specs, not the implementation:
 - Every asset importable by Unity MUST have a sibling `.meta` file with a
   deterministic GUID (the `.meta` IS the asset reference on disk).
 - Sprite importer MUST set textureType=8 and spriteMode=1 or the SpriteRenderer
   silently renders nothing.
 - Copying must preserve directory structure (Unity's SpriteRenderer uses the
   relative path for loading).
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

from src.exporter.project_scaffolder import (
    _ASSETS_ROOT,
    _copy_project_sprites,
    _sprite_meta_yaml,
    _write_default_sprites,
)


# ---------------------------------------------------------------------------
# 1. Missing source directory => no-op returning 0
# ---------------------------------------------------------------------------
def test_no_source_directory_returns_zero_and_creates_nothing(tmp_path):
    output_dir = tmp_path / "proj"
    output_dir.mkdir()

    count = _copy_project_sprites("__nonexistent_game__", output_dir)

    assert count == 0
    # No PNGs should have been created
    assert not any(output_dir.rglob("*.png"))
    assert not any(output_dir.rglob("*.meta"))


def test_empty_source_directory_returns_zero(tmp_path, monkeypatch):
    """Even if the directory exists but has no PNGs, return 0."""
    # Create a fake empty assets root so we don't depend on live data
    fake_assets_root = tmp_path / "assets_root"
    (fake_assets_root / "ghost_game" / "Sprites").mkdir(parents=True)
    monkeypatch.setattr(
        "src.exporter.project_scaffolder._ASSETS_ROOT", fake_assets_root
    )

    output_dir = tmp_path / "proj"
    output_dir.mkdir()
    count = _copy_project_sprites("ghost_game", output_dir)
    assert count == 0


# ---------------------------------------------------------------------------
# 2. PNGs are copied byte-for-byte and every PNG has a sibling .meta
# ---------------------------------------------------------------------------
def test_flappy_bird_pngs_copied_byte_for_byte(tmp_path):
    output_dir = tmp_path / "flappy"
    output_dir.mkdir()

    count = _copy_project_sprites("flappy_bird", output_dir)

    source_dir = _ASSETS_ROOT / "flappy_bird" / "Sprites"
    source_pngs = sorted(source_dir.rglob("*.png"))
    assert count == len(source_pngs)
    assert count > 0, "flappy_bird should have sprite assets in data/assets/"

    dest_dir = output_dir / "Assets" / "Art" / "Sprites"
    for src_png in source_pngs:
        rel = src_png.relative_to(source_dir)
        dest = dest_dir / rel
        assert dest.is_file(), f"PNG {rel} was not copied"
        assert (
            hashlib.sha256(src_png.read_bytes()).hexdigest()
            == hashlib.sha256(dest.read_bytes()).hexdigest()
        ), f"byte mismatch on {rel}"

        # Sibling .meta must exist with matching filename
        meta = dest.with_name(dest.name + ".meta")
        assert meta.is_file(), f"missing .meta for {rel}"


def test_every_png_has_sibling_meta(tmp_path):
    output_dir = tmp_path / "flappy"
    output_dir.mkdir()
    _copy_project_sprites("flappy_bird", output_dir)

    sprites_dir = output_dir / "Assets" / "Art" / "Sprites"
    pngs = list(sprites_dir.rglob("*.png"))
    for png in pngs:
        meta = png.with_name(png.name + ".meta")
        assert meta.exists(), f"{png.name} is missing its .meta"


# ---------------------------------------------------------------------------
# 3. Deterministic GUIDs
# ---------------------------------------------------------------------------
def test_guid_deterministic_across_calls(tmp_path):
    """Unity requires deterministic GUIDs so references in scenes/prefabs survive
    regeneration. The same asset path on two separate scaffold runs must yield
    the same GUID."""
    out1 = tmp_path / "p1"
    out2 = tmp_path / "p2"
    out1.mkdir()
    out2.mkdir()

    _copy_project_sprites("flappy_bird", out1)
    _copy_project_sprites("flappy_bird", out2)

    meta1 = (out1 / "Assets" / "Art" / "Sprites" / "Bird_01.png.meta").read_text()
    meta2 = (out2 / "Assets" / "Art" / "Sprites" / "Bird_01.png.meta").read_text()
    g1 = re.search(r"guid:\s*([0-9a-f]{32})", meta1).group(1)
    g2 = re.search(r"guid:\s*([0-9a-f]{32})", meta2).group(1)
    assert g1 == g2
    # and matches the ground-truth already checked in repo
    assert g1 == "552f41487df5b622a40b16d3bb3ea9cf"


def test_different_paths_produce_different_guids(tmp_path):
    """Distinct asset paths must map to distinct GUIDs — otherwise Unity picks
    one arbitrarily and breaks references."""
    out = tmp_path / "p"
    out.mkdir()
    _copy_project_sprites("flappy_bird", out)

    guids = set()
    for meta in (out / "Assets" / "Art" / "Sprites").rglob("*.meta"):
        m = re.search(r"guid:\s*([0-9a-f]{32})", meta.read_text())
        guids.add(m.group(1))
    # We expect as many unique GUIDs as copied .meta files
    assert len(guids) == len(list((out / "Assets" / "Art" / "Sprites").rglob("*.meta")))


# ---------------------------------------------------------------------------
# 4. Sprite-critical texture importer settings
# ---------------------------------------------------------------------------
def test_meta_textureType_is_8_sprite(tmp_path):
    """textureType: 8 = Sprite (2D). Any other value and the asset imports
    as a 3D Texture2D, causing SpriteRenderer to silently render nothing."""
    out = tmp_path / "p"
    out.mkdir()
    _copy_project_sprites("flappy_bird", out)

    for meta in (out / "Assets" / "Art" / "Sprites").rglob("*.meta"):
        content = meta.read_text()
        assert re.search(r"^\s*textureType:\s*8\s*$", content, re.MULTILINE), (
            f"{meta.name} missing textureType: 8"
        )


def test_meta_spriteMode_is_1_single(tmp_path):
    """spriteMode: 1 = Single (one sprite per texture). Multiple (2) requires
    sprite-sheet definitions and breaks automatic loading."""
    out = tmp_path / "p"
    out.mkdir()
    _copy_project_sprites("flappy_bird", out)

    for meta in (out / "Assets" / "Art" / "Sprites").rglob("*.meta"):
        content = meta.read_text()
        assert re.search(r"^\s*spriteMode:\s*1\s*$", content, re.MULTILINE), (
            f"{meta.name} missing spriteMode: 1"
        )


def test_meta_has_pixel_art_defaults(tmp_path):
    """filterMode: 0 (Point) and spritePixelsToUnits: 32 needed for 32px
    pixel-art to render crisp at unit scale."""
    out = tmp_path / "p"
    out.mkdir()
    _copy_project_sprites("flappy_bird", out)

    sample = next((out / "Assets" / "Art" / "Sprites").rglob("*.meta"))
    content = sample.read_text()
    assert re.search(r"^\s*filterMode:\s*0\s*$", content, re.MULTILINE)
    assert re.search(r"^\s*spritePixelsToUnits:\s*32\s*$", content, re.MULTILINE)
    assert content.startswith("fileFormatVersion: 2\n")


# ---------------------------------------------------------------------------
# 5. Nested subdirectories preserved
# ---------------------------------------------------------------------------
def test_nested_subdirectories_preserved(tmp_path, monkeypatch):
    fake_assets_root = tmp_path / "assets_root"
    src = fake_assets_root / "game_x" / "Sprites" / "Ghosts"
    src.mkdir(parents=True)
    (src / "Ghost_Body_01.png").write_bytes(b"\x89PNG\r\n\x1a\nFAKEBODY")
    nested = fake_assets_root / "game_x" / "Sprites" / "Ghosts" / "Eyes"
    nested.mkdir()
    (nested / "Ghost_Eyes_Left.png").write_bytes(b"\x89PNG\r\n\x1a\nFAKEEYE")
    # also a top-level one for variety
    (fake_assets_root / "game_x" / "Sprites" / "Background.png").write_bytes(
        b"\x89PNG\r\n\x1a\nFAKEBG"
    )

    monkeypatch.setattr(
        "src.exporter.project_scaffolder._ASSETS_ROOT", fake_assets_root
    )

    out = tmp_path / "proj"
    out.mkdir()
    count = _copy_project_sprites("game_x", out)
    assert count == 3

    sprites_dir = out / "Assets" / "Art" / "Sprites"
    assert (sprites_dir / "Background.png").is_file()
    assert (sprites_dir / "Background.png.meta").is_file()
    assert (sprites_dir / "Ghosts" / "Ghost_Body_01.png").is_file()
    assert (sprites_dir / "Ghosts" / "Ghost_Body_01.png.meta").is_file()
    assert (sprites_dir / "Ghosts" / "Eyes" / "Ghost_Eyes_Left.png").is_file()
    assert (sprites_dir / "Ghosts" / "Eyes" / "Ghost_Eyes_Left.png.meta").is_file()


def test_nested_meta_uses_relative_unity_path_for_guid(tmp_path, monkeypatch):
    """The GUID seed must include the full Unity relative path so that two
    sprites with the same basename in different subfolders get different
    GUIDs."""
    fake_assets_root = tmp_path / "assets_root"
    (fake_assets_root / "g" / "Sprites" / "A").mkdir(parents=True)
    (fake_assets_root / "g" / "Sprites" / "B").mkdir(parents=True)
    (fake_assets_root / "g" / "Sprites" / "A" / "icon.png").write_bytes(b"AAA")
    (fake_assets_root / "g" / "Sprites" / "B" / "icon.png").write_bytes(b"BBB")

    monkeypatch.setattr(
        "src.exporter.project_scaffolder._ASSETS_ROOT", fake_assets_root
    )

    out = tmp_path / "proj"
    out.mkdir()
    _copy_project_sprites("g", out)

    meta_a = (out / "Assets" / "Art" / "Sprites" / "A" / "icon.png.meta").read_text()
    meta_b = (out / "Assets" / "Art" / "Sprites" / "B" / "icon.png.meta").read_text()
    g_a = re.search(r"guid:\s*([0-9a-f]{32})", meta_a).group(1)
    g_b = re.search(r"guid:\s*([0-9a-f]{32})", meta_b).group(1)
    assert g_a != g_b


# ---------------------------------------------------------------------------
# 6. Fallback sprites coexist with real copies when call order matches
#    scaffold_project (_copy_project_sprites, then _write_default_sprites)
# ---------------------------------------------------------------------------
def test_fallback_sprites_coexist_with_real_copies(tmp_path):
    out = tmp_path / "p"
    out.mkdir()

    # Mirror scaffold_project order: copy real sprites first, then fallbacks
    _copy_project_sprites("flappy_bird", out)
    _write_default_sprites(out)

    sprites_dir = out / "Assets" / "Art" / "Sprites"
    # Fallbacks exist
    assert (sprites_dir / "WhiteSquare.png").is_file()
    assert (sprites_dir / "WhiteSquare.png.meta").is_file()
    assert (sprites_dir / "Circle.png").is_file()
    assert (sprites_dir / "Circle.png.meta").is_file()
    # Real copies also exist
    assert (sprites_dir / "Bird_01.png").is_file()
    assert (sprites_dir / "Background.png").is_file()


def test_fallback_does_not_overwrite_real_copy(tmp_path, monkeypatch):
    """If a real asset happens to be named WhiteSquare.png, _write_default_sprites
    must not clobber it (it checks png_path.exists() AND meta_path.exists())."""
    fake_assets_root = tmp_path / "assets_root"
    (fake_assets_root / "mygame" / "Sprites").mkdir(parents=True)
    sentinel = b"REAL_PIXEL_DATA_DO_NOT_OVERWRITE"
    (fake_assets_root / "mygame" / "Sprites" / "WhiteSquare.png").write_bytes(sentinel)

    monkeypatch.setattr(
        "src.exporter.project_scaffolder._ASSETS_ROOT", fake_assets_root
    )

    out = tmp_path / "p"
    out.mkdir()
    _copy_project_sprites("mygame", out)
    _write_default_sprites(out)

    content = (out / "Assets" / "Art" / "Sprites" / "WhiteSquare.png").read_bytes()
    assert content == sentinel


# ---------------------------------------------------------------------------
# Bonus: _sprite_meta_yaml behaviour in isolation (unit level sanity)
# ---------------------------------------------------------------------------
def test_sprite_meta_yaml_is_deterministic():
    a = _sprite_meta_yaml("Assets/Art/Sprites/Foo.png")
    b = _sprite_meta_yaml("Assets/Art/Sprites/Foo.png")
    assert a == b


def test_sprite_meta_yaml_includes_required_fields():
    meta = _sprite_meta_yaml("Assets/Art/Sprites/Foo.png")
    assert "textureType: 8" in meta
    assert "spriteMode: 1" in meta
    assert "fileFormatVersion: 2" in meta
    assert re.search(r"guid:\s*[0-9a-f]{32}", meta)
