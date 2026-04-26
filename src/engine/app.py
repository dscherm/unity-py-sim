"""Main game loop entry point — integrates all engine systems."""

from __future__ import annotations

from typing import Callable

from src.engine.time_manager import Time
from src.engine.input_manager import Input
from src.engine.lifecycle import LifecycleManager
from src.engine.physics.physics_manager import PhysicsManager
from src.engine.rendering.camera import Camera
from src.engine.rendering.display import DisplayManager
from src.engine.rendering.renderer import RenderManager
from src.engine.tweening import TweenManager


def run(
    scene_setup: Callable[[], None],
    width: int = 800,
    height: int = 600,
    target_fps: int = 60,
    title: str = "Unity-Py-Sim",
    headless: bool = False,
    max_frames: int | None = None,
) -> None:
    """Run the game loop.

    Args:
        scene_setup: Function that creates GameObjects for the scene.
        width: Display width in pixels.
        height: Display height in pixels.
        target_fps: Target frames per second.
        title: Window title.
        headless: If True, runs without display (for testing).
        max_frames: If set, stops after this many frames (for testing).
    """
    import pygame

    display = DisplayManager(width, height, title)
    DisplayManager._instance = display
    display.init(headless=headless)

    lifecycle = LifecycleManager.instance()
    physics = PhysicsManager.instance()

    Time._reset()
    Input._reset()
    TweenManager.reset()

    # User sets up the scene
    scene_setup()

    fixed_dt = Time._fixed_delta_time
    accumulator = 0.0
    clock = pygame.time.Clock() if not headless else None

    frames = 0
    running = True

    while running and not display.should_quit:
        if max_frames is not None and frames >= max_frames:
            break

        # Timing
        if clock is not None:
            dt = clock.tick(target_fps) / 1000.0
        else:
            dt = 1.0 / target_fps  # Simulated dt for headless mode

        Time._delta_time = dt
        Time._time += dt
        Time._frame_count += 1

        # Input
        display.poll_events()

        # Lifecycle: Awake + Start
        lifecycle.process_awake_queue()
        lifecycle.process_start_queue()

        # Fixed update + Physics
        accumulator += dt
        while accumulator >= fixed_dt:
            lifecycle.run_fixed_update()
            physics.step(fixed_dt)
            accumulator -= fixed_dt

        # Update + Tweens + LateUpdate
        lifecycle.run_update()
        TweenManager.tick(dt)
        lifecycle.run_late_update()

        # Render
        if not headless:
            cam = Camera.main
            bg = cam.background_color if cam else (0, 0, 0)
            display.clear(bg)
            RenderManager.render_all(display._surface, cam, width, height)
            # UI overlay (after world rendering)
            from src.engine.ui import UIRenderManager
            UIRenderManager.render_all(display._surface, width, height)
            display.flip()

        # Cleanup
        lifecycle.process_destroy_queue()

        frames += 1

    display.quit()
