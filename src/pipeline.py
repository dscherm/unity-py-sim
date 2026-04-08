"""Unified pipeline CLI — translate -> scaffold -> gate in one command.

Usage:
    python -m src.pipeline --game breakout --output data/generated/breakout_project/ --validate

Steps:
    1. Translate all Python files in the source directory to C#
    2. Extract required Unity packages from translation output
    3. Scaffold a Unity project structure with the translated files
    4. (Optional) Run structural and convention gates on each .cs file
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="src.pipeline",
        description="Run the full translate -> scaffold -> gate pipeline.",
    )
    parser.add_argument(
        "--game",
        required=True,
        help="Name of the game (e.g. breakout, pong, space_invaders).",
    )
    parser.add_argument(
        "--source",
        default=None,
        help=(
            "Python source directory to translate. "
            "Defaults to examples/{game}/{game}_python."
        ),
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory for the scaffolded Unity project.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run structural and convention gates on generated C# files.",
    )
    parser.add_argument(
        "--tags",
        nargs="*",
        default=None,
        help="Custom Unity tags to add to TagManager.",
    )
    parser.add_argument(
        "--layers",
        nargs="*",
        default=None,
        help="Custom layers as name:index pairs (e.g. Player:8 Enemy:9).",
    )

    args = parser.parse_args(argv)

    # Resolve source directory
    source_dir = args.source or f"examples/{args.game}/{args.game}_python"
    source_path = Path(source_dir)

    if not source_path.is_dir():
        print(f"ERROR: Source directory not found: {source_path}", file=sys.stderr)
        return 1

    output_dir = Path(args.output)

    # Parse layers arg into dict
    layers: dict[str, int] | None = None
    if args.layers:
        layers = {}
        for pair in args.layers:
            if ":" in pair:
                name, idx = pair.rsplit(":", 1)
                try:
                    layers[name] = int(idx)
                except ValueError:
                    print(f"WARNING: Invalid layer spec '{pair}', skipping.",
                          file=sys.stderr)

    # ---- Step 1: Translate ----
    print(f"[1/3] Translating {source_path} ...")
    from src.translator.project_translator import translate_project

    cs_files = translate_project(source_path)

    cs_only = {k: v for k, v in cs_files.items() if k.endswith(".cs")}
    print(f"       Translated {len(cs_only)} file(s) to C#.")

    # ---- Step 2: Extract packages ----
    packages: list[str] = []
    pkg_json = cs_files.get("_required_packages.json")
    if pkg_json:
        try:
            pkg_list = json.loads(pkg_json)
            packages = [p["package"] for p in pkg_list]
            print(f"       Detected {len(packages)} required package(s): {', '.join(packages)}")
        except (json.JSONDecodeError, KeyError):
            pass

    # ---- Step 3: Scaffold ----
    print(f"[2/3] Scaffolding Unity project at {output_dir} ...")
    from src.exporter.project_scaffolder import scaffold_project

    scaffold_project(
        args.game,
        output_dir,
        cs_files=cs_files,
        tags=args.tags,
        layers=layers,
        required_packages=packages,
    )
    print("       Done.")

    # ---- Step 4: Validate (optional) ----
    if args.validate:
        print("[3/3] Running gates ...")
        exit_code = _run_gates(output_dir)
    else:
        print("[3/3] Skipped validation (use --validate to enable).")
        exit_code = 0

    # ---- Final report ----
    scripts_dir = output_dir / "Assets" / "_Project" / "Scripts"
    cs_count = len(list(scripts_dir.glob("*.cs"))) if scripts_dir.exists() else 0
    print(f"\nPipeline complete: {cs_count} C# file(s) in {scripts_dir}")

    return exit_code


def _run_gates(output_dir: Path) -> int:
    """Run structural and convention gates on all .cs files in the project."""
    from src.gates.structural_gate import validate_csharp
    from src.gates.convention_gate import check_conventions

    scripts_dir = output_dir / "Assets" / "_Project" / "Scripts"
    cs_files = sorted(scripts_dir.glob("*.cs")) if scripts_dir.exists() else []

    if not cs_files:
        print("       No .cs files found to validate.")
        return 1

    structural_pass = 0
    structural_fail = 0
    convention_pass = 0
    convention_fail = 0

    for cs_file in cs_files:
        source = cs_file.read_text(encoding="utf-8")
        name = cs_file.name

        # Structural gate
        s_result = validate_csharp(source)
        if s_result.valid:
            structural_pass += 1
        else:
            structural_fail += 1
            for err in s_result.errors[:3]:
                print(f"       STRUCTURAL FAIL [{name}]: {err}")

        # Convention gate
        c_result = check_conventions(source)
        if c_result.passed:
            convention_pass += 1
        else:
            convention_fail += 1
            for v in c_result.violations[:3]:
                print(f"       CONVENTION FAIL [{name}]: {v}")

    total = len(cs_files)
    print(f"\n       Structural: {structural_pass}/{total} pass, {structural_fail}/{total} fail")
    print(f"       Convention: {convention_pass}/{total} pass, {convention_fail}/{total} fail")

    if structural_fail > 0 or convention_fail > 0:
        print("       RESULT: FAIL")
        return 1
    else:
        print("       RESULT: PASS")
        return 0


if __name__ == "__main__":
    sys.exit(main())
