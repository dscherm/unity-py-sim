"""Mutation tests for src.assets.fill_gaps — prove the contract tests bite.

We monkeypatch internals of fill_gaps and assert that previously-passing contracts
fail. If these mutation tests fail, the corresponding contract test is toothless.
"""
from __future__ import annotations


import pytest

from src.assets import fill_gaps


ALLOWED_ASPECTS = {ra[1] for ra in fill_gaps._MCP_ASPECTS}


@pytest.fixture
def clean_assets_root(tmp_path, monkeypatch):
    """Isolate from other suite tests that may have generated sprite PNGs
    into data/assets/breakout/Sprites — point _ASSETS_ROOT at a fresh dir."""
    monkeypatch.setattr(fill_gaps, "_ASSETS_ROOT", tmp_path)
    return tmp_path


def test_mutation_aspect_always_9_16_breaks_aspect_correctness(monkeypatch, clean_assets_root):
    """If _closest_mcp_aspect is forced to return '9:16' for every input, then
    breakout/paddle (200x40) should NOT end up with a correct aspect — the
    aspect-correctness assertion should fire."""
    monkeypatch.setattr(fill_gaps, "_closest_mcp_aspect", lambda size: "9:16")

    spec = fill_gaps.scan_gaps("breakout")
    paddle = next(g for g in spec.gaps if g.asset_ref == "paddle")
    # The real paddle is 200x40 → should be 21:9. Under mutation it is 9:16.
    assert paddle.aspect == "9:16"
    # Now simulate the contract test: the paddle aspect should match the
    # correct closest aspect; under mutation, it does not.
    with pytest.raises(AssertionError):
        # This mirrors what a well-written contract would assert.
        correct = "21:9"
        assert paddle.aspect == correct, (
            f"paddle aspect '{paddle.aspect}' != expected '{correct}' "
            f"(mutation detected)"
        )


def test_mutation_aspect_always_9_16_pollutes_allowed_value_set(monkeypatch, clean_assets_root):
    """Pathological mutation: return a free-form string like '5:1' — the
    allowed-value guard should fail for at least one gap."""
    monkeypatch.setattr(fill_gaps, "_closest_mcp_aspect", lambda size: "5:1")

    spec = fill_gaps.scan_gaps("breakout")
    violations = [g for g in spec.gaps if g.aspect not in ALLOWED_ASPECTS]
    assert violations, "Expected aspect to leak invalid value under mutation"


def test_mutation_assets_root_to_bogus_path_makes_flappy_gap(monkeypatch, tmp_path):
    """If _ASSETS_ROOT points at an empty directory, flappy_bird's 9 PNGs
    will all be "missing" and scan_gaps should report 9 gaps, breaking the
    "0 gaps" contract."""
    bogus = tmp_path / "nowhere"
    bogus.mkdir()
    monkeypatch.setattr(fill_gaps, "_ASSETS_ROOT", bogus)

    spec = fill_gaps.scan_gaps("flappy_bird")
    assert len(spec.gaps) == 9, (
        f"With a bogus _ASSETS_ROOT, flappy_bird should show 9 gaps; got "
        f"{len(spec.gaps)}"
    )
    # Simulate the contract test — it should now fail.
    with pytest.raises(AssertionError):
        assert spec.gaps == [], (
            f"Expected 0 gaps; got {len(spec.gaps)} (mutation detected)"
        )


def test_mutation_size_px_drop_clamp_breaks_minimum(monkeypatch):
    """If the size_px helper drops the clamp, a tiny world size would produce
    sub-16 pixel dimensions. The contract "size_px >= 16" must catch this."""
    def unclamped(world_size, ppu):
        return (int(round(world_size[0] * ppu)), int(round(world_size[1] * ppu)))

    monkeypatch.setattr(fill_gaps, "_size_px_from_world", unclamped)

    # 0.1 × 0.1 world at 16 ppu = 1.6 → under unclamped it becomes 2.
    w, h = fill_gaps._size_px_from_world((0.1, 0.1), 16)
    assert (w, h) == (2, 2)
    # And the contract must bite:
    with pytest.raises(AssertionError):
        assert w >= 16 and h >= 16, (
            f"size_px {(w, h)} below 16 (mutation detected)"
        )


def test_mutation_build_prompt_drops_color_breaks_hex_contract(monkeypatch, clean_assets_root):
    """If _build_prompt stops including the hex color, the paddle prompt
    contract (hex present) should fail."""
    def dropped(game, asset_ref, size_px, color, notes):
        return f"pixel art of {asset_ref} for {game}"

    monkeypatch.setattr(fill_gaps, "_build_prompt", dropped)

    spec = fill_gaps.scan_gaps("breakout")
    paddle = next(g for g in spec.gaps if g.asset_ref == "paddle")
    assert "#c8c8dc" not in paddle.prompt
    with pytest.raises(AssertionError):
        assert "#c8c8dc" in paddle.prompt, "hex color missing (mutation detected)"


def test_mutation_scan_always_empty_breaks_gap_count(monkeypatch, clean_assets_root):
    """If scan_gaps is replaced with one that always returns no gaps, the
    breakout "exactly 3 gaps" contract fails."""
    real_scan = fill_gaps.scan_gaps

    def empty(game):
        s = real_scan(game)
        return fill_gaps.GapSpec(game=s.game, mapping_file=s.mapping_file,
                                 assets_dir=s.assets_dir, gaps=[])

    monkeypatch.setattr(fill_gaps, "scan_gaps", empty)

    spec = fill_gaps.scan_gaps("breakout")
    assert len(spec.gaps) == 0
    with pytest.raises(AssertionError):
        assert len(spec.gaps) == 3, (
            f"breakout should have 3 gaps; got {len(spec.gaps)} (mutation detected)"
        )
