"""Post-process generated C# to fix known translator artifacts.

Removes Python docstrings, inline imports, and fixes common patterns
that the AST-based translator doesn't handle yet.
"""

import re
import sys
from pathlib import Path


def postprocess(source: str) -> str:
    """Clean up generated C# source."""
    lines = source.split("\n")
    cleaned = []

    for line in lines:
        stripped = line.strip()

        # Remove Python docstrings (triple-quoted strings)
        if stripped.startswith('"""') and stripped.endswith('""";'):
            continue
        if stripped.startswith("'''") and stripped.endswith("''';"):
            continue

        # Remove Python from...import statements
        if re.match(r"^\s*from\s+\w+.*import\s+", stripped):
            continue

        # Remove Python import statements
        if re.match(r"^\s*import\s+\w+", stripped) and "using" not in stripped:
            continue

        # Fix multi-line Vector2/Vector3 constructors:
        # new Vector2(;\n{\n  x,;\n  y,;\n}\n); → new Vector2(x, y);
        # (handled below as a multi-pass)

        cleaned.append(line)

    result = "\n".join(cleaned)

    # Fix broken multi-line constructors: new Vector2(\n{\n  val1,;\n  val2,;\n}\n);
    # Pattern: "new Vector2(;\n" followed by block
    result = re.sub(
        r"new (Vector[23])\(;\s*\n\s*\{\s*\n\s*([^;]+);\s*\n\s*([^;]+);\s*\n\s*\}\s*\n\s*\);",
        lambda m: f"new {m.group(1)}({m.group(2).strip().rstrip(',')}, {m.group(3).strip().rstrip(',')});",
        result,
    )

    # Fix "self" references that leaked through
    result = result.replace("(self)", "(this)")
    result = re.sub(r"\bself\b", "this", result)

    # Fix _snake_case method calls that should be PascalCase private methods
    # _move_right() → MoveRight(), _despawn() → Despawn(), etc.
    def fix_private_call(m):
        name = m.group(1)
        # Convert _snake_case to PascalCase
        parts = name.lstrip('_').split('_')
        pascal = ''.join(p.capitalize() for p in parts)
        return pascal + '('

    result = re.sub(r"_([a-z_]+)\(", fix_private_call, result)

    # Fix snake_case field access in method bodies
    for snake, camel in [
        ("left_destination", "leftDestination"),
        ("right_destination", "rightDestination"),
        ("invoke_timer", "invokeTimer"),
        ("invoke_pending", "invokePending"),
        ("invoke_callback", "invokeCallback"),
        ("invoke_delay", "invokeDelay"),
        ("cycle_time", "cycleTime"),
        ("sprite_renderer", "spriteRenderer"),
        ("box_collider", "boxCollider"),
        ("animation_frame", "animationFrame"),
        ("animation_sprites", "animationSprites"),
        ("animation_time", "animationTime"),
        ("game_over_ui", "gameOverUI"),
        ("score_text", "scoreText"),
        ("lives_text", "livesText"),
        ("mystery_ship", "mysteryShip"),
        ("speed_curve_max", "speedCurveMax"),
        ("missile_spawn_rate", "missileSpawnRate"),
        ("missile_timer", "missileTimer"),
        ("invader_children", "invaderChildren"),
        ("initial_position", "initialPosition"),
        ("amount_alive", "amountAlive"),
        ("amount_killed", "amountKilled"),
        ("percent_killed", "percentKilled"),
        ("total_count", "totalCount"),
        ("left_edge", "leftEdge"),
        ("right_edge", "rightEdge"),
        ("splat_radius", "splatRadius"),
        ("original_cells", "originalCells"),
        ("laser_prefab", "laserPrefab"),
        ("status_text", "statusText"),
    ]:
        result = result.replace(snake, camel)

    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python postprocess_cs.py <input_dir> [output_dir]")
        sys.exit(1)

    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else input_dir.parent / "cleaned_cs"
    output_dir.mkdir(parents=True, exist_ok=True)

    for cs_file in sorted(input_dir.glob("*.cs")):
        source = cs_file.read_text(encoding="utf-8")
        cleaned = postprocess(source)
        (output_dir / cs_file.name).write_text(cleaned, encoding="utf-8")
        print(f"  {cs_file.name} → {output_dir / cs_file.name}")


if __name__ == "__main__":
    main()
