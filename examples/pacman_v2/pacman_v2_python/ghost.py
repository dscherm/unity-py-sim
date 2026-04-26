from __future__ import annotations
"""Ghost — central controller aggregating all ghost behaviors.

Port of zigurous Ghost.cs. Holds references to home/scatter/chase/frightened.
Handles collision with Pacman (eat or be eaten).

Lesson applied: Awake runs regardless of enabled state.
Lesson applied: component auto-registration (no manual register calls).
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector2

from src.engine.rendering.renderer import SpriteRenderer

from .movement import Movement
from .ghost_home import GhostHome
from .ghost_scatter import GhostScatter
from .ghost_chase import GhostChase
from .ghost_frightened import GhostFrightened
from .ghost_eyes import GhostEyes


PACMAN_LAYER: int = 3


class Ghost(MonoBehaviour):
    movement: Movement | None = None
    home: GhostHome | None = None
    scatter: GhostScatter | None = None
    chase: GhostChase | None = None
    frightened: GhostFrightened | None = None
    eyes: GhostEyes | None = None

    initial_behavior: object = None  # GhostBehavior component to start with
    target: GameObject | None = None   # What this ghost chases (usually Pacman)
    points: int = 200

    def awake(self) -> None:
        self.movement = self.get_component(Movement)

    def start(self) -> None:
        # Look up behaviors in start() — they're added after Ghost in scene setup,
        # so they don't exist yet during awake(). This was a v1 lesson.
        self.home = self.get_component(GhostHome)
        self.scatter = self.get_component(GhostScatter)
        self.chase = self.get_component(GhostChase)
        self.frightened = self.get_component(GhostFrightened)

        # Find eyes on child object
        for child in self.transform.children:
            eyes = child.game_object.get_component(GhostEyes)
            if eyes:
                self.eyes = eyes
                break

        self.reset_state()

    def reset_state(self) -> None:
        self.game_object.active = True
        if self.movement:
            self.movement.reset_state()

        # Match V1 exactly: only disable frightened and chase, then enable scatter.
        # Do NOT disable scatter here — that triggers GhostScatter.on_disable which
        # enables chase, leaving both scatter+chase active simultaneously.
        if self.frightened:
            self.frightened.disable()
        if self.chase:
            self.chase.disable()

        # Enable scatter (default cycle entry) — this is the V1 pattern
        if self.scatter:
            self.scatter.enable()

        if self.home is not self.initial_behavior:
            if self.home:
                self.home.disable()

        if self.initial_behavior is not None:
            self.initial_behavior.enable()

    def on_collision_enter_2d(self, collision) -> None:
        other_go = getattr(collision, "game_object", collision)
        if other_go.layer == PACMAN_LAYER:
            if self.frightened and self.frightened.enabled and not self.frightened.eaten:
                # Ghost is eaten by Pacman
                from .game_manager import GameManager
                if GameManager.instance:
                    GameManager.instance.ghost_eaten(self)
            else:
                # Pacman is eaten by ghost
                from .game_manager import GameManager
                if GameManager.instance:
                    GameManager.instance.pacman_eaten()
