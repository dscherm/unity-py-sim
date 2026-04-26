"""Invader — single alien with score value and sprite animation.

Line-by-line port of: zigurous/Invader.cs
"""
from __future__ import annotations

from src.engine.core import MonoBehaviour, GameObject
from src.engine.time_manager import Time
from src.engine.rendering.renderer import SpriteRenderer


class Invader(MonoBehaviour):
    """[RequireComponent(typeof(SpriteRenderer))]
    [RequireComponent(typeof(Rigidbody2D))]
    [RequireComponent(typeof(BoxCollider2D))]"""

    def __init__(self) -> None:
        super().__init__()
        # public Sprite[] animationSprites — we use colors instead of Sprite assets
        self.animation_sprites: list[tuple[int, int, int]] = []
        self.animation_time: float = 1.0
        self.score: int = 10

        # private SpriteRenderer spriteRenderer
        self.sprite_renderer: SpriteRenderer | None = None
        # private int animationFrame
        self.animation_frame: int = 0
        self._timer: float = 0.0

    def awake(self) -> None:
        # spriteRenderer = GetComponent<SpriteRenderer>()
        self.sprite_renderer = self.get_component(SpriteRenderer)
        # spriteRenderer.sprite = animationSprites[0]
        if self.sprite_renderer and self.animation_sprites:
            self.sprite_renderer.color = self.animation_sprites[0]

    def start(self) -> None:
        # InvokeRepeating(nameof(AnimateSprite), animationTime, animationTime)
        # Simulated via timer in update
        pass

    def update(self) -> None:
        # InvokeRepeating equivalent
        self._timer += Time.delta_time
        if self._timer >= self.animation_time:
            self._timer -= self.animation_time
            self._animate_sprite()

    def _animate_sprite(self) -> None:
        """private void AnimateSprite()"""
        self.animation_frame += 1

        # if (animationFrame >= animationSprites.Length)
        if self.animation_frame >= len(self.animation_sprites):
            self.animation_frame = 0

        # spriteRenderer.sprite = animationSprites[animationFrame]
        if self.sprite_renderer and self.animation_sprites:
            self.sprite_renderer.color = self.animation_sprites[self.animation_frame]

    def on_trigger_enter_2d(self, other: GameObject) -> None:
        from space_invaders_python.player import Layers

        # if (other.gameObject.layer == LayerMask.NameToLayer("Laser"))
        if other.layer == Layers.LASER:
            # GameManager.Instance.OnInvaderKilled(this)
            from space_invaders_python.game_manager import GameManager
            if GameManager.instance is not None:
                GameManager.instance.on_invader_killed(self)
        # else if (other.gameObject.layer == LayerMask.NameToLayer("Boundary"))
        elif other.layer == Layers.BOUNDARY:
            from space_invaders_python.game_manager import GameManager
            if GameManager.instance is not None:
                GameManager.instance.on_boundary_reached()
