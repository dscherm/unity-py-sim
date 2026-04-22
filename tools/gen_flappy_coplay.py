"""Generate a CoPlay MCP scene-reconstruction script for Flappy Bird.

Runs the Python Flappy Bird setup_scene(), serializes the resulting scene
graph, and feeds it (plus data/mappings/flappy_bird_mapping.json) into
src.exporter.coplay_generator to produce an editor-C# script that will
reconstruct the scene in Unity with original assets wired.

Usage:
    python tools/gen_flappy_coplay.py \
        --output data/generated/flappy_bird_project/Assets/Editor/GeneratedSceneSetup.cs \
        [--validation-output data/generated/flappy_bird_project/Assets/Editor/GeneratedSceneValidation.cs]

Running this module as __main__ only — never imported.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FLAPPY_DIR = REPO_ROOT / "examples" / "flappy_bird"


def _load_flappy_setup():
    """Import examples/flappy_bird/run_flappy_bird.py under a synthetic name
    so its top-level ``sys.path.insert(...)`` runs and ``setup_scene`` is
    available without triggering the pygame run loop."""
    # Make examples/flappy_bird/ importable for its relative modules
    sys.path.insert(0, str(FLAPPY_DIR))
    sys.path.insert(0, str(REPO_ROOT))

    path = FLAPPY_DIR / "run_flappy_bird.py"
    spec = importlib.util.spec_from_file_location("rfb_runner", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rfb_runner"] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_mapping() -> dict:
    path = REPO_ROOT / "data" / "mappings" / "flappy_bird_mapping.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _translated_class_names(package_dir: Path) -> set[str]:
    """Return the set of MonoBehaviour class names the translator will emit
    .cs files for when run on ``package_dir``.  Used to filter the scene
    serializer output so that inline MonoBehaviours defined in
    ``run_*.py`` (which aren't translated) don't leak into the Unity
    scene.  See coplay_generator_gaps.md gap 4.
    """
    from src.translator.python_parser import parse_python_file

    names: set[str] = set()
    for py in sorted(package_dir.glob("*.py")):
        if py.name == "__init__.py":
            continue
        parsed = parse_python_file(py)
        for cls in parsed.classes:
            if cls.is_monobehaviour:
                names.add(cls.name)
    return names


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(REPO_ROOT / "data" / "generated" / "flappy_bird_project"
                    / "Assets" / "Editor" / "GeneratedSceneSetup.cs"),
    )
    parser.add_argument("--validation-output", default=None,
                        help="Optional path for the companion validation script.")
    parser.add_argument("--scene-json", default=None,
                        help="Optional path to also dump the serialized scene JSON.")
    parser.add_argument("--namespace", default="",
                        help="C# namespace wrapper for emitted component refs. "
                             "Leave empty (default) when translated scripts live "
                             "in the global namespace — which the current translator "
                             "always emits.")
    args = parser.parse_args()

    runner = _load_flappy_setup()
    # Reset engine registry so re-runs stay clean
    from src.engine.core import _clear_registry
    _clear_registry()
    runner.setup_scene()

    from src.exporter.scene_serializer import serialize_scene
    from src.exporter.coplay_generator import (
        generate_scene_script,
        generate_validation_script,
    )

    # Build the translated-class registry from the Flappy Bird package so
    # the serializer drops inline MonoBehaviours from run_flappy_bird.py
    # (PlayButtonHandler, QuitHandler) that have no .cs counterpart.
    # See coplay_generator_gaps.md gap 4.
    translated_classes = _translated_class_names(FLAPPY_DIR / "flappy_bird_python")
    scene_data = serialize_scene(translated_classes=translated_classes)
    mapping_data = _load_mapping()

    if args.scene_json:
        Path(args.scene_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.scene_json).write_text(
            json.dumps(scene_data, indent=2), encoding="utf-8",
        )

    cs_code = generate_scene_script(
        scene_data, mapping_data, namespace=args.namespace,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(cs_code, encoding="utf-8")
    print(f"[ok] CoPlay scene setup -> {out} ({out.stat().st_size} bytes)")

    if args.validation_output:
        val_cs = generate_validation_script(scene_data, namespace=args.namespace)
        vout = Path(args.validation_output)
        vout.parent.mkdir(parents=True, exist_ok=True)
        vout.write_text(val_cs, encoding="utf-8")
        print(f"[ok] CoPlay validation -> {vout} ({vout.stat().st_size} bytes)")

    go_count = len(scene_data.get("game_objects", []))
    print(f"[info] {go_count} GameObjects serialized, "
          f"{len(mapping_data.get('sprites', {}))} sprite mappings, "
          f"{len(translated_classes)} translated classes in registry: "
          f"{sorted(translated_classes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
