"""Capture a single frame of any example to verify sprites render.

Usage:
    python tools/screenshot_game.py breakout
    python tools/screenshot_game.py flappy_bird [--frames 5]

Writes to data/lessons/<game>_sprite_check.png.
"""

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXAMPLES = {
    "breakout": "examples/breakout/run_breakout.py",
    "flappy_bird": "examples/flappy_bird/run_flappy_bird.py",
    "pong": "examples/pong/run_pong.py",
    "space_invaders": "examples/space_invaders/run_space_invaders.py",
    "angry_birds": "examples/angry_birds/run_angry_birds.py",
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("game", choices=sorted(EXAMPLES.keys()))
    parser.add_argument("--frames", type=int, default=8)
    parser.add_argument("--snapshot-at", type=int, default=5)
    args = parser.parse_args()

    script = ROOT / EXAMPLES[args.game]
    out_path = ROOT / "data" / "lessons" / f"{args.game}_sprite_check.png"

    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(script.parent))

    import pygame
    pygame.init()
    pygame.display.set_mode((800, 600))

    from src.engine.app import run
    spec = importlib.util.spec_from_file_location("run_mod", script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    frame = [0]
    original_flip = pygame.display.flip

    def hooked_flip():
        frame[0] += 1
        if frame[0] == args.snapshot_at:
            surf = pygame.display.get_surface()
            if surf is not None:
                pygame.image.save(surf, str(out_path))
                print(f"[screenshot] wrote {out_path}")
        original_flip()

    pygame.display.flip = hooked_flip

    run(mod.setup_scene, width=800, height=600, headless=False,
        max_frames=args.frames, title=f"{args.game} sprite check")
    print("[screenshot] done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
