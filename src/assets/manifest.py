"""Extract asset references from a running scene into an asset manifest.

Scans all GameObjects for SpriteRenderer.asset_ref and AudioSource.clip_ref,
producing a JSON manifest that maps symbolic asset names to their properties
(color hint, size, sorting order, component type).

Usage:
    python -m src.assets.manifest <setup_module> [--output path.json]

Example:
    python -m src.assets.manifest examples/angry_birds/run_angry_birds.py --output data/manifests/angry_birds.json
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Any

from src.engine.core import _game_objects, GameObject
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.audio import AudioSource


@dataclass
class SpriteAssetInfo:
    """Metadata for a sprite asset reference."""
    asset_ref: str
    color_hint: tuple[int, int, int] = (255, 255, 255)
    size: tuple[float, float] = (1.0, 1.0)
    sorting_order: int = 0
    game_objects: list[str] = field(default_factory=list)


@dataclass
class AudioAssetInfo:
    """Metadata for an audio asset reference."""
    clip_ref: str
    game_objects: list[str] = field(default_factory=list)


@dataclass
class AssetManifest:
    """Collection of all asset references found in a scene."""
    sprites: dict[str, SpriteAssetInfo] = field(default_factory=dict)
    audio: dict[str, AudioAssetInfo] = field(default_factory=dict)
    tags_used: list[str] = field(default_factory=list)

    @classmethod
    def from_scene(cls) -> AssetManifest:
        """Scan the current scene's global registry for asset references."""
        manifest = cls()
        tags = set()

        for go in _game_objects.values():
            if not go.active:
                continue

            tags.add(go.tag)

            # Scan SpriteRenderers
            for sr in go.get_components(SpriteRenderer):
                if sr.asset_ref is not None:
                    if sr.asset_ref not in manifest.sprites:
                        manifest.sprites[sr.asset_ref] = SpriteAssetInfo(
                            asset_ref=sr.asset_ref,
                            color_hint=sr.color,
                            size=(sr.size.x, sr.size.y),
                            sorting_order=sr.sorting_order,
                        )
                    manifest.sprites[sr.asset_ref].game_objects.append(go.name)

            # Scan AudioSources
            for audio in go.get_components(AudioSource):
                if audio.clip_ref is not None:
                    if audio.clip_ref not in manifest.audio:
                        manifest.audio[audio.clip_ref] = AudioAssetInfo(
                            clip_ref=audio.clip_ref,
                        )
                    manifest.audio[audio.clip_ref].game_objects.append(go.name)

        manifest.tags_used = sorted(t for t in tags if t != "Untagged")
        return manifest

    def to_dict(self) -> dict[str, Any]:
        """Convert to a JSON-serializable dictionary."""
        return {
            "sprites": {k: asdict(v) for k, v in self.sprites.items()},
            "audio": {k: asdict(v) for k, v in self.audio.items()},
            "tags_used": self.tags_used,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_json(cls, text: str) -> AssetManifest:
        """Deserialize from JSON string."""
        data = json.loads(text)
        manifest = cls()
        for k, v in data.get("sprites", {}).items():
            manifest.sprites[k] = SpriteAssetInfo(**v)
        for k, v in data.get("audio", {}).items():
            manifest.audio[k] = AudioAssetInfo(**v)
        manifest.tags_used = data.get("tags_used", [])
        return manifest


def generate_manifest_from_setup(setup_func: callable) -> AssetManifest:
    """Run a setup function and extract the asset manifest from the resulting scene.

    Clears the engine state before and after to avoid cross-contamination.
    """
    from src.engine.core import _clear_registry
    from src.engine.lifecycle import LifecycleManager
    from src.engine.physics.physics_manager import PhysicsManager

    # Clean slate
    _clear_registry()
    LifecycleManager._instance = None
    PhysicsManager._instance = None

    # Run setup to populate the scene
    setup_func()

    # Extract manifest
    manifest = AssetManifest.from_scene()

    # Cleanup
    _clear_registry()
    LifecycleManager._instance = None
    PhysicsManager._instance = None

    return manifest


def main():
    """CLI entry point.

    Supports two modes:
      python -m src.assets.manifest examples/breakout/run_breakout.py
      python -m src.assets.manifest angry_birds [--level level_1]
    """
    import sys
    import importlib.util
    import os
    from pathlib import Path

    args = sys.argv[1:]
    if not args:
        print("Usage: python -m src.assets.manifest <run_file.py|example_name> [--output path.json] [--level name]")
        sys.exit(1)

    target = args[0]
    output_path = None
    level_name = "level_1"
    if "--output" in args:
        idx = args.index("--output")
        output_path = Path(args[idx + 1])
    if "--level" in args:
        idx = args.index("--level")
        level_name = args[idx + 1]

    setup_func = None
    module_path = Path(target)

    if module_path.exists() and module_path.suffix == ".py":
        # Load the run file — it adds its own parent to sys.path
        sys.path.insert(0, os.getcwd())
        sys.path.insert(0, str(module_path.parent.resolve()))
        spec = importlib.util.spec_from_file_location("setup_module", str(module_path.resolve()))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find setup function
        for name in ["setup_scene", "setup_level_1"]:
            if hasattr(module, name):
                setup_func = getattr(module, name)
                break

        if setup_func is None and hasattr(module, "register_all_levels"):
            module.register_all_levels()
            from src.engine.scene import SceneManager
            setup_func = SceneManager._scenes.get(level_name)
    else:
        # Try as an example name: "angry_birds" -> examples/angry_birds/
        example_dir = Path("examples") / target
        run_file = example_dir / f"run_{target}.py"
        if run_file.exists():
            sys.path.insert(0, os.getcwd())
            sys.path.insert(0, str(example_dir.resolve()))
            spec = importlib.util.spec_from_file_location("setup_module", str(run_file.resolve()))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name in ["setup_scene", "setup_level_1"]:
                if hasattr(module, name):
                    setup_func = getattr(module, name)
                    break

    if setup_func is None:
        print(f"ERROR: Could not find setup function in {target}")
        sys.exit(1)

    manifest = generate_manifest_from_setup(setup_func)

    print(f"Found {len(manifest.sprites)} sprite assets, {len(manifest.audio)} audio assets")
    print(f"Tags used: {manifest.tags_used}")

    for name, info in manifest.sprites.items():
        print(f"  sprite: {name} (color={info.color_hint}, size={info.size}, used by {len(info.game_objects)} objects)")
    for name, info in manifest.audio.items():
        print(f"  audio: {name} (used by {len(info.game_objects)} objects)")

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(manifest.to_json(), encoding="utf-8")
        print(f"\nManifest written to {output_path}")
    else:
        print("\n" + manifest.to_json())


if __name__ == "__main__":
    main()
