"""Asset mapping — links symbolic asset_ref names to Unity asset paths.

A mapping file bridges the gap between Python's colored-rectangle placeholders
and real Unity assets (sprites, audio clips, materials).

Usage:
    python -m src.assets.mapping validate <manifest.json> <mapping.json>
    python -m src.assets.mapping scaffold <manifest.json> --output <mapping.json>
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


@dataclass
class SpriteMapping:
    """Maps a sprite asset_ref to a Unity asset."""
    unity_path: str  # e.g. "Assets/Sprites/Birds/bird_red.png"
    sprite_name: str | None = None  # sub-sprite name if sprite sheet
    ppu: int = 100  # pixels per unit
    material: str = "Sprite-Unlit-Default"  # URP material name
    sorting_layer: str = "Default"
    filter_mode: str = "Point"  # Point, Bilinear, Trilinear
    compression: str = "Normal"  # None, Low, Normal, High
    is_readable: bool = False  # True if runtime pixel manipulation needed
    notes: str = ""


@dataclass
class AudioMapping:
    """Maps an audio clip_ref to a Unity asset."""
    unity_path: str  # e.g. "Assets/Audio/bird_launch.wav"
    notes: str = ""


@dataclass
class AssetMapping:
    """Complete mapping from asset_refs to Unity asset paths."""
    sprites: dict[str, SpriteMapping] = field(default_factory=dict)
    audio: dict[str, AudioMapping] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "sprites": {k: asdict(v) for k, v in self.sprites.items()},
            "audio": {k: asdict(v) for k, v in self.audio.items()},
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, text: str) -> AssetMapping:
        data = json.loads(text)
        mapping = cls()
        for k, v in data.get("sprites", {}).items():
            mapping.sprites[k] = SpriteMapping(**v)
        for k, v in data.get("audio", {}).items():
            mapping.audio[k] = AudioMapping(**v)
        return mapping

    @classmethod
    def from_file(cls, path: str | Path) -> AssetMapping:
        return cls.from_json(Path(path).read_text(encoding="utf-8"))

    def save(self, path: str | Path) -> None:
        Path(path).write_text(self.to_json(), encoding="utf-8")


def validate_mapping(manifest_path: str | Path, mapping_path: str | Path) -> list[str]:
    """Validate that a mapping covers all asset_refs in a manifest.

    Returns a list of warning/error strings. Empty list means valid.
    """
    from src.assets.manifest import AssetManifest

    manifest = AssetManifest.from_json(Path(manifest_path).read_text(encoding="utf-8"))
    mapping = AssetMapping.from_file(mapping_path)

    issues = []

    # Check all manifest sprites have mappings
    for ref in manifest.sprites:
        if ref not in mapping.sprites:
            issues.append(f"UNMAPPED sprite: '{ref}' (used by {len(manifest.sprites[ref].game_objects)} objects)")
        else:
            sm = mapping.sprites[ref]
            if not sm.unity_path:
                issues.append(f"EMPTY unity_path for sprite: '{ref}'")

    # Check all manifest audio have mappings
    for ref in manifest.audio:
        if ref not in mapping.audio:
            issues.append(f"UNMAPPED audio: '{ref}' (used by {len(manifest.audio[ref].game_objects)} objects)")
        else:
            am = mapping.audio[ref]
            if not am.unity_path:
                issues.append(f"EMPTY unity_path for audio: '{ref}'")

    # Check for orphan mappings (in mapping but not in manifest)
    for ref in mapping.sprites:
        if ref not in manifest.sprites:
            issues.append(f"ORPHAN sprite mapping: '{ref}' not in manifest")
    for ref in mapping.audio:
        if ref not in manifest.audio:
            issues.append(f"ORPHAN audio mapping: '{ref}' not in manifest")

    return issues


def scaffold_mapping(manifest_path: str | Path) -> AssetMapping:
    """Generate a skeleton mapping file from a manifest with TODO placeholders."""
    from src.assets.manifest import AssetManifest

    manifest = AssetManifest.from_json(Path(manifest_path).read_text(encoding="utf-8"))
    mapping = AssetMapping()

    for ref, info in manifest.sprites.items():
        mapping.sprites[ref] = SpriteMapping(
            unity_path=f"Assets/Sprites/{ref}.png",
            sprite_name=f"{ref}_0",
            ppu=100,
            material="Sprite-Unlit-Default",
            notes=f"color_hint={list(info.color_hint)}, size={list(info.size)}",
        )

    for ref, info in manifest.audio.items():
        mapping.audio[ref] = AudioMapping(
            unity_path=f"Assets/Audio/{ref}.wav",
            notes=f"used by {len(info.game_objects)} objects",
        )

    return mapping


def main():
    import sys

    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage:")
        print("  python -m src.assets.mapping validate <manifest.json> <mapping.json>")
        print("  python -m src.assets.mapping scaffold <manifest.json> --output <mapping.json>")
        sys.exit(1)

    command = args[0]

    if command == "validate":
        if len(args) < 3:
            print("Usage: python -m src.assets.mapping validate <manifest.json> <mapping.json>")
            sys.exit(1)
        issues = validate_mapping(args[1], args[2])
        if issues:
            print(f"VALIDATION FAILED — {len(issues)} issue(s):")
            for issue in issues:
                print(f"  {issue}")
            sys.exit(1)
        else:
            print("VALIDATION PASSED — all asset_refs are mapped")

    elif command == "scaffold":
        output_path = None
        if "--output" in args:
            idx = args.index("--output")
            output_path = Path(args[idx + 1])

        mapping = scaffold_mapping(args[1])
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            mapping.save(output_path)
            print(f"Scaffold mapping written to {output_path}")
            print(f"  {len(mapping.sprites)} sprite mappings, {len(mapping.audio)} audio mappings")
            print("  Edit the file to fill in actual Unity asset paths")
        else:
            print(mapping.to_json())

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
