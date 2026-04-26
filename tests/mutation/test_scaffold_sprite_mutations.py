"""Mutation tests — prove the sprite tests fail when the underlying
implementation is broken.

Each test monkeypatches a key helper to produce invalid output, then runs the
scaffold and asserts the expected post-condition is violated. If any of these
fails to fail, the tests aren't actually catching the bug."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from src.exporter import project_scaffolder as ps


def _count_real_pngs(sprites_dir: Path) -> list[Path]:
    """All PNGs in the sprites dir EXCEPT the two fallbacks."""
    out: list[Path] = []
    for p in sprites_dir.rglob("*.png"):
        if p.name in {"WhiteSquare.png", "Circle.png"}:
            continue
        out.append(p)
    return out


def test_if_copy_returns_zero_scaffold_has_no_real_sprites(tmp_path, monkeypatch):
    """Monkeypatch `_copy_project_sprites` to be a no-op. After scaffolding
    flappy_bird, the project should contain ZERO real sprites (only fallbacks).
    This demonstrates that `test_scaffold_flappy_bird_has_9_real_plus_2_fallback_pngs`
    would fail under this mutation."""

    def broken_copy(game_name, output_dir):  # noqa: ARG001
        return 0

    monkeypatch.setattr(ps, "_copy_project_sprites", broken_copy)

    out = tmp_path / "mut"
    ps.scaffold_project(
        "flappy_bird",
        out,
        cs_files={"Dummy.cs": "using UnityEngine;\npublic class Dummy : MonoBehaviour {}\n"},
    )

    sprites_dir = out / "Assets" / "Art" / "Sprites"
    real = _count_real_pngs(sprites_dir)
    # The mutation should remove all real sprites. This assertion is the proof.
    assert real == [], (
        f"Expected ZERO real sprites under the broken-copy mutation, got {real}. "
        "The contract test would have passed even without the real implementation — "
        "meaning the test is not actually covering the copy behaviour."
    )
    # Fallbacks still present (scaffold still writes defaults)
    assert (sprites_dir / "WhiteSquare.png").is_file()
    assert (sprites_dir / "Circle.png").is_file()


def test_if_meta_has_wrong_textureType_contract_test_would_catch_it(tmp_path, monkeypatch):
    """Monkeypatch `_sprite_meta_yaml` to emit textureType: 0. The
    `test_meta_textureType_is_8_sprite` contract should then flag a violation.
    We re-run the same detection logic here to prove it."""

    def broken_meta(asset_path: str) -> str:
        # Keep a valid fileFormatVersion but set textureType to 0 (Default)
        # — Unity would import as Texture2D, SpriteRenderer renders nothing.
        from src.exporter.project_scaffolder import _stable_guid
        guid = _stable_guid(asset_path)
        return (
            "fileFormatVersion: 2\n"
            f"guid: {guid}\n"
            "TextureImporter:\n"
            "  textureType: 0\n"
            "  spriteMode: 1\n"
        )

    monkeypatch.setattr(ps, "_sprite_meta_yaml", broken_meta)

    out = tmp_path / "mut"
    ps.scaffold_project(
        "flappy_bird",
        out,
        cs_files={"Dummy.cs": "using UnityEngine;\npublic class Dummy : MonoBehaviour {}\n"},
    )

    sprites_dir = out / "Assets" / "Art" / "Sprites"
    metas = list(sprites_dir.rglob("*.meta"))
    assert metas, "no .meta files were produced"

    # Reproduce the textureType check from the contract test — it MUST fail
    # under this mutation.
    bad_count = 0
    for meta in metas:
        content = meta.read_text()
        if not re.search(r"^\s*textureType:\s*8\s*$", content, re.MULTILINE):
            bad_count += 1
    assert bad_count == len(metas), (
        "Under the broken-meta mutation we expected every .meta to violate the "
        "textureType=8 check; if fewer violate, our contract test is weaker than "
        "it should be."
    )


def test_if_meta_has_wrong_spriteMode_contract_test_would_catch_it(tmp_path, monkeypatch):
    """Same pattern as above but for spriteMode."""

    def broken_meta(asset_path: str) -> str:
        from src.exporter.project_scaffolder import _stable_guid
        guid = _stable_guid(asset_path)
        return (
            "fileFormatVersion: 2\n"
            f"guid: {guid}\n"
            "TextureImporter:\n"
            "  textureType: 8\n"
            "  spriteMode: 2\n"
        )

    monkeypatch.setattr(ps, "_sprite_meta_yaml", broken_meta)

    out = tmp_path / "mut"
    ps.scaffold_project(
        "flappy_bird",
        out,
        cs_files={"Dummy.cs": "using UnityEngine;\npublic class Dummy : MonoBehaviour {}\n"},
    )

    sprites_dir = out / "Assets" / "Art" / "Sprites"
    metas = list(sprites_dir.rglob("*.meta"))
    assert metas

    bad_count = 0
    for meta in metas:
        content = meta.read_text()
        if not re.search(r"^\s*spriteMode:\s*1\s*$", content, re.MULTILINE):
            bad_count += 1
    assert bad_count == len(metas), (
        "Broken-meta mutation should fail the spriteMode=1 contract on every file."
    )


def test_if_copy_skips_meta_generation_sprites_are_dangling(tmp_path, monkeypatch):
    """Mutation: copy PNGs but skip .meta file generation. Unity treats PNGs
    without .meta files as unimported (or assigns a fresh random GUID on import
    which breaks references). We detect this by counting .meta files."""

    real_copy = ps._copy_project_sprites

    def half_broken_copy(game_name, output_dir):
        """Call through, then delete all .meta files produced by the copy."""
        result = real_copy(game_name, output_dir)
        sprites_dir = output_dir / "Assets" / "Art" / "Sprites"
        for meta in sprites_dir.rglob("*.png.meta"):
            # Only delete metas for non-fallback PNGs to simulate "forgot to
            # generate metas"
            if meta.stem not in {"WhiteSquare.png", "Circle.png"}:
                meta.unlink()
        return result

    monkeypatch.setattr(ps, "_copy_project_sprites", half_broken_copy)

    out = tmp_path / "mut"
    ps.scaffold_project(
        "flappy_bird",
        out,
        cs_files={"Dummy.cs": "using UnityEngine;\npublic class Dummy : MonoBehaviour {}\n"},
    )
    sprites_dir = out / "Assets" / "Art" / "Sprites"

    # Real PNGs should NOT have sibling .meta under this mutation
    real_pngs = _count_real_pngs(sprites_dir)
    assert real_pngs, "expected real PNGs to still be copied"
    missing_metas = [p for p in real_pngs if not p.with_name(p.name + ".meta").exists()]
    assert missing_metas == real_pngs, (
        "Under the broken-copy-without-meta mutation, every real PNG should be "
        "missing its .meta. If any have one, our 'every PNG has a sibling .meta' "
        "contract test would have missed the regression."
    )
