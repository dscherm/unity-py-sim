"""Contract tests for src.assets.fill_gaps — the MCP gap scanner.

Derived from the behavioral spec for Direction C's image-asset pipeline
scanner, not from the implementation's test file. Tests verify:
  - gap counts match the ground truth of data/assets/<game>/Sprites/
  - FileNotFoundError for missing mappings
  - aspect-ratio helper returns only allowed MCP values
  - size_px clamp to >= 16
  - prompt composition contains expected content
  - idempotency and CLI JSON round-trip
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import is_dataclass, asdict
from pathlib import Path

import pytest

from src.assets import fill_gaps
from src.assets.fill_gaps import (
    _MCP_ASPECTS,
    _build_prompt,
    _closest_mcp_aspect,
    _parse_color_from_notes,
    _parse_size_from_notes,
    _size_px_from_world,
    GapSpec,
    scan_gaps,
)


ALLOWED_ASPECTS = {ra[1] for ra in _MCP_ASPECTS}
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def clean_assets_root(tmp_path, monkeypatch):
    """Point _ASSETS_ROOT at an empty tmp dir so "on-disk PNG" state is fully
    controlled. Other integration tests in this suite generate PNGs into the
    real data/assets/<game>/Sprites/ directories, which would otherwise
    contaminate our gap-count expectations.
    """
    monkeypatch.setattr(fill_gaps, "_ASSETS_ROOT", tmp_path)
    return tmp_path


# ---------------------------------------------------------------------------
# Gap-count contracts
# ---------------------------------------------------------------------------

def test_flappy_bird_has_zero_gaps():
    """All 9 PNGs for flappy_bird are on disk → scanner must find no gaps."""
    spec = scan_gaps("flappy_bird")
    assert isinstance(spec, GapSpec)
    assert spec.game == "flappy_bird"
    assert spec.gaps == [], (
        f"Expected 0 gaps for flappy_bird (all sprites present) — got "
        f"{len(spec.gaps)}: {[g.asset_ref for g in spec.gaps]}"
    )


def test_breakout_has_three_gaps(clean_assets_root):
    """breakout mapping has 3 sprites — on a clean assets root every one is a gap."""
    spec = scan_gaps("breakout")
    assert len(spec.gaps) == 3
    refs = {g.asset_ref for g in spec.gaps}
    assert refs == {"paddle", "ball", "brick"}


def test_pacman_has_over_twenty_gaps(clean_assets_root):
    """pacman mapping has 32 sprite entries — on a clean assets root all are gaps."""
    spec = scan_gaps("pacman")
    assert len(spec.gaps) > 20, (
        f"Expected >20 gaps for pacman, got {len(spec.gaps)}"
    )


def test_missing_mapping_raises_filenotfound():
    with pytest.raises(FileNotFoundError):
        scan_gaps("no_such_game_xyz")


# ---------------------------------------------------------------------------
# Aspect helper contracts
# ---------------------------------------------------------------------------

def test_closest_aspect_wide_maps_to_21_9():
    """200x40 → ratio 5.0, closest MCP-accepted is 21:9 (2.33)."""
    assert _closest_mcp_aspect((200, 40)) == "21:9"


def test_closest_aspect_square_maps_to_1_1():
    assert _closest_mcp_aspect((40, 40)) == "1:1"


def test_closest_aspect_tall_maps_to_9_16():
    """40x200 → ratio 0.2, closest is 9:16 (0.5625)."""
    assert _closest_mcp_aspect((40, 200)) == "9:16"


def test_closest_aspect_zero_height_returns_auto():
    """Height of 0 is a degenerate input — must not raise ZeroDivisionError."""
    assert _closest_mcp_aspect((100, 0)) == "auto"


def test_every_scan_aspect_is_allowed_value():
    """For every real scan, the emitted aspect field must be one of the MCP-accepted
    values. This guards against free-form strings like '5:1' leaking into the spec."""
    for game in ("breakout", "pacman", "space_invaders", "angry_birds"):
        spec = scan_gaps(game)
        for g in spec.gaps:
            assert g.aspect in ALLOWED_ASPECTS, (
                f"{game}/{g.asset_ref}: aspect '{g.aspect}' not in {ALLOWED_ASPECTS}"
            )


def test_mcp_aspects_list_contains_all_coplay_values():
    """Sanity check — the _MCP_ASPECTS list matches the CoPlay MCP's accepted set
    (1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9)."""
    expected = {"1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"}
    assert ALLOWED_ASPECTS == expected


# ---------------------------------------------------------------------------
# Pixel-size helper contracts
# ---------------------------------------------------------------------------

def test_size_px_clamped_to_minimum_16():
    """0.1 × 0.1 world * 16 ppu → 1.6 pre-clamp; must emerge as 16 × 16."""
    assert _size_px_from_world((0.1, 0.1), 16) == (16, 16)


def test_size_px_scales_linearly_when_above_floor():
    """2.0 world * 100 ppu = 200 (no clamp)."""
    assert _size_px_from_world((2.0, 0.4), 100) == (200, 40)


def test_size_px_rounds_half_to_int():
    """0.315 * 100 = 31.5 → 32 (banker's rounding in Python, but test exact)."""
    w, h = _size_px_from_world((0.315, 0.5), 100)
    assert (w, h) == (32, 50)


# ---------------------------------------------------------------------------
# Note parser contracts
# ---------------------------------------------------------------------------

def test_parse_color_extracts_rgb_tuple():
    assert _parse_color_from_notes("color_hint=[200, 200, 220], size=[2.0, 0.4]") == (200, 200, 220)


def test_parse_color_none_when_absent():
    assert _parse_color_from_notes("") is None
    assert _parse_color_from_notes("some other note") is None


def test_parse_size_extracts_float_tuple():
    assert _parse_size_from_notes("color_hint=[200, 200, 220], size=[2.0, 0.4]") == (2.0, 0.4)


def test_parse_size_none_when_absent():
    assert _parse_size_from_notes("") is None


# ---------------------------------------------------------------------------
# Prompt composition contracts
# ---------------------------------------------------------------------------

def test_paddle_prompt_contains_hex_and_game_name(clean_assets_root):
    """Prompt for breakout/paddle must carry the hex color and game name."""
    spec = scan_gaps("breakout")
    paddle_gap = next(g for g in spec.gaps if g.asset_ref == "paddle")
    assert "#c8c8dc" in paddle_gap.prompt
    assert "breakout" in paddle_gap.prompt


def test_prompt_contains_pixel_dimensions(clean_assets_root):
    spec = scan_gaps("breakout")
    ball_gap = next(g for g in spec.gaps if g.asset_ref == "ball")
    assert "40x40" in ball_gap.prompt


def test_build_prompt_uses_neutral_grey_when_color_missing():
    prompt = _build_prompt("foo", "thing", (16, 16), None, "")
    assert "neutral grey" in prompt
    assert "foo" in prompt
    assert "thing" in prompt


# ---------------------------------------------------------------------------
# Sprite gap structure contracts
# ---------------------------------------------------------------------------

def test_sprite_gap_shape(clean_assets_root):
    """Each gap entry exposes all fields expected by the MCP consumer."""
    spec = scan_gaps("breakout")
    assert spec.gaps, "breakout gaps must be non-empty for shape assertions"
    for g in spec.gaps:
        assert is_dataclass(g)
        assert g.dest_path.endswith(".png")
        assert g.unity_path.startswith("Assets/")
        assert g.prompt  # non-empty
        assert isinstance(g.size_px, tuple) and len(g.size_px) == 2
        assert g.size_px[0] >= 16 and g.size_px[1] >= 16
        assert g.object_size == f"{g.size_px[0]},{g.size_px[1]}"
        assert g.aspect in ALLOWED_ASPECTS
        assert g.ppu >= 1


def test_dest_path_under_game_sprites_dir(clean_assets_root):
    """dest_path must land under <assets_root>/<game>/Sprites/<basename>."""
    spec = scan_gaps("breakout")
    assert spec.gaps
    for g in spec.gaps:
        dest = Path(g.dest_path)
        # Normalize both sides — the file may not exist yet.
        assert dest.parent.name == "Sprites"
        assert dest.parent.parent.name == "breakout"


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

def test_scan_gaps_idempotent(clean_assets_root):
    """Calling scan_gaps twice must yield equal specs — no hidden state."""
    a = scan_gaps("breakout")
    b = scan_gaps("breakout")
    assert a == b
    # Deep-equality fallback — dataclass equality should already cover this,
    # but verify gap field-by-field for robustness.
    assert [asdict(g) for g in a.gaps] == [asdict(g) for g in b.gaps]


# ---------------------------------------------------------------------------
# CLI round-trip
# ---------------------------------------------------------------------------

def test_cli_writes_valid_json_with_allowed_aspects(tmp_path):
    """End-to-end: `python -m src.assets.fill_gaps space_invaders --output X`
    produces a parseable JSON doc where every gap's aspect is an allowed MCP
    value. We use space_invaders (no on-disk PNGs in any test scenario) rather
    than breakout because integration tests in this suite generate PNGs into
    data/assets/breakout/Sprites during their execution."""
    out_file = tmp_path / "spec.json"
    env = dict(os.environ)
    # Ensure the project root is on PYTHONPATH when invoking as a module.
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "src.assets.fill_gaps", "space_invaders",
         "--output", str(out_file)],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        env=env,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"CLI exited {result.returncode}\nstdout={result.stdout}\nstderr={result.stderr}"
    )
    assert out_file.exists(), "CLI did not write output file"
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["game"] == "space_invaders"
    assert len(data["gaps"]) >= 1, "space_invaders mapping has sprites, none on disk"
    for g in data["gaps"]:
        assert g["aspect"] in ALLOWED_ASPECTS


def test_cli_strict_exits_nonzero_when_gaps_exist(tmp_path):
    """--strict flag should cause exit 1 for a game with gaps (space_invaders
    has no on-disk PNGs in any test scenario, so always has gaps)."""
    out_file = tmp_path / "spec.json"
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "src.assets.fill_gaps", "space_invaders",
         "--strict", "--output", str(out_file)],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        env=env,
        timeout=60,
    )
    assert result.returncode == 1, (
        f"--strict should exit 1 when gaps exist; got {result.returncode}"
    )


def test_cli_strict_exits_zero_when_no_gaps(tmp_path):
    """flappy_bird has every PNG on disk, so --strict must exit 0."""
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PROJECT_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, "-m", "src.assets.fill_gaps", "flappy_bird", "--strict"],
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        env=env,
        timeout=60,
    )
    assert result.returncode == 0, (
        f"flappy_bird has no gaps; --strict should exit 0; got {result.returncode}"
    )
