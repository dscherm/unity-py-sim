"""CLI entry point for Unity project scaffolder.

Usage:
    python -m src.exporter.scaffold --game breakout --output output/breakout_unity
"""

from __future__ import annotations

import argparse
from pathlib import Path

from src.exporter.project_scaffolder import scaffold_project
from src.translator.project_translator import translate_project


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a Unity project from translated Python game files.",
    )
    parser.add_argument(
        "--game",
        required=True,
        help="Name of the game to scaffold.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory for the Unity project.",
    )
    parser.add_argument(
        "--source",
        default=None,
        help="Python source directory to translate. If omitted, scaffolds with empty files.",
    )
    parser.add_argument(
        "--tags",
        nargs="*",
        default=None,
        help="Custom Unity tags to add to TagManager.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)

    if args.source:
        cs_files = translate_project(args.source)
    else:
        cs_files = {}

    result = scaffold_project(
        args.game,
        output_dir,
        cs_files=cs_files,
        tags=args.tags,
    )
    print(f"Scaffolded Unity project at: {result}")


if __name__ == "__main__":
    main()
