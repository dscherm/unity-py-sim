from __future__ import annotations
"""AnimatedSprite — frame-based sprite animation via timer.

Line-by-line port of AnimatedSprite.cs from zigurous/unity-pacman-tutorial.
"""

from src.engine.core import MonoBehaviour
from src.engine.rendering.renderer import SpriteRenderer


class AnimatedSprite(MonoBehaviour):
    sprite_refs: list[str]  # asset_ref names for each frame
    animation_time: float = 0.25
    loop: bool = True

    sprite_renderer: SpriteRenderer | None = None
    _animation_frame: int = 0
    _timer: float = 0.0

    def __init__(self) -> None:
        super().__init__()
        self.sprite_refs = []

    def awake(self) -> None:
        self.sprite_renderer = self.get_component(SpriteRenderer)

    def on_enable(self) -> None:
        if self.sprite_renderer is not None:
            self.sprite_renderer.enabled = True

    def on_disable(self) -> None:
        if self.sprite_renderer is not None:
            self.sprite_renderer.enabled = False

    def update(self) -> None:
        from src.engine.time_manager import Time

        self._timer += Time.delta_time
        if self._timer >= self.animation_time:
            self._timer -= self.animation_time
            self._advance()

    def _advance(self) -> None:
        if self.sprite_renderer is None or not self.sprite_renderer.enabled:
            return

        self._animation_frame += 1

        if self._animation_frame >= len(self.sprite_refs) and self.loop:
            self._animation_frame = 0

        if 0 <= self._animation_frame < len(self.sprite_refs):
            self.sprite_renderer.asset_ref = self.sprite_refs[self._animation_frame]

    def restart(self) -> None:
        self._animation_frame = -1
        self._advance()
