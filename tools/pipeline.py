"""End-to-end pipeline: translate → scaffold → validate.

Generates a complete Unity project from a Python game.

Usage:
    python tools/pipeline.py breakout
    python tools/pipeline.py breakout --output data/generated/breakout_project
    python tools/pipeline.py breakout --validate
    python tools/pipeline.py breakout --scaffold --validate
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Game source directory mapping
_GAME_PATHS = {
    "pong": "examples/pong/pong_python",
    "breakout": "examples/breakout/breakout_python",
    "space_invaders": "examples/space_invaders/space_invaders_python",
    "angry_birds": "examples/angry_birds/angry_birds_python",
    "fsm_platformer": "examples/fsm_platformer/fsm_platformer_python",
    "pacman": "examples/pacman/pacman_python",
    "pacman_v2": "examples/pacman_v2/pacman_v2_python",
    "flappy_bird": "examples/flappy_bird/flappy_bird_python",
}

# GAME_NAMESPACES lives in src.translator.project_translator so the
# CoPlay generators can also default to the same per-game namespace
# without duplicating the table.  Keep `_NAMESPACES` as a local alias
# so the rest of this script reads naturally.
from src.translator.project_translator import GAME_NAMESPACES as _NAMESPACES  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="End-to-end Python → Unity pipeline")
    parser.add_argument("game", choices=sorted(_GAME_PATHS.keys()), help="Game to process")
    parser.add_argument("--output", "-o", help="Output directory (default: data/generated/<game>_project)")
    parser.add_argument("--unity-version", type=int, default=6, help="Unity version (5 or 6)")
    parser.add_argument("--input-system", default="new", choices=["new", "legacy"], help="Input system")
    parser.add_argument("--validate", action="store_true", help="Run structural + convention gates")
    parser.add_argument("--no-scaffold", action="store_true", help="Skip Unity project scaffolding")
    args = parser.parse_args()

    game = args.game
    src_path = _GAME_PATHS[game]
    namespace = _NAMESPACES[game]
    output_dir = Path(args.output) if args.output else ROOT / "data" / "generated" / f"{game}_project"

    start = time.time()
    print(f"{'=' * 60}")
    print(f"PIPELINE: {game} → {output_dir}")
    print(f"{'=' * 60}")

    # Step 1: Translate
    print(f"\n--- Step 1: Translate ({src_path}) ---")
    from src.translator.project_translator import translate_project
    cs_files = translate_project(src_path, input_system=args.input_system, unity_version=args.unity_version, namespace=namespace)
    cs_only = {k: v for k, v in cs_files.items() if k.endswith(".cs")}
    print(f"  {len(cs_only)} C# files generated")

    # Step 2: Scaffold
    if not args.no_scaffold:
        print(f"\n--- Step 2: Scaffold ({output_dir}) ---")
        from src.exporter.project_scaffolder import scaffold_project

        # Extract tags from translated code
        tags = set()
        for code in cs_only.values():
            import re
            for m in re.finditer(r'\.tag\s*=\s*"(\w+)"', code):
                tags.add(m.group(1))
            for m in re.finditer(r'CompareTag\("(\w+)"\)', code):
                tags.add(m.group(1))
            for m in re.finditer(r'FindWithTag\("(\w+)"\)', code):
                tags.add(m.group(1))
            for m in re.finditer(r'FindGameObjectsWithTag\("(\w+)"\)', code):
                tags.add(m.group(1))

        # Detect prefab candidates so scaffold_project can regenerate
        # .prefab YAML with deterministic script-binding GUIDs matching the
        # fresh .cs.meta files.  Without this, stale .prefab files from
        # earlier runs keep their old m_Script GUIDs (flappy_bird_deploy.md
        # gap 7) and Unity silently drops the MonoBehaviour on Instantiate.
        try:
            from src.exporter.prefab_detector import detect_prefabs
            prefab_data = detect_prefabs(str(ROOT / src_path))
        except Exception as e:
            print(f"  (prefab detection skipped: {e})")
            prefab_data = None

        scaffold_project(
            game_name=game,
            output_dir=output_dir,
            cs_files=cs_files,
            tags=sorted(tags) if tags else None,
            prefab_data=prefab_data,
        )
        # Count output files
        file_count = sum(1 for _ in output_dir.rglob("*") if _.is_file())
        print(f"  {file_count} files in Unity project")
    else:
        # Just write C# files to output
        cs_dir = output_dir / "cs"
        cs_dir.mkdir(parents=True, exist_ok=True)
        for name, code in cs_files.items():
            (cs_dir / name).write_text(code, encoding="utf-8")
        print(f"  Scaffold skipped — {len(cs_files)} files written to {cs_dir}")

    # Step 3: Validate
    failed_steps = []
    if args.validate:
        print("\n--- Step 3: Structural Gate ---")
        from src.gates.structural_gate import validate_csharp
        total_errors = 0
        for name, code in cs_only.items():
            result = validate_csharp(code)
            if result.error_count > 0:
                total_errors += result.error_count
                print(f"  FAIL {name}: {result.error_count} parse errors")
        print(f"  {len(cs_only)} files, {total_errors} parse errors")
        if total_errors > 0:
            failed_steps.append("structural")

        print("\n--- Step 4: Convention Gate ---")
        from src.gates.convention_gate import check_conventions
        total_violations = 0
        total_checks = 0
        for name, code in cs_only.items():
            if len(code) < 50:
                continue
            result = check_conventions(code)
            total_checks += result.checks_run
            total_violations += len(result.violations)
        pct = ((total_checks - total_violations) / total_checks * 100) if total_checks > 0 else 0
        print(f"  {total_checks} checks, {total_violations} violations ({pct:.0f}% pass)")

    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    if failed_steps:
        print(f"PIPELINE FAILED — {', '.join(failed_steps)}")
    else:
        print("PIPELINE PASSED")
    print(f"Elapsed: {elapsed:.1f}s")
    print(f"{'=' * 60}")

    return 1 if failed_steps else 0


if __name__ == "__main__":
    sys.exit(main())
