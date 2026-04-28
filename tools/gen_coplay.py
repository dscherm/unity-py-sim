"""Generic CoPlay MCP scene-reconstruction script generator.

Runs an example's setup_scene(), serializes the resulting scene graph, and
feeds it (plus its asset mapping) into src.exporter.coplay_generator to
produce editor-C# scripts for CoPlay MCP.

Usage:
    python tools/gen_coplay.py \\
        --runner examples/pacman_v2/run_pacman_v2.py \\
        --mapping data/mappings/pacman_mapping.json \\
        --namespace PacmanV2 \\
        --output data/generated/pacman_v2_project/Assets/Editor/GeneratedSceneSetup.cs \\
        --validation-output data/generated/pacman_v2_project/Assets/Editor/GeneratedSceneValidation.cs

The runner file must define ``setup_scene()`` at module scope.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Push REPO_ROOT onto sys.path so `from src...` imports below resolve
# when this script is invoked directly (`python tools/gen_coplay.py`).
# _load_runner() also inserts the runner's parent for its relative
# imports.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _load_runner(runner_path: Path):
    """Import a runner module by path so its top-level sys.path edits run.
    Returns the loaded module; caller invokes ``mod.setup_scene()`` itself."""
    # Make the runner's own directory importable (examples/*/ often import
    # sibling python packages via bare module names)
    sys.path.insert(0, str(runner_path.parent))
    sys.path.insert(0, str(REPO_ROOT))

    spec = importlib.util.spec_from_file_location("coplay_runner", runner_path)
    assert spec and spec.loader, f"Cannot load {runner_path}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules["coplay_runner"] = mod
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runner", required=True,
                        help="Path to an examples/*/run_*.py that exposes setup_scene().")
    parser.add_argument("--mapping", default=None,
                        help="Path to data/mappings/*_mapping.json (optional).")
    parser.add_argument("--output", required=True,
                        help="Where to write GeneratedSceneSetup.cs.")
    parser.add_argument("--validation-output", default=None,
                        help="Optional path for GeneratedSceneValidation.cs.")
    parser.add_argument("--scene-json", default=None,
                        help="Optional dump of the serialized scene JSON.")
    # Default is sentinel `None` so we can tell "user said empty string"
    # apart from "user didn't pass the flag" — the latter triggers
    # auto-derivation from the runner stem against GAME_NAMESPACES.
    parser.add_argument(
        "--namespace",
        default=None,
        help="C# namespace for MonoBehaviour components in the output. "
             "Defaults to the per-game namespace the translator emits "
             "(derived from the runner stem via GAME_NAMESPACES). Pass "
             "an explicit empty string to regenerate against output "
             "that isn't wrapped.",
    )
    parser.add_argument(
        "--source", default=None,
        help="Python package dir whose MonoBehaviours become the translated-class "
             "registry passed to the scene serializer (drops inline handlers "
             "defined in the runner script — see coplay_generator_gaps.md gap 4). "
             "If omitted, derived as the sibling '{game}_python/' directory of "
             "the runner when that exists; otherwise the filter is disabled.",
    )
    args = parser.parse_args()

    runner_path = Path(args.runner).resolve()

    # Derive default namespace from the runner stem when the flag wasn't
    # passed.  Mirrors `tools/pipeline.py`'s game→namespace mapping so
    # CoPlay regen produces editor scripts that resolve against the
    # translator's `namespace <Game> { ... }` wrapper.  Empty string
    # (passed explicitly) keeps the legacy un-namespaced behavior.
    if args.namespace is None:
        from src.translator.project_translator import GAME_NAMESPACES
        stem = runner_path.stem
        derived_game = stem[4:] if stem.startswith("run_") else stem
        args.namespace = GAME_NAMESPACES.get(derived_game, "")

    runner = _load_runner(runner_path)
    assert hasattr(runner, "setup_scene"), (
        f"{runner_path} must define setup_scene() at module scope."
    )

    from src.engine.core import _clear_registry
    _clear_registry()
    runner.setup_scene()

    from src.exporter.scene_serializer import serialize_scene
    from src.exporter.coplay_generator import (
        generate_scene_script,
        generate_validation_script,
    )
    from src.translator.project_translator import get_translated_class_names

    # Build the translated-class registry so the serializer drops inline
    # MonoBehaviours defined in run_*.py (which have no .cs counterpart).
    # See coplay_generator_gaps.md gap 4.
    source_dir: Path | None = Path(args.source).resolve() if args.source else None
    if source_dir is None:
        # Derive: examples/<game>/run_<game>.py → examples/<game>/<game>_python/
        stem = runner_path.stem
        derived = runner_path.parent / (
            stem[4:] + "_python" if stem.startswith("run_") else f"{stem}_python"
        )
        if derived.is_dir():
            source_dir = derived

    translated_classes: set[str] | None = None
    if source_dir and source_dir.is_dir():
        translated_classes = get_translated_class_names(source_dir)

    scene_data = serialize_scene(translated_classes=translated_classes)
    mapping_data = None
    if args.mapping:
        mapping_data = json.loads(Path(args.mapping).read_text(encoding="utf-8"))

    if args.scene_json:
        p = Path(args.scene_json)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(scene_data, indent=2), encoding="utf-8")

    cs_code = generate_scene_script(scene_data, mapping_data, namespace=args.namespace)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(cs_code, encoding="utf-8")
    print(f"[ok] CoPlay scene setup -> {out} ({out.stat().st_size} bytes)")

    if args.validation_output:
        val_cs = generate_validation_script(scene_data, namespace=args.namespace)
        v = Path(args.validation_output)
        v.parent.mkdir(parents=True, exist_ok=True)
        v.write_text(val_cs, encoding="utf-8")
        print(f"[ok] CoPlay validation -> {v} ({v.stat().st_size} bytes)")

    go_count = len(scene_data.get("game_objects", []))
    sprite_count = len(mapping_data.get("sprites", {})) if mapping_data else 0
    registry_info = (
        f", {len(translated_classes)} translated classes in registry"
        if translated_classes is not None else
        " (no translated-class filter)"
    )
    print(f"[info] {go_count} GameObjects serialized, "
          f"{sprite_count} sprite mappings{registry_info}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
