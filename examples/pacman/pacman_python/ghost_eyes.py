"""GhostEyes — swap eye sprite based on movement direction.

Line-by-line port of GhostEyes.cs from zigurous/unity-pacman-tutorial.
"""

from src.engine.core import MonoBehaviour
from src.engine.rendering.renderer import SpriteRenderer
from pacman_python.movement import Movement


class GhostEyes(MonoBehaviour):
    up_ref: str = "ghost_eyes_up"
    down_ref: str = "ghost_eyes_down"
    left_ref: str = "ghost_eyes_left"
    right_ref: str = "ghost_eyes_right"

    sprite_renderer: SpriteRenderer | None = None
    movement: Movement | None = None

    def awake(self) -> None:
        self.sprite_renderer = self.get_component(SpriteRenderer)
        # Movement is on the parent ghost GO
        self.movement = self.game_object.get_component(Movement)
        if self.movement is None and self.transform.parent is not None:
            parent_go = self.transform.parent.game_object
            if parent_go is not None:
                self.movement = parent_go.get_component(Movement)

    def update(self) -> None:
        if self.sprite_renderer is None or self.movement is None:
            return

        d = self.movement.direction
        if d.y > 0:
            self.sprite_renderer.asset_ref = self.up_ref
        elif d.y < 0:
            self.sprite_renderer.asset_ref = self.down_ref
        elif d.x < 0:
            self.sprite_renderer.asset_ref = self.left_ref
        elif d.x > 0:
            self.sprite_renderer.asset_ref = self.right_ref
