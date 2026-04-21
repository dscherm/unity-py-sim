"""Scan a game's mapping for missing sprite PNGs and emit a prompt spec.

Direction C of the image-asset pipeline: rather than hand-sourcing art, the
scanner finds mapping entries where ``data/assets/<game>/Sprites/<basename>``
is missing and writes a JSON prompt spec that a Claude session (or any
image-generation tool) can consume to fill the gaps.

Usage::

    python -m src.assets.fill_gaps breakout
    python -m src.assets.fill_gaps flappy_bird --output prompts.json
    python -m src.assets.fill_gaps pacman_v2 --strict   # exit 1 if gaps exist

The consumer side lives in Claude Code: it reads ``prompts.json``, invokes
``mcp__coplay-mcp__generate_or_edit_images`` per entry, and writes the returned
PNG to ``dest_path``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

from src.assets.mapping import AssetMapping

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ASSETS_ROOT = _PROJECT_ROOT / "data" / "assets"
_MAPPINGS_ROOT = _PROJECT_ROOT / "data" / "mappings"


_MCP_ASPECTS: tuple[tuple[float, str], ...] = (
    (21 / 9, "21:9"), (16 / 9, "16:9"), (3 / 2, "3:2"),
    (4 / 3, "4:3"), (5 / 4, "5:4"), (1.0, "1:1"),
    (4 / 5, "4:5"), (3 / 4, "3:4"), (2 / 3, "2:3"),
    (9 / 16, "9:16"),
)


def _closest_mcp_aspect(size_px: tuple[int, int]) -> str:
    """Map a pixel (w, h) to the closest aspect the CoPlay MCP accepts."""
    w, h = size_px
    if h <= 0:
        return "auto"
    ratio = w / h
    return min(_MCP_ASPECTS, key=lambda ra: abs(ra[0] - ratio))[1]


@dataclass
class SpriteGap:
    asset_ref: str
    dest_path: str          # absolute path where PNG should land
    unity_path: str         # mapping's Unity path (for reference)
    prompt: str             # image-gen prompt
    size_px: tuple[int, int]
    object_size: str        # CSV width,height for mcp object_size
    aspect: str             # closest MCP-accepted aspect ratio
    color_hint: tuple[int, int, int] | None
    ppu: int
    notes: str


@dataclass
class GapSpec:
    game: str
    mapping_file: str
    assets_dir: str
    gaps: list[SpriteGap]


_COLOR_NOTE_RE = re.compile(r"color_hint=\[([\d,\s]+)\]")
_SIZE_NOTE_RE = re.compile(r"size=\[([\d.,\s]+)\]")


def _parse_color_from_notes(notes: str) -> tuple[int, int, int] | None:
    m = _COLOR_NOTE_RE.search(notes or "")
    if not m:
        return None
    parts = [int(float(p.strip())) for p in m.group(1).split(",")]
    return (parts[0], parts[1], parts[2]) if len(parts) >= 3 else None


def _parse_size_from_notes(notes: str) -> tuple[float, float] | None:
    m = _SIZE_NOTE_RE.search(notes or "")
    if not m:
        return None
    parts = [float(p.strip()) for p in m.group(1).split(",")]
    return (parts[0], parts[1]) if len(parts) >= 2 else None


def _size_px_from_world(world_size: tuple[float, float], ppu: int) -> tuple[int, int]:
    """World units (from Python size field) × PPU → pixel dimensions, clamped to power of two >= 16."""
    w = max(16, int(round(world_size[0] * ppu)))
    h = max(16, int(round(world_size[1] * ppu)))
    return (w, h)


def _shape_hint(size_px: tuple[int, int]) -> str:
    w, h = size_px
    ratio = w / h if h else 1.0
    if ratio > 2.0:
        return "wide horizontal"
    if ratio < 0.5:
        return "tall vertical"
    return "square"


def _color_hex(color: tuple[int, int, int] | None) -> str:
    if color is None:
        return "neutral grey"
    return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"


def _build_prompt(game: str, asset_ref: str, size_px: tuple[int, int],
                  color: tuple[int, int, int] | None, notes: str) -> str:
    shape = _shape_hint(size_px)
    color_txt = _color_hex(color)
    descriptor = asset_ref.replace("_", " ")
    extra = f" ({notes.strip()})" if notes and "color_hint" not in notes else ""
    return (
        f"Pixel art sprite of a {descriptor} for the {game} game, "
        f"{shape} {size_px[0]}x{size_px[1]} PNG, dominant color {color_txt}, "
        f"transparent background, 8-bit retro style, crisp pixel edges{extra}"
    )


def scan_gaps(game: str) -> GapSpec:
    mapping_path = _MAPPINGS_ROOT / f"{game}_mapping.json"
    if not mapping_path.exists():
        raise FileNotFoundError(f"No mapping for '{game}' at {mapping_path}")

    mapping = AssetMapping.from_file(mapping_path)
    sprites_dir = _ASSETS_ROOT / game / "Sprites"

    gaps: list[SpriteGap] = []
    for ref, sm in mapping.sprites.items():
        if not sm.unity_path:
            continue
        basename = Path(sm.unity_path).name
        dest = sprites_dir / basename
        if dest.exists():
            continue

        color = _parse_color_from_notes(sm.notes)
        world_size = _parse_size_from_notes(sm.notes) or (1.0, 1.0)
        size_px = _size_px_from_world(world_size, sm.ppu)
        prompt = _build_prompt(game, ref, size_px, color, sm.notes)

        gaps.append(SpriteGap(
            asset_ref=ref,
            dest_path=str(dest),
            unity_path=sm.unity_path,
            prompt=prompt,
            size_px=size_px,
            object_size=f"{size_px[0]},{size_px[1]}",
            aspect=_closest_mcp_aspect(size_px),
            color_hint=color,
            ppu=sm.ppu,
            notes=sm.notes,
        ))

    return GapSpec(
        game=game,
        mapping_file=str(mapping_path),
        assets_dir=str(sprites_dir),
        gaps=gaps,
    )


def _spec_to_dict(spec: GapSpec) -> dict[str, Any]:
    return {
        "game": spec.game,
        "mapping_file": spec.mapping_file,
        "assets_dir": spec.assets_dir,
        "gaps": [asdict(g) for g in spec.gaps],
    }


def _placeholder_png(size_px: tuple[int, int], color: tuple[int, int, int],
                     shape: str) -> bytes:
    """Solid-color RGBA PNG with a shape-aware silhouette.

    Non-AI fallback for Direction C when MCP image gen isn't reachable.
    Makes the Python simulator visual without waiting on a home-machine pass.
    """
    from src.exporter.project_scaffolder import _encode_png
    w, h = size_px
    r, g, b = color
    pixels = bytearray(w * h * 4)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    radius = min(w, h) / 2.0 - 1.0

    for y in range(h):
        for x in range(w):
            off = (y * w + x) * 4
            inside = True
            if shape == "circle":
                dx, dy = x - cx, y - cy
                inside = (dx * dx + dy * dy) <= radius * radius
            pixels[off] = r if inside else 0
            pixels[off + 1] = g if inside else 0
            pixels[off + 2] = b if inside else 0
            pixels[off + 3] = 255 if inside else 0
    return _encode_png(w, h, bytes(pixels))


def _shape_for_ref(asset_ref: str) -> str:
    """Heuristic: 'ball'/'pellet'/'dot' → circle; everything else → rectangle."""
    lower = asset_ref.lower()
    if any(k in lower for k in ("ball", "pellet", "dot", "coin", "orb")):
        return "circle"
    return "rect"


def fill_with_placeholders(spec: GapSpec) -> int:
    """Write a procedural PNG for every gap in ``spec``. Returns count written."""
    written = 0
    for gap in spec.gaps:
        color = gap.color_hint or (200, 200, 200)
        shape = _shape_for_ref(gap.asset_ref)
        png_bytes = _placeholder_png(gap.size_px, color, shape)
        dest = Path(gap.dest_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(png_bytes)
        written += 1
    return written


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game", help="Game name (matches data/mappings/<game>_mapping.json)")
    parser.add_argument("--output", default=None, help="Write spec JSON here (default: stdout)")
    parser.add_argument("--strict", action="store_true",
                        help="Exit 1 when gaps exist (for CI/hook integration)")
    parser.add_argument("--fill-placeholders", action="store_true",
                        help="Write procedural PNGs for every gap (non-AI fallback)")
    args = parser.parse_args(argv)

    spec = scan_gaps(args.game)

    if args.fill_placeholders:
        n = fill_with_placeholders(spec)
        print(f"[fill_gaps] wrote {n} placeholder PNG(s) to {spec.assets_dir}")
        return 0

    payload = json.dumps(_spec_to_dict(spec), indent=2)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(payload, encoding="utf-8")
        print(f"[fill_gaps] {len(spec.gaps)} gap(s) for {args.game} -> {out_path}")
    else:
        print(payload)

    if args.strict and spec.gaps:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
