"""Capture a single frame of flappy_bird to verify real sprites render.

Writes screenshot to data/lessons/flappy_bird_sprite_check.png.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "examples" / "flappy_bird"))

import pygame

pygame.init()
pygame.display.set_mode((800, 600))

from src.engine.app import run
from examples.flappy_bird.run_flappy_bird import setup_scene

out_path = ROOT / "data" / "lessons" / "flappy_bird_sprite_check.png"


def _screenshot_after_n_frames(n: int):
    frame_count = [0]
    original_flip = pygame.display.flip

    def hooked_flip():
        frame_count[0] += 1
        if frame_count[0] == n:
            surf = pygame.display.get_surface()
            if surf is not None:
                pygame.image.save(surf, str(out_path))
                print(f"[screenshot] wrote {out_path}")
        original_flip()

    pygame.display.flip = hooked_flip


_screenshot_after_n_frames(5)
run(setup_scene, width=800, height=600, headless=False, max_frames=8, title="Flappy Bird sprite check")
print(f"[screenshot] done, output at {out_path}")
