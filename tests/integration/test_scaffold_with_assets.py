"""Integration tests: full `scaffold_project` calls with real assets.

We exercise the public API end-to-end and verify file-counts, byte equality
against the source assets, and that scaffolding a game WITHOUT a
`data/assets/<name>/` dir still succeeds (just emits fallbacks).
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from src.exporter.project_scaffolder import _ASSETS_ROOT, scaffold_project


def _count_pngs(root: Path) -> list[Path]:
    return sorted(root.rglob("*.png"))


def _count_metas(root: Path) -> list[Path]:
    return sorted(root.rglob("*.png.meta"))


def test_scaffold_flappy_bird_has_9_real_plus_2_fallback_pngs(tmp_path):
    """Acceptance criterion: flappy_bird scaffold => 9 source PNGs + 2
    fallback PNGs (WhiteSquare, Circle), each with a sibling .meta."""
    out = tmp_path / "flappy_unity"
    result = scaffold_project(
        "flappy_bird",
        out,
        cs_files={"Dummy.cs": "using UnityEngine;\npublic class Dummy : MonoBehaviour {}\n"},
    )
    assert result == out

    sprites_dir = out / "Assets" / "Art" / "Sprites"
    pngs = _count_pngs(sprites_dir)
    metas = _count_metas(sprites_dir)

    # Determine ground-truth source PNGs
    source_pngs = list((_ASSETS_ROOT / "flappy_bird" / "Sprites").rglob("*.png"))
    assert len(source_pngs) == 9, (
        f"Expected flappy_bird to ship 9 source PNGs; found {len(source_pngs)}. "
        "Test assertion pinned by the PR description."
    )

    assert len(pngs) == 9 + 2, f"expected 11 PNGs, got {len(pngs)}: {pngs}"
    assert len(metas) == 9 + 2, f"expected 11 .meta files, got {len(metas)}: {metas}"

    # Every source PNG should be present, byte-identical, with sibling .meta
    for src in source_pngs:
        dest = sprites_dir / src.name
        assert dest.is_file()
        assert hashlib.sha256(src.read_bytes()).hexdigest() == \
            hashlib.sha256(dest.read_bytes()).hexdigest()
        assert (sprites_dir / (src.name + ".meta")).is_file()

    # Fallbacks also present
    assert (sprites_dir / "WhiteSquare.png").is_file()
    assert (sprites_dir / "WhiteSquare.png.meta").is_file()
    assert (sprites_dir / "Circle.png").is_file()
    assert (sprites_dir / "Circle.png.meta").is_file()


def test_scaffold_breakout_has_only_fallback_sprites(tmp_path):
    """breakout currently has no `data/assets/breakout/Sprites/` directory, so
    scaffold should still succeed and emit ONLY the two fallback PNGs."""
    breakout_src = _ASSETS_ROOT / "breakout" / "Sprites"
    # Precondition: breakout has no source sprites (as the task description states)
    if breakout_src.exists() and any(breakout_src.rglob("*.png")):
        pytest.skip(
            "breakout now has source sprites; precondition for this test no longer holds"
        )

    out = tmp_path / "breakout_unity"
    scaffold_project(
        "breakout",
        out,
        cs_files={"Dummy.cs": "using UnityEngine;\npublic class Dummy : MonoBehaviour {}\n"},
    )

    sprites_dir = out / "Assets" / "Art" / "Sprites"
    pngs = _count_pngs(sprites_dir)
    metas = _count_metas(sprites_dir)
    names = {p.name for p in pngs}

    assert names == {"WhiteSquare.png", "Circle.png"}, (
        f"expected only fallback sprites for breakout, got {names}"
    )
    assert len(metas) == 2


def test_scaffold_nonexistent_game_still_succeeds(tmp_path):
    """A game with no `data/assets/<name>/` dir should not crash scaffold."""
    out = tmp_path / "phantom_unity"
    result = scaffold_project(
        "__phantom_game_does_not_exist__",
        out,
        cs_files={"Dummy.cs": "using UnityEngine;\npublic class Dummy : MonoBehaviour {}\n"},
    )
    assert result == out

    sprites_dir = out / "Assets" / "Art" / "Sprites"
    # Only fallback sprites
    pngs = _count_pngs(sprites_dir)
    assert len(pngs) == 2
    assert {p.name for p in pngs} == {"WhiteSquare.png", "Circle.png"}


def test_scaffold_produces_valid_unity_project_structure(tmp_path):
    """Even with sprite copying, scaffold must still produce the baseline
    Unity project layout."""
    out = tmp_path / "unity"
    scaffold_project(
        "flappy_bird",
        out,
        cs_files={"Foo.cs": "using UnityEngine;\npublic class Foo : MonoBehaviour {}\n"},
    )
    # Core directories
    assert (out / "Assets" / "_Project" / "Scripts").is_dir()
    assert (out / "Assets" / "_Project" / "Scenes" / "Scene.unity").is_file()
    assert (out / "Assets" / "Art" / "Sprites").is_dir()
    assert (out / "Packages" / "manifest.json").is_file()
    assert (out / "ProjectSettings" / "ProjectVersion.txt").is_file()
    assert (out / "ProjectSettings" / "ProjectSettings.asset").is_file()
    # Script was placed
    assert (out / "Assets" / "_Project" / "Scripts" / "Foo.cs").is_file()


def test_scaffold_is_idempotent(tmp_path):
    """Calling scaffold twice on the same output dir must not double-count
    or corrupt sprites/.meta files."""
    out = tmp_path / "unity"
    scaffold_project(
        "flappy_bird",
        out,
        cs_files={"Dummy.cs": "using UnityEngine;\npublic class Dummy : MonoBehaviour {}\n"},
    )
    first_pngs = {p.name for p in _count_pngs(out / "Assets" / "Art" / "Sprites")}

    scaffold_project(
        "flappy_bird",
        out,
        cs_files={"Dummy.cs": "using UnityEngine;\npublic class Dummy : MonoBehaviour {}\n"},
    )
    second_pngs = {p.name for p in _count_pngs(out / "Assets" / "Art" / "Sprites")}

    assert first_pngs == second_pngs
    assert len(second_pngs) == 9 + 2
